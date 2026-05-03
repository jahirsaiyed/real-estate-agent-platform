"""Appointments API — CRUD + availability."""
from __future__ import annotations

import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_db
from app.models.appointment import AppointmentStatus
from app.models.user import User
from app.repositories.appointment import AppointmentRepository
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
    AvailabilityResponse,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("/availability", response_model=AvailabilityResponse)
async def get_availability(
    agent_id: uuid.UUID,
    for_date: date,
    duration_min: int = Query(default=60, ge=30, le=180),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AvailabilityResponse:
    repo = AppointmentRepository(db)
    slots = await repo.get_availability(
        agent_id=agent_id,
        tenant_id=current_user.tenant_id,
        for_date=for_date,
        duration_min=duration_min,
    )
    return AvailabilityResponse(date=str(for_date), slots=slots)


@router.get("", response_model=list[AppointmentResponse])
async def list_appointments(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    agent_id: uuid.UUID | None = None,
    lead_id: uuid.UUID | None = None,
    appt_status: AppointmentStatus | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[AppointmentResponse]:
    repo = AppointmentRepository(db)
    rows, _ = await repo.list(
        current_user.tenant_id,
        agent_id=agent_id,
        lead_id=lead_id,
        status=appt_status,
        page=page,
        limit=limit,
    )
    return [AppointmentResponse.model_validate(r) for r in rows]


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    data: AppointmentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AppointmentResponse:
    repo = AppointmentRepository(db)
    appt = await repo.create(current_user.tenant_id, data)
    await db.commit()
    await db.refresh(appt)
    return AppointmentResponse.model_validate(appt)


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AppointmentResponse:
    repo = AppointmentRepository(db)
    appt = await repo.get_by_id(appointment_id, current_user.tenant_id)
    if not appt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    return AppointmentResponse.model_validate(appt)


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: uuid.UUID,
    data: AppointmentUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AppointmentResponse:
    repo = AppointmentRepository(db)
    appt = await repo.get_by_id(appointment_id, current_user.tenant_id)
    if not appt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    appt = await repo.update(appt, data)
    await db.commit()
    await db.refresh(appt)
    return AppointmentResponse.model_validate(appt)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_appointment(
    appointment_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    repo = AppointmentRepository(db)
    appt = await repo.get_by_id(appointment_id, current_user.tenant_id)
    if not appt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    await repo.cancel(appt)
    await db.commit()
