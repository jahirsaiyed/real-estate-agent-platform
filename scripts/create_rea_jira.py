#!/usr/bin/env python3
"""
create_rea_jira.py
Create all Jira Epics, Stories, and Subtasks for the REA project.

Structure:
  5 Epics (one per roadmap phase)
  50 Stories
  ~190 Subtasks

Usage:
    python scripts/create_rea_jira.py
"""

import io
import os
import sys
import json
import time
import requests
from requests.auth import HTTPBasicAuth

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Config ────────────────────────────────────────────────────────────────────
JIRA_BASE = os.environ.get("JIRA_BASE", "https://jsaiyed.atlassian.net")
EMAIL     = os.environ.get("ATLASSIAN_EMAIL", "")
TOKEN     = os.environ.get("ATLASSIAN_API_TOKEN", "")

if not EMAIL or not TOKEN:
    print("ERROR: Set ATLASSIAN_EMAIL and ATLASSIAN_API_TOKEN environment variables.")
    sys.exit(1)
PROJECT   = "REA"
DELAY     = 0.2   # seconds between API calls

AUTH    = HTTPBasicAuth(EMAIL, TOKEN)
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

EPIC_ID    = "10011"
STORY_ID   = "10010"
SUBTASK_ID = "10012"

# ── ADF helpers ───────────────────────────────────────────────────────────────

def adf(*lines) -> dict:
    """Build Atlassian Document Format body from plain text lines.
    Lines starting with '- ' become bullet list items.
    Lines starting with '## ' become h2 headings.
    """
    content = []
    bullets = []

    def flush():
        if bullets:
            content.append({
                "type": "bulletList",
                "content": [
                    {"type": "listItem", "content": [
                        {"type": "paragraph", "content": [{"type": "text", "text": b}]}
                    ]} for b in bullets
                ]
            })
            bullets.clear()

    for line in lines:
        if line.startswith("## "):
            flush()
            content.append({
                "type": "heading", "attrs": {"level": 2},
                "content": [{"type": "text", "text": line[3:], "marks": [{"type": "strong"}]}]
            })
        elif line.startswith("- "):
            bullets.append(line[2:])
        else:
            flush()
            content.append({"type": "paragraph", "content": [{"type": "text", "text": line}]})
    flush()
    return {"type": "doc", "version": 1, "content": content}


# ── API helpers ───────────────────────────────────────────────────────────────

def create_issue(fields: dict) -> str:
    """Create a Jira issue and return its key. Returns '' on failure."""
    resp = requests.post(
        f"{JIRA_BASE}/rest/api/3/issue",
        auth=AUTH, headers=HEADERS,
        data=json.dumps({"fields": fields}),
        timeout=30,
    )
    time.sleep(DELAY)
    if resp.status_code not in (200, 201):
        summary = fields.get("summary", "?")[:60]
        print(f"    ERROR {resp.status_code} '{summary}': {resp.text[:200]}")
        return ""
    return resp.json()["key"]


def create_epic(summary: str, description: dict, labels: list) -> str:
    key = create_issue({
        "project":     {"key": PROJECT},
        "summary":     summary,
        "issuetype":   {"id": EPIC_ID},
        "description": description,
        "labels":      labels,
    })
    print(f"  EPIC {key}: {summary}")
    return key


def create_story(summary: str, description: dict, labels: list, epic_key: str) -> str:
    key = create_issue({
        "project":     {"key": PROJECT},
        "summary":     summary,
        "issuetype":   {"id": STORY_ID},
        "description": description,
        "labels":      labels,
        "parent":      {"key": epic_key},
    })
    print(f"    STORY {key}: {summary[:70]}")
    return key


def create_subtask(summary: str, story_key: str, labels: list) -> str:
    key = create_issue({
        "project":   {"key": PROJECT},
        "summary":   summary,
        "issuetype": {"id": SUBTASK_ID},
        "labels":    labels,
        "parent":    {"key": story_key},
    })
    print(f"      TASK {key}: {summary[:65]}")
    return key


# ── Data ──────────────────────────────────────────────────────────────────────

EPICS = [

    # ═══════════════════════════════════════════════════════════════════════════
    # EPIC 1 — Phase 1: Foundation & Infrastructure (Weeks 1–3)
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "summary": "[Phase 1] Foundation & Infrastructure",
        "labels":  ["phase-1", "foundation", "infrastructure"],
        "description": adf(
            "Establish the complete project foundation: monorepo, CI/CD, all cloud services, "
            "database schema, FastAPI skeleton, LLM abstraction, LangGraph skeleton, and "
            "Next.js 14 frontend scaffold.",
            "## Acceptance Criteria",
            "- All health endpoints green on Render + Vercel",
            "- CI pipeline passes (lint, type-check, unit tests, Lighthouse CI)",
            "- All cloud services reachable (PostgreSQL, Redis, Qdrant, RabbitMQ, R2)",
            "- Basic message -> LLM -> response E2E flow working",
            "- Alembic migrations run cleanly from scratch",
        ),
        "stories": [
            {
                "summary": "Monorepo setup, GitHub Actions CI/CD and cloud service provisioning",
                "labels":  ["phase-1", "devops", "infrastructure"],
                "description": adf(
                    "Initialize the monorepo and set up the full CI/CD pipeline for both backend and frontend, "
                    "then provision all required cloud services.",
                    "## Acceptance Criteria",
                    "- GitHub monorepo created with backend/, frontend/, scripts/, docs/ structure",
                    "- GitHub Actions CI runs on every PR: lint, type-check, unit tests, security scan",
                    "- Render web service + background worker + managed PostgreSQL provisioned",
                    "- Vercel project linked with preview + production environments",
                    "- All environment variable groups configured (Render) and project secrets (Vercel)",
                    "- Deployment on merge to main is fully automated",
                ),
                "tasks": [
                    "Initialize GitHub monorepo with backend/, frontend/, scripts/, docs/ structure",
                    "Configure GitHub Actions CI: ruff lint, mypy, pytest, Lighthouse CI gate",
                    "Set up Render web service (FastAPI) + worker service (Celery) + managed PostgreSQL 16",
                    "Create Vercel project linked to repo with preview + production environments",
                    "Configure environment variable groups in Render and project secrets in Vercel",
                    "Add check-phi-leaks.sh and validate-env.sh to CI pipeline",
                ],
            },
            {
                "summary": "PostgreSQL schema design and Alembic migration framework",
                "labels":  ["phase-1", "backend", "database"],
                "description": adf(
                    "Design and implement the full PostgreSQL schema with PostGIS extension, "
                    "Alembic migration framework, and all performance indexes.",
                    "## Acceptance Criteria",
                    "- PostGIS extension installed and geometry columns on properties + locations tables",
                    "- All 20+ tables created via Alembic migrations (runs cleanly from scratch)",
                    "- tenant_id present and indexed on every table",
                    "- All performance indexes applied (geo, price, type, time-based, full-text)",
                    "- SQLAlchemy models with relationships defined for all tables",
                ),
                "tasks": [
                    "Install PostGIS extension and configure SQLAlchemy + psycopg3 connection pool",
                    "Initialize Alembic with env.py, version tracking and naming convention",
                    "Migration 001: tenants, users, leads, conversations, messages",
                    "Migration 002: properties, locations (PostGIS), appointments, documents",
                    "Migration 003: off_plan_projects, eoi_submissions, etl_jobs, analytics_events, audit_logs",
                    "Migration 004: notifications, notification_templates, saved_searches, fx_rates, guardrail_rules",
                    "Add all performance indexes (tenant scoping, geo GIST, price, type, time DESC)",
                ],
            },
            {
                "summary": "FastAPI backend skeleton — JWT auth, RBAC and API versioning",
                "labels":  ["phase-1", "backend", "auth"],
                "description": adf(
                    "Build the FastAPI application skeleton with proper authentication, "
                    "role-based access control, API versioning, and middleware stack.",
                    "## Acceptance Criteria",
                    "- JWT auth (RS256) with access + refresh token rotation",
                    "- 4-role RBAC enforced: superadmin, tenant_admin, agent, readonly",
                    "- All routes prefixed with /api/v1/",
                    "- OpenAPI spec auto-generated and accessible at /api/v1/docs",
                    "- Rate limiting, CORS, and request ID middleware active",
                    "- Health check and readiness endpoints return 200",
                ),
                "tasks": [
                    "Scaffold FastAPI app with /api/v1/ prefix, lifespan events, and middleware stack",
                    "Implement JWT auth: RS256 key pair, access token (15min) + refresh token (7d)",
                    "Implement 4-role RBAC middleware with tenant_id scoping",
                    "Implement rate limiting (slowapi): per-tenant and per-IP sliding window",
                    "Configure CORS, request ID, and structured JSON logging middleware",
                    "Create GET /health and GET /api/v1/system/status endpoints",
                    "Write unit tests for auth and RBAC (20+ scenarios)",
                ],
            },
            {
                "summary": "LLM abstraction layer with model-agnostic interface",
                "labels":  ["phase-1", "ai", "backend"],
                "description": adf(
                    "Build the LLM provider abstraction layer so the model can be swapped "
                    "via a single environment variable with no code changes.",
                    "## Acceptance Criteria",
                    "- LLMProvider interface with ainvoke, astream, and embed methods",
                    "- OpenRouter adapter working with blissful_ishizaka_626/gemma4-cloud",
                    "- Anthropic and OpenAI adapters implemented (for future swap)",
                    "- LLM_MODEL_ID env var switches adapter at startup",
                    "- All LLM calls wrapped with LangSmith tracing",
                    "- Unit tests verify adapter switching and mock LLM responses",
                ),
                "tasks": [
                    "Define LLMProvider abstract base class (ainvoke, astream, embed, health_check)",
                    "Implement OpenRouter adapter for blissful_ishizaka_626/gemma4-cloud",
                    "Implement Anthropic Claude adapter (claude-sonnet-4-6)",
                    "Implement OpenAI-compatible adapter (gpt-4o, any OpenAI-compatible endpoint)",
                    "Integrate LangSmith tracing wrapper (project, tags, metadata) around all calls",
                    "Write unit tests: adapter switching via LLM_MODEL_ID, mock responses, stream chunks",
                ],
            },
            {
                "summary": "LangGraph orchestrator skeleton with intent classification",
                "labels":  ["phase-1", "ai", "backend", "langgraph"],
                "description": adf(
                    "Build the LangGraph agent state machine skeleton with all nodes defined, "
                    "wired with correct edges, and basic intent classification working.",
                    "## Acceptance Criteria",
                    "- AgentState TypedDict with all fields defined",
                    "- memory_loader, intent_classifier, guardrails_node, memory_update nodes implemented",
                    "- Intent classification working for: search, book, calculate, qualify, info, handoff, smalltalk, unclear",
                    "- E2E test: message -> intent classified -> response generated",
                    "- Rule-based fast path for explicit handoff requests",
                ),
                "tasks": [
                    "Define AgentState TypedDict (all fields per architecture doc 09)",
                    "Implement memory_loader node (Redis session + Qdrant retrieval + PG lead context)",
                    "Implement intent_classifier node (LLM primary + rule-based fast path)",
                    "Implement response_generator node (persona prompt + LLM call + streaming)",
                    "Implement guardrails_node skeleton (RERA statement + violation logging)",
                    "Implement memory_update node (Redis save + PG lead update + analytics event)",
                    "Wire all nodes into LangGraph StateGraph with conditional routing edges",
                    "Write E2E test: message -> intent -> response -> memory saved",
                ],
            },
            {
                "summary": "Next.js 14 frontend scaffold — Tailwind, shadcn/ui and admin shell",
                "labels":  ["phase-1", "frontend"],
                "description": adf(
                    "Initialize the Next.js 14 App Router frontend with the full component library, "
                    "internationalization, auth guard, and admin shell navigation.",
                    "## Acceptance Criteria",
                    "- Next.js 14 App Router with TypeScript strict mode",
                    "- Tailwind CSS + shadcn/ui component library configured",
                    "- next-intl set up for EN/AR/HI/RU with RTL direction switching",
                    "- Admin shell renders with sidebar navigation + auth guard",
                    "- Playwright E2E framework configured with first passing test",
                    "- Lighthouse CI gate configured (> 90 performance + PWA)",
                ),
                "tasks": [
                    "Initialize Next.js 14 App Router with TypeScript strict + ESLint + Prettier",
                    "Configure Tailwind CSS + shadcn/ui with custom design tokens (brand colors)",
                    "Set up next-intl with EN/AR/HI/RU locales and RTL direction provider for AR",
                    "Build admin shell: sidebar navigation, topbar, breadcrumbs, auth guard (JWT cookie)",
                    "Configure ISR defaults and Next.js image optimization (remote domains)",
                    "Set up Playwright E2E framework with first smoke test (admin login flow)",
                ],
            },
            {
                "summary": "Infrastructure connectivity — Redis, Qdrant, RabbitMQ and Cloudflare R2",
                "labels":  ["phase-1", "infrastructure", "devops"],
                "description": adf(
                    "Connect and verify all four managed cloud services needed at runtime.",
                    "## Acceptance Criteria",
                    "- Redis (Upstash) client with retry logic and connection pool",
                    "- Qdrant Cloud client with properties and knowledge_base collections created",
                    "- RabbitMQ (CloudAMQP) connected with queues and exchanges declared",
                    "- Cloudflare R2 client (S3-compatible) with bucket and lifecycle policies set",
                    "- Integration smoke test pings all 4 services and reports health",
                ),
                "tasks": [
                    "Configure Upstash Redis client (redis-py async, retry on connection error, pool size 20)",
                    "Configure Qdrant Cloud client — create 'properties' and 'knowledge_base' collections (1536-dim)",
                    "Configure CloudAMQP RabbitMQ — declare exchanges, queues, DLQ, and bindings",
                    "Configure Cloudflare R2 boto3 client — create bucket, set 7-year lifecycle rule",
                    "Write connectivity smoke test script (validate-ci.sh + Python health pings)",
                ],
            },
        ],
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # EPIC 2 — Phase 2: Core Agent & Property Features (Weeks 4–6)
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "summary": "[Phase 2] Core Agent & Property Features",
        "labels":  ["phase-2", "agent", "property"],
        "description": adf(
            "Deliver the core AI agent capabilities and all property-related features: "
            "hybrid search, booking, CRM sync, memory, RAG, chat widget, listing pages, "
            "WhatsApp/Telegram integration, and notification service.",
            "## Acceptance Criteria",
            "- Full E2E flow: search -> book -> CRM update -> WhatsApp confirmation",
            "- Property search returns relevant results in < 800ms P95",
            "- Appointment booking creates events in Google Calendar and sends WhatsApp confirmation",
            "- CRM lead record created/updated in Zoho and HubSpot on qualification",
            "- Web chat widget embeddable via <script> tag",
        ),
        "stories": [
            {
                "summary": "Property search tool — PostGIS + Qdrant hybrid search",
                "labels":  ["phase-2", "backend", "ai", "search"],
                "description": adf(
                    "Implement the property search LangGraph tool combining PostGIS geospatial queries "
                    "with Qdrant dense + sparse vector search and RRF re-ranking.",
                    "## Acceptance Criteria",
                    "- PostGIS polygon containment + radius search on properties table",
                    "- Qdrant dense (text embedding) + BM25 sparse search in parallel",
                    "- RRF merge and rank — returns top 10 with scores",
                    "- Dubai 3-level area taxonomy (community -> sub-community -> building) resolves correctly",
                    "- Freehold, off-plan, Golden Visa filters applied at DB level",
                    "- Search latency P95 < 800ms in unit tests with mock data",
                    "- Registered as LangGraph tool with structured input/output schema",
                ),
                "tasks": [
                    "Implement PropertyFilters dataclass with all filter dimensions (type, price, beds, geo, flags)",
                    "Build PostGIS query builder (polygon containment from area slug + optional radius)",
                    "Build Qdrant hybrid query (dense embedding + BM25 sparse) with tenant + status filter",
                    "Implement Reciprocal Rank Fusion (RRF) merge and deduplication",
                    "Load Dubai area taxonomy (community/sub-community/building) into locations table",
                    "Register property_search as LangGraph tool with JSON schema validation",
                    "Write unit tests: 10 search scenarios (area filter, price range, bedrooms, freehold)",
                ],
            },
            {
                "summary": "Booking service — custom calendar engine and availability API",
                "labels":  ["phase-2", "backend", "booking"],
                "description": adf(
                    "Build the platform's own calendar engine as source of truth for agent availability, "
                    "with conflict detection and appointment CRUD API.",
                    "## Acceptance Criteria",
                    "- Slot availability query returns free slots for given agent + date range",
                    "- Double-booking prevented at DB level (unique constraint + optimistic lock)",
                    "- Appointment CRUD API (POST, GET, PATCH, DELETE /api/v1/appointments)",
                    "- 24h and 1h reminder Celery tasks scheduled on appointment creation",
                    "- GET /api/v1/appointments/availability returns slots with 15-min granularity",
                ),
                "tasks": [
                    "Design calendar_events table with agent_id, start_time, end_time, type, appointment_id FK",
                    "Implement availability query (working hours config + existing bookings + buffer time)",
                    "Implement conflict detection with DB-level unique constraint + row-level lock",
                    "Build appointments CRUD API endpoints (POST, GET, PATCH /appointments, GET /availability)",
                    "Implement Celery tasks: appointment_reminder_24h and appointment_reminder_1h",
                    "Write unit tests: conflict detection, availability edge cases (full day, overlapping)",
                ],
            },
            {
                "summary": "Google Calendar bidirectional sync adapter",
                "labels":  ["phase-2", "backend", "integration", "calendar"],
                "description": adf(
                    "Implement the Google Calendar adapter so agents can see platform appointments "
                    "in their Google Calendar and the platform reflects Google Calendar availability.",
                    "## Acceptance Criteria",
                    "- OAuth2 flow works for per-agent Google Calendar authorization",
                    "- Creating appointment on platform creates event in agent's Google Calendar",
                    "- Google Calendar changes sync back to platform availability",
                    "- All times stored internally as UTC, displayed as GST (UTC+4)",
                    "- Revoked OAuth handled gracefully (fallback to DB-only calendar)",
                ),
                "tasks": [
                    "Implement OAuth2 flow for Google Calendar API (per-agent token storage in DB)",
                    "Implement CalendarAdapter interface (get_availability, create_event, update_event, delete_event)",
                    "Build Google Calendar push notification webhook receiver",
                    "Handle timezone conversion: platform UTC <-> Google Calendar/user timezone",
                    "Handle OAuth token refresh and revocation gracefully",
                    "Write integration tests with Google Calendar API test account",
                ],
            },
            {
                "summary": "CRM adapters — Zoho CRM and HubSpot",
                "labels":  ["phase-2", "backend", "integration", "crm"],
                "description": adf(
                    "Build the CRM adapter layer with Zoho and HubSpot implementations "
                    "using a normalized internal interface for bidirectional lead sync.",
                    "## Acceptance Criteria",
                    "- Normalized Lead and Contact schemas defined for CRM adapter interface",
                    "- Zoho CRM adapter: upsert_lead, get_contact, log_activity, sync_deals",
                    "- HubSpot adapter: identical interface, different API",
                    "- Bidirectional sync with conflict resolution (platform wins on conflict)",
                    "- CRM webhook receivers handle inbound contact changes",
                    "- Unit tests with mocked API responses for both adapters",
                ),
                "tasks": [
                    "Define CRMAdapter interface (upsert_lead, get_contact, log_activity, sync_deals)",
                    "Implement ZohoCRMAdapter (OAuth2 auth, all interface methods)",
                    "Implement HubSpotAdapter (API key auth, all interface methods)",
                    "Build CRM sync service: lead -> CRM on qualification, CRM -> lead on webhook",
                    "Implement conflict resolution logic (platform data wins, log discrepancies)",
                    "Implement CRM webhook receivers (Zoho + HubSpot inbound events)",
                    "Write unit tests for both adapters with mocked API responses (15+ scenarios)",
                ],
            },
            {
                "summary": "Conversation memory — Redis session and Qdrant long-term memory",
                "labels":  ["phase-2", "backend", "ai", "memory"],
                "description": adf(
                    "Implement the two-tier memory system: short-term session in Redis "
                    "and long-term summarized memory in Qdrant for returning leads.",
                    "## Acceptance Criteria",
                    "- Redis session stores last 20 messages, entities, qualification state (TTL 24h)",
                    "- Qdrant long-term memory stores summarized past interactions per lead",
                    "- memory_loader retrieves both tiers before each agent graph execution",
                    "- memory_update persists session to Redis and upserts Qdrant on conversation end",
                    "- Returning lead: agent correctly recalls previous property preferences",
                ),
                "tasks": [
                    "Implement RedisSessionStore (load, save, expire TTL 24h, schema validation)",
                    "Define session schema: last 20 messages, extracted entities, qualification state, language",
                    "Implement QdrantMemoryStore (upsert conversation summary embedding, similarity search)",
                    "Integrate memory_loader node with both Redis + Qdrant retrieval",
                    "Integrate memory_update node with Redis save + Qdrant upsert on turn end",
                    "Write tests: session expiry, retrieval on returning lead, long-term memory recall",
                ],
            },
            {
                "summary": "RAG pipeline — document ingestion, chunking, embedding and retrieval",
                "labels":  ["phase-2", "backend", "ai", "rag"],
                "description": adf(
                    "Build the full RAG pipeline from document ingestion to grounded response generation, "
                    "supporting PDF, DOCX, and text formats.",
                    "## Acceptance Criteria",
                    "- PDF, DOCX, and plain text documents ingested and chunked (512 tokens, 128 overlap)",
                    "- Chunks embedded and upserted into Qdrant knowledge_base collection",
                    "- Hybrid retrieval (dense + BM25 sparse + RRF reranking) returns top 5 chunks",
                    "- RAG agent node injects retrieved context into LLM prompt",
                    "- Retrieval quality > 80% on 20-item golden test set",
                    "- Source citations included in generated response",
                ),
                "tasks": [
                    "Implement text chunker (512 tokens, 128 overlap, section boundary respect)",
                    "Implement embedding pipeline (batch 100/call, async with retry, cache embeddings)",
                    "Build document ingestion worker (PDF via pdfplumber, DOCX via python-docx, text)",
                    "Implement hybrid retrieval: dense + BM25 sparse search + RRF reranking",
                    "Build RAG agent LangGraph node (retrieve -> inject context -> grounded generation)",
                    "Wire RAG ingestion trigger on document upload (Celery async task)",
                    "Write retrieval quality tests against 20-item golden dataset",
                ],
            },
            {
                "summary": "Embeddable web chat widget with WebSocket streaming",
                "labels":  ["phase-2", "frontend", "chat"],
                "description": adf(
                    "Build the chat widget as a standalone embeddable component with "
                    "WebSocket streaming, property cards, appointment picker, and file upload.",
                    "## Acceptance Criteria",
                    "- Widget embeddable via <script> tag on any website (iframe isolation)",
                    "- Streaming responses display token-by-token (typewriter effect)",
                    "- Property card components render with image, price, beds, badges, CTA",
                    "- Appointment slot picker functional (select date/time -> confirm booking)",
                    "- File upload works (drag-drop, progress bar, type validation)",
                    "- Widget works in Arabic RTL mode",
                    "- Playwright E2E test covers full search -> book conversation flow",
                ),
                "tasks": [
                    "Build chat widget as Next.js route (/widget) with embed script generator",
                    "Implement WebSocket client with auto-reconnect and message queue",
                    "Build streaming message display (token-by-token, typewriter, markdown rendering)",
                    "Build PropertyCard component (image, price AED, beds, area, badges, CTA button)",
                    "Build AppointmentPicker component (calendar UI, slot selection, confirmation)",
                    "Build FileUpload component (drag-drop, progress, 10MB limit, PDF/image/doc types)",
                    "Write Playwright E2E tests: search flow, booking flow, file upload",
                ],
            },
            {
                "summary": "Property listing and detail pages — ISR, SEO and Open Graph",
                "labels":  ["phase-2", "frontend", "seo"],
                "description": adf(
                    "Build SEO-optimized property pages with ISR for performance, "
                    "rich metadata, Golden Visa badge, virtual tour embed, and all calculators.",
                    "## Acceptance Criteria",
                    "- Listing page /search with SSR filter rendering < 200ms TTFB",
                    "- Detail page /properties/[slug] with ISR (1hr revalidation)",
                    "- Open Graph + JSON-LD structured data on all listing pages",
                    "- Golden Visa badge shown for properties >= AED 2M",
                    "- Matterport virtual tour embed (lazy-load, fullscreen mode)",
                    "- Lighthouse SEO score > 95, Performance > 90",
                ),
                "tasks": [
                    "Build property listing page /search (SSR, filter params in URL, pagination)",
                    "Build property detail page /properties/[slug] with ISR 1hr revalidation",
                    "Implement Open Graph meta tags (og:title, og:image, og:description, og:url)",
                    "Implement JSON-LD structured data (RealEstateListing schema)",
                    "Add Golden Visa badge (>= AED 2M), Off-plan badge, RERA number display",
                    "Implement Matterport virtual tour embed (lazy iframe, fullscreen toggle)",
                    "Add social share (WhatsApp, copy link) + Save to favourites (localStorage)",
                    "Configure Lighthouse CI gate in GitHub Actions (SEO > 95, Perf > 90)",
                ],
            },
            {
                "summary": "Search UI — conversational filter panel and Mapbox map view",
                "labels":  ["phase-2", "frontend", "search", "maps"],
                "description": adf(
                    "Build the property search UI combining a conversational chat interface "
                    "with a visible editable filter panel, Mapbox map view, and saved searches.",
                    "## Acceptance Criteria",
                    "- Filter panel syncs with chat conversation (chat sets filters, panel shows them)",
                    "- Mapbox map renders property pins with Dubai community polygon overlays",
                    "- Cluster markers on zoom-out, individual pins on zoom-in",
                    "- Saved searches persist (localStorage + DB for logged-in leads)",
                    "- Filter state serialized in URL query params (shareable links)",
                    "- Chat inline results show 3-card preview + 'View all' link",
                ),
                "tasks": [
                    "Build filter panel component (bedrooms, type, price range, area, purpose, freehold toggle)",
                    "Integrate Mapbox GL JS with property pin markers (custom SVG icons, price labels)",
                    "Add Dubai community polygon overlays from GeoJSON (PostGIS export)",
                    "Implement cluster markers (supercluster) on zoom-out",
                    "Build saved search UI (save button, saved searches drawer, alert toggle)",
                    "Serialize filter state to/from URL query params for shareable searches",
                    "Build 3-card inline chat result component with 'View all' navigation",
                ],
            },
            {
                "summary": "WhatsApp Business API + Telegram bot channel integration",
                "labels":  ["phase-2", "backend", "whatsapp", "telegram", "channels"],
                "description": adf(
                    "Integrate WhatsApp Business API and Telegram Bot API as first-class "
                    "channels with normalized message handling.",
                    "## Acceptance Criteria",
                    "- WhatsApp webhook receives messages (HMAC-SHA256 signature verified)",
                    "- WhatsApp sends text, template, interactive button messages, and media",
                    "- Telegram webhook receives messages and bot sends replies",
                    "- Both channels normalized to same internal message format",
                    "- Per-user channel preference routing (prefer WhatsApp, fallback to email)",
                    "- Conversation continues across channel switch (same session)",
                ),
                "tasks": [
                    "Implement WhatsApp webhook receiver (POST /webhooks/whatsapp, HMAC-SHA256 verify)",
                    "Build WhatsApp message sender (text, approved templates, interactive lists, media)",
                    "Implement Telegram webhook receiver (POST /webhooks/telegram, bot token verify)",
                    "Build Telegram message sender (text, inline keyboards, document send)",
                    "Define ChannelAdapter interface normalizing inbound messages across channels",
                    "Implement per-user channel preference lookup and routing logic",
                    "Write integration tests with WhatsApp webhook simulator and Telegram mock",
                ],
            },
            {
                "summary": "Notification service and template registry",
                "labels":  ["phase-2", "backend", "notifications"],
                "description": adf(
                    "Build the centralized notification service with template registry, "
                    "channel routing, delivery tracking, and retry logic.",
                    "## Acceptance Criteria",
                    "- notification_templates CRUD API with per-channel and per-language variants",
                    "- Template variable substitution works for all languages including Arabic",
                    "- Notifications dispatched via correct channel (WhatsApp > Email > SMS)",
                    "- Delivery status tracked (sent, delivered, read, failed) via webhooks",
                    "- Failed notifications retried 3 times with exponential backoff",
                ),
                "tasks": [
                    "Build notification_templates CRUD API (POST, GET, PATCH /api/v1/admin/notification-templates)",
                    "Implement template renderer with variable substitution and language selection",
                    "Build notification dispatcher (channel routing: WhatsApp > Email > SMS > Telegram)",
                    "Implement delivery status webhook handlers (WhatsApp read receipts, email open)",
                    "Implement retry logic for failed notifications (3 attempts, exponential backoff, DLQ)",
                ],
            },
        ],
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # EPIC 3 — Phase 3: Intelligence Layer & Content (Weeks 7–9)
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "summary": "[Phase 3] Intelligence Layer & Content",
        "labels":  ["phase-3", "intelligence", "content"],
        "description": adf(
            "Add the intelligence and content layers: lead qualification engine, sentiment analysis, "
            "guardrails, financial calculators, ETL adapters, Celery jobs, agent dashboard, "
            "admin panel, multilingual UI, PWA, document handling, and UTM attribution.",
            "## Acceptance Criteria",
            "- Full qualification flow works (8 dimensions, configurable per tenant)",
            "- All 5 financial calculators return correct UAE-specific results",
            "- Platform is installable as PWA with Lighthouse > 90",
            "- Arabic RTL UI renders correctly across all pages",
            "- Document upload, storage, and RAG indexing works end-to-end",
        ),
        "stories": [
            {
                "summary": "Lead qualification engine — 8-dimension scorecard",
                "labels":  ["phase-3", "backend", "ai", "qualification"],
                "description": adf(
                    "Build the configurable 8-dimension lead qualification engine with "
                    "entity extraction, progressive scoring, and next-question logic.",
                    "## 8 Dimensions",
                    "- Budget, Property Type, Purchase Purpose, Timeline, Nationality, Pre-approval, Preferred Locations, Contact Preference",
                    "## Acceptance Criteria",
                    "- All 8 dimensions scored 0-10 from conversation entities",
                    "- Scoring weights configurable per tenant (stored in tenant settings JSON)",
                    "- Status: unqualified (0-29) / in_progress (30-69) / qualified (70+)",
                    "- Next-question selector picks lowest-scored uncollected dimension",
                    "- Lead DB record updated after every qualification turn",
                    "- Unit tests covering 20 conversation qualification scenarios",
                ),
                "tasks": [
                    "Implement 8-dimension scorer with configurable weights per tenant",
                    "Build entity extractor (parse budget range, locations, bedrooms, purpose from text)",
                    "Implement qualification status thresholds (unqualified/in_progress/qualified)",
                    "Build next-question selector (lowest-scored uncollected dimension)",
                    "Build qualification_agent LangGraph node (score -> update DB -> select next question)",
                    "Implement GET /api/v1/leads/{id}/score endpoint with full scorecard breakdown",
                    "Write unit tests for 20 qualification conversation scenarios",
                ],
            },
            {
                "summary": "Sentiment analysis and frustration detection",
                "labels":  ["phase-3", "backend", "ai"],
                "description": adf(
                    "Detect user frustration from message sentiment and trigger escalation "
                    "after 2 frustration signals or 3 consecutive failed interactions.",
                    "## Acceptance Criteria",
                    "- Sentiment score (-1 to 1) computed per message via LLM classifier",
                    "- Frustration signals detected (negative keywords + low sentiment threshold)",
                    "- After 2 frustration signals: proactive empathy response + offer human agent",
                    "- After 3 consecutive failures: auto-trigger handoff",
                    "- Frustration count and sentiment stored in conversations table",
                ),
                "tasks": [
                    "Implement LLM-based sentiment scorer (per-message, -1 to 1 scale, cached)",
                    "Build frustration signal detector (pattern matching + sentiment threshold < -0.5)",
                    "Integrate frustration_count and consecutive_failures into AgentState",
                    "Implement 3-strike escalation routing in LangGraph intent_classifier",
                    "Persist sentiment_score and frustration_count to conversations table",
                    "Write unit tests for frustration detection (8 scenarios including edge cases)",
                ],
            },
            {
                "summary": "Guardrails system — post-LLM filter, RERA compliance and audit log",
                "labels":  ["phase-3", "backend", "ai", "compliance"],
                "description": adf(
                    "Build the complete guardrail system to ensure every LLM response is safe, "
                    "compliant with UAE/RERA rules, and within configured topic boundaries.",
                    "## Acceptance Criteria",
                    "- RERA compliance statement auto-injected in first message of every conversation",
                    "- Price guarantee language detected and replaced with disclaimer",
                    "- Competitor mentions blocked per tenant rules",
                    "- Configurable blocked topics via admin panel",
                    "- Regeneration loop (max 2 retries on hard violation)",
                    "- All guardrail events written to audit_logs (immutable)",
                    "- Unit tests for 15 guardrail scenarios",
                ),
                "tasks": [
                    "Implement post-LLM output filter (price guarantee, competitor, blocked topics regex)",
                    "Build RERA compliance statement injection (first message per conversation)",
                    "Implement disclaimer injection for financial/legal/mortgage topics",
                    "Build guardrail_rules CRUD API (POST/GET/PATCH/DELETE /api/v1/admin/guardrail-rules)",
                    "Build admin UI for guardrail rule editor with test mode (preview on sample text)",
                    "Implement regeneration loop (remove last assistant message, retry with safer prompt)",
                    "Write audit log entry for every guardrail trigger (append-only, immutable)",
                    "Write unit tests for 15 guardrail scenarios (soft violations, hard blocks, RERA)",
                ],
            },
            {
                "summary": "Financial calculators — mortgage, ROI, TCO, off-plan and Golden Visa",
                "labels":  ["phase-3", "backend", "frontend", "calculators"],
                "description": adf(
                    "Build all 5 UAE-specific financial calculators as both API endpoints "
                    "and embedded interactive UI components.",
                    "## Calculators",
                    "- Mortgage (UAE rules: DLD 4%, registration fee, bank charges, eligibility)",
                    "- ROI / Yield (gross + net yield, 5yr + 10yr projections)",
                    "- TCO — Total Cost of Ownership (full acquisition cost breakdown)",
                    "- Off-plan payment plan simulator (milestone-based schedule)",
                    "- Golden Visa eligibility checker (AED 2M net equity threshold)",
                    "## Acceptance Criteria",
                    "- All calculator API endpoints return correct results vs verified test cases",
                    "- All calculators accessible on property detail page and /calculators page",
                    "- LangGraph calculator_agent tool registered and functional",
                ),
                "tasks": [
                    "Implement UAE mortgage calculator (DLD 4%, registration, bank processing, eligibility rules)",
                    "Implement ROI/yield calculator (gross yield, net yield, 5yr and 10yr projections)",
                    "Implement TCO calculator (DLD fee, agent fee, registration, service charge buffer)",
                    "Implement off-plan payment plan simulator (milestone-based schedule from payment_plan JSON)",
                    "Implement Golden Visa eligibility checker (AED 2M net equity, mortgage deduction rule)",
                    "Build calculator_agent LangGraph node (route to correct calculator, format output)",
                    "Build interactive calculator UI components (React hooks, AED formatting, copy results)",
                    "Write unit tests with 10 verified UAE real estate calculation examples per calculator",
                ],
            },
            {
                "summary": "Property ETL adapters — CSV import, Bayut and Property Finder",
                "labels":  ["phase-3", "backend", "etl", "integration"],
                "description": adf(
                    "Build the ETL layer for property data ingestion from multiple sources "
                    "with validation, normalization, deduplication, and error reporting.",
                    "## Acceptance Criteria",
                    "- CSV importer: validate headers, report errors per row, preview before commit",
                    "- Bayut adapter: fetches listings, normalizes to internal schema, upserts",
                    "- Property Finder adapter: same interface, different API",
                    "- ETL job tracking with status, record counts, and error details in DB",
                    "- Deduplication via external_id + source composite key",
                    "- Admin UI for CSV upload with live import status",
                ),
                "tasks": [
                    "Build CSV property importer with header validation, row error reporting, and preview mode",
                    "Implement Bayut API adapter (fetch, paginate, normalize to Property schema)",
                    "Implement Property Finder API adapter (same interface)",
                    "Build ETL job tracking model (etl_jobs table: status, records_processed, records_failed)",
                    "Implement deduplication (UPSERT ON CONFLICT external_id + source)",
                    "Build admin UI: CSV drag-drop upload + ETL job status dashboard with live updates",
                    "Write unit tests for normalizer with 20 sample raw records from each source",
                ],
            },
            {
                "summary": "Celery job scheduler — nightly ETL, reminders and KB re-index",
                "labels":  ["phase-3", "backend", "celery", "jobs"],
                "description": adf(
                    "Configure Celery Beat with all scheduled jobs and implement the core "
                    "async task workers for ETL, notifications, and knowledge base maintenance.",
                    "## Schedule",
                    "- Nightly 2:00 AM UAE: property sync (all portal adapters per tenant)",
                    "- Daily 7:00 AM UAE: FX rate refresh",
                    "- Weekly Sunday 3:00 AM UAE: off-plan project sync",
                    "- On-demand: KB re-index on document publish",
                    "- Event-triggered: appointment reminders, follow-up cadence",
                    "## Acceptance Criteria",
                    "- All scheduled tasks run reliably (no missed executions in 7-day test)",
                    "- Failed tasks go to dead-letter queue (not silently dropped)",
                    "- Task execution logged to etl_jobs table",
                ),
                "tasks": [
                    "Configure Celery Beat schedule (CELERY_BEAT_SCHEDULE with cron expressions in UAE timezone)",
                    "Implement nightly_property_sync task (iterate tenants, call all portal adapters)",
                    "Implement fx_rate_refresh task (fetch daily rates, update fx_rates table)",
                    "Implement appointment_reminder_24h and appointment_reminder_1h tasks",
                    "Implement lead_followup_reminder task (3d, 7d, 14d no-activity cadence)",
                    "Implement kb_reindex_on_publish Celery task (triggered from FastAPI on content save)",
                    "Configure dead-letter queue handling and task failure alerting (Slack webhook)",
                ],
            },
            {
                "summary": "Agent dashboard — lead queue, conversation viewer and calendar",
                "labels":  ["phase-3", "frontend", "dashboard"],
                "description": adf(
                    "Build the agent-facing dashboard for managing leads, viewing conversations, "
                    "handling handoffs, and tracking appointments.",
                    "## Acceptance Criteria",
                    "- Lead queue sortable by score, channel, date, status",
                    "- Conversation viewer shows full transcript with AI summary and lead profile",
                    "- Real-time handoff notifications arrive via WebSocket without page refresh",
                    "- Agent can update lead fields inline (CRM quick-update panel)",
                    "- Calendar view shows all appointments with Google Calendar sync status",
                ),
                "tasks": [
                    "Build lead queue page (sortable table: score, channel, date, status, assigned agent)",
                    "Build conversation viewer (full transcript, AI summary panel, lead profile sidebar)",
                    "Build CRM quick-update panel (inline lead field editing, sync status indicator)",
                    "Build real-time handoff notification (WebSocket push -> toast + queue update)",
                    "Build agent calendar view (day/week, appointment detail modal, status update)",
                    "Build conversation search and filter (channel, status, date range, assigned agent)",
                ],
            },
            {
                "summary": "Admin panel — tenant config, guardrails, user management and properties",
                "labels":  ["phase-3", "frontend", "admin"],
                "description": adf(
                    "Build the non-technical-friendly admin panel for tenant configuration, "
                    "user management, guardrail rules, property management, and notifications.",
                    "## Acceptance Criteria",
                    "- Non-technical admin can configure AI persona, tone, and system prompt additions",
                    "- User invite + role assignment + deactivation works",
                    "- Guardrail rule CRUD UI with test mode functional",
                    "- Property management: listing table, bulk CSV import, media upload",
                    "- All admin routes enforce correct RBAC (superadmin/tenant_admin only)",
                ),
                "tasks": [
                    "Build tenant configuration page (AI persona name, tone, system prompt, RERA number)",
                    "Build user management page (invite by email, assign role, deactivate, audit trail)",
                    "Build guardrail rules editor (create/edit/delete rules, test mode, live preview)",
                    "Build property management (listings table with search/filter, bulk CSV import UI)",
                    "Build notification template manager (per channel, per language, approval status)",
                    "Enforce RBAC across all admin routes (superadmin/tenant_admin guard component)",
                ],
            },
            {
                "summary": "Multilingual UI — Arabic RTL, Hindi and Russian language switcher",
                "labels":  ["phase-3", "frontend", "i18n", "rtl"],
                "description": adf(
                    "Implement full multilingual support across the entire frontend with "
                    "correct RTL layout for Arabic and language switcher component.",
                    "## Acceptance Criteria",
                    "- All UI strings translated to AR, HI, RU",
                    "- Arabic pages render correctly in RTL (flex direction, text alignment, icons mirrored)",
                    "- Language switcher persists preference to user profile",
                    "- Chat widget responds in user's selected language",
                    "- Playwright tests verify RTL layout in Arabic mode",
                ),
                "tasks": [
                    "Define all translation keys in EN as baseline (next-intl JSON structure)",
                    "Translate all UI strings to AR, HI, RU (LLM-assisted + human review queue)",
                    "Implement RTL layout provider (dir=rtl, flex-direction flip, margin/padding mirror)",
                    "Build language switcher component (dropdown, persists to user preference + cookie)",
                    "Test all pages in RTL mode: chat widget, property listing, admin, dashboard",
                    "Write Playwright tests for language switching and Arabic RTL layout correctness",
                ],
            },
            {
                "summary": "PWA — service worker, offline support and push notifications",
                "labels":  ["phase-3", "frontend", "pwa"],
                "description": adf(
                    "Make the platform a fully installable Progressive Web App with offline "
                    "saved properties, push notifications, and Lighthouse > 90.",
                    "## Acceptance Criteria",
                    "- App installable on iOS (Safari) and Android (Chrome)",
                    "- Saved properties accessible offline (IndexedDB cache)",
                    "- Push notifications delivered for price alerts and handoff events",
                    "- Lighthouse PWA audit score > 90 as CI gate",
                    "- Service worker caches critical assets and API responses",
                ),
                "tasks": [
                    "Configure next-pwa (workbox) with service worker, caching strategies, offline fallback",
                    "Build install prompt component for iOS Safari and Android Chrome",
                    "Set up push notification subscription (VAPID keys, PushSubscription stored in DB)",
                    "Implement offline saved properties (IndexedDB via idb-keyval, sync on reconnect)",
                    "Add web app manifest (icons 192/512, theme_color, background_color, display standalone)",
                    "Add Lighthouse PWA CI gate to GitHub Actions (score > 90)",
                ],
            },
            {
                "summary": "Document upload (Cloudflare R2) and WeasyPrint PDF generation",
                "labels":  ["phase-3", "backend", "documents"],
                "description": adf(
                    "Build secure document upload, storage, signed URL access, PDF generation, "
                    "and automatic RAG indexing for all uploaded documents.",
                    "## Acceptance Criteria",
                    "- Multipart upload to R2 with type validation (PDF, DOCX, images) and 10MB limit",
                    "- Signed URLs (1h expiry) for secure document download",
                    "- WeasyPrint generates PDF for: mortgage summary, viewing confirmation, offer letter",
                    "- Uploaded documents auto-indexed into Qdrant (async Celery task)",
                    "- 7-year lifecycle retention rule configured on R2 bucket",
                ),
                "tasks": [
                    "Build document upload endpoint (multipart, type validation, R2 key generation)",
                    "Implement signed URL generator (1h expiry, audit log on access)",
                    "Build WeasyPrint PDF templates: mortgage summary, viewing confirmation, offer letter",
                    "Implement PDF generation endpoint (POST /api/v1/documents/generate-pdf)",
                    "Wire RAG indexing Celery task trigger on document upload (chunk -> embed -> upsert Qdrant)",
                    "Configure Cloudflare R2 lifecycle policy (7-year retention, delete on expiry)",
                ],
            },
            {
                "summary": "LLM auto-translation and human review queue",
                "labels":  ["phase-3", "backend", "frontend", "i18n"],
                "description": adf(
                    "Automatically translate all content to AR/HI/RU on save, with a "
                    "human review queue for quality control (Arabic priority).",
                    "## Acceptance Criteria",
                    "- All property titles, descriptions, and CMS content auto-translated on save",
                    "- Translation review queue shows pending/approved/rejected per locale",
                    "- Translation memory prevents re-translating already-approved strings",
                    "- External reviewer role can approve translations without full admin access",
                    "- WhatsApp template approval status tracked per language",
                ),
                "tasks": [
                    "Implement auto-translate-on-save hook (SQLAlchemy event listener on content fields)",
                    "Build translation_reviews table (original, translated, locale, status, reviewer_id)",
                    "Build translation review UI (side-by-side comparison, approve/reject/edit inline)",
                    "Implement translation memory (hash original text -> cache approved translation)",
                    "Add external reviewer RBAC role with translation-only access scope",
                    "Build WhatsApp template approval status tracker per language in admin panel",
                ],
            },
            {
                "summary": "UTM attribution and campaign tracking",
                "labels":  ["phase-3", "backend", "frontend", "analytics"],
                "description": adf(
                    "Capture UTM parameters and referral codes at all entry points, "
                    "store first-touch and last-touch attribution, and build the source dashboard.",
                    "## Acceptance Criteria",
                    "- UTM params captured on web entry, WhatsApp deeplinks, and QR codes",
                    "- First-touch and last-touch attribution stored on lead record",
                    "- Unique WhatsApp/QR links generated per campaign with UTM auto-appended",
                    "- Attribution source dashboard shows top sources and conversion rates",
                    "- Referral codes tracked per agent and per campaign",
                ),
                "tasks": [
                    "Implement UTM parameter capture middleware (web query params + WhatsApp ref param)",
                    "Store first-touch and last-touch attribution fields on leads table",
                    "Build unique WhatsApp/QR link generator (short link + UTM params per campaign)",
                    "Build attribution source dashboard page (top UTM sources, channel breakdown, conversion)",
                    "Implement referral code system (per agent, per campaign, stored on lead record)",
                ],
            },
        ],
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # EPIC 4 — Phase 4: Production Hardening (Weeks 10–12)
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "summary": "[Phase 4] Production Hardening",
        "labels":  ["phase-4", "production", "hardening"],
        "description": adf(
            "Harden the platform for production: off-plan features, broker API adapters, "
            "e-signature, event-driven workflows, full observability, content pages, "
            "analytics reports, public API docs, and 500-concurrent load testing.",
            "## Acceptance Criteria",
            "- All 36 product decisions implemented and verified",
            "- 100-item golden QA dataset passes at > 85% quality score",
            "- Lighthouse > 90 on all public pages (CI gate)",
            "- Load test: 500 concurrent conversations at P95 < 2s response time",
            "- Kubernetes manifests prepared for AWS UAE migration",
        ),
        "stories": [
            {
                "summary": "Off-plan EOI flow and Matterport virtual tour embeds",
                "labels":  ["phase-4", "backend", "frontend", "off-plan"],
                "description": adf(
                    "Build the complete off-plan project experience including EOI submission flow, "
                    "Matterport virtual tour embeds, and launch event visibility.",
                    "## Acceptance Criteria",
                    "- Off-plan project detail pages render with payment plan simulator",
                    "- EOI submission form sends confirmation WhatsApp message",
                    "- EOI status transitions (submitted -> under review -> approved/rejected) notify lead",
                    "- Matterport virtual tour embeds load lazily and open fullscreen",
                ),
                "tasks": [
                    "Build off_plan_projects CRUD API and data model",
                    "Build EOI submission endpoint (POST /eoi) + eoi_submissions table",
                    "Build Matterport embed component (lazy iframe, fullscreen, mobile-responsive)",
                    "Build off-plan project detail page with payment plan simulator UI",
                    "Implement EOI status notification flow (WhatsApp on status change)",
                ],
            },
            {
                "summary": "Emaar and Damac broker API adapters",
                "labels":  ["phase-4", "backend", "integration", "off-plan"],
                "description": adf(
                    "Build broker API adapters for Emaar and Damac to sync off-plan project data.",
                    "## Acceptance Criteria",
                    "- Emaar adapter fetches project listings, availability, and pricing",
                    "- Damac adapter with same interface",
                    "- Weekly broker data sync Celery task running",
                    "- broker_api_id deduplication prevents duplicate projects",
                ),
                "tasks": [
                    "Implement Emaar broker API adapter (project listings, unit availability, pricing)",
                    "Implement Damac broker API adapter (same PropertySourceAdapter interface)",
                    "Build broker data deduplication (broker_api_id + broker_source unique key)",
                    "Implement weekly broker sync Celery task (Sunday 3AM UAE)",
                    "Write integration tests with broker API sandbox responses",
                ],
            },
            {
                "summary": "Launch event broadcast system",
                "labels":  ["phase-4", "backend", "frontend", "off-plan"],
                "description": adf(
                    "Build a system for announcing off-plan project launches to segmented lead audiences.",
                    "## Acceptance Criteria",
                    "- Admin can create launch event with target audience filters (budget + area)",
                    "- Broadcast dispatched to WhatsApp + Telegram + email simultaneously",
                    "- Delivery tracking shows sent/delivered/read counts per channel",
                    "- Broadcasts scheduled for future dates",
                ),
                "tasks": [
                    "Build launch_events table and CRUD API",
                    "Implement audience segmentation (filter leads by budget range + preferred locations)",
                    "Build broadcast dispatcher (WhatsApp template + Telegram + SendGrid email in parallel)",
                    "Build admin UI for creating, scheduling, and monitoring launch broadcasts",
                    "Implement broadcast delivery tracking analytics",
                ],
            },
            {
                "summary": "DocuSign / HelloSign e-signature integration",
                "labels":  ["phase-4", "backend", "documents", "integration"],
                "description": adf(
                    "Integrate e-signature capability so agents can send contracts for signing "
                    "directly via chat or from the lead profile.",
                    "## Acceptance Criteria",
                    "- DocuSign API adapter creates envelope and returns signing URL",
                    "- Signing link sent via WhatsApp/web chat message",
                    "- Signature completion webhook updates document record status",
                    "- Signed document stored in R2 with audit trail",
                    "- HelloSign adapter as configured fallback",
                ),
                "tasks": [
                    "Implement DocuSign API adapter (create_envelope, get_signing_url, get_status)",
                    "Implement HelloSign adapter (same ESignatureAdapter interface)",
                    "Build sign-via-chat flow (send signing link in WhatsApp/web message)",
                    "Implement DocuSign webhook receiver (envelope completed -> update document record)",
                    "Build signed document audit trail (who signed, when, IP, stored in audit_logs)",
                ],
            },
            {
                "summary": "Event-driven workflows — price alerts and follow-up triggers",
                "labels":  ["phase-4", "backend", "workflows"],
                "description": adf(
                    "Build automated event-driven workflows triggered by data changes and time intervals.",
                    "## Acceptance Criteria",
                    "- Price drop > 5% triggers WhatsApp alert to leads with matching saved searches",
                    "- 7-day no-activity trigger sends re-engagement message",
                    "- 24h post-viewing follow-up sent automatically",
                    "- All workflow triggers logged in audit_logs",
                    "- Opt-out respected for price alerts",
                ),
                "tasks": [
                    "Implement price change detector (ETL compare vs current DB price, > 5% threshold)",
                    "Build saved_search matching engine (run lead filters against changed properties)",
                    "Implement price alert WhatsApp notification with opt-out token link",
                    "Implement 7d no-activity re-engagement Celery task",
                    "Implement 24h post-viewing follow-up task (triggered on appointment completion)",
                    "Log all workflow trigger events to analytics_events and audit_logs",
                ],
            },
            {
                "summary": "Observability — Prometheus exporters, Grafana dashboards and alerts",
                "labels":  ["phase-4", "devops", "observability"],
                "description": adf(
                    "Set up the full observability stack with metrics exporters, dashboards, "
                    "and actionable alerts for the operations team.",
                    "## Acceptance Criteria",
                    "- Prometheus metrics exported: request latency, LLM latency, error rates, active conversations",
                    "- 3 Grafana dashboards: API health, AI performance, business KPIs",
                    "- Slack webhook alerts firing on: error rate > 1%, P95 latency > 3s, queue > 50",
                    "- Render health check alerts configured for all services",
                    "- SLA target: 99.9% monthly uptime tracked via Grafana",
                ),
                "tasks": [
                    "Implement Prometheus metrics exporters (FastAPI middleware: latency, status codes, active convs)",
                    "Add LLM-specific metrics (inference latency, token usage, intent distribution)",
                    "Configure Grafana Cloud workspace + Prometheus remote write endpoint",
                    "Build API health dashboard (request rate, error rate, latency P50/P95/P99)",
                    "Build AI performance dashboard (intent accuracy, LLM latency, escalation rate)",
                    "Build business KPI dashboard (leads/day, conversion rate, bookings, handoffs)",
                    "Configure Slack webhook alerts with runbook links for each alert rule",
                ],
            },
            {
                "summary": "LangSmith tracing, golden QA dataset and automated evaluation",
                "labels":  ["phase-4", "ai", "quality", "observability"],
                "description": adf(
                    "Set up LangSmith for complete LLM observability and build the golden QA "
                    "dataset with nightly automated evaluation to catch quality regressions.",
                    "## Acceptance Criteria",
                    "- Every LangGraph node execution traced in LangSmith with inputs/outputs",
                    "- 100-item golden QA dataset covers: search, qualification, booking, calculator, RAG flows",
                    "- Nightly evaluation run scores > 85% overall quality",
                    "- LangSmith alert fires on quality regression (< 80% score)",
                    "- conversation_analytics table populated with daily aggregates",
                ),
                "tasks": [
                    "Configure LangSmith project, traces for all LangGraph nodes (name, tags, metadata)",
                    "Implement custom evaluators: intent accuracy, response relevance, guardrail compliance",
                    "Build 100-item golden QA dataset (input + expected_output + metadata JSON)",
                    "Implement nightly evaluation Celery task (run golden set, score, store results)",
                    "Build conversation_analytics daily aggregation job (Celery, store per tenant per day)",
                    "Configure LangSmith quality regression alert (< 80% -> Slack notification)",
                ],
            },
            {
                "summary": "Content pages — community guides, developer profiles and blog CMS",
                "labels":  ["phase-4", "frontend", "content", "seo"],
                "description": adf(
                    "Build the SEO-optimized content pages with live data, Tiptap CMS, "
                    "and automatic RAG indexing for AI knowledge enrichment.",
                    "## Acceptance Criteria",
                    "- Community guide pages render with live PostGIS area stats and property counts",
                    "- Developer profile pages show all projects and available units",
                    "- Blog CMS uses Tiptap editor with image upload and multilingual content",
                    "- Market reports downloadable as PDF and RAG-indexed",
                    "- Sitemap.xml auto-generated and submitted to Google Search Console",
                ),
                "tasks": [
                    "Build community guide page template (/communities/[slug]) with live PostGIS stats",
                    "Build developer profile pages (/developers/[slug]) with project listing",
                    "Integrate Tiptap editor in admin CMS (blog, community guides, market reports)",
                    "Build market reports page (/reports): PDF download + RAG indexing on publish",
                    "Build ROI comparison tool (side-by-side 2-4 properties, all metrics)",
                    "Generate sitemap.xml (all listings, communities, blog posts) and ping Google",
                ],
            },
            {
                "summary": "Analytics reports — daily digest email and weekly PDF auto-report",
                "labels":  ["phase-4", "backend", "analytics"],
                "description": adf(
                    "Build automated analytics reporting delivering daily email digests "
                    "and weekly comprehensive PDF reports to agency admins.",
                    "## Acceptance Criteria",
                    "- Daily digest email sent 8AM UAE with: new leads, conversations, bookings, top sources",
                    "- Weekly PDF report generated Monday 9AM UAE with full funnel analysis",
                    "- Metabase custom query builder accessible in admin panel",
                    "- All analytics respect tenant isolation (no cross-tenant data)",
                ),
                "tasks": [
                    "Build analytics aggregation queries (funnel stages, channel breakdown, agent metrics)",
                    "Implement daily digest SendGrid email (HTML template with KPI metrics)",
                    "Implement weekly PDF report (WeasyPrint + matplotlib charts: funnel, trends, top agents)",
                    "Schedule digest (Celery Beat: daily 8AM GST) and weekly report (Monday 9AM GST)",
                    "Embed Metabase iframe in admin analytics page (custom query builder, pre-built dashboards)",
                ],
            },
            {
                "summary": "Public API documentation site and developer webhook portal",
                "labels":  ["phase-4", "backend", "frontend", "api"],
                "description": adf(
                    "Publish comprehensive API documentation and a developer portal for "
                    "third-party integrations, including outbound webhook management.",
                    "## Acceptance Criteria",
                    "- Swagger UI at /api/v1/docs and ReDoc at /api/v1/redoc",
                    "- API usage guide covers: auth, pagination, webhooks, rate limits, versioning",
                    "- Developer portal page has code examples in Python, JS, cURL",
                    "- Outbound webhooks signed with HMAC-SHA256 (X-Signature header)",
                    "- Webhook management UI lets tenants register, test, and view delivery logs",
                ),
                "tasks": [
                    "Enrich OpenAPI spec with full examples, response schemas, and error codes",
                    "Write API usage guide (auth flow, pagination pattern, webhook setup, rate limits)",
                    "Build developer portal page (Next.js static, code examples, SDK snippets)",
                    "Implement HMAC-SHA256 outbound webhook signing (X-Signature header)",
                    "Build webhook management UI (register endpoint, select events, test, view delivery log)",
                    "Document API versioning and deprecation policy in developer portal",
                ],
            },
            {
                "summary": "Load testing — 500 concurrent conversations",
                "labels":  ["phase-4", "testing", "performance"],
                "description": adf(
                    "Validate the platform can handle 500 concurrent conversations at launch "
                    "with acceptable response times, then document scaling thresholds.",
                    "## Acceptance Criteria",
                    "- Locust scenarios: search (40%), qualify (30%), book (20%), RAG (10%)",
                    "- 500 concurrent users at P95 < 2s response time",
                    "- Error rate < 0.1% under load",
                    "- Bottlenecks identified and resolved (slow queries indexed, pool sizes tuned)",
                    "- Load test report documenting results and scaling thresholds",
                ),
                "tasks": [
                    "Set up Locust load test project with 4 conversation scenarios (search, qualify, book, RAG)",
                    "Run baseline load test (50 users) and establish performance baseline",
                    "Run 500-concurrent test, capture P50/P95/P99 and error rates",
                    "Analyze slow queries (EXPLAIN ANALYZE), add missing indexes, tune connection pools",
                    "Re-run 500-concurrent test after optimizations (pass criterion: P95 < 2s)",
                    "Document load test results, bottlenecks, fixes, and scaling thresholds in Confluence",
                ],
            },
            {
                "summary": "Kubernetes manifests and AWS UAE migration preparation",
                "labels":  ["phase-4", "devops", "kubernetes", "aws"],
                "description": adf(
                    "Prepare Kubernetes manifests for the future AWS UAE (me-central-1) migration "
                    "so the team can execute it with minimal downtime.",
                    "## Acceptance Criteria",
                    "- K8s Deployments for FastAPI, Celery worker, Celery beat",
                    "- HPA configured (FastAPI: 3-10 pods, Celery: 2-8 pods)",
                    "- Ingress with TLS (nginx-ingress)",
                    "- ConfigMap + Secrets templates (AWS Secrets Manager integration)",
                    "- Migration runbook documented in Confluence (step-by-step, < 30min downtime)",
                ),
                "tasks": [
                    "Write K8s Deployment manifests (fastapi, celery-worker, celery-beat) with resource limits",
                    "Write HorizontalPodAutoscaler (HPA) for API (3-10 pods) and worker (2-8 pods)",
                    "Write K8s Service (ClusterIP) and Ingress (nginx-ingress with TLS cert-manager)",
                    "Write ConfigMap for non-secret config + Secret templates (AWS Secrets Manager ref)",
                    "Write migration runbook (Render -> AWS EKS: DNS cutover, data migration, rollback plan)",
                ],
            },
        ],
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # EPIC 5 — Phase 5: v1.1 Adapters & Expansion (Weeks 13–18)
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "summary": "[Phase 5] v1.1 — Adapters & Expansion",
        "labels":  ["phase-5", "v1.1", "expansion"],
        "description": adf(
            "Expand the platform with additional CRM adapters, RERA data, Dubizzle feed, "
            "ZH/FR/DE language support, Arabic admin panel, Outlook calendar, "
            "live mortgage rates, and React Native app planning.",
            "## Acceptance Criteria",
            "- All planned v1.1 adapters functional and covered by tests",
            "- 6 languages supported at launch (EN, AR, HI, RU + ZH, FR, DE)",
            "- Arabic admin panel fully RTL and reviewed by native speaker",
            "- React Native project scaffold created with design mockups approved",
        ),
        "stories": [
            {
                "summary": "Additional CRM adapters — Salesforce, Propspace and Masterkey",
                "labels":  ["phase-5", "backend", "integration", "crm"],
                "description": adf(
                    "Extend the CRM adapter layer with three additional providers "
                    "popular in the UAE real estate market.",
                    "## Acceptance Criteria",
                    "- Salesforce, Propspace, Masterkey adapters implement CRMAdapter interface",
                    "- Unit tests with mocked API responses for all three adapters",
                    "- CRM adapter selection configurable per tenant in admin panel",
                ),
                "tasks": [
                    "Implement Salesforce CRM adapter (OAuth2, upsert_lead, log_activity, sync_deals)",
                    "Implement Propspace adapter (API key auth, contact + property sync)",
                    "Implement Masterkey adapter (lead sync, activity log)",
                    "Add CRM adapter selector to admin tenant configuration panel",
                    "Write unit tests for all three adapters (mocked API responses)",
                ],
            },
            {
                "summary": "RERA transaction data integration",
                "labels":  ["phase-5", "backend", "integration", "rera"],
                "description": adf(
                    "Integrate RERA transaction data to show regulatory property history "
                    "and maintain compliance data on listings.",
                    "## Acceptance Criteria",
                    "- RERA transaction data synced weekly and shown on property detail pages",
                    "- DLD registration number and broker license displayed on all listings",
                    "- RERA compliance badge on verified listings",
                ),
                "tasks": [
                    "Implement RERA API adapter (transaction history, developer registrations)",
                    "Normalize RERA data to internal property + compliance schema",
                    "Implement weekly RERA sync Celery task (Saturday 2AM UAE)",
                    "Display RERA transaction badges and DLD registration on property detail pages",
                    "Build RERA compliance data section in property admin editor",
                ],
            },
            {
                "summary": "Dubizzle property feed adapter",
                "labels":  ["phase-5", "backend", "integration", "etl"],
                "description": adf(
                    "Add Dubizzle as a fourth property data source with deduplication "
                    "against existing Bayut and Property Finder records.",
                    "## Acceptance Criteria",
                    "- Dubizzle feed parsed and normalized to internal Property schema",
                    "- Cross-portal deduplication prevents duplicate listings",
                    "- Dubizzle included in nightly ETL schedule",
                ),
                "tasks": [
                    "Implement Dubizzle feed adapter (PropertySourceAdapter interface, XML/API parse)",
                    "Build cross-portal deduplication (fuzzy match on title + address + price)",
                    "Add Dubizzle to nightly_property_sync Celery task rotation",
                    "Write unit tests for Dubizzle feed parsing (20 sample records)",
                ],
            },
            {
                "summary": "Mandarin, French and German language support",
                "labels":  ["phase-5", "frontend", "i18n"],
                "description": adf(
                    "Extend the platform to support three additional languages (ZH, FR, DE) "
                    "for the international buyer segment.",
                    "## Acceptance Criteria",
                    "- All UI strings translated to ZH, FR, DE",
                    "- WhatsApp Business templates submitted and approved in ZH, FR, DE",
                    "- Language switcher includes all 7 options (EN, AR, HI, RU, ZH, FR, DE)",
                    "- Chat agent responds correctly in ZH, FR, DE",
                ),
                "tasks": [
                    "Add ZH, FR, DE locale files (LLM-assisted translation of all UI strings)",
                    "Submit WhatsApp Business message templates in ZH, FR, DE for Meta approval",
                    "Extend language switcher to include ZH, FR, DE options",
                    "Test all chat flows in ZH, FR, DE (search, qualify, book scenarios)",
                ],
            },
            {
                "summary": "Full Arabic admin panel with RTL layout",
                "labels":  ["phase-5", "frontend", "admin", "rtl", "arabic"],
                "description": adf(
                    "Translate the entire admin panel to Arabic and ensure full RTL "
                    "layout correctness reviewed by a native Arabic speaker.",
                    "## Acceptance Criteria",
                    "- All admin panel strings translated to Arabic",
                    "- Full RTL layout across all admin pages",
                    "- Email and notification templates available in Arabic",
                    "- Native Arabic speaker QA review completed and sign-off received",
                ),
                "tasks": [
                    "Translate all admin panel UI strings to Arabic (all next-intl keys for admin routes)",
                    "Verify and fix RTL layout across all admin pages (tables, forms, modals, charts)",
                    "Translate all email notification templates to Arabic",
                    "Conduct native Arabic speaker QA review session and address feedback",
                ],
            },
            {
                "summary": "Microsoft Outlook calendar adapter",
                "labels":  ["phase-5", "backend", "integration", "calendar"],
                "description": adf(
                    "Add Microsoft 365 Outlook as a second calendar integration option "
                    "for agents using the Microsoft ecosystem.",
                    "## Acceptance Criteria",
                    "- Microsoft Graph API OAuth2 flow works for per-agent authorization",
                    "- CalendarAdapter interface fully implemented for Outlook",
                    "- Bidirectional sync works (availability read + event create/update/delete)",
                    "- Recurring event conflicts handled gracefully",
                ),
                "tasks": [
                    "Implement Microsoft Graph API OAuth2 flow (per-agent, token storage in DB)",
                    "Implement OutlookCalendarAdapter (full CalendarAdapter interface)",
                    "Build bidirectional sync: platform -> Outlook events and Outlook -> platform availability",
                    "Handle timezone, recurring events, and conflict resolution",
                    "Write integration tests with Microsoft Graph API sandbox",
                ],
            },
            {
                "summary": "Live UAE bank mortgage rate integration",
                "labels":  ["phase-5", "backend", "integration", "calculators"],
                "description": adf(
                    "Replace static mortgage rates with live rates from UAE banks, "
                    "refreshed weekly and displayed with last-updated timestamp.",
                    "## Acceptance Criteria",
                    "- Live rates fetched from at least 3 UAE banks (ADCB, Emirates NBD, FAB)",
                    "- Weekly rate refresh Celery task running",
                    "- Mortgage calculator uses live rates with last-updated timestamp shown",
                    "- Rate comparison table on calculator page",
                ),
                "tasks": [
                    "Research UAE bank mortgage rate API endpoints (ADCB, Emirates NBD, FAB) and authenticate",
                    "Implement bank rate adapters normalized to internal MortgageRate schema",
                    "Implement weekly rate refresh Celery task (Monday 8AM UAE)",
                    "Update mortgage calculator to use live rates from DB with last-updated display",
                    "Build rate comparison table on /calculators page (side-by-side bank offers)",
                ],
            },
            {
                "summary": "React Native v2 app — planning, design and scaffold",
                "labels":  ["phase-5", "mobile", "react-native"],
                "description": adf(
                    "Plan and design the React Native mobile app (v2) that extends the PWA "
                    "with native capabilities.",
                    "## Acceptance Criteria",
                    "- v2 app scope documented (features beyond PWA parity)",
                    "- Full user flows designed in Figma (chat, search, listings, dashboard)",
                    "- API contract changes documented for mobile requirements",
                    "- React Native + Expo project scaffold created",
                    "- Design mockups reviewed and approved by stakeholders",
                ),
                "tasks": [
                    "Define React Native v2 app scope (native push, biometric auth, camera, offline-first)",
                    "Create information architecture and user flow diagrams for all mobile screens",
                    "Design UI mockups in Figma (chat, property search, listing detail, agent dashboard)",
                    "Document API contract changes needed for mobile (pagination, image sizes, offline sync)",
                    "Create React Native + Expo project scaffold (TypeScript, React Navigation, Zustand)",
                ],
            },
        ],
    },
]


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    total_epics  = len(EPICS)
    total_stories = sum(len(e["stories"]) for e in EPICS)
    total_tasks   = sum(len(s["tasks"]) for e in EPICS for s in e["stories"])
    print(f"Creating {total_epics} Epics / {total_stories} Stories / {total_tasks} Subtasks")
    print(f"Project: {JIRA_BASE}/jira/software/projects/{PROJECT}/boards\n")

    created_epics   = 0
    created_stories = 0
    created_tasks   = 0
    errors          = 0

    for epic_data in EPICS:
        print(f"\n{'='*70}")

        # Create Epic
        epic_key = create_epic(
            epic_data["summary"],
            epic_data["description"],
            epic_data["labels"],
        )
        if not epic_key:
            errors += 1
            continue
        created_epics += 1

        # Create Stories under this Epic
        for story_data in epic_data["stories"]:
            story_key = create_story(
                story_data["summary"],
                story_data["description"],
                story_data["labels"],
                epic_key,
            )
            if not story_key:
                errors += 1
                continue
            created_stories += 1

            # Create Subtasks under this Story
            for task_summary in story_data["tasks"]:
                task_key = create_subtask(
                    task_summary,
                    story_key,
                    story_data["labels"],
                )
                if task_key:
                    created_tasks += 1
                else:
                    errors += 1

    print(f"\n{'='*70}")
    print(f"DONE")
    print(f"  Epics:    {created_epics}/{total_epics}")
    print(f"  Stories:  {created_stories}/{total_stories}")
    print(f"  Tasks:    {created_tasks}/{total_tasks}")
    print(f"  Errors:   {errors}")
    print(f"\nBoard: {JIRA_BASE}/jira/software/projects/{PROJECT}/boards")


if __name__ == "__main__":
    main()
