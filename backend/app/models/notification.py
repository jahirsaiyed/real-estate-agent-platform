import enum
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, new_uuid


class NotificationStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    delivered = "delivered"
    read = "read"
    failed = "failed"


class NotificationDeliveryChannel(str, enum.Enum):
    whatsapp = "whatsapp"
    email = "email"
    sms = "sms"
    telegram = "telegram"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    lead_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="SET NULL"), nullable=True
    )
    template_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("notification_templates.id", ondelete="SET NULL"),
        nullable=True,
    )
    type: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    channel: Mapped[NotificationDeliveryChannel] = mapped_column(
        sa.Enum(NotificationDeliveryChannel, name="notification_delivery_channel"), nullable=False
    )
    status: Mapped[NotificationStatus] = mapped_column(
        sa.Enum(NotificationStatus, name="notification_status"),
        nullable=False,
        server_default=NotificationStatus.pending.value,
    )
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    external_message_id: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )
