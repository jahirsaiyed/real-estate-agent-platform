# Deployment Architecture

Two deployment topologies: MVP (Render + Vercel) for launch, Production (AWS UAE) at scale.

---

## MVP Deployment — Render + Vercel

Target: Launch (Phases 1–4). Supports 500 concurrent conversations.

```mermaid
graph TB
    subgraph "Global CDN"
        Vercel["Vercel Edge Network\nNext.js 14 App\n(SSR + ISR + static)\nCDN caching for listing pages\nEdge middleware for auth\nCustom domain + SSL"]
    end

    subgraph "Render Cloud"
        subgraph "Web Services"
            API["FastAPI Backend\nRender Web Service\n2x CPU / 4GB RAM\nAuto-scale: 1–4 instances\ngunicorn + uvicorn workers\nPort: 8000"]
        end

        subgraph "Background Workers"
            CeleryW["Celery Worker\nRender Background Worker\n2x CPU / 2GB RAM\nConcurrency: 8 per instance\n1–2 instances"]
            CeleryBeat["Celery Beat\nRender Background Worker\n0.5 CPU / 512MB\nScheduler (single instance)"]
        end

        subgraph "Managed Databases (Render)"
            PG["PostgreSQL 16\nRender Managed DB\n2 CPU / 4GB RAM / 50GB SSD\nAutomated daily backups\nPoint-in-time recovery\nPostGIS extension"]
            PGReplica["Read Replica\nMetabase analytics only\n1 CPU / 2GB RAM"]
        end
    end

    subgraph "Managed Cloud Services"
        Upstash["Upstash Redis\nServerless Redis\nGlobal replication\nPay-per-request"]
        QdrantCloud["Qdrant Cloud\nManaged cluster\n2 nodes / 4GB RAM each\n50GB vector storage"]
        CloudAMQP["CloudAMQP\nRabbitMQ\nLemur plan (launch)\nJackrabbit (production)"]
        R2["Cloudflare R2\nObject storage\nZero egress fees\nS3-compatible API"]
    end

    subgraph "External APIs"
        WhatsApp["Meta WhatsApp\nBusiness API"]
        Telegram["Telegram\nBot API"]
        LLMProv["LLM Provider\ngemma4-cloud"]
        SendGrid["SendGrid\nTransactional Email"]
        Twilio["Twilio SMS"]
    end

    subgraph "Observability"
        LangSmith["LangSmith\nLLM tracing"]
        Grafana["Grafana Cloud\nPrometheus remote write\nMetrics + alerts\nSlack webhook"]
        Metabase["Metabase\nRender Web Service\nConnected to PG replica"]
    end

    Users[Users / Agents] -->|"HTTPS"| Vercel
    Vercel -->|"REST API calls\nHTTPS"| API

    WhatsApp & Telegram -->|"Webhooks"| API

    API <-->|"TCP 5432"| PG
    API <-->|"TCP 6379"| Upstash
    API <-->|"HTTPS gRPC"| QdrantCloud
    API -->|"AMQP"| CloudAMQP
    API -->|"HTTPS"| R2
    API -->|"HTTPS"| LLMProv
    API -->|"HTTPS"| WhatsApp & SendGrid & Twilio

    CloudAMQP -->|"AMQP"| CeleryW
    CeleryW <-->|"TCP 5432"| PG
    CeleryW <-->|"TCP 6379"| Upstash
    CeleryW -->|"HTTPS gRPC"| QdrantCloud
    CeleryBeat -->|"AMQP"| CloudAMQP

    PG -->|"Replication"| PGReplica
    PGReplica --> Metabase

    API -.->|"Traces"| LangSmith
    API -.->|"Prometheus\nremote write"| Grafana

    style API fill:#2d6a4f,color:#fff
    style Vercel fill:#1168bd,color:#fff
    style PG fill:#6b4226,color:#fff
    style Upstash fill:#c9184a,color:#fff
    style QdrantCloud fill:#7b2d8b,color:#fff
```

---

## Production Deployment — AWS UAE (me-central-1)

Target: Post-migration (500+ concurrent, Phase 5+). Kubernetes-based.

```mermaid
graph TB
    subgraph "AWS UAE — me-central-1"
        subgraph "VPC — 10.0.0.0/16"

            subgraph "Public Subnets (Multi-AZ)"
                ALB["Application Load Balancer\nHTTPS termination\nWAF (OWASP rules)\nDDoS protection"]
                NAT["NAT Gateway\nOutbound traffic\nfrom private subnets"]
            end

            subgraph "Private Subnet — App Tier"
                EKS["EKS Cluster\n---\nfastapi-deployment (3–10 pods)\ncelery-worker (2–8 pods)\ncelery-beat (1 pod)\nHPA on CPU + custom metrics\nNode group: c6i.xlarge"]
            end

            subgraph "Private Subnet — Data Tier"
                RDS["RDS PostgreSQL 16\nMulti-AZ (Primary + Standby)\nr6g.xlarge\n500GB gp3 SSD\nAuto-scaling storage\nPostGIS, pg_vector extensions"]
                RDSRead["RDS Read Replica\nMetabase + Analytics\nAuto-promoted on failure"]
                ElastiCache["ElastiCache Redis 7\nCluster mode enabled\n3 shards / 2 replicas\ncache.r6g.large"]
            end

            subgraph "Private Subnet — Message Bus"
                AmazonMQ["Amazon MQ (RabbitMQ)\nBroker: mq.m5.large\nMulti-AZ active/standby\nTLS + auth"]
            end
        end

        subgraph "AWS Managed Services"
            ECR["ECR\nContainer Registry\nImage scanning enabled"]
            S3["S3 (me-central-1)\nDocument storage\nVersioning + lifecycle rules\n7-year retention policy"]
            CloudFront["CloudFront\nCDN for static assets\nEdge locations"]
            Route53["Route 53\nDNS + health checks\nFailover routing"]
            SecretsManager["Secrets Manager\nDB credentials, API keys\nAuto-rotation enabled"]
            CloudWatch["CloudWatch\nLogs + metrics\nContainer Insights"]
        end

        subgraph "Kubernetes Workloads"
            Ingress["nginx-ingress\nSSL termination\nRate limiting\nCORS policy"]
            FastAPIPods["FastAPI Pods\nHPA: 3–10 replicas\nRequests: 500m CPU, 512Mi\nLimits: 2 CPU, 2Gi\nReadiness + liveness probes"]
            CeleryPods["Celery Worker Pods\nHPA: 2–8 replicas\nRequests: 1 CPU, 1Gi"]
            CeleryBeatPod["Celery Beat\n1 replica (leader election)"]
        end
    end

    subgraph "External Services (retained)"
        Vercel2["Vercel (Next.js)\nGlobal CDN stays on Vercel\nor migrated to CloudFront"]
        QdrantProd["Qdrant Cloud\nProduction cluster (scaled up)\nor self-hosted on EKS"]
        LLMProv2["LLM Provider\ngemma4-cloud"]
    end

    Users[Users] -->|"HTTPS"| Route53
    Route53 --> CloudFront --> ALB
    ALB --> Ingress --> FastAPIPods

    FastAPIPods <--> RDS
    FastAPIPods <--> ElastiCache
    FastAPIPods --> AmazonMQ
    FastAPIPods <--> S3
    FastAPIPods --> LLMProv2
    FastAPIPods --> QdrantProd

    AmazonMQ --> CeleryPods
    CeleryBeatPod --> AmazonMQ
    CeleryPods <--> RDS & ElastiCache & S3 & QdrantProd

    FastAPIPods -.->|"pull images"| ECR
    CeleryPods -.->|"pull images"| ECR
    FastAPIPods -.->|"secrets"| SecretsManager
    FastAPIPods -.->|"logs"| CloudWatch

    RDS --> RDSRead --> Metabase2[Metabase\non EKS]
```

---

## CI/CD Pipeline

```mermaid
flowchart LR
    Dev[Developer\npush to branch] --> PR[Pull Request\nGitHub]

    PR --> CI

    subgraph "CI — GitHub Actions"
        CI[Trigger on PR]
        CI --> Lint[Lint + Type Check\nruff, mypy, eslint]
        CI --> UnitTest[Unit Tests\npytest, jest\nCoverage check: >80%]
        CI --> IntTest[Integration Tests\nDocker Compose\nTestcontainers]
        CI --> PHICheck[PHI/PII Scan\ncheck-phi-leaks.sh]
        CI --> LHCheck[Lighthouse CI\nPWA score >90]
        Lint & UnitTest & IntTest & PHICheck & LHCheck --> CIPass{All pass?}
    end

    CIPass -->|"yes"| MergeMain[Merge to main]
    CIPass -->|"no"| Block[Block merge]

    MergeMain --> CD

    subgraph "CD — Render + Vercel (MVP)"
        CD[Auto-deploy on merge to main]
        CD --> BuildBackend[Build FastAPI Docker image]
        CD --> BuildFrontend[Build Next.js]
        BuildBackend --> PushRender[Deploy to Render\nBlue/green deployment]
        BuildFrontend --> PushVercel[Deploy to Vercel\nAutomatic preview → production]
        PushRender --> DBMigrate[Run Alembic migrations\nPre-deployment hook]
        DBMigrate --> SmokeTest[Smoke tests\nHealth endpoint checks]
        SmokeTest --> Notify[Slack notification\nDeploy success/failure]
    end
```

---

## Environment Configuration

| Variable Group | MVP (Render) | Production (AWS) | Notes |
|----------------|-------------|-----------------|-------|
| Database | `DATABASE_URL` Render managed | `DATABASE_URL` RDS via Secrets Manager | Same env var name — no code change |
| Redis | `REDIS_URL` Upstash | `REDIS_URL` ElastiCache | Same |
| Object Storage | `R2_*` Cloudflare R2 | `S3_*` or `R2_*` | Adapter config switch |
| Message Bus | `RABBITMQ_URL` CloudAMQP | `RABBITMQ_URL` Amazon MQ | Same |
| LLM | `LLM_MODEL_ID` | `LLM_MODEL_ID` | Swappable via single env var |
| Qdrant | `QDRANT_URL` + `QDRANT_API_KEY` | Same (scaled cluster) | Same |
| WhatsApp | `WHATSAPP_*` | `WHATSAPP_*` | Same |

All secrets managed via Render Environment Groups (MVP) → AWS Secrets Manager (production).
