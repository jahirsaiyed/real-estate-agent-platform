# Real Estate Agent Platform

AI-powered real estate agent for the Dubai/UAE market. Multi-tenant, multi-channel, multilingual — qualifies leads, searches properties, books viewings, and escalates to human agents via WhatsApp, Telegram, and web chat.

---

## Architecture at a Glance

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 (App Router), Tailwind CSS, shadcn/ui |
| Backend | FastAPI (Python 3.12), Pydantic v2, SQLAlchemy 2 async |
| Orchestration | LangGraph + LangChain |
| LLM | `blissful_ishizaka_626/gemma4-cloud` via OpenRouter (model-agnostic) |
| Embeddings | OpenAI `text-embedding-3-small` (1536-dim) |
| Relational DB | PostgreSQL 16 + PostGIS |
| Vector DB | Qdrant Cloud |
| Cache / Sessions | Redis (Upstash) |
| Event Bus | RabbitMQ (CloudAMQP) |
| Object Storage | Cloudflare R2 |
| Job Scheduler | Celery + Redis Beat |
| Channels | WhatsApp Business API, Telegram Bot, Web Chat Widget |
| Hosting (MVP) | Vercel (frontend) + Render (backend) |
| Hosting (Prod) | AWS UAE `me-central-1` |

---

## Repository Structure

```
real-estate-agent/
├── backend/                    # FastAPI + LangGraph
│   ├── app/
│   │   ├── main.py             # App factory + Qdrant startup
│   │   ├── core/               # config, security (RS256 JWT), database
│   │   ├── api/v1/             # REST routes + WebSocket chat
│   │   │   ├── auth.py
│   │   │   ├── properties.py   # /search, CRUD, /similar
│   │   │   ├── conversations.py # REST + WS /chat/stream/{id}
│   │   │   ├── appointments.py # CRUD + /availability
│   │   │   ├── leads.py        # CRUD + /score + /assign + /crm-sync
│   │   │   ├── calculators.py  # mortgage, ROI, TCO, golden-visa
│   │   │   ├── webhooks.py     # WhatsApp + Telegram inbound
│   │   │   └── health.py
│   │   ├── models/             # 19 SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic v2 request/response schemas
│   │   ├── repositories/       # Data access layer (property, conv, appt, lead)
│   │   ├── services/           # embedding, notification, crm
│   │   └── agents/             # LangGraph graph + all nodes
│   │       ├── graph.py        # Full orchestrator
│   │       ├── state.py        # AgentState TypedDict
│   │       ├── memory.py       # Redis session + Qdrant long-term memory
│   │       ├── llm.py          # LLMProvider (model-agnostic)
│   │       └── nodes/          # property_search, booking, rag, qualification, handoff
│   ├── alembic/versions/       # 001 initial schema, 002 property slug
│   ├── scripts/seed.py         # Seed tenant + admin + sample properties
│   ├── tests/
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── render.yaml
├── frontend/                   # Next.js 14 admin shell
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/login/
│   │   │   └── (admin)/
│   │   │       ├── dashboard/
│   │   │       ├── properties/
│   │   │       ├── conversations/
│   │   │       ├── leads/
│   │   │       ├── appointments/
│   │   │       └── chat/[id]/  # Full chat interface
│   │   ├── components/
│   │   │   ├── admin/          # sidebar, header
│   │   │   └── chat/           # ChatWidget (embeddable React)
│   │   └── lib/                # api (Axios), auth helpers, utils
│   ├── public/widget.js        # Vanilla JS embeddable chat widget
│   ├── package.json
│   ├── Dockerfile
│   └── vercel.json
├── docker-compose.yml          # Local dev: postgres, redis, rabbitmq
├── .github/workflows/          # CI — backend + frontend
└── docs/                       # Architecture docs (01–09)
```

---

## Quick Start (Local Dev)

### Prerequisites

- Docker + Docker Compose
- Python 3.12 + [uv](https://github.com/astral-sh/uv)
- Node.js 20

### 1. Start backing services

```bash
docker compose up -d
# Starts: postgres (PostGIS 16), redis 7, rabbitmq 3.13
```

### 2. Configure environment

```bash
cp .env.example .env
# Required: OPENROUTER_API_KEY
# Optional: OPENAI_API_KEY (embeddings), WHATSAPP_TOKEN, TELEGRAM_BOT_TOKEN
#           ZOHO_CLIENT_ID, HUBSPOT_API_KEY, QDRANT_URL, LANGSMITH_API_KEY
```

### 3. Generate JWT keys (one-time)

```bash
mkdir -p backend/secrets
openssl genrsa -out backend/secrets/jwt_private.pem 2048
openssl rsa -in backend/secrets/jwt_private.pem -pubout -out backend/secrets/jwt_public.pem
```

### 4. Backend — install, migrate, seed, run

```bash
cd backend
uv sync --extra dev
alembic upgrade head          # runs migrations 001 + 002
python -m scripts.seed        # creates tenant + admin user + 5 sample properties
uvicorn app.main:app --reload
```

- API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/api/v1/docs`
- Admin login: `admin@sceptreestate.com` / `Admin@12345!`

### 5. Frontend

```bash
cd frontend
npm ci
npm run dev
```

Admin shell: `http://localhost:3000`

---

## Key API Endpoints

### Auth

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/auth/login` | Email + password → `access_token` + `refresh_token` |
| `POST` | `/api/v1/auth/refresh` | Rotate access token |
| `POST` | `/api/v1/auth/logout` | Revoke token (Redis JTI blocklist) |
| `GET` | `/api/v1/auth/me` | Current user profile + role + tenant |

### Properties

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/properties/search` | Hybrid text + geo + vector search |
| `GET` | `/api/v1/properties/{id}` | Property detail |
| `GET` | `/api/v1/properties/slug/{slug}` | Property by SEO slug |
| `GET` | `/api/v1/properties/{id}/similar` | Vector similarity results |
| `POST` | `/api/v1/properties` | Create property |
| `PATCH` | `/api/v1/properties/{id}` | Update property |
| `DELETE` | `/api/v1/properties/{id}` | Archive property |

### Conversations & Chat

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/conversations` | Create conversation |
| `GET` | `/api/v1/conversations` | List (filter by status, channel) |
| `POST` | `/api/v1/conversations/{id}/messages` | Send message (REST fallback) |
| `GET` | `/api/v1/conversations/{id}/messages` | Message history |
| `WS` | `/api/v1/chat/stream/{id}` | WebSocket streaming chat |
| `POST` | `/api/v1/conversations/{id}/handoff` | Trigger human handoff |
| `POST` | `/api/v1/conversations/{id}/resolve` | Resolve conversation |

### Leads

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/leads` | List (filter by qualification status) |
| `GET` | `/api/v1/leads/{id}/score` | 8-dimension qualification scorecard |
| `POST` | `/api/v1/leads/{id}/assign` | Assign to agent |
| `POST` | `/api/v1/leads/{id}/crm-sync` | Force Zoho/HubSpot sync |

### Appointments

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/appointments/availability` | Agent free slots for a date |
| `POST` | `/api/v1/appointments` | Book appointment |
| `PATCH` | `/api/v1/appointments/{id}` | Reschedule / update status |

### Calculators (no auth required)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/calculators/mortgage` | UAE mortgage (LTV, monthly payment) |
| `POST` | `/api/v1/calculators/roi` | Gross/net yield + 5yr/10yr ROI |
| `POST` | `/api/v1/calculators/tco` | Total cost of ownership (DLD, agent, registration) |
| `POST` | `/api/v1/calculators/golden-visa` | 10-year Golden Visa eligibility |

### Webhooks

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/webhooks/whatsapp` | Meta webhook verification |
| `POST` | `/api/v1/webhooks/whatsapp` | Inbound WhatsApp messages |
| `POST` | `/api/v1/webhooks/telegram` | Inbound Telegram Bot updates |

Full API reference: [`docs/architecture/08-api-design.md`](docs/architecture/08-api-design.md)

---

## Agent Graph

```
memory_loader
    └── intent_classifier
            ├── search    → property_search_agent → response_generator
            ├── book      → booking_agent         → response_generator
            ├── qualify   → qualification_agent   → response_generator
            ├── rag       → rag_agent             → response_generator
            ├── handoff   → handoff_agent         → END
            ├── smalltalk →                         response_generator
            └── unclear   → clarification_node   → response_generator
                                                        └── guardrails_node
                                                                ├── violation → response_generator (retry ≤2)
                                                                └── pass      → memory_update → END
```

| Node | Description |
|------|-------------|
| `memory_loader` | Loads Redis session (entities, qualification) + Qdrant lead memory |
| `intent_classifier` | Rule-based fast path + LLM JSON classification; extracts entities |
| `property_search_agent` | PostGIS bounding-box filter + Qdrant semantic search → RRF merge |
| `booking_agent` | Returns available agent slots or creates confirmed appointment |
| `qualification_agent` | Scores 8 dimensions (budget, type, purpose, timeline, nationality, pre-approval, locations, contact) |
| `rag_agent` | Semantic search over tenant knowledge base |
| `handoff_agent` | Multilingual escalation message + marks conversation for agent pickup |
| `response_generator` | LLM call with full context (memory + tool outputs + guardrail rules) |
| `guardrails_node` | Price guarantee removal, competitor redaction, blocked-topic detection |
| `memory_update` | Persists session to Redis + conversation chunk to Qdrant |

---

## Embeddable Chat Widget

Drop onto any website:

```html
<script src="https://your-domain.com/widget.js"
        data-api-base="https://api.your-domain.com"
        data-agent-name="Layla"
        data-primary-color="#2563eb">
</script>
```

Or use inside Next.js:

```tsx
import { ChatWidget } from "@/components/chat/ChatWidget";
<ChatWidget agentName="Layla" apiBase="https://api.your-domain.com" />
```

---

## Database

19 tables with row-level multi-tenancy (`tenant_id` on every table). PostGIS spatial columns on `properties` (`POINT`) and `locations` (`POLYGON`). Hybrid search combines SQL filters with Qdrant vector similarity via Reciprocal Rank Fusion.

Full schema ERD: [`docs/architecture/07-database-schema.md`](docs/architecture/07-database-schema.md)

---

## RBAC

| Role | Access |
|------|--------|
| `superadmin` | All tenants, platform config |
| `tenant_admin` | Full access within their tenant |
| `agent` | Own leads + shared conversations |
| `readonly` | Read-only dashboard access |

---

## CI/CD

| Workflow | Trigger | Steps |
|----------|---------|-------|
| `backend-ci.yml` | push/PR to `main`, `develop` | ruff → mypy → alembic upgrade → pytest --cov |
| `frontend-ci.yml` | push/PR to `main`, `develop` | tsc → eslint → next build |

---

## Deployment

**MVP** — push to `main` auto-deploys:
- Frontend → Vercel (`frontend/vercel.json`)
- Backend → Render (`backend/render.yaml`)

**Production** — AWS UAE `me-central-1` (ECS Fargate, RDS Aurora PostGIS, ElastiCache Redis, Qdrant Cloud). See [`docs/architecture/06-deployment.md`](docs/architecture/06-deployment.md).

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `REDIS_URL` | Yes | Redis connection string |
| `OPENROUTER_API_KEY` | Yes | LLM inference via OpenRouter |
| `OPENAI_API_KEY` | Recommended | Text embeddings (falls back to zero vector) |
| `QDRANT_URL` | Yes | Qdrant vector DB URL |
| `QDRANT_API_KEY` | Cloud only | Qdrant Cloud API key |
| `WHATSAPP_TOKEN` | Optional | Meta WhatsApp Business API token |
| `WHATSAPP_PHONE_NUMBER_ID` | Optional | WhatsApp sender phone number ID |
| `WHATSAPP_VERIFY_TOKEN` | Optional | Webhook verification token |
| `TELEGRAM_BOT_TOKEN` | Optional | Telegram Bot API token |
| `ZOHO_CLIENT_ID` | Optional | Zoho CRM OAuth client |
| `HUBSPOT_API_KEY` | Optional | HubSpot CRM API key |
| `SENDGRID_API_KEY` | Optional | Email (Phase 3) |
| `LANGSMITH_API_KEY` | Optional | LangSmith tracing |
| `LLM_MODEL_ID` | No | Default: `blissful_ishizaka_626/gemma4-cloud` |

---

## Documentation

| Document | Description |
|----------|-------------|
| [`docs/architecture/01-system-overview.md`](docs/architecture/01-system-overview.md) | C4 Context, design principles |
| [`docs/architecture/02-c4-containers.md`](docs/architecture/02-c4-containers.md) | All deployable containers |
| [`docs/architecture/03-component-diagram.md`](docs/architecture/03-component-diagram.md) | Component-level breakdown |
| [`docs/architecture/04-sequence-diagrams.md`](docs/architecture/04-sequence-diagrams.md) | 6 key user flows |
| [`docs/architecture/05-data-flow.md`](docs/architecture/05-data-flow.md) | Data ingestion + memory architecture |
| [`docs/architecture/06-deployment.md`](docs/architecture/06-deployment.md) | MVP + production topology |
| [`docs/architecture/07-database-schema.md`](docs/architecture/07-database-schema.md) | Full ERD + indexes |
| [`docs/architecture/08-api-design.md`](docs/architecture/08-api-design.md) | All REST endpoints |
| [`docs/architecture/09-agent-architecture.md`](docs/architecture/09-agent-architecture.md) | LangGraph nodes, tools, LLM abstraction |
| [`prd_real_estate_agent_platform.md`](prd_real_estate_agent_platform.md) | Full product requirements |
