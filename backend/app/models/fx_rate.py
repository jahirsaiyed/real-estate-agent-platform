import uuid
from datetime import date, datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, new_uuid


class FXRate(Base):
    __tablename__ = "fx_rates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    base_currency: Mapped[str] = mapped_column(sa.String(10), nullable=False)
    target_currency: Mapped[str] = mapped_column(sa.String(10), nullable=False)
    rate: Mapped[sa.Numeric] = mapped_column(sa.Numeric(18, 8), nullable=False)
    rate_date: Mapped[date] = mapped_column(sa.Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )

    __table_args__ = (
        sa.UniqueConstraint("base_currency", "target_currency", "rate_date", name="uq_fx_rate_daily"),
        sa.Index("idx_fx_rates_lookup", "base_currency", "target_currency", "rate_date"),
    )
