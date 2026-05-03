import enum
import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, new_uuid


class NotificationChannel(str, enum.Enum):
    whatsapp = "whatsapp"
    email = "email"
    sms = "sms"
    telegram = "telegram"


class TemplateLanguage(str, enum.Enum):
    en = "en"
    ar = "ar"
    hi = "hi"
    ru = "ru"


class TemplateStatus(str, enum.Enum):
    pending_approval = "pending_approval"
    approved = "approved"
    rejected = "rejected"


class NotificationTemplate(TimestampMixin, Base):
    __tablename__ = "notification_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    channel: Mapped[NotificationChannel] = mapped_column(
        sa.Enum(NotificationChannel, name="notification_channel"), nullable=False
    )
    language: Mapped[TemplateLanguage] = mapped_column(
        sa.Enum(TemplateLanguage, name="template_language"), nullable=False
    )
    content: Mapped[str] = mapped_column(sa.Text, nullable=False)
    whatsapp_template_id: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    status: Mapped[TemplateStatus] = mapped_column(
        sa.Enum(TemplateStatus, name="template_status"),
        nullable=False,
        server_default=TemplateStatus.pending_approval.value,
    )
