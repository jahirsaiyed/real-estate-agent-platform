# Sequence Diagrams — Key Flows

Covers the six primary workflows in the platform.

---

## 1. New Lead — WhatsApp Message to Qualification

```mermaid
sequenceDiagram
    actor User as End User (WhatsApp)
    participant WA as WhatsApp Business API
    participant GW as FastAPI Gateway
    participant LG as LangGraph Orchestrator
    participant IC as Intent Classifier
    participant QA as Qualification Agent
    participant RG as Response Generator
    participant GR as Guardrails Node
    participant Redis as Redis (Session)
    participant PG as PostgreSQL
    participant WAPI as WhatsApp API (outbound)

    User->>WA: "Hi, I'm looking for a 2BR apartment in Dubai Marina"
    WA->>GW: POST /webhooks/whatsapp (HMAC verified)
    GW->>GW: Validate HMAC-SHA256 signature
    GW->>PG: Upsert lead record (phone number, channel=whatsapp)
    GW->>Redis: Get/create conversation session
    GW->>LG: Invoke agent graph (message, session, tenant_config)

    LG->>Redis: Load session memory + lead context
    LG->>IC: Classify intent
    IC-->>LG: intent=qualify, entities={bedrooms:2, area:"Dubai Marina"}

    LG->>QA: Run qualification agent
    QA->>PG: Load existing lead qualification scores
    QA-->>LG: Missing dimensions: budget, purpose, timeline
    Note over QA,LG: Dimension 1/8 collected. Ask next question.

    LG->>RG: Generate response (ask about budget, warm tone, EN)
    RG->>RG: Call LLM with prompt + context
    RG-->>LG: "Great! What is your budget range for this property?"

    LG->>GR: Post-LLM filter
    GR->>GR: Check for RERA compliance, disclaimers
    GR-->>LG: pass (no violations)

    LG->>Redis: Update session (dimension collected, conversation state)
    LG->>PG: Update lead qualification_status=in_progress

    LG-->>GW: Response text + updated state
    GW->>WAPI: Send WhatsApp message to user
    WAPI->>User: "Great! What is your budget range for this property?"

    Note over User,WAPI: Qualification continues across multiple turns until all 8 dimensions are scored
```

---

## 2. Property Search Flow

```mermaid
sequenceDiagram
    actor User
    participant GW as FastAPI Gateway
    participant LG as LangGraph Orchestrator
    participant SA as Property Search Agent
    participant PG as PostgreSQL + PostGIS
    participant Qdrant as Qdrant Cloud
    participant RG as Response Generator

    User->>GW: "Show me 3BR villas in Palm Jumeirah under 5M AED freehold"
    GW->>LG: Invoke agent graph

    LG->>LG: Intent = search
    LG->>SA: Execute property search tool

    SA->>SA: Parse filters
    Note over SA: bedrooms=3, type=villa,<br/>area="Palm Jumeirah",<br/>price_max=5000000, freehold=true

    par Parallel search
        SA->>PG: PostGIS geo query (Palm Jumeirah polygon)\n+ structured filters (beds, type, price, freehold)
        SA->>Qdrant: Dense vector search (query embedding)\n+ sparse BM25 (keyword match)
    end

    PG-->>SA: 12 matching property IDs
    Qdrant-->>SA: 20 semantically similar results (with scores)

    SA->>SA: Merge + deduplicate + rank by relevance + recency
    SA->>PG: Fetch full property details (top 10)
    SA-->>LG: Top 10 properties with metadata

    LG->>RG: Generate response with search results
    RG->>RG: Format 3-card preview + "View all" link
    RG->>RG: Include Golden Visa badge if price >= 2M AED
    RG->>RG: Append RERA disclaimer

    RG-->>GW: Response + property_cards payload
    GW-->>User: Message with 3 property cards + map view
    Note over User: User can tap a card to see full listing<br/>or refine search in same conversation
```

---

## 3. Appointment Booking Flow

```mermaid
sequenceDiagram
    actor User
    participant GW as FastAPI Gateway
    participant LG as LangGraph Orchestrator
    participant BA as Booking Agent
    participant CalEngine as Calendar Engine (DB)
    participant GCal as Google Calendar API
    participant CRM as CRM Adapter (Zoho/HubSpot)
    participant NS as Notification Service
    participant WhatsApp as WhatsApp API
    participant PG as PostgreSQL

    User->>GW: "I'd like to view the Palm villa on Saturday morning"
    GW->>LG: Invoke agent graph

    LG->>LG: Intent = book
    LG->>BA: Execute booking tool (property_id, lead_id, preferred: Saturday morning)

    BA->>PG: Get assigned agent for lead
    BA->>CalEngine: Query available slots (agent_id, date=Saturday, time=morning)
    CalEngine->>GCal: Check Google Calendar free/busy
    GCal-->>CalEngine: Busy: 9AM-10AM
    CalEngine-->>BA: Available slots: 10:00 AM, 11:00 AM, 11:30 AM

    BA-->>LG: Slot options returned
    LG->>LG: Present slots to user
    GW-->>User: "Available Saturday: 10:00 AM, 11:00 AM, 11:30 AM — which works?"

    User->>GW: "11 AM works!"
    GW->>LG: Invoke agent (slot selection)

    LG->>BA: Confirm booking (slot=11:00 AM Saturday)
    BA->>PG: INSERT appointment (lead_id, agent_id, property_id, time, status=confirmed)
    BA->>CalEngine: Block slot in DB calendar
    BA->>GCal: Create Google Calendar event (agent + lead)
    GCal-->>BA: event_id returned
    BA->>PG: Update appointment with google_event_id
    BA->>CRM: Log activity: "Viewing scheduled for Palm villa"

    BA->>NS: Trigger appointment_confirmed notification
    NS->>WhatsApp: Send confirmation to user (template: appt_confirmed)
    NS->>WhatsApp: Send reminder to agent

    BA-->>LG: Booking confirmed
    LG-->>GW: Confirmation message + appointment details
    GW-->>User: "Confirmed! Saturday 11:00 AM at Palm Jumeirah villa. You'll receive a reminder 24hrs before."

    Note over BA,PG: Celery job scheduled: 24hr reminder\n+ 1hr reminder before viewing
```

---

## 4. Human Handoff Flow

```mermaid
sequenceDiagram
    actor User
    participant LG as LangGraph Orchestrator
    participant QA as Qualification Agent
    participant HA as Handoff Agent
    participant PG as PostgreSQL
    participant Redis as Redis
    participant NS as Notification Service
    participant AgentDash as Agent Dashboard (Next.js)
    participant HumanAgent as Human Agent

    Note over LG,QA: Trigger condition detected:\nLead qualified + requested callback\nOR budget > AED 5M\nOR 3 consecutive failed attempts\nOR explicit "speak to agent" request\nOR after-hours urgency

    LG->>QA: Check qualification score
    QA-->>LG: Score: 78/100, status=qualified, trigger=budget>5M

    LG->>HA: Execute handoff
    HA->>PG: Query available agents (tenant_id, current_load, specialization)
    HA->>PG: SELECT best available agent (round-robin + load balancing)

    alt Agent available
        HA->>PG: INSERT handoff record (lead_id, agent_id, reason, transcript)
        HA->>PG: UPDATE conversation status=handoff
        HA->>PG: UPDATE lead assigned_agent_id
        HA->>Redis: Tag session as human_handoff=true (stop LLM responses)

        HA->>NS: Notify agent (WhatsApp + dashboard push)
        NS->>AgentDash: WebSocket push: new handoff notification
        NS-->>HumanAgent: WhatsApp: "New qualified lead: budget AED 7M, Palm Jumeirah 3BR"

        HA-->>LG: Handoff complete, agent assigned
        LG-->>User: "I'm connecting you with one of our specialists now. [Agent Name] will be with you shortly. Full conversation context has been shared."

    else No agent available
        HA->>PG: INSERT handoff_queue record (priority=high if urgent)
        HA-->>LG: Queued, no agent available
        LG-->>User: "All specialists are currently busy. You're next in queue. Expect a response within 30 minutes. I'll continue helping you in the meantime."
        Note over LG: LLM continues handling basic\nqueries until agent picks up
    end

    HumanAgent->>AgentDash: Open handoff queue
    AgentDash->>PG: Load full conversation transcript + lead profile + AI summary
    HumanAgent->>AgentDash: Accept handoff
    AgentDash->>PG: UPDATE handoff status=accepted
```

---

## 5. RAG Document Retrieval Flow

```mermaid
sequenceDiagram
    participant User
    participant LG as LangGraph Orchestrator
    participant RA as RAG Agent
    participant Embed as Embedding Model
    participant Qdrant as Qdrant Cloud
    participant PG as PostgreSQL
    participant RG as Response Generator

    User->>LG: "What are the service charges for DAMAC Hills?"

    LG->>LG: Intent = info/rag
    LG->>RA: Execute RAG retrieval (query="DAMAC Hills service charges")

    RA->>Embed: Embed query → dense vector (1536-dim)
    Embed-->>RA: query_vector

    par Hybrid search
        RA->>Qdrant: Dense vector search (query_vector, collection=knowledge_base, top_k=10)
        RA->>Qdrant: Sparse BM25 search ("DAMAC Hills service charges", top_k=10)
    end

    Qdrant-->>RA: Dense results (chunks + scores)
    Qdrant-->>RA: Sparse results (chunks + scores)

    RA->>RA: Reciprocal Rank Fusion (RRF) reranking
    RA->>PG: Fetch document metadata for top 5 chunks (source, title, published_date)
    PG-->>RA: Document metadata

    RA-->>LG: Top 5 chunks + source citations

    LG->>RG: Generate response grounded in retrieved context
    RG->>RG: Build prompt: system + context chunks + conversation history + query
    RG->>RG: Call LLM (grounded generation, cite sources)
    RG-->>LG: "According to the DAMAC Hills community guide (updated Jan 2026), service charges are..."

    LG-->>User: Answer with source citation + "View full report" link
```

---

## 6. Nightly ETL Pipeline

```mermaid
sequenceDiagram
    participant Scheduler as Celery Beat (2:00 AM UAE)
    participant RMQ as RabbitMQ
    participant Worker as Celery Worker
    participant Adapter as Property Source Adapter
    participant Source as Portal API (Bayut/PF/RERA)
    participant PG as PostgreSQL
    participant Embed as Embedding Model
    participant Qdrant as Qdrant Cloud
    participant NS as Notification Service

    Scheduler->>RMQ: Enqueue etl.nightly_property_sync (tenant_id)
    RMQ->>Worker: Deliver job
    Worker->>PG: INSERT etl_job (type=portal_sync, status=running)

    Worker->>Adapter: fetch_listings(source=bayut, since=last_sync)
    Adapter->>Source: API call with auth + pagination
    Source-->>Adapter: Raw listing data (paginated)
    Adapter->>Adapter: normalize() → internal Property schema

    loop For each property batch (100 records)
        Worker->>PG: UPSERT properties (conflict on external_id)\nUPDATE price, availability, status
        Worker->>Embed: Embed property title + description + location
        Embed-->>Worker: dense vector
        Worker->>Qdrant: Upsert property vectors (id, vector, payload)
    end

    Worker->>PG: UPDATE etl_job (status=completed, records_processed=N)
    Worker->>PG: Log price changes as analytics_events

    alt Price drops > 5% detected
        Worker->>PG: Query saved_searches matching changed properties
        Worker->>NS: Trigger price_alert notifications for matched leads
        NS->>NS: Send WhatsApp alerts to opted-in users
    end

    Note over Scheduler,Qdrant: Also runs: FX rate refresh (daily)\nOff-plan project updates (weekly)\nKB re-index on document publish (on-demand)
```
