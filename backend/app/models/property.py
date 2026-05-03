import enum
import uuid
from datetime import date, datetime

import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, new_uuid


class PropertySource(str, enum.Enum):
    csv = "csv"
    zoho = "zoho"
    hubspot = "hubspot"
    bayut = "bayut"
    property_finder = "property_finder"
    rera = "rera"
    emaar = "emaar"
    damac = "damac"


class PropertyType(str, enum.Enum):
    apartment = "apartment"
    villa = "villa"
    townhouse = "townhouse"
    penthouse = "penthouse"
    studio = "studio"
    office = "office"
    warehouse = "warehouse"


class PropertyStatus(str, enum.Enum):
    available = "available"
    sold = "sold"
    rented = "rented"
    reserved = "reserved"
    off_plan = "off_plan"


class PropertyPurpose(str, enum.Enum):
    buy = "buy"
    rent = "rent"
    both = "both"


class Property(TimestampMixin, Base):
    __tablename__ = "properties"
    __table_args__ = (
        sa.Index("idx_properties_tenant", "tenant_id"),
        sa.Index("idx_properties_status", "tenant_id", "status", "purpose"),
        sa.Index("idx_properties_price", "tenant_id", "price_aed"),
        sa.Index("idx_properties_type", "tenant_id", "property_type", "bedrooms"),
        sa.Index("idx_properties_geom", "geom", postgresql_using="gist"),
        sa.Index(
            "idx_properties_freehold",
            "tenant_id",
            "is_freehold",
            postgresql_where=sa.text("is_freehold = true"),
        ),
        sa.Index(
            "idx_properties_offplan",
            "tenant_id",
            "is_off_plan",
            postgresql_where=sa.text("is_off_plan = true"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("locations.id", ondelete="SET NULL"), nullable=True
    )
    external_id: Mapped[str | None] = mapped_column(sa.String(255), nullable=True, index=True)
    source: Mapped[PropertySource | None] = mapped_column(
        sa.Enum(PropertySource, name="property_source"), nullable=True
    )
    title: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    title_ar: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    description_ar: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    property_type: Mapped[PropertyType] = mapped_column(
        sa.Enum(PropertyType, name="property_type"), nullable=False
    )
    status: Mapped[PropertyStatus] = mapped_column(
        sa.Enum(PropertyStatus, name="property_status"),
        nullable=False,
        server_default=PropertyStatus.available.value,
    )
    purpose: Mapped[PropertyPurpose] = mapped_column(
        sa.Enum(PropertyPurpose, name="property_purpose"), nullable=False
    )
    price_aed: Mapped[sa.Numeric | None] = mapped_column(sa.Numeric(15, 2), nullable=True)
    bedrooms: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    bathrooms: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    area_sqft: Mapped[sa.Numeric | None] = mapped_column(sa.Numeric(10, 2), nullable=True)
    address: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    latitude: Mapped[sa.Numeric | None] = mapped_column(sa.Numeric(10, 7), nullable=True)
    longitude: Mapped[sa.Numeric | None] = mapped_column(sa.Numeric(10, 7), nullable=True)
    geom: Mapped[bytes | None] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )
    is_off_plan: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default="false")
    is_freehold: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default="false")
    is_golden_visa_eligible: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default="false"
    )
    developer: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    completion_date: Mapped[date | None] = mapped_column(sa.Date, nullable=True)
    payment_plan: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    virtual_tour_url: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    images: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    floor_plan_url: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    brochure_r2_key: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    rera_number: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    roi_estimated: Mapped[sa.Numeric | None] = mapped_column(sa.Numeric(5, 2), nullable=True)
    embedding_id: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
