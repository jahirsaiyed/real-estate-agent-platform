"""Appointment repository with availability slot logic."""
from __future__ import annotations

import uuid
from datetime import date, datetime, time, timedelta, timezone

import sqlalchemy as sa
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment, AppointmentStatus
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AvailabilitySlot


# Business hours for availability (Dubai timezone offset handled by caller)
SLOT_DURATION_MINUTES = 60
BUSINESS_START = time(9, 0)   # 09:00
BUSINESS_END = time(18, 0)    # 18:00


class AppointmentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, tenant_id: uuid.UUID, data: AppointmentCreate) -> Appointment:
        appt = Appointment(
            tenant_id=tenant_id,
            **data.model_dump(exclude_none=True),
        )
        self.db.add(appt)
        await self.db.flush()
        await self.db.refresh(appt)
        return appt

    async def get_by_id(self, appt_id: uuid.UUID, tenant_id: uuid.UUID) -> Appointment | None:
        stmt = select(Appointment).where(
            Appointment.id == appt_id, Appointment.tenant_id == tenant_id
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def list(
        self,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID | None = None,
        lead_id: uuid.UUID | None = None,
        status: AppointmentStatus | None = None,
        from_dt: datetime | None = None,
        to_dt: datetime | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Appointment], int]:
        stmt = select(Appointment).where(Appointment.tenant_id == tenant_id)
        if agent_id:
            stmt = stmt.where(Appointment.agent_id == agent_id)
        if lead_id:
            stmt = stmt.where(Appointment.lead_id == lead_id)
        if status:
            stmt = stmt.where(Appointment.status == status)
        if from_dt:
            stmt = stmt.where(Appointment.start_time >= from_dt)
        if to_dt:
            stmt = stmt.where(Appointment.start_time <= to_dt)

        total = (await self.db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
        stmt = stmt.order_by(Appointment.start_time.asc()).offset((page - 1) * limit).limit(limit)
        rows = list((await self.db.execute(stmt)).scalars().all())
        return rows, total

    async def update(self, appt: Appointment, data: AppointmentUpdate) -> Appointment:
        updates = data.model_dump(exclude_none=True)
        for key, val in updates.items():
            setattr(appt, key, val)
        await self.db.flush()
        await self.db.refresh(appt)
        return appt

    async def cancel(self, appt: Appointment) -> Appointment:
        appt.status = AppointmentStatus.cancelled  # type: ignore[assignment]
        await self.db.flush()
        await self.db.refresh(appt)
        return appt

    async def get_availability(
        self,
        agent_id: uuid.UUID,
        tenant_id: uuid.UUID,
        for_date: date,
        duration_min: int = 60,
    ) -> list[AvailabilitySlot]:
        """Return free slots for an agent on a given date."""
        day_start = datetime.combine(for_date, BUSINESS_START).replace(tzinfo=timezone.utc)
        day_end = datetime.combine(for_date, BUSINESS_END).replace(tzinfo=timezone.utc)

        # Load existing appointments for this agent on this day
        stmt = select(Appointment).where(
            Appointment.tenant_id == tenant_id,
            Appointment.agent_id == agent_id,
            Appointment.status.notin_([AppointmentStatus.cancelled]),
            Appointment.start_time >= day_start,
            Appointment.end_time <= day_end,
        )
        booked = list((await self.db.execute(stmt)).scalars().all())
        booked_ranges = [(a.start_time, a.end_time) for a in booked]

        # Generate slots
        slots: list[AvailabilitySlot] = []
        cursor = day_start
        delta = timedelta(minutes=duration_min)

        while cursor + delta <= day_end:
            slot_end = cursor + delta
            conflict = any(
                not (slot_end <= bs or cursor >= be) for bs, be in booked_ranges
            )
            if not conflict:
                slots.append(AvailabilitySlot(start_time=cursor, end_time=slot_end, agent_id=agent_id))
            cursor += timedelta(minutes=SLOT_DURATION_MINUTES)

        return slots
