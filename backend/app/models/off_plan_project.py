import enum
import uuid
from datetime import date, datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, new_uuid


class OffPlanStatus(str, enum.Enum):
    upcoming = "upcoming"
    launched = "launched"
    under_construction = "under_construction"
    handed_over = "handed_over"


class BrokerSource(str, enum.Enum):
    emaar = "emaar"
    damac = "damac"
    csv = "csv"


class OffPlanProject(TimestampMixin, Base):
    __tablename__ = "off_plan_projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("locations.id", ondelete="SET NULL"), nullable=True
    )
    developer: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    project_name: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    project_name_ar: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    status: Mapped[OffPlanStatus] = mapped_column(
        sa.Enum(OffPlanStatus, name="off_plan_status"),
        nullable=False,
        server_default=OffPlanStatus.upcoming.value,
    )
    total_units: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    available_units: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    price_from_aed: Mapped[sa.Numeric | None] = mapped_column(sa.Numeric(15, 2), nullable=True)
    completion_date: Mapped[date | None] = mapped_column(sa.Date, nullable=True)
    payment_plan: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    matterport_url: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    launch_event_date: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    eoi_open: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default="false")
    broker_api_id: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    broker_source: Mapped[BrokerSource | None] = mapped_column(
        sa.Enum(BrokerSource, name="broker_source"), nullable=True
    )
