"""Property schemas for API request/response."""
from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from app.models.property import PropertyPurpose, PropertyStatus, PropertyType


class PropertySearchParams(BaseModel):
    q: str | None = None
    property_type: PropertyType | None = None
    purpose: PropertyPurpose | None = None
    price_min: Decimal | None = None
    price_max: Decimal | None = None
    bedrooms: int | None = None
    area: str | None = None
    radius_km: float | None = None
    lat: float | None = None
    lng: float | None = None
    is_freehold: bool | None = None
    is_off_plan: bool | None = None
    is_golden_visa_eligible: bool | None = None
    sort: str = "relevance"
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


class PropertySummary(BaseModel):
    id: uuid.UUID
    title: str
    title_ar: str | None
    property_type: str
    status: str
    purpose: str
    price_aed: Decimal | None
    bedrooms: int | None
    bathrooms: int | None
    area_sqft: Decimal | None
    address: str | None
    latitude: Decimal | None
    longitude: Decimal | None
    is_off_plan: bool
    is_freehold: bool
    is_golden_visa_eligible: bool
    images: list[Any] | None
    slug: str | None
    roi_estimated: Decimal | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PropertyResponse(PropertySummary):
    tenant_id: uuid.UUID
    description: str | None
    description_ar: str | None
    developer: str | None
    completion_date: date | None
    payment_plan: dict | None
    virtual_tour_url: str | None
    floor_plan_url: str | None
    rera_number: str | None
    embedding_id: str | None
    last_synced_at: datetime | None
    updated_at: datetime

    model_config = {"from_attributes": True}


class PropertyCreate(BaseModel):
    title: str = Field(..., max_length=500)
    title_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    property_type: PropertyType
    status: PropertyStatus = PropertyStatus.available
    purpose: PropertyPurpose
    price_aed: Decimal | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    area_sqft: Decimal | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    is_off_plan: bool = False
    is_freehold: bool = False
    is_golden_visa_eligible: bool = False
    developer: str | None = None
    completion_date: date | None = None
    payment_plan: dict | None = None
    virtual_tour_url: str | None = None
    images: list[Any] | None = None
    rera_number: str | None = None
    roi_estimated: Decimal | None = None
    location_id: uuid.UUID | None = None


class PropertyUpdate(BaseModel):
    title: str | None = None
    title_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    status: PropertyStatus | None = None
    price_aed: Decimal | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    area_sqft: Decimal | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    is_off_plan: bool | None = None
    is_freehold: bool | None = None
    is_golden_visa_eligible: bool | None = None
    developer: str | None = None
    completion_date: date | None = None
    payment_plan: dict | None = None
    virtual_tour_url: str | None = None
    images: list[Any] | None = None
    rera_number: str | None = None
    roi_estimated: Decimal | None = None


class PropertyListResponse(BaseModel):
    items: list[PropertySummary]
    total: int
    page: int
    limit: int
    pages: int
