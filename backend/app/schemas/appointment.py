"""Appointment schemas."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.appointment import AppointmentStatus, AppointmentType


class AppointmentCreate(BaseModel):
    lead_id: uuid.UUID | None = None
    property_id: uuid.UUID | None = None
    agent_id: uuid.UUID | None = None
    title: str = Field(..., max_length=500)
    type: AppointmentType = AppointmentType.viewing
    start_time: datetime
    end_time: datetime
    location: str | None = None
    notes: str | None = None


class AppointmentUpdate(BaseModel):
    status: AppointmentStatus | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    location: str | None = None
    notes: str | None = None
    agent_id: uuid.UUID | None = None


class AppointmentResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    lead_id: uuid.UUID | None
    property_id: uuid.UUID | None
    agent_id: uuid.UUID | None
    title: str
    type: str
    status: str
    start_time: datetime
    end_time: datetime
    location: str | None
    notes: str | None
    google_event_id: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AvailabilitySlot(BaseModel):
    start_time: datetime
    end_time: datetime
    agent_id: uuid.UUID


class AvailabilityResponse(BaseModel):
    date: str
    slots: list[AvailabilitySlot]
