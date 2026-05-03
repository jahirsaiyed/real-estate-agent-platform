import enum
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, new_uuid


class ConversationChannel(str, enum.Enum):
    web = "web"
    whatsapp = "whatsapp"
    telegram = "telegram"


class ConversationStatus(str, enum.Enum):
    active = "active"
    resolved = "resolved"
    handoff = "handoff"
    abandoned = "abandoned"


class ConversationLanguage(str, enum.Enum):
    en = "en"
    ar = "ar"
    hi = "hi"
    ru = "ru"


class Conversation(TimestampMixin, Base):
    __tablename__ = "conversations"
    __table_args__ = (
        sa.Index("idx_conversations_tenant", "tenant_id"),
        sa.Index("idx_conversations_lead", "lead_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    lead_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="SET NULL"), nullable=True
    )
    channel: Mapped[ConversationChannel] = mapped_column(
        sa.Enum(ConversationChannel, name="conversation_channel"),
        nullable=False,
        server_default=ConversationChannel.web.value,
    )
    external_thread_id: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    status: Mapped[ConversationStatus] = mapped_column(
        sa.Enum(ConversationStatus, name="conversation_status"),
        nullable=False,
        server_default=ConversationStatus.active.value,
    )
    language: Mapped[ConversationLanguage] = mapped_column(
        sa.Enum(ConversationLanguage, name="conversation_language"),
        nullable=False,
        server_default=ConversationLanguage.en.value,
    )
    sentiment_score: Mapped[float | None] = mapped_column(sa.Float, nullable=True)
    frustration_count: Mapped[int] = mapped_column(sa.Integer, nullable=False, server_default="0")
    handoff_reason: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    handoff_agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    handoff_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
