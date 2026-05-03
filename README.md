# Real Estate Agent Platform

AI-powered real estate agent for the Dubai/UAE market. Multi-tenant, multi-channel, multilingual — built to qualify leads, search properties, book viewings, and escalate to human agents via WhatsApp, Telegram, and web chat.

---

## Architecture at a Glance

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 (App Router), Tailwind CSS, shadcn/ui |
| Backend | FastAPI (Python 3.12), Pydantic v2, SQLAlchemy 2 async |
| Orchestration | LangGraph + LangChain |
| LLM | `blissful_ishizaka_626/gemma4-cloud` via OpenRouter (model-agnostic) |
| Relational DB | PostgreSQL 16 + PostGIS |
| Vector DB | Qdrant Cloud |
| Cache / Sessions | Redis (Upstash) |
| Event Bus | RabbitMQ (CloudAMQP) |
| Object Storage | Cloudflare R2 |
| Job Scheduler | Celery + Redis Beat |
| Channels | WhatsApp Business API, Telegram, Web Chat Widget |
| Hosting (MVP) | Vercel (frontend) + Render (backend) |
| Hosting (Prod) | AWS UAE `me-central-1` |

---

## Repository Structure

```
real-estate-agent/
├── backend/                  # FastAPI + LangGraph
│   ├── app/
│   │   ├── main.py
│   │   ├── core/             # config, security (RS256 JWT), database
│   │   ├── api/v1/           # health, auth, (future: leads, properties, …)
│   │   ├── models/           # 19 SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic v2 request/response schemas
│   │   └── agents/           # LangGraph graph, AgentState, LLMProvider
│   ├── alembic/              # DB migrations
│   ├── tests/
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── render.yaml
├── frontend/                 # Next.js 14 admin shell
│   ├── src/
│   │   ├── app/              # App Router pages
│   │   │   ├── (auth)/login/
│   │   │   └── (admin)/dashboard/
│   │   ├── components/admin/ # sidebar, header
│   │   └── lib/              # api (Axios), auth (token helpers), utils
│   ├── package.json
│   ├── Dockerfile
│   └── vercel.json
├── docker-compose.yml        # Local dev services
├── .github/workflows/        # CI — backend + frontend
└── docs/                     # Architecture docs (01–09)
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
# Fill in OPENROUTER_API_KEY, LANGSMITH_API_KEY, QDRANT_URL, etc.
```

### 3. Generate JWT keys (one-time)

```bash
mkdir -p backend/secrets
openssl genrsa -out backend/secrets/jwt_private.pem 2048
openssl rsa -in backend/secrets/jwt_private.pem -pubout -out backend/secrets/jwt_public.pem
```

### 4. Backend

```bash
cd backend
uv sync --extra dev
alembic upgrade head       # runs all DB migrations (creates PostGIS + 19 tables)
uvicorn app.main:app --reload
```

API available at `http://localhost:8000`
Docs (Swagger) at `http://localhost:8000/api/v1/docs`

### 5. Frontend

```bash
cd frontend
npm ci
npm run dev
```

Admin shell at `http://localhost:3000`

---

## Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Liveness check → `{status: "ok"}` |
| `GET` | `/api/v1/health/ready` | Readiness — checks DB, Redis, Qdrant |
| `POST` | `/api/v1/auth/login` | Email + password → `access_token` + `refresh_token` |
| `POST` | `/api/v1/auth/refresh` | Rotate access token |
| `POST` | `/api/v1/auth/logout` | Revoke token (Redis blocklist) |
| `GET` | `/api/v1/auth/me` | Current user profile + role + tenant |

Full API reference: [`docs/architecture/08-api-design.md`](docs/architecture/08-api-design.md)

---

## Agent Graph (Sprint 1 Skeleton)

```
memory_loader → intent_classifier → response_generator → guardrails_node → memory_update
```

- **`memory_loader`** — loads Redis session + Qdrant long-term memory (stub in Sprint 1)
- **`intent_classifier`** — rule-based keyword matching + LLM fallback; detects: `search`, `book`, `calculate`, `qualify`, `rag`, `handoff`, `smalltalk`
- **`response_generator`** — calls `LLMProvider` (routes to OpenRouter / Anthropic / OpenAI based on `LLM_MODEL_ID`)
- **`guardrails_node`** — post-response validation; RERA compliance, competitor checks (stub in Sprint 1)
- **`memory_update`** — persists to Redis + Qdrant (stub in Sprint 1)

Full node implementations: [`docs/architecture/09-agent-architecture.md`](docs/architecture/09-agent-architecture.md)

---

## Database

19 tables with row-level multi-tenancy (`tenant_id` on every table). PostGIS spatial columns on `properties` (`POINT`) and `locations` (`POLYGON`).

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

**MVP** — push to `main` deploys automatically:
- Frontend → Vercel (configured via `frontend/vercel.json`)
- Backend → Render (configured via `backend/render.yaml`)

**Production** — AWS UAE `me-central-1` (ECS Fargate, RDS Aurora, ElastiCache). See [`docs/architecture/06-deployment.md`](docs/architecture/06-deployment.md).

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
