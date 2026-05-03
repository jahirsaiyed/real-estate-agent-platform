import enum
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, new_uuid


class AppointmentType(str, enum.Enum):
    viewing = "viewing"
    call = "call"
    virtual_tour = "virtual_tour"
    meeting = "meeting"


class AppointmentStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"
    no_show = "no_show"


class Appointment(TimestampMixin, Base):
    __tablename__ = "appointments"
    __table_args__ = (
        sa.Index("idx_appointments_agent_time", "agent_id", "start_time"),
        sa.Index("idx_appointments_lead", "lead_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    lead_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="SET NULL"), nullable=True
    )
    property_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("properties.id", ondelete="SET NULL"), nullable=True
    )
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    type: Mapped[AppointmentType] = mapped_column(
        sa.Enum(AppointmentType, name="appointment_type"), nullable=False
    )
    status: Mapped[AppointmentStatus] = mapped_column(
        sa.Enum(AppointmentStatus, name="appointment_status"),
        nullable=False,
        server_default=AppointmentStatus.pending.value,
    )
    start_time: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    location: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    google_event_id: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    outlook_event_id: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    reminder_24h_sent_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    reminder_1h_sent_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
