# C4 Level 3 — Component Diagram

Shows internal components within the FastAPI backend and LangGraph orchestrator.

---

## FastAPI Backend Components

```mermaid
graph TB
    subgraph "FastAPI Backend — /api/v1/"

        subgraph "API Gateway Layer"
            RL[Rate Limiter\nSliding window\nper tenant/IP]
            Auth[JWT Auth Middleware\nRS256 tokens\nRBAC enforcement]
            WH[Webhook Handler\nHMAC-SHA256 verification\nWhatsApp + Telegram]
        end

        subgraph "Routers"
            ConvRouter[Conversations Router\nPOST /conversations\nGET /conversations/:id\nWS /chat/stream]
            LeadRouter[Leads Router\nCRUD /leads\nGET /leads/:id/score\nPOST /leads/:id/handoff]
            PropRouter[Properties Router\nGET /properties/search\nGET /properties/:id\nPOST /properties/import]
            ApptRouter[Appointments Router\nPOST /appointments\nGET /appointments\nPATCH /appointments/:id]
            AdminRouter[Admin Router\nTenant config\nUser management\nGuardrail rules\nAnalytics]
            WebhookRouter[Webhook Router\nPOST /webhooks/whatsapp\nPOST /webhooks/telegram\nPOST /webhooks/crm]
        end

        subgraph "Service Layer"
            ConvService[Conversation Service\nSession lifecycle\nMessage persistence\nSentiment tracking]
            LeadService[Lead Qualification Service\n8-dimension scorecard\nConfigurable per tenant\n3-strike + frustration detection]
            PropService[Property Search Service\nPostGIS geo queries\nHybrid Qdrant search\nDubai area taxonomy\nFreehold/off-plan filters]
            BookService[Booking Service\nCustom calendar engine\nSlot availability\nConflict detection\nGoogle Cal + Outlook sync]
            CRMService[CRM Adapter Service\nZoho adapter\nHubSpot adapter\nNormalized lead schema\nBidirectional sync]
            NotifService[Notification Service\nTemplate registry\nChannel routing\nDelivery tracking\nPer-user channel pref]
            DocService[Document Service\nR2 upload/download\nWeasyPrint PDF gen\nDocuSign integration\nRAG indexing trigger]
            CalcService[Calculator Service\nMortgage (UAE rules engine)\nROI estimator\nTCO calculator\nOff-plan payment simulator\nGolden Visa eligibility]
            ETLService[ETL / Ingestion Service\nCSV importer\nCRM sync adapter\nBayut / PF adapters\nRERA adapter\nEmbedding pipeline]
            GuardrailService[Guardrail Service\nPost-LLM output filter\nDisclaimer injection\nRERA compliance statement\nConfigurable boundary rules\nFull audit logging]
            AnalyticsService[Analytics Service\nFunnel event tracking\nUTM attribution\nConversation analytics\nDaily digest trigger\nWeekly PDF report]
            I18nService[i18n / Translation Service\nLLM auto-translate\nHuman review queue\nTranslation memory\nRTL support flag]
        end

        subgraph "Data Access Layer"
            PropRepo[Property Repository\nPostgreSQL + PostGIS\nQdrant vector ops]
            LeadRepo[Lead Repository\nPostgreSQL CRUD\nQualification state]
            ConvRepo[Conversation Repository\nMessage store\nRedis session cache]
            UserRepo[User / Tenant Repository\nRBAC roles\nTenant config]
            AuditRepo[Audit Log Repository\nImmutable append-only\nAll user actions]
        end
    end

    RL --> Auth --> ConvRouter & LeadRouter & PropRouter & ApptRouter & AdminRouter
    WH --> WebhookRouter

    ConvRouter --> ConvService
    LeadRouter --> LeadService
    PropRouter --> PropService
    ApptRouter --> BookService
    AdminRouter --> LeadService & PropService & AnalyticsService & GuardrailService
    WebhookRouter --> ConvService

    ConvService --> GuardrailService
    LeadService --> CRMService & NotifService
    PropService --> PropRepo
    BookService --> CRMService & NotifService
    DocService --> ETLService

    ConvService --> ConvRepo
    LeadService --> LeadRepo
    PropService --> PropRepo
    BookService --> LeadRepo
    AnalyticsService --> AuditRepo
    GuardrailService --> AuditRepo
```

---

## LangGraph Orchestrator — Agent Graph

```mermaid
graph TB
    START([START\nIncoming message]) --> MemLoad

    MemLoad[Memory Loader\nLoad Redis session\nLoad lead context\nLoad tenant config] --> IntentNode

    IntentNode{Intent Classifier\nLLM-based primary\nRule-based fallback\n---\nSearch / Book / Calculate\nQualify / Info / Handoff\nSmallTalk / Unclear}

    IntentNode -->|search| SearchAgent
    IntentNode -->|book| BookingAgent
    IntentNode -->|calculate| CalcAgent
    IntentNode -->|qualify| QualAgent
    IntentNode -->|info / rag| RAGAgent
    IntentNode -->|handoff| HandoffAgent
    IntentNode -->|smalltalk| ResponseGen
    IntentNode -->|unclear / fallback| ClarifyNode

    subgraph "Tool Agents"
        SearchAgent[Property Search Agent\nBuild Qdrant hybrid query\nApply PostGIS geo filter\nRank + format results\nReturn 3-card preview]

        BookingAgent[Booking Agent\nCheck calendar availability\nResolve agent + property\nCreate appointment\nTrigger confirmations]

        CalcAgent[Calculator Agent\nMortgage / ROI / TCO\nOff-plan payment plan\nGolden Visa check\nReturn formatted output]

        QualAgent[Qualification Agent\nScore 8 dimensions\nUpdate lead record\nDetect frustration\nDecide escalation]

        RAGAgent[RAG Retrieval Agent\nEmbed query\nQdrant similarity search\nRerank chunks\nInject into context]

        HandoffAgent[Handoff Agent\nCheck trigger conditions\nFind available agent\nTransfer full transcript\nSend notification]
    end

    ClarifyNode[Clarification Node\nGenerate clarifying question\nTrack attempt count\n3rd attempt → escalate]

    SearchAgent & BookingAgent & CalcAgent & QualAgent & RAGAgent & ClarifyNode --> ResponseGen

    HandoffAgent --> HandoffEnd([HANDOFF\nHuman agent takes over])

    ResponseGen[Response Generator\nBuild prompt with context\nCall LLM\nStream response\nApply tone persona\nLanguage: EN/AR/HI/RU]

    ResponseGen --> GuardrailNode

    GuardrailNode[Guardrails Node\nPost-LLM output filter\nDisclaimer injection\nRERA compliance check\nHallucination detection\nLog violations]

    GuardrailNode -->|pass| MemUpdate
    GuardrailNode -->|violation| Regenerate[Regenerate with\nsafer prompt]
    Regenerate --> GuardrailNode

    MemUpdate[Memory Update\nPersist to Redis session\nUpdate lead qualification\nUpsert Qdrant long-term\nLog analytics event]

    MemUpdate --> END([END\nDeliver response])

    style START fill:#2d6a4f,color:#fff
    style END fill:#2d6a4f,color:#fff
    style HandoffEnd fill:#c9184a,color:#fff
    style IntentNode fill:#1168bd,color:#fff
    style GuardrailNode fill:#e85d04,color:#fff
```

---

## Frontend Component Breakdown

```mermaid
graph TB
    subgraph "Next.js 14 App Router"

        subgraph "Public Routes — app/(public)/"
            HomePage[Home Page\n/\nHero + search bar]
            SearchPage[Search Page\n/search\nFilter panel + Mapbox + results]
            ListingPage[Listing Detail\n/properties/[slug]\nISR 1hr revalidation\nOpen Graph + SEO]
            CommunityPage[Community Guides\n/communities/[slug]\nLive data + RAG content]
            BlogPage[Blog & Reports\n/blog /reports\nTiptap CMS content]
            CalculatorsPage[Calculators\n/calculators\nMortgage, ROI, TCO, Golden Visa]
        end

        subgraph "Chat Widget — app/widget/"
            ChatWidget[Embeddable Chat Widget\n<script> embed\niFrame isolation\nWebSocket / SSE\nRTL Arabic support\nLanguage switcher]
            ChatMessages[Message Thread\nStreaming responses\nProperty cards\nAppointment picker\nDocument upload]
            ChatInput[Chat Input\nText + file upload\nQuick reply buttons\nVoice (future)]
        end

        subgraph "Admin Panel — app/admin/"
            TenantConfig[Tenant Configuration\nAI persona (Layla)\nGuardrail rules\nLanguage settings\nChannel config]
            PropertyMgmt[Property Management\nCSV import UI\nListing editor\nMedia upload]
            ContentCMS[Content CMS\nTiptap editor\nTranslation review queue\nMarket reports]
            AnalyticsDash[Analytics Dashboard\nFunnel metrics\nAgent performance\nAI quality scores\nMetabase embed]
        end

        subgraph "Agent Dashboard — app/dashboard/"
            LeadQueue[Lead Queue\nQualified leads\nHandoff notifications\nAssignment management]
            ConvViewer[Conversation Viewer\nFull transcript\nAI summary\nLead profile\nCRM quick-update]
            AgentCalendar[Agent Calendar\nAppointment view\nGoogle Cal sync status]
            Notifications[Notification Center\nInbound handoffs\nPrice alerts\nSystem events]
        end

        subgraph "Shared Components"
            PropertyCard[Property Card\nImage, price, beds, area\nGolden Visa badge\nOff-plan badge\nSave + share]
            MapView[Mapbox Map\nProperty pins\nDubai community polygons\nCluster on zoom-out]
            RTLProvider[RTL Provider\nArabic layout switching\ndirection: rtl CSS]
            AuthGuard[Auth Guard\nJWT cookie\nRole-based route guard]
        end
    end
```

---

## Adapter Pattern — External Integrations

All external systems are accessed through normalized adapter interfaces, making them swappable.

```mermaid
classDiagram
    class CRMAdapter {
        <<interface>>
        +upsert_lead(lead: Lead) ContactID
        +get_contact(external_id: str) Contact
        +log_activity(contact_id: str, activity: Activity)
        +sync_deals(tenant_id: str)
    }

    class ZohoCRMAdapter {
        +upsert_lead(lead)
        +get_contact(external_id)
        +log_activity(contact_id, activity)
        +sync_deals(tenant_id)
    }

    class HubSpotAdapter {
        +upsert_lead(lead)
        +get_contact(external_id)
        +log_activity(contact_id, activity)
        +sync_deals(tenant_id)
    }

    class PropertySourceAdapter {
        <<interface>>
        +fetch_listings(filters: dict) List~Property~
        +get_listing(external_id: str) Property
        +normalize(raw: dict) Property
    }

    class BayutAdapter {
        +fetch_listings(filters)
        +get_listing(external_id)
        +normalize(raw)
    }

    class PropertyFinderAdapter {
        +fetch_listings(filters)
        +get_listing(external_id)
        +normalize(raw)
    }

    class CalendarAdapter {
        <<interface>>
        +get_availability(agent_id, date_range) List~Slot~
        +create_event(appointment: Appointment) EventID
        +update_event(event_id, appointment)
        +delete_event(event_id)
    }

    class GoogleCalendarAdapter {
        +get_availability(agent_id, date_range)
        +create_event(appointment)
        +update_event(event_id, appointment)
        +delete_event(event_id)
    }

    class OutlookAdapter {
        +get_availability(agent_id, date_range)
        +create_event(appointment)
        +update_event(event_id, appointment)
        +delete_event(event_id)
    }

    CRMAdapter <|-- ZohoCRMAdapter
    CRMAdapter <|-- HubSpotAdapter
    PropertySourceAdapter <|-- BayutAdapter
    PropertySourceAdapter <|-- PropertyFinderAdapter
    CalendarAdapter <|-- GoogleCalendarAdapter
    CalendarAdapter <|-- OutlookAdapter
```
