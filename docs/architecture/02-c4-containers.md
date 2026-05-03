# C4 Level 2 — Container Diagram

Shows all deployable units (containers) within the platform and how they communicate.

---

## Container Diagram

```mermaid
graph TB
    classDef frontend fill:#1168bd,color:#fff,stroke:#0e5ca8
    classDef backend fill:#2d6a4f,color:#fff,stroke:#1b4332
    classDef data fill:#6b4226,color:#fff,stroke:#4a2c1a
    classDef worker fill:#7b2d8b,color:#fff,stroke:#5c1f6b
    classDef external fill:#666,color:#fff,stroke:#555

    %% Actors
    EndUser["End User"]
    Agent["Agent / Admin"]

    %% Frontend
    subgraph "Vercel — Frontend"
        NextJS["Next.js 14 App\n---\nApp Router, SSR/ISR\nTailwind + shadcn/ui\nPWA (service worker)\nEmbeddable chat widget\nListing + detail pages\nAdmin panel\nAgent dashboard\nMapbox map views\nPort: 443 (HTTPS)"]
    end

    %% API
    subgraph "Render — Backend"
        FastAPI["FastAPI Backend\n---\nREST API /api/v1/\nJWT auth + RBAC\nOpenAPI auto-spec\nRate limiting\nWebhook handler\nPort: 8000"]

        LangGraph["LangGraph Orchestrator\n---\nIntent classifier\nAgent state machine\nTool execution graph\nMemory read/write\nGuardrails node\n(runs inside FastAPI process)"]

        CeleryWorker["Celery Workers\n---\nNightly ETL (2AM UAE)\nFollow-up reminders\nPrice alert triggers\nKB re-index jobs\nNotification dispatch\nPDF report generation"]
    end

    %% Channels
    subgraph "External Channel Adapters (within FastAPI)"
        WAAdapter["WhatsApp Adapter\n---\nMeta Business API\nWebhook receiver\nTemplate management"]
        TGAdapter["Telegram Adapter\n---\nBot API\nWebhook receiver"]
        WebAdapter["Web Chat Adapter\n---\nWebSocket / SSE\nSession management"]
    end

    %% Data stores
    subgraph "Managed Data Services"
        PostgreSQL["PostgreSQL\n---\nRender Managed\nPostGIS extension\nRead replica → Metabase\nAll relational data\nPort: 5432"]

        Redis["Redis\n---\nUpstash (serverless)\nSession / short-term memory\nCelery broker & result store\nRate limit counters\nPub/sub for real-time\nPort: 6379"]

        QdrantCloud["Qdrant Cloud\n---\nVector store\nProperty embeddings\nKB / document chunks\nConversation memory\nHybrid search (dense+sparse)"]

        CloudflareR2["Cloudflare R2\n---\nS3-compatible\nDocument uploads\nProperty images\nGenerated PDFs\nBrochures"]
    end

    %% Message bus
    subgraph "Event Bus"
        RabbitMQ["RabbitMQ\n---\nCloudAMQP Managed\nEvent routing\nDead-letter queues\nFanout for broadcasts\nPort: 5672 / 15672"]
    end

    %% Observability
    subgraph "Observability Stack"
        LangSmith["LangSmith\nLLM tracing"]
        Prometheus["Prometheus + Grafana\nMetrics + alerting"]
        Metabase["Metabase\nBusiness analytics\nOn PG read replica"]
    end

    %% External
    LLMProvider["LLM Provider\nblissful_ishizaka_626/gemma4-cloud"]
    WhatsAppAPI["WhatsApp Business API"]
    TelegramAPI["Telegram Bot API"]
    CRMs["CRM Systems\n(Zoho / HubSpot)"]
    Calendars["Calendar Systems\n(Google / Outlook)"]
    PropertyPortals["Property Portals\n(Bayut / Property Finder / RERA)"]

    %% Flows
    EndUser -->|"HTTPS"| NextJS
    Agent -->|"HTTPS"| NextJS
    NextJS -->|"REST /api/v1/\nHTTPS"| FastAPI

    WhatsAppAPI -->|"Webhook POST"| WAAdapter
    TelegramAPI -->|"Webhook POST"| TGAdapter
    WAAdapter & TGAdapter & WebAdapter --> FastAPI

    FastAPI <-->|"Orchestration\ncalls"| LangGraph
    FastAPI -->|"Enqueue\njobs"| Redis
    FastAPI -->|"Publish\nevents"| RabbitMQ

    LangGraph -->|"LLM inference"| LLMProvider
    LangGraph -->|"Vector search\n& upsert"| QdrantCloud
    LangGraph <-->|"Session\nmemory"| Redis
    LangGraph <-->|"Relational\nqueries"| PostgreSQL

    FastAPI <-->|"CRUD"| PostgreSQL
    FastAPI <-->|"Cache + sessions"| Redis
    FastAPI <-->|"Document ops"| CloudflareR2

    RabbitMQ -->|"Consume\njobs"| CeleryWorker
    CeleryWorker <-->|"Data write"| PostgreSQL
    CeleryWorker <-->|"Queue ops"| Redis
    CeleryWorker -->|"Vector upsert"| QdrantCloud
    CeleryWorker -->|"CRM push"| CRMs
    CeleryWorker -->|"Notifications"| WhatsAppAPI

    FastAPI -->|"CRM sync"| CRMs
    FastAPI -->|"Calendar sync"| Calendars
    CeleryWorker -->|"Portal ETL"| PropertyPortals

    FastAPI -.->|"Traces"| LangSmith
    FastAPI -.->|"Metrics"| Prometheus
    PostgreSQL -.->|"Read replica"| Metabase

    class NextJS frontend
    class FastAPI,LangGraph,CeleryWorker,WAAdapter,TGAdapter,WebAdapter backend
    class PostgreSQL,Redis,QdrantCloud,CloudflareR2,RabbitMQ data
    class LangSmith,Prometheus,Metabase worker
    class LLMProvider,WhatsAppAPI,TelegramAPI,CRMs,Calendars,PropertyPortals external
```

---

## Container Responsibilities

| Container | Technology | Host | Primary Responsibility |
|-----------|-----------|------|----------------------|
| Next.js Web App | Next.js 14, Tailwind, shadcn/ui | Vercel | SSR frontend, chat widget, listing pages, admin/agent UI, PWA |
| FastAPI Backend | Python 3.12, FastAPI | Render (web service) | REST API, business logic, webhook handling, orchestration entry point |
| LangGraph Orchestrator | LangGraph, LangChain | In-process (FastAPI) | Agent state machine, intent routing, tool execution, guardrails |
| Celery Workers | Celery 5, Python | Render (worker service) | Async jobs: ETL, nightly sync, notifications, report generation |
| PostgreSQL | PostgreSQL 16 + PostGIS | Render Managed DB | All relational data — leads, conversations, properties, tenants, audit logs |
| Redis | Redis 7 | Upstash | Session/short-term memory, Celery broker, rate limiting, pub/sub |
| Qdrant Cloud | Qdrant | Qdrant Cloud | Vector store for property search (hybrid), RAG chunks, long-term memory |
| Cloudflare R2 | S3-compatible | Cloudflare | Document/image storage, PDF output, brochures, 7-year retention |
| RabbitMQ | RabbitMQ 3 | CloudAMQP | Event bus for async workflows — price alerts, follow-ups, broadcasts |

---

## Inter-Container Communication

| From | To | Protocol | Notes |
|------|-----|----------|-------|
| Next.js | FastAPI | HTTPS REST | All API calls, auth via JWT |
| WhatsApp API | FastAPI | HTTPS Webhook | Signed with HMAC-SHA256 |
| Telegram API | FastAPI | HTTPS Webhook | Bot token verified |
| FastAPI | LangGraph | In-process call | Single process, no network hop |
| FastAPI | PostgreSQL | TCP (psycopg3) | Connection pool via SQLAlchemy |
| FastAPI | Redis | TCP (redis-py) | Sessions, cache, Celery enqueue |
| FastAPI | Qdrant | HTTPS gRPC | Vector ops via qdrant-client |
| FastAPI | RabbitMQ | AMQP | Event publishing |
| RabbitMQ | Celery | AMQP | Job consumption |
| Celery | PostgreSQL | TCP | Job result persistence |
| LangGraph | LLM Provider | HTTPS | LLM inference, streamed responses |
