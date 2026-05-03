# Technical Documentation — Real Estate Agent Platform

Dubai/UAE AI-powered real estate agent platform. Multi-tenant, multi-channel, multilingual.

---

## Documents

| # | Document | Contents |
|---|----------|---------|
| 01 | [System Overview](architecture/01-system-overview.md) | C4 Context diagram, high-level architecture layers, design principles |
| 02 | [C4 Container Diagram](architecture/02-c4-containers.md) | All deployable units: Next.js, FastAPI, LangGraph, Celery, PostgreSQL, Redis, Qdrant, R2, RabbitMQ |
| 03 | [Component Diagram](architecture/03-component-diagram.md) | FastAPI services, LangGraph agent graph, frontend components, adapter pattern |
| 04 | [Sequence Diagrams](architecture/04-sequence-diagrams.md) | 6 key flows: lead qualification, property search, booking, handoff, RAG retrieval, nightly ETL |
| 05 | [Data Flow](architecture/05-data-flow.md) | Ingestion → transformation → storage, memory architecture, ETL schedule, retention policy |
| 06 | [Deployment Architecture](architecture/06-deployment.md) | MVP (Render + Vercel) and Production (AWS UAE me-central-1) topologies + CI/CD pipeline |
| 07 | [Database Schema](architecture/07-database-schema.md) | ERD with 20+ tables, indexes, design decisions |
| 08 | [API Design](architecture/08-api-design.md) | All REST endpoints, request/response schemas, auth, versioning, webhooks |
| 09 | [Agent Architecture](architecture/09-agent-architecture.md) | LangGraph state schema, graph nodes, tool registry, LLM abstraction, persona config |

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, Tailwind CSS, shadcn/ui, Mapbox, PWA |
| Backend | FastAPI (Python 3.12), Pydantic v2 |
| Orchestration | LangGraph, LangChain |
| LLM | blissful_ishizaka_626/gemma4-cloud (model-agnostic) |
| Vector DB | Qdrant Cloud |
| Relational DB | PostgreSQL 16 + PostGIS |
| Cache / Sessions | Redis (Upstash) |
| Object Storage | Cloudflare R2 |
| Event Bus | RabbitMQ (CloudAMQP) |
| Job Scheduler | Celery + Redis Beat |
| Observability | Prometheus + Grafana + LangSmith + Metabase |
| Channels | WhatsApp Business, Telegram, Web Chat Widget |
| Hosting (MVP) | Vercel + Render |
| Hosting (Prod) | AWS UAE me-central-1 |

---

## Related Documents

- [PRD](../prd_real_estate_agent_platform.md) — Full product requirements
- [Product Decisions](../memory/product-decisions.md) — All 36 confirmed architectural decisions
- [Roadmap](../memory/roadmap.md) — 5-phase, 6-month implementation plan
