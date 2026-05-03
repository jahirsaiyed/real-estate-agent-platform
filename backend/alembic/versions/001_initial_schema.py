"""Initial schema — all tables

Revision ID: 001
Revises:
Create Date: 2026-05-03 00:00:00.000000

"""
from typing import Sequence, Union

import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable PostGIS extension
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # ── Enums ────────────────────────────────────────────────────────────────────
    op.execute("CREATE TYPE user_role AS ENUM ('superadmin', 'tenant_admin', 'agent', 'readonly')")
    op.execute("CREATE TYPE user_language AS ENUM ('en', 'ar', 'hi', 'ru')")
    op.execute(
        "CREATE TYPE lead_qualification_status AS ENUM "
        "('unqualified', 'in_progress', 'qualified', 'handoff')"
    )
    op.execute(
        "CREATE TYPE lead_property_type AS ENUM "
        "('apartment', 'villa', 'townhouse', 'penthouse', 'studio')"
    )
    op.execute("CREATE TYPE lead_purpose AS ENUM ('buy', 'rent', 'invest')")
    op.execute("CREATE TYPE lead_contact_preference AS ENUM ('whatsapp', 'call', 'email')")
    op.execute("CREATE TYPE lead_source_channel AS ENUM ('web', 'whatsapp', 'telegram')")
    op.execute("CREATE TYPE lead_language AS ENUM ('en', 'ar', 'hi', 'ru')")
    op.execute("CREATE TYPE conversation_channel AS ENUM ('web', 'whatsapp', 'telegram')")
    op.execute(
        "CREATE TYPE conversation_status AS ENUM ('active', 'resolved', 'handoff', 'abandoned')"
    )
    op.execute("CREATE TYPE conversation_language AS ENUM ('en', 'ar', 'hi', 'ru')")
    op.execute("CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system', 'tool')")
    op.execute(
        "CREATE TYPE property_source AS ENUM "
        "('csv', 'zoho', 'hubspot', 'bayut', 'property_finder', 'rera', 'emaar', 'damac')"
    )
    op.execute(
        "CREATE TYPE property_type AS ENUM "
        "('apartment', 'villa', 'townhouse', 'penthouse', 'studio', 'office', 'warehouse')"
    )
    op.execute(
        "CREATE TYPE property_status AS ENUM "
        "('available', 'sold', 'rented', 'reserved', 'off_plan')"
    )
    op.execute("CREATE TYPE property_purpose AS ENUM ('buy', 'rent', 'both')")
    op.execute(
        "CREATE TYPE location_level AS ENUM ('community', 'sub_community', 'building')"
    )
    op.execute(
        "CREATE TYPE appointment_type AS ENUM ('viewing', 'call', 'virtual_tour', 'meeting')"
    )
    op.execute(
        "CREATE TYPE appointment_status AS ENUM "
        "('pending', 'confirmed', 'cancelled', 'completed', 'no_show')"
    )
    op.execute(
        "CREATE TYPE document_type AS ENUM "
        "('passport', 'proof_of_funds', 'noc', 'soa', 'brochure', 'report', 'contract', 'other')"
    )
    op.execute(
        "CREATE TYPE notification_channel AS ENUM ('whatsapp', 'email', 'sms', 'telegram')"
    )
    op.execute("CREATE TYPE template_language AS ENUM ('en', 'ar', 'hi', 'ru')")
    op.execute(
        "CREATE TYPE template_status AS ENUM ('pending_approval', 'approved', 'rejected')"
    )
    op.execute(
        "CREATE TYPE notification_delivery_channel AS ENUM ('whatsapp', 'email', 'sms', 'telegram')"
    )
    op.execute(
        "CREATE TYPE notification_status AS ENUM ('pending', 'sent', 'delivered', 'read', 'failed')"
    )
    op.execute(
        "CREATE TYPE off_plan_status AS ENUM "
        "('upcoming', 'launched', 'under_construction', 'handed_over')"
    )
    op.execute("CREATE TYPE broker_source AS ENUM ('emaar', 'damac', 'csv')")
    op.execute(
        "CREATE TYPE eoi_status AS ENUM ('submitted', 'under_review', 'approved', 'rejected')"
    )
    op.execute(
        "CREATE TYPE etl_job_type AS ENUM "
        "('csv_import', 'crm_sync', 'bayut_sync', 'pf_sync', 'rera_sync', "
        "'broker_sync', 'kb_reindex', 'fx_rates')"
    )
    op.execute(
        "CREATE TYPE etl_job_status AS ENUM ('queued', 'running', 'completed', 'failed', 'partial')"
    )
    op.execute("CREATE TYPE analytics_channel AS ENUM ('web', 'whatsapp', 'telegram')")
    op.execute(
        "CREATE TYPE guardrail_rule_type AS ENUM "
        "('blocked_topic', 'required_disclaimer', 'competitor_mention', 'price_guarantee')"
    )

    # ── tenants ───────────────────────────────────────────────────────────────────
    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("plan", sa.String(50), nullable=False, server_default="starter"),
        sa.Column("settings", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_tenants_slug", "tenants", ["slug"])

    # ── users ─────────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("superadmin", "tenant_admin", "agent", "readonly", name="user_role", create_type=False), nullable=False, server_default="agent"),
        sa.Column("language", sa.Enum("en", "ar", "hi", "ru", name="user_language", create_type=False), nullable=False, server_default="en"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_users_tenant", "users", ["tenant_id"])
    op.create_index("idx_users_email", "users", ["email"])

    # ── conversations (created before leads due to circular FK) ──────────────────
    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("channel", sa.Enum("web", "whatsapp", "telegram", name="conversation_channel", create_type=False), nullable=False, server_default="web"),
        sa.Column("external_thread_id", sa.String(255), nullable=True),
        sa.Column("status", sa.Enum("active", "resolved", "handoff", "abandoned", name="conversation_status", create_type=False), nullable=False, server_default="active"),
        sa.Column("language", sa.Enum("en", "ar", "hi", "ru", name="conversation_language", create_type=False), nullable=False, server_default="en"),
        sa.Column("sentiment_score", sa.Float, nullable=True),
        sa.Column("frustration_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("handoff_reason", sa.String(255), nullable=True),
        sa.Column("handoff_agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("handoff_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_conversations_tenant", "conversations", ["tenant_id"])

    # ── leads ─────────────────────────────────────────────────────────────────────
    op.create_table(
        "leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("assigned_agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("nationality", sa.String(100), nullable=True),
        sa.Column("language", sa.Enum("en", "ar", "hi", "ru", name="lead_language", create_type=False), nullable=False, server_default="en"),
        sa.Column("qualification_score", sa.Integer, nullable=False, server_default="0"),
        sa.Column("qualification_status", sa.Enum("unqualified", "in_progress", "qualified", "handoff", name="lead_qualification_status", create_type=False), nullable=False, server_default="unqualified"),
        sa.Column("budget_min_aed", sa.Numeric(15, 2), nullable=True),
        sa.Column("budget_max_aed", sa.Numeric(15, 2), nullable=True),
        sa.Column("preferred_locations", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("property_type", sa.Enum("apartment", "villa", "townhouse", "penthouse", "studio", name="lead_property_type", create_type=False), nullable=True),
        sa.Column("purpose", sa.Enum("buy", "rent", "invest", name="lead_purpose", create_type=False), nullable=True),
        sa.Column("pre_approved", sa.Boolean, nullable=True),
        sa.Column("timeline_months", sa.Integer, nullable=True),
        sa.Column("contact_preference", sa.Enum("whatsapp", "call", "email", name="lead_contact_preference", create_type=False), nullable=True),
        sa.Column("crm_contact_id", sa.String(255), nullable=True),
        sa.Column("source_channel", sa.Enum("web", "whatsapp", "telegram", name="lead_source_channel", create_type=False), nullable=False, server_default="web"),
        sa.Column("utm_source", sa.String(100), nullable=True),
        sa.Column("utm_medium", sa.String(100), nullable=True),
        sa.Column("utm_campaign", sa.String(100), nullable=True),
        sa.Column("referral_code", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_leads_tenant", "leads", ["tenant_id"])
    op.create_index("idx_leads_phone", "leads", ["phone"])
    op.create_index("idx_leads_qualification", "leads", ["tenant_id", "qualification_status"])
    op.create_index("idx_leads_channel", "leads", ["tenant_id", "source_channel"])

    # Add FK from conversations.lead_id → leads (deferred)
    op.create_foreign_key(
        "fk_conversations_lead_id", "conversations", "leads", ["lead_id"], ["id"],
        ondelete="SET NULL"
    )

    # ── messages ──────────────────────────────────────────────────────────────────
    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.Enum("user", "assistant", "system", "tool", name="message_role", create_type=False), nullable=False),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("tool_name", sa.String(100), nullable=True),
        sa.Column("tool_input", postgresql.JSONB(), nullable=True),
        sa.Column("tool_output", postgresql.JSONB(), nullable=True),
        sa.Column("tokens_used", sa.Integer, nullable=True),
        sa.Column("latency_ms", sa.Integer, nullable=True),
        sa.Column("guardrail_triggered", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("guardrail_reason", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_messages_tenant", "messages", ["tenant_id"])
    op.create_index("idx_messages_conversation", "messages", ["conversation_id", "created_at"])

    # ── locations ─────────────────────────────────────────────────────────────────
    op.create_table(
        "locations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("locations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("level", sa.Enum("community", "sub_community", "building", name="location_level", create_type=False), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("name_ar", sa.String(255), nullable=True),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("polygon", geoalchemy2.types.Geometry(geometry_type="POLYGON", srid=4326), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_locations_tenant", "locations", ["tenant_id"])
    op.create_index("idx_locations_slug", "locations", ["slug"])

    # ── properties ────────────────────────────────────────────────────────────────
    op.create_table(
        "properties",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("locations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("source", sa.Enum("csv", "zoho", "hubspot", "bayut", "property_finder", "rera", "emaar", "damac", name="property_source", create_type=False), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("title_ar", sa.String(500), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("description_ar", sa.Text, nullable=True),
        sa.Column("property_type", sa.Enum("apartment", "villa", "townhouse", "penthouse", "studio", "office", "warehouse", name="property_type", create_type=False), nullable=False),
        sa.Column("status", sa.Enum("available", "sold", "rented", "reserved", "off_plan", name="property_status", create_type=False), nullable=False, server_default="available"),
        sa.Column("purpose", sa.Enum("buy", "rent", "both", name="property_purpose", create_type=False), nullable=False),
        sa.Column("price_aed", sa.Numeric(15, 2), nullable=True),
        sa.Column("bedrooms", sa.Integer, nullable=True),
        sa.Column("bathrooms", sa.Integer, nullable=True),
        sa.Column("area_sqft", sa.Numeric(10, 2), nullable=True),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("latitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("geom", geoalchemy2.types.Geometry(geometry_type="POINT", srid=4326), nullable=True),
        sa.Column("is_off_plan", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_freehold", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_golden_visa_eligible", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("developer", sa.String(255), nullable=True),
        sa.Column("completion_date", sa.Date, nullable=True),
        sa.Column("payment_plan", postgresql.JSONB(), nullable=True),
        sa.Column("virtual_tour_url", sa.String(500), nullable=True),
        sa.Column("images", postgresql.JSONB(), nullable=True),
        sa.Column("floor_plan_url", sa.String(500), nullable=True),
        sa.Column("brochure_r2_key", sa.String(500), nullable=True),
        sa.Column("rera_number", sa.String(100), nullable=True),
        sa.Column("roi_estimated", sa.Numeric(5, 2), nullable=True),
        sa.Column("embedding_id", sa.String(255), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_properties_tenant", "properties", ["tenant_id"])
    op.create_index("idx_properties_status", "properties", ["tenant_id", "status", "purpose"])
    op.create_index("idx_properties_price", "properties", ["tenant_id", "price_aed"])
    op.create_index("idx_properties_type", "properties", ["tenant_id", "property_type", "bedrooms"])
    op.create_index("idx_properties_geom", "properties", ["geom"], postgresql_using="gist")
    op.create_index("idx_properties_external", "properties", ["external_id"])
    op.execute(
        "CREATE INDEX idx_properties_freehold ON properties(tenant_id, is_freehold) "
        "WHERE is_freehold = true"
    )
    op.execute(
        "CREATE INDEX idx_properties_offplan ON properties(tenant_id, is_off_plan) "
        "WHERE is_off_plan = true"
    )

    # ── appointments ──────────────────────────────────────────────────────────────
    op.create_table(
        "appointments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="SET NULL"), nullable=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id", ondelete="SET NULL"), nullable=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("type", sa.Enum("viewing", "call", "virtual_tour", "meeting", name="appointment_type", create_type=False), nullable=False),
        sa.Column("status", sa.Enum("pending", "confirmed", "cancelled", "completed", "no_show", name="appointment_status", create_type=False), nullable=False, server_default="pending"),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("location", sa.String(500), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("google_event_id", sa.String(255), nullable=True),
        sa.Column("outlook_event_id", sa.String(255), nullable=True),
        sa.Column("reminder_24h_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reminder_1h_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_appointments_tenant", "appointments", ["tenant_id"])
    op.create_index("idx_appointments_agent_time", "appointments", ["agent_id", "start_time"])
    op.create_index("idx_appointments_lead", "appointments", ["lead_id", "status"])

    # ── documents ─────────────────────────────────────────────────────────────────
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="SET NULL"), nullable=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("type", sa.Enum("passport", "proof_of_funds", "noc", "soa", "brochure", "report", "contract", "other", name="document_type", create_type=False), nullable=False),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("r2_key", sa.String(500), nullable=False),
        sa.Column("r2_url", sa.String(1000), nullable=True),
        sa.Column("size_bytes", sa.Integer, nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("is_rag_indexed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("qdrant_point_id", sa.String(255), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_documents_tenant", "documents", ["tenant_id"])
    op.create_index("idx_documents_lead", "documents", ["lead_id"])

    # ── notification_templates ────────────────────────────────────────────────────
    op.create_table(
        "notification_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("channel", sa.Enum("whatsapp", "email", "sms", "telegram", name="notification_channel", create_type=False), nullable=False),
        sa.Column("language", sa.Enum("en", "ar", "hi", "ru", name="template_language", create_type=False), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("whatsapp_template_id", sa.String(255), nullable=True),
        sa.Column("status", sa.Enum("pending_approval", "approved", "rejected", name="template_status", create_type=False), nullable=False, server_default="pending_approval"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_notification_templates_tenant", "notification_templates", ["tenant_id"])

    # ── notifications ─────────────────────────────────────────────────────────────
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="SET NULL"), nullable=True),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("notification_templates.id", ondelete="SET NULL"), nullable=True),
        sa.Column("type", sa.String(100), nullable=False),
        sa.Column("channel", sa.Enum("whatsapp", "email", "sms", "telegram", name="notification_delivery_channel", create_type=False), nullable=False),
        sa.Column("status", sa.Enum("pending", "sent", "delivered", "read", "failed", name="notification_status", create_type=False), nullable=False, server_default="pending"),
        sa.Column("payload", postgresql.JSONB(), nullable=True),
        sa.Column("external_message_id", sa.String(255), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_notifications_tenant", "notifications", ["tenant_id"])

    # ── off_plan_projects ─────────────────────────────────────────────────────────
    op.create_table(
        "off_plan_projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("locations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("developer", sa.String(255), nullable=False),
        sa.Column("project_name", sa.String(500), nullable=False),
        sa.Column("project_name_ar", sa.String(500), nullable=True),
        sa.Column("status", sa.Enum("upcoming", "launched", "under_construction", "handed_over", name="off_plan_status", create_type=False), nullable=False, server_default="upcoming"),
        sa.Column("total_units", sa.Integer, nullable=True),
        sa.Column("available_units", sa.Integer, nullable=True),
        sa.Column("price_from_aed", sa.Numeric(15, 2), nullable=True),
        sa.Column("completion_date", sa.Date, nullable=True),
        sa.Column("payment_plan", postgresql.JSONB(), nullable=True),
        sa.Column("matterport_url", sa.String(500), nullable=True),
        sa.Column("launch_event_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("eoi_open", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("broker_api_id", sa.String(255), nullable=True),
        sa.Column("broker_source", sa.Enum("emaar", "damac", "csv", name="broker_source", create_type=False), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_off_plan_projects_tenant", "off_plan_projects", ["tenant_id"])

    # ── eoi_submissions ───────────────────────────────────────────────────────────
    op.create_table(
        "eoi_submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("off_plan_projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("expression_of_interest", sa.Text, nullable=True),
        sa.Column("unit_preferences", postgresql.JSONB(), nullable=True),
        sa.Column("status", sa.Enum("submitted", "under_review", "approved", "rejected", name="eoi_status", create_type=False), nullable=False, server_default="submitted"),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_eoi_submissions_tenant", "eoi_submissions", ["tenant_id"])

    # ── etl_jobs ──────────────────────────────────────────────────────────────────
    op.create_table(
        "etl_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_type", sa.Enum("csv_import", "crm_sync", "bayut_sync", "pf_sync", "rera_sync", "broker_sync", "kb_reindex", "fx_rates", name="etl_job_type", create_type=False), nullable=False),
        sa.Column("status", sa.Enum("queued", "running", "completed", "failed", "partial", name="etl_job_status", create_type=False), nullable=False, server_default="queued"),
        sa.Column("source", sa.String(255), nullable=True),
        sa.Column("records_processed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("records_failed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_etl_jobs_tenant", "etl_jobs", ["tenant_id"])

    # ── analytics_events ──────────────────────────────────────────────────────────
    op.create_table(
        "analytics_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("properties", postgresql.JSONB(), nullable=True),
        sa.Column("channel", sa.Enum("web", "whatsapp", "telegram", name="analytics_channel", create_type=False), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_analytics_events_tenant_time", "analytics_events", ["tenant_id", "created_at"])
    op.create_index("idx_analytics_events_type", "analytics_events", ["tenant_id", "event_type", "created_at"])

    # ── saved_searches ────────────────────────────────────────────────────────────
    op.create_table(
        "saved_searches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("filters", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("alert_enabled", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("last_alert_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_saved_searches_tenant", "saved_searches", ["tenant_id"])
    op.create_index("idx_saved_searches_lead", "saved_searches", ["lead_id"])

    # ── fx_rates ──────────────────────────────────────────────────────────────────
    op.create_table(
        "fx_rates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("base_currency", sa.String(10), nullable=False),
        sa.Column("target_currency", sa.String(10), nullable=False),
        sa.Column("rate", sa.Numeric(18, 8), nullable=False),
        sa.Column("rate_date", sa.Date, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("base_currency", "target_currency", "rate_date", name="uq_fx_rate_daily"),
    )
    op.create_index("idx_fx_rates_lookup", "fx_rates", ["base_currency", "target_currency", "rate_date"])

    # ── guardrail_rules ───────────────────────────────────────────────────────────
    op.create_table(
        "guardrail_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rule_name", sa.String(255), nullable=False),
        sa.Column("rule_type", sa.Enum("blocked_topic", "required_disclaimer", "competitor_mention", "price_guarantee", name="guardrail_rule_type", create_type=False), nullable=False),
        sa.Column("rule_pattern", sa.Text, nullable=False),
        sa.Column("disclaimer_text", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_guardrail_rules_tenant", "guardrail_rules", ["tenant_id"])

    # ── audit_logs ────────────────────────────────────────────────────────────────
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("before_state", postgresql.JSONB(), nullable=True),
        sa.Column("after_state", postgresql.JSONB(), nullable=True),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_audit_logs_tenant_time", "audit_logs", ["tenant_id", "created_at"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("guardrail_rules")
    op.drop_table("fx_rates")
    op.drop_table("saved_searches")
    op.drop_table("analytics_events")
    op.drop_table("etl_jobs")
    op.drop_table("eoi_submissions")
    op.drop_table("off_plan_projects")
    op.drop_table("notifications")
    op.drop_table("notification_templates")
    op.drop_table("documents")
    op.drop_table("appointments")
    op.drop_table("properties")
    op.drop_table("locations")
    op.drop_table("messages")
    op.drop_constraint("fk_conversations_lead_id", "conversations", type_="foreignkey")
    op.drop_table("leads")
    op.drop_table("conversations")
    op.drop_table("users")
    op.drop_table("tenants")

    # Drop enums
    for enum_name in [
        "guardrail_rule_type", "analytics_channel", "etl_job_status", "etl_job_type",
        "eoi_status", "broker_source", "off_plan_status", "notification_status",
        "notification_delivery_channel", "template_status", "template_language",
        "notification_channel", "document_type", "appointment_status", "appointment_type",
        "location_level", "property_purpose", "property_status", "property_type",
        "property_source", "message_role", "conversation_language", "conversation_status",
        "conversation_channel", "lead_language", "lead_source_channel", "lead_contact_preference",
        "lead_purpose", "lead_property_type", "lead_qualification_status",
        "user_language", "user_role",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")

    op.execute("DROP EXTENSION IF EXISTS postgis")
