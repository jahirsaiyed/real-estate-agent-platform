import enum
import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, new_uuid


class LeadQualificationStatus(str, enum.Enum):
    unqualified = "unqualified"
    in_progress = "in_progress"
    qualified = "qualified"
    handoff = "handoff"


class LeadPropertyType(str, enum.Enum):
    apartment = "apartment"
    villa = "villa"
    townhouse = "townhouse"
    penthouse = "penthouse"
    studio = "studio"


class LeadPurpose(str, enum.Enum):
    buy = "buy"
    rent = "rent"
    invest = "invest"


class LeadContactPreference(str, enum.Enum):
    whatsapp = "whatsapp"
    call = "call"
    email = "email"


class LeadSourceChannel(str, enum.Enum):
    web = "web"
    whatsapp = "whatsapp"
    telegram = "telegram"


class LeadLanguage(str, enum.Enum):
    en = "en"
    ar = "ar"
    hi = "hi"
    ru = "ru"


class Lead(TimestampMixin, Base):
    __tablename__ = "leads"
    __table_args__ = (
        sa.Index("idx_leads_tenant", "tenant_id"),
        sa.Index("idx_leads_phone", "phone"),
        sa.Index("idx_leads_qualification", "tenant_id", "qualification_status"),
        sa.Index("idx_leads_channel", "tenant_id", "source_channel"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True
    )
    assigned_agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    full_name: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    nationality: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    language: Mapped[LeadLanguage] = mapped_column(
        sa.Enum(LeadLanguage, name="lead_language"),
        nullable=False,
        server_default=LeadLanguage.en.value,
    )
    qualification_score: Mapped[int] = mapped_column(sa.Integer, nullable=False, server_default="0")
    qualification_status: Mapped[LeadQualificationStatus] = mapped_column(
        sa.Enum(LeadQualificationStatus, name="lead_qualification_status"),
        nullable=False,
        server_default=LeadQualificationStatus.unqualified.value,
    )
    budget_min_aed: Mapped[sa.Numeric | None] = mapped_column(sa.Numeric(15, 2), nullable=True)
    budget_max_aed: Mapped[sa.Numeric | None] = mapped_column(sa.Numeric(15, 2), nullable=True)
    preferred_locations: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    property_type: Mapped[LeadPropertyType | None] = mapped_column(
        sa.Enum(LeadPropertyType, name="lead_property_type"), nullable=True
    )
    purpose: Mapped[LeadPurpose | None] = mapped_column(
        sa.Enum(LeadPurpose, name="lead_purpose"), nullable=True
    )
    pre_approved: Mapped[bool | None] = mapped_column(sa.Boolean, nullable=True)
    timeline_months: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    contact_preference: Mapped[LeadContactPreference | None] = mapped_column(
        sa.Enum(LeadContactPreference, name="lead_contact_preference"), nullable=True
    )
    crm_contact_id: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    source_channel: Mapped[LeadSourceChannel] = mapped_column(
        sa.Enum(LeadSourceChannel, name="lead_source_channel"),
        nullable=False,
        server_default=LeadSourceChannel.web.value,
    )
    utm_source: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    utm_medium: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    utm_campaign: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    referral_code: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
