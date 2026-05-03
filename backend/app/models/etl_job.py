import enum
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, new_uuid


class ETLJobType(str, enum.Enum):
    csv_import = "csv_import"
    crm_sync = "crm_sync"
    bayut_sync = "bayut_sync"
    pf_sync = "pf_sync"
    rera_sync = "rera_sync"
    broker_sync = "broker_sync"
    kb_reindex = "kb_reindex"
    fx_rates = "fx_rates"


class ETLJobStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"
    partial = "partial"


class ETLJob(Base):
    __tablename__ = "etl_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_type: Mapped[ETLJobType] = mapped_column(
        sa.Enum(ETLJobType, name="etl_job_type"), nullable=False
    )
    status: Mapped[ETLJobStatus] = mapped_column(
        sa.Enum(ETLJobStatus, name="etl_job_status"),
        nullable=False,
        server_default=ETLJobStatus.queued.value,
    )
    source: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    records_processed: Mapped[int] = mapped_column(sa.Integer, nullable=False, server_default="0")
    records_failed: Mapped[int] = mapped_column(sa.Integer, nullable=False, server_default="0")
    error_message: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )
