"""Lead schemas."""
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field

from app.models.lead import (
    LeadContactPreference,
    LeadLanguage,
    LeadPropertyType,
    LeadPurpose,
    LeadQualificationStatus,
    LeadSourceChannel,
)


class LeadCreate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    nationality: str | None = None
    language: LeadLanguage = LeadLanguage.en
    source_channel: LeadSourceChannel = LeadSourceChannel.web
    utm_source: str | None = None
    utm_medium: str | None = None
    utm_campaign: str | None = None
    referral_code: str | None = None


class LeadUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    nationality: str | None = None
    language: LeadLanguage | None = None
    budget_min_aed: Decimal | None = None
    budget_max_aed: Decimal | None = None
    preferred_locations: list[str] | None = None
    property_type: LeadPropertyType | None = None
    purpose: LeadPurpose | None = None
    pre_approved: bool | None = None
    timeline_months: int | None = None
    contact_preference: LeadContactPreference | None = None
    crm_contact_id: str | None = None


class LeadSummary(BaseModel):
    id: uuid.UUID
    full_name: str | None
    phone: str | None
    email: str | None
    nationality: str | None
    language: str
    qualification_score: int
    qualification_status: str
    source_channel: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeadResponse(LeadSummary):
    tenant_id: uuid.UUID
    conversation_id: uuid.UUID | None
    assigned_agent_id: uuid.UUID | None
    budget_min_aed: Decimal | None
    budget_max_aed: Decimal | None
    preferred_locations: list
    property_type: str | None
    purpose: str | None
    pre_approved: bool | None
    timeline_months: int | None
    contact_preference: str | None
    crm_contact_id: str | None
    utm_source: str | None
    utm_medium: str | None
    utm_campaign: str | None

    model_config = {"from_attributes": True}


class QualificationDimension(BaseModel):
    score: int
    max: int = 10
    value: str | None = None


class QualificationScoreResponse(BaseModel):
    total_score: int
    status: str
    dimensions: dict[str, QualificationDimension]


class LeadListResponse(BaseModel):
    items: list[LeadSummary]
    total: int
    page: int
    limit: int
    pages: int


class LeadAssignRequest(BaseModel):
    agent_id: uuid.UUID = Field(..., description="Agent user ID to assign lead to")
