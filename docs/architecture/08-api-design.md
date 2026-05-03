# API Design — FastAPI Backend

Base URL: `/api/v1/`
Authentication: JWT Bearer token (RS256). Tenant scoped via token claims.
Format: JSON. OpenAPI spec auto-generated at `/api/v1/docs`.

---

## Authentication & Authorization

```
POST   /api/v1/auth/login          → { access_token, refresh_token }
POST   /api/v1/auth/refresh        → { access_token }
POST   /api/v1/auth/logout
GET    /api/v1/auth/me             → User profile + role + tenant
```

**RBAC Roles:**

| Role | Access |
|------|--------|
| `superadmin` | All tenants, platform config |
| `tenant_admin` | Full access within their tenant |
| `agent` | Own leads + shared conversations, no admin config |
| `readonly` | Read-only dashboard access |

---

## Conversations & Chat

```
POST   /api/v1/conversations                          → Create conversation (returns session token)
GET    /api/v1/conversations/{id}                     → Get conversation + messages
GET    /api/v1/conversations/{id}/messages            → Paginated message list
POST   /api/v1/conversations/{id}/messages            → Send message (REST fallback)
WS     /api/v1/chat/stream/{conversation_id}          → WebSocket streaming chat
GET    /api/v1/conversations                          → List conversations (filterable)
PATCH  /api/v1/conversations/{id}                     → Update status, assign agent
POST   /api/v1/conversations/{id}/handoff             → Trigger human handoff
POST   /api/v1/conversations/{id}/resolve             → Resolve conversation
```

**POST /api/v1/conversations/{id}/messages — Request:**
```json
{
  "content": "I'm looking for a 2BR in Dubai Marina under 2M",
  "language": "en",
  "attachments": []
}
```

**Response (streamed via WebSocket):**
```json
{
  "role": "assistant",
  "content": "Great choice! Here are the top 3 listings...",
  "tool_outputs": {
    "property_search": {
      "results": [...],
      "total_count": 24
    }
  },
  "qualification_update": {
    "dimensions_collected": ["area", "bedrooms", "budget"],
    "score": 35,
    "status": "in_progress"
  }
}
```

---

## Leads

```
GET    /api/v1/leads                          → List leads (filter: status, channel, agent, date)
POST   /api/v1/leads                          → Create lead manually
GET    /api/v1/leads/{id}                     → Lead detail + qualification scores
PATCH  /api/v1/leads/{id}                     → Update lead fields
DELETE /api/v1/leads/{id}                     → Delete (with audit log)
GET    /api/v1/leads/{id}/conversations       → Lead's conversation history
GET    /api/v1/leads/{id}/appointments        → Lead's appointments
GET    /api/v1/leads/{id}/documents           → Lead's documents
GET    /api/v1/leads/{id}/score               → Current qualification scorecard
POST   /api/v1/leads/{id}/assign              → Assign to agent
POST   /api/v1/leads/{id}/crm-sync            → Force CRM sync
```

**Lead qualification scorecard (GET /leads/{id}/score):**
```json
{
  "total_score": 72,
  "status": "qualified",
  "dimensions": {
    "budget": { "score": 10, "max": 10, "value": "AED 2M–3M" },
    "property_type": { "score": 8, "max": 10, "value": "Apartment" },
    "purpose": { "score": 10, "max": 10, "value": "Buy" },
    "timeline": { "score": 8, "max": 10, "value": "3 months" },
    "nationality": { "score": 10, "max": 10, "value": "UK" },
    "pre_approval": { "score": 6, "max": 10, "value": false },
    "locations": { "score": 10, "max": 10, "value": ["Dubai Marina", "JBR"] },
    "contact_preference": { "score": 10, "max": 10, "value": "WhatsApp" }
  }
}
```

---

## Properties

```
GET    /api/v1/properties/search              → Hybrid search (text + filters + geo)
GET    /api/v1/properties/{id}                → Property detail
GET    /api/v1/properties/{slug}              → Property by SEO slug
POST   /api/v1/properties                     → Create property (admin/agent)
PATCH  /api/v1/properties/{id}                → Update property
DELETE /api/v1/properties/{id}                → Archive property
POST   /api/v1/properties/import/csv          → Bulk import via CSV upload
POST   /api/v1/properties/{id}/sync-crm       → Push to CRM
GET    /api/v1/properties/{id}/similar        → Vector similarity search
```

**GET /api/v1/properties/search — Query params:**
```
?q=3BR villa Palm Jumeirah
&property_type=villa
&purpose=buy
&price_min=3000000
&price_max=7000000
&bedrooms=3
&area=Palm+Jumeirah
&radius_km=2.0
&lat=25.1124
&lng=55.1390
&is_freehold=true
&is_off_plan=false
&is_golden_visa_eligible=true
&sort=relevance|price_asc|price_desc|newest
&page=1
&limit=20
```

---

## Appointments

```
GET    /api/v1/appointments                   → List appointments (agent view)
POST   /api/v1/appointments                   → Create appointment
GET    /api/v1/appointments/{id}              → Appointment detail
PATCH  /api/v1/appointments/{id}              → Update (reschedule, status)
DELETE /api/v1/appointments/{id}              → Cancel
GET    /api/v1/appointments/availability      → Agent available slots
  ?agent_id=...&date=2026-06-01&duration_min=60
```

---

## Documents

```
POST   /api/v1/documents/upload               → Upload document (multipart/form-data)
GET    /api/v1/documents/{id}                 → Get signed download URL
DELETE /api/v1/documents/{id}                 → Delete
POST   /api/v1/documents/{id}/sign            → Initiate DocuSign e-signature
GET    /api/v1/documents/{id}/sign/status     → Signature status
POST   /api/v1/documents/generate-pdf         → Generate PDF (WeasyPrint)
  body: { template: "mortgage_summary", data: {...} }
```

---

## Calculators

```
POST   /api/v1/calculators/mortgage
  body: { property_price_aed, down_payment_pct, interest_rate, term_years, nationality }
  → { monthly_payment, total_interest, total_cost, eligibility }

POST   /api/v1/calculators/roi
  body: { purchase_price_aed, annual_rent_aed, service_charges, management_fee_pct }
  → { gross_yield_pct, net_yield_pct, roi_5yr, roi_10yr }

POST   /api/v1/calculators/tco
  body: { property_price_aed, mortgage_term_years, ... }
  → { dld_fee, agent_fee, registration_fee, mortgage_processing, total_acquisition_cost }

POST   /api/v1/calculators/off-plan-payment
  body: { project_id, unit_price_aed, payment_plan_id }
  → { schedule: [{milestone, date, amount_aed}] }

POST   /api/v1/calculators/golden-visa
  body: { property_price_aed, mortgage_amount_aed, nationality }
  → { eligible: true/false, reason, threshold_aed: 2000000 }
```

---

## Admin — Tenant Configuration

```
GET    /api/v1/admin/tenant                   → Get tenant config
PATCH  /api/v1/admin/tenant                   → Update config (persona, settings)
GET    /api/v1/admin/users                    → List users
POST   /api/v1/admin/users                    → Invite user
PATCH  /api/v1/admin/users/{id}               → Update role/status
DELETE /api/v1/admin/users/{id}               → Remove user

GET    /api/v1/admin/guardrail-rules          → List guardrail rules
POST   /api/v1/admin/guardrail-rules          → Create rule
PATCH  /api/v1/admin/guardrail-rules/{id}     → Update rule
DELETE /api/v1/admin/guardrail-rules/{id}     → Delete rule

GET    /api/v1/admin/notification-templates   → List templates
POST   /api/v1/admin/notification-templates   → Create template
PATCH  /api/v1/admin/notification-templates/{id}
```

---

## Analytics

```
GET    /api/v1/analytics/overview             → KPI summary (leads, convs, bookings, handoffs)
  ?period=7d|30d|90d|custom&from=&to=

GET    /api/v1/analytics/funnel               → Lead funnel (unqualified→qualified→booked→closed)
GET    /api/v1/analytics/channels             → Breakdown by channel (web/whatsapp/telegram)
GET    /api/v1/analytics/agents               → Per-agent metrics (leads, convs, bookings)
GET    /api/v1/analytics/ai-quality           → LLM performance (intent accuracy, escalation rate)
GET    /api/v1/analytics/attribution          → UTM source breakdown
POST   /api/v1/analytics/report/pdf           → Generate weekly PDF report (async)
GET    /api/v1/analytics/report/{job_id}      → Download generated report
```

---

## Webhooks (Inbound)

```
POST   /api/v1/webhooks/whatsapp              → Meta webhook (HMAC-SHA256 verified)
POST   /api/v1/webhooks/telegram              → Telegram update
POST   /api/v1/webhooks/crm/zoho              → Zoho CRM event
POST   /api/v1/webhooks/crm/hubspot           → HubSpot event
POST   /api/v1/webhooks/calendar/google       → Google Calendar push notification
POST   /api/v1/webhooks/docusign              → DocuSign envelope event
```

All inbound webhooks verify signatures before processing. Async processing via RabbitMQ.

---

## Outbound Webhooks (Developer API)

Tenants can register webhook endpoints to receive platform events:

```
GET    /api/v1/developer/webhooks             → List registered endpoints
POST   /api/v1/developer/webhooks             → Register endpoint
  body: { url, events: ["lead.qualified", "appointment.booked", "handoff.triggered"] }
PATCH  /api/v1/developer/webhooks/{id}        → Update endpoint
DELETE /api/v1/developer/webhooks/{id}        → Remove endpoint
POST   /api/v1/developer/webhooks/{id}/test   → Send test event
```

**Webhook payload (HMAC-SHA256 signed via X-Signature header):**
```json
{
  "event": "lead.qualified",
  "tenant_id": "...",
  "timestamp": "2026-05-03T10:00:00Z",
  "data": {
    "lead_id": "...",
    "score": 82,
    "status": "qualified"
  }
}
```

---

## Health & System

```
GET    /health                                → { status: "ok", version, uptime }
GET    /api/v1/system/status                  → Service dependencies health check
GET    /metrics                               → Prometheus metrics endpoint
```

---

## API Versioning & Deprecation Policy

- URL-based versioning: `/api/v1/`, `/api/v2/`
- Breaking changes require a new version
- Old version supported for minimum 6 months after new version release
- Deprecation notice via `Sunset` and `Deprecation` response headers
- Migration guide published in developer docs before deprecation
