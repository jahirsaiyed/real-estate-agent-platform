import enum
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, new_uuid


class AnalyticsChannel(str, enum.Enum):
    web = "web"
    whatsapp = "whatsapp"
    telegram = "telegram"


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    __table_args__ = (
        sa.Index("idx_analytics_events_tenant_time", "tenant_id", "created_at"),
        sa.Index("idx_analytics_events_type", "tenant_id", "event_type", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True
    )
    lead_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="SET NULL"), nullable=True
    )
    event_type: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    properties: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    channel: Mapped[AnalyticsChannel | None] = mapped_column(
        sa.Enum(AnalyticsChannel, name="analytics_channel"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )
