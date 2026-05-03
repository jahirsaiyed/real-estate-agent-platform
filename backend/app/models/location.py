import enum
import uuid
from datetime import datetime

import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, new_uuid


class LocationLevel(str, enum.Enum):
    community = "community"
    sub_community = "sub_community"
    building = "building"


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("locations.id", ondelete="SET NULL"), nullable=True
    )
    level: Mapped[LocationLevel] = mapped_column(
        sa.Enum(LocationLevel, name="location_level"), nullable=False
    )
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    name_ar: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    slug: Mapped[str] = mapped_column(sa.String(100), nullable=False, index=True)
    polygon: Mapped[bytes | None] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )
