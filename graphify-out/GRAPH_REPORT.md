# Graph Report - .  (2026-05-04)

## Corpus Check
- 116 files · ~87,310 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 766 nodes · 1212 edges · 65 communities detected
- Extraction: 72% EXTRACTED · 27% INFERRED · 0% AMBIGUOUS · INFERRED: 333 edges (avg confidence: 0.62)
- Token cost: 4,200 input · 1,850 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Database Model Layer|Database Model Layer]]
- [[_COMMUNITY_API Routes and Schemas|API Routes and Schemas]]
- [[_COMMUNITY_Property Search and Listing|Property Search and Listing]]
- [[_COMMUNITY_LangGraph Agent Pipeline|LangGraph Agent Pipeline]]
- [[_COMMUNITY_UI Design Canvas Prototype|UI Design Canvas Prototype]]
- [[_COMMUNITY_Lead Management Domain|Lead Management Domain]]
- [[_COMMUNITY_Architecture Documentation|Architecture Documentation]]
- [[_COMMUNITY_Vector Search and Embeddings|Vector Search and Embeddings]]
- [[_COMMUNITY_Agent Infrastructure Core|Agent Infrastructure Core]]
- [[_COMMUNITY_Agent Node Implementations|Agent Node Implementations]]
- [[_COMMUNITY_Booking and Appointment Flow|Booking and Appointment Flow]]
- [[_COMMUNITY_UI Screen Data and Helpers|UI Screen Data and Helpers]]
- [[_COMMUNITY_CRM and Conversation Layer|CRM and Conversation Layer]]
- [[_COMMUNITY_ORM Entity Classes|ORM Entity Classes]]
- [[_COMMUNITY_Authentication and Security|Authentication and Security]]
- [[_COMMUNITY_Jira Automation Scripts|Jira Automation Scripts]]
- [[_COMMUNITY_Notification and Webhook Service|Notification and Webhook Service]]
- [[_COMMUNITY_Frontend Admin Shell|Frontend Admin Shell]]
- [[_COMMUNITY_Confluence API Helpers|Confluence API Helpers]]
- [[_COMMUNITY_Sprint Management|Sprint Management]]
- [[_COMMUNITY_UI Design Handoff Assets|UI Design Handoff Assets]]
- [[_COMMUNITY_Jira Issue Creator|Jira Issue Creator]]
- [[_COMMUNITY_Config and Database Setup|Config and Database Setup]]
- [[_COMMUNITY_Frontend Admin Components|Frontend Admin Components]]
- [[_COMMUNITY_Confluence Docs Publisher|Confluence Docs Publisher]]
- [[_COMMUNITY_LLM Provider Abstraction|LLM Provider Abstraction]]
- [[_COMMUNITY_Lead Qualification Scoring|Lead Qualification Scoring]]
- [[_COMMUNITY_Module 31|Module 31]]
- [[_COMMUNITY_Module 32|Module 32]]
- [[_COMMUNITY_Module 33|Module 33]]
- [[_COMMUNITY_Module 34|Module 34]]
- [[_COMMUNITY_Module 35|Module 35]]
- [[_COMMUNITY_Module 36|Module 36]]
- [[_COMMUNITY_Module 37|Module 37]]
- [[_COMMUNITY_Module 38|Module 38]]
- [[_COMMUNITY_Module 39|Module 39]]
- [[_COMMUNITY_Module 40|Module 40]]
- [[_COMMUNITY_Module 43|Module 43]]
- [[_COMMUNITY_Module 44|Module 44]]
- [[_COMMUNITY_Module 45|Module 45]]
- [[_COMMUNITY_Module 50|Module 50]]
- [[_COMMUNITY_Module 51|Module 51]]
- [[_COMMUNITY_Module 52|Module 52]]
- [[_COMMUNITY_Module 53|Module 53]]
- [[_COMMUNITY_Module 54|Module 54]]
- [[_COMMUNITY_Module 55|Module 55]]
- [[_COMMUNITY_Module 56|Module 56]]
- [[_COMMUNITY_Module 57|Module 57]]
- [[_COMMUNITY_Module 75|Module 75]]
- [[_COMMUNITY_Module 76|Module 76]]
- [[_COMMUNITY_Module 77|Module 77]]
- [[_COMMUNITY_Module 78|Module 78]]
- [[_COMMUNITY_Module 79|Module 79]]
- [[_COMMUNITY_Module 80|Module 80]]
- [[_COMMUNITY_Module 81|Module 81]]
- [[_COMMUNITY_Module 82|Module 82]]
- [[_COMMUNITY_Module 83|Module 83]]
- [[_COMMUNITY_Module 84|Module 84]]
- [[_COMMUNITY_Module 85|Module 85]]
- [[_COMMUNITY_Module 86|Module 86]]
- [[_COMMUNITY_Module 87|Module 87]]
- [[_COMMUNITY_Module 88|Module 88]]
- [[_COMMUNITY_Module 89|Module 89]]
- [[_COMMUNITY_Module 90|Module 90]]
- [[_COMMUNITY_Module 91|Module 91]]

## God Nodes (most connected - your core abstractions)
1. `Base` - 53 edges
2. `TimestampMixin` - 32 edges
3. `PropertyRepository` - 24 edges
4. `LeadRepository` - 21 edges
5. `SQLAlchemy DeclarativeBase` - 17 edges
6. `new_uuid (UUID4 factory)` - 17 edges
7. `ConversationRepository` - 16 edges
8. `ConversationChannel` - 14 edges
9. `ConversationStatus` - 14 edges
10. `ConversationLanguage` - 14 edges

## Surprising Connections (you probably didn't know these)
- `Sidebar (Admin Sidebar Component)` --semantically_similar_to--> `App (Main Shell + Router)`  [INFERRED] [semantically similar]
  frontend/src/components/admin/sidebar.tsx → docs/real-estate-agent/project/app.jsx
- `Create Confluence Pages Script` --references--> `05 Data Flow Diagram`  [EXTRACTED]
  scripts/create_confluence_pages.py → docs/architecture/05-data-flow.md
- `git-commit Skill â€” Conventional Commits Automation` --conceptually_related_to--> `Agent Architecture â€” LangGraph Orchestrator`  [AMBIGUOUS]
  skills/git-commit/SKILL.md → docs/architecture/09-agent-architecture.md
- `grill-me Skill â€” Relentless Design Interview` --conceptually_related_to--> `Agent Architecture â€” LangGraph Orchestrator`  [AMBIGUOUS]
  skills/grill-me/SKILL.md → docs/architecture/09-agent-architecture.md
- `build_graph()` --calls--> `property_search_agent()`  [INFERRED]
  backend\app\agents\graph.py → backend\app\agents\nodes\property_search.py

## Hyperedges (group relationships)
- **LangGraph Agent Pipeline: memory_loader â†’ intent_classifier â†’ specialist_nodes â†’ response_generator â†’ guardrails â†’ memory_update** — agents_graph, agents_state, agents_memory [EXTRACTED 1.00]
- **Hybrid Property Search: PropertySearchAgent + PropertyRepository + Qdrant Embeddings** — nodes_property_search, api_v1_properties, concept_hybrid_search [INFERRED 0.95]
- **Auth Security Stack: JWT RS256 + Redis Blocklist + Role-Based Access** — api_v1_auth, api_v1_deps, concept_rs256_jwt [INFERRED 0.95]
- **Multi-Tenant Cascade Isolation Pattern** — models_Lead, models_Conversation, models_Property [INFERRED 0.95]
- **Conversation-Message-Guardrail Agent Safety Flow** — models_Conversation, models_Message, models_GuardrailRule [INFERRED 0.85]
- **Lead Notification Delivery via Templates** — models_Lead, models_Notification, models_NotificationTemplate [EXTRACTED 1.00]
- **Hybrid PostGIS + Qdrant Property Search Pipeline** — repositories_property_PropertyRepository, services_embedding_search_properties, repositories_property_reciprocal_rank_fusion [EXTRACTED 0.95]
- **Lead Qualification Score Pipeline** — repositories_lead_LeadRepository, schemas_lead_QualificationScoreResponse, schemas_lead_QualificationDimension [EXTRACTED 1.00]
- **CRM Sync Zoho/HubSpot Fallback Pipeline** — services_crm_sync_lead_to_crm, services_crm_ZohoAdapter, services_crm_HubSpotAdapter [EXTRACTED 1.00]
- **UI Prototype System (DesignCanvas + Artboards + TweaksPanel)** — design_canvas_DesignCanvas, tweaks_panel_TweaksPanel, tweaks_panel_useTweaks [INFERRED 0.95]
- **Dual-Surface Design Review (Desktop + Mobile on Single Canvas)** — app_canvas_CanvasRoot, app_canvas_DesktopApp, mobile_app_MobileApp [EXTRACTED 1.00]
- **Frontend Auth Flow (Login â†’ Token Store â†’ API Requests)** — frontend_login_page, frontend_auth_helpers, frontend_api_axiosInstance [INFERRED 0.95]
- **Atlassian Toolchain â€” Jira REA + Confluence + Sprint Setup** — scripts_create_rea_jira, scripts_create_confluence_pages, scripts_setup_sprints, scripts_push_decisions_confluence [INFERRED 0.95]
- **Architecture Documentation Suite â€” 01 through 08** — arch_01_system_overview, arch_02_c4_containers, arch_03_component_diagram, arch_05_data_flow, arch_06_deployment, arch_07_database_schema, arch_08_api_design [EXTRACTED 1.00]
- **Local Dev Infrastructure â€” docker-compose + render.yaml + README** — root_docker_compose, backend_render_yaml, root_readme [INFERRED 0.85]
- **LangGraph Core Conversation Pipeline** — 09_memory_loader, 09_intent_classifier, 09_response_generator, 09_guardrails_node, 09_memory_update [EXTRACTED 0.95]
- **Hybrid Property Search (PostGIS + Qdrant + RRF)** — 09_property_search_agent, 09_rrf_ranking, 09_tool_registry [INFERRED 0.85]
- **UI v2 Shared JSX Components** — ui_v2_html, ui_screens1_jsx, ui_screens2_jsx, ui_data_jsx [EXTRACTED 0.95]

## Communities (92 total, 28 thin omitted)

### Community 0 - "Database Model Layer"
Cohesion: 0.08
Nodes (42): Base, DeclarativeBase, AnalyticsChannel, AnalyticsEvent, Appointment, AuditLog, Base, TimestampMixin (+34 more)

### Community 1 - "API Routes and Schemas"
Cohesion: 0.07
Nodes (37): BaseModel, ConversationChannel, ConversationLanguage, ConversationStatus, Message, ConversationRepository, MessageRepository, Conversation and message repositories. (+29 more)

### Community 2 - "Property Search and Listing"
Cohesion: 0.09
Nodes (30): PropertyPurpose, PropertyStatus, PropertyType, _build_search_query(), property_search_agent(), Property search agent node: hybrid PostGIS + Qdrant search., Execute hybrid property search and populate state['search_results']., Build a natural-language query string from extracted entities. (+22 more)

### Community 3 - "LangGraph Agent Pipeline"
Cohesion: 0.06
Nodes (29): clarification_node(), guardrails_node(), intent_classifier(), memory_loader(), memory_update(), Sprint 2 — Full LangGraph orchestrator.  Graph:   memory_loader → intent_classif, LLM intent classification with rule-based fast path., Increment clarification attempts counter. (+21 more)

### Community 4 - "UI Design Canvas Prototype"
Cohesion: 0.1
Nodes (34): CanvasRoot (Design Canvas Entry), DesktopApp (Canvas-Constrained Shell), App (Main Shell + Router), AGENTS (Mock Agent Records), LEADS (Mock Lead Records), MY_ACTIVITY (Buyer Activity Feed), MY_ALERTS (Buyer Alert Configs), MY_DOCUMENTS (Buyer Document Records) (+26 more)

### Community 5 - "Lead Management Domain"
Cohesion: 0.2
Nodes (18): LeadContactPreference, LeadLanguage, LeadPropertyType, LeadPurpose, LeadQualificationStatus, LeadSourceChannel, LeadRepository, Build the qualification scorecard response from a lead + entities. (+10 more)

### Community 6 - "Architecture Documentation"
Cohesion: 0.1
Nodes (30): 01 System Overview, 02 C4 Container Diagram, 03 Component Diagram, 05 Data Flow Diagram, 06 Deployment Architecture, 07 Database Schema, 08 API Design, Render Deployment Config (+22 more)

### Community 7 - "Vector Search and Embeddings"
Cohesion: 0.12
Nodes (27): MessageRepository, PropertyRepository, Merge PostGIS and Qdrant results using Reciprocal Rank Fusion., Hybrid PostGIS + Qdrant search. Returns (results, total_count)., _reciprocal_rank_fusion(), MessageCreate Schema, PropertyCreate Schema, PropertySearchParams Schema (+19 more)

### Community 8 - "Agent Infrastructure Core"
Cohesion: 0.1
Nodes (23): LangGraph Agent Orchestrator, LLM Provider (Model-Agnostic), Agent Memory (Redis + Qdrant), AgentState TypedDict, Initial Schema Migration 001, Alembic Env (Migration Runner), Auth API Router, FastAPI Dependencies (get_db, get_current_user) (+15 more)

### Community 9 - "Agent Node Implementations"
Cohesion: 0.12
Nodes (26): Agent Architecture â€” LangGraph Orchestrator, AgentState TypedDict, booking_agent Node, calculator_agent Node, clarification_node, guardrails_node â€” Post-LLM Output Validation, handoff_agent Node, intent_classifier Node (+18 more)

### Community 10 - "Booking and Appointment Flow"
Cohesion: 0.13
Nodes (14): build_graph(), AppointmentStatus, AppointmentType, booking_agent(), Booking agent node: check availability + create appointments., Handle booking intent: check slots or create appointment., AppointmentRepository, Appointment repository with availability slot logic. (+6 more)

### Community 11 - "UI Screen Data and Helpers"
Cohesion: 0.1
Nodes (6): fmtAED(), fmtAEDShort(), PropertyCard(), PropertyDetailScreen(), PropertyRow(), PipelineScreen()

### Community 12 - "CRM and Conversation Layer"
Cohesion: 0.1
Nodes (19): ConversationRepository, LeadRepository, ConversationCreate Schema, LeadCreate Schema, LeadResponse Schema, LeadUpdate Schema, QualificationDimension Schema, QualificationScoreResponse Schema (+11 more)

### Community 13 - "ORM Entity Classes"
Cohesion: 0.32
Nodes (20): AnalyticsEvent ORM Model, Appointment ORM Model, AuditLog ORM Model, SQLAlchemy DeclarativeBase, Conversation ORM Model, Document ORM Model, EOISubmission ORM Model, ETLJob ORM Model (+12 more)

### Community 14 - "Authentication and Security"
Cohesion: 0.17
Nodes (10): create_access_token(), create_refresh_token(), decode_token(), _load_key(), _private_key(), _public_key(), verify_password(), login() (+2 more)

### Community 15 - "Jira Automation Scripts"
Cohesion: 0.2
Nodes (16): build_subtask_map(), extract_role(), generate_subtask_description(), main(), make_doc(), para(), Build a map of {issue_key: description_adf} for all subtasks.     Keys are assig, Checkbox-style task list using ADF taskList. (+8 more)

### Community 16 - "Notification and Webhook Service"
Cohesion: 0.12
Nodes (16): parse_telegram_webhook(), parse_whatsapp_webhook(), Notification service: WhatsApp, Telegram, (email stub)., Extract messages from Meta WhatsApp webhook payload., Extract message from Telegram update payload., Email via SendGrid — stub until Phase 3 document/notification features., # TODO: Phase 3 — implement via SendGrid HTTP API, Send a WhatsApp text message via Meta Business API. (+8 more)

### Community 17 - "Frontend Admin Shell"
Cohesion: 0.15
Nodes (8): Header(), Sidebar(), clearTokens(), getAccessToken(), isAuthenticated(), setTokens(), cn(), handleSubmit()

### Community 18 - "Confluence API Helpers"
Cohesion: 0.3
Nodes (13): api_get(), api_post(), api_put(), code_macro(), create_page(), get_page_by_title(), inline_format(), main() (+5 more)

### Community 20 - "Sprint Management"
Cohesion: 0.26
Nodes (11): create_sprint(), get_all_issues(), get_existing_sprints(), main(), move_issues_to_sprint(), Fetch all issues (stories + subtasks) from REA project., Return dict of sprint name → sprint id for existing sprints on BOARD_ID., Move a batch of issues to a sprint (max 50 per call). (+3 more)

### Community 21 - "UI Design Handoff Assets"
Cohesion: 0.25
Nodes (11): app-canvas.jsx (v2 only), app.jsx (v1 only), data.jsx (shared), design-canvas.jsx (v2 only), mobile-app.jsx (v2 only), UI Design Handoff README (Claude Design Export), screens-1.jsx (shared), screens-2.jsx (shared) (+3 more)

### Community 23 - "Jira Issue Creator"
Cohesion: 0.39
Nodes (8): adf(), create_epic(), create_issue(), create_story(), create_subtask(), main(), Build Atlassian Document Format body from plain text lines.     Lines starting w, Create a Jira issue and return its key. Returns '' on failure.

### Community 24 - "Config and Database Setup"
Cohesion: 0.22
Nodes (9): Settings (Pydantic BaseSettings), get_settings (lru_cache factory), AsyncSessionLocal (async_sessionmaker), SQLAlchemy Async Engine, get_db (async session dependency), RS256 JWT Pattern, create_access_token, create_refresh_token (+1 more)

### Community 25 - "Frontend Admin Components"
Cohesion: 0.28
Nodes (9): Header (Admin Header Component), AdminLayout (Route Group Layout), Sidebar (Admin Sidebar Component), Axios API Client (frontend/src/lib/api.ts), Auth Token Helpers (frontend/src/lib/auth.ts), DashboardPage (Admin Dashboard), LoginPage (Auth Login), RootPage (Redirect to /admin/dashboard) (+1 more)

### Community 27 - "Confluence Docs Publisher"
Cohesion: 0.5
Nodes (7): get_page(), inline_format(), main(), md_to_storage(), table_to_storage(), upsert(), xml_escape()

### Community 29 - "Lead Qualification Scoring"
Cohesion: 0.43
Nodes (6): _get_last_user_text(), qualification_agent(), Qualification agent node: 8-dimension lead scoring., Score 8 qualification dimensions from extracted entities., _score_budget(), _score_timeline()

### Community 31 - "Module 31"
Cohesion: 0.53
Nodes (4): get_url(), run_async_migrations(), run_migrations_offline(), run_migrations_online()

### Community 32 - "Module 32"
Cohesion: 0.6
Nodes (4): create_issue(), get_issue_type_ids(), main(), Create a Jira issue and return its key.

### Community 33 - "Module 33"
Cohesion: 0.4
Nodes (5): AppointmentRepository, Appointment Availability Slot Logic, AppointmentCreate Schema, AppointmentUpdate Schema, AvailabilitySlot Schema

### Community 35 - "Module 35"
Cohesion: 0.5
Nodes (3): handoff_agent(), Handoff agent node: trigger human escalation., Prepare handoff message and mark conversation for human agent pickup.

### Community 36 - "Module 36"
Cohesion: 0.5
Nodes (3): rag_agent(), RAG agent node: semantic search over knowledge base., Retrieve relevant knowledge base chunks to augment response.

### Community 37 - "Module 37"
Cohesion: 0.67
Nodes (3): BaseSettings, get_settings(), Settings

### Community 38 - "Module 38"
Cohesion: 0.67
Nodes (4): Models Package Init, Tenant ORM Model, User ORM Model, UserProfile Schema

### Community 39 - "Module 39"
Cohesion: 0.5
Nodes (4): IOSDevice (iOS 26 Device Frame), IOSGlassPill (Liquid Glass Pill), IOSKeyboard (iOS 26 Liquid Glass Keyboard), IOSStatusBar (iOS Status Bar)

### Community 40 - "Module 40"
Cohesion: 0.5
Nodes (4): Jira KAN Project â€” GCC Wellness / Legacy, Add Jira Descriptions Script, Create Jira Subtasks Script, Create Jira Tickets Script (KAN project)

### Community 44 - "Module 44"
Cohesion: 0.67
Nodes (3): Email Stub (SendGrid Phase 3), Telegram Notification Function, WhatsApp Notification Functions

### Community 45 - "Module 45"
Cohesion: 0.67
Nodes (3): HealthResponse Schema, ReadinessResponse Schema, Health Endpoint Tests

## Ambiguous Edges - Review These
- `Agent Architecture â€” LangGraph Orchestrator` → `git-commit Skill â€” Conventional Commits Automation`  [AMBIGUOUS]
  skills/git-commit/SKILL.md · relation: conceptually_related_to
- `Agent Architecture â€” LangGraph Orchestrator` → `grill-me Skill â€” Relentless Design Interview`  [AMBIGUOUS]
  skills/grill-me/SKILL.md · relation: conceptually_related_to

## Knowledge Gaps
- **173 isolated node(s):** `Initial schema — all tables  Revision ID: 001 Revises: Create Date: 2026-05-03 0`, `Sprint 2 — Full LangGraph orchestrator.  Graph:   memory_loader → intent_classif`, `Load Redis session + Qdrant long-term memory.`, `LLM intent classification with rule-based fast path.`, `Increment clarification attempts counter.` (+168 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Agent Architecture â€” LangGraph Orchestrator` and `git-commit Skill â€” Conventional Commits Automation`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Agent Architecture â€” LangGraph Orchestrator` and `grill-me Skill â€” Relentless Design Interview`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `PropertyRepository` connect `Property Search and Listing` to `Database Model Layer`, `Vector Search and Embeddings`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `_reciprocal_rank_fusion()` connect `Vector Search and Embeddings` to `Property Search and Listing`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Why does `Base` connect `Database Model Layer` to `API Routes and Schemas`, `Booking and Appointment Flow`, `Property Search and Listing`, `Lead Management Domain`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 51 inferred relationships involving `Base` (e.g. with `AnalyticsChannel` and `AnalyticsEvent`) actually correct?**
  _`Base` has 51 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `TimestampMixin` (e.g. with `AppointmentType` and `AppointmentStatus`) actually correct?**
  _`TimestampMixin` has 31 INFERRED edges - model-reasoned connections that need verification._