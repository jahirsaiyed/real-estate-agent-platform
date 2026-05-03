"""Booking agent node: check availability + create appointments."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.state import AgentState
from app.repositories.appointment import AppointmentRepository
from app.schemas.appointment import AppointmentCreate

logger = logging.getLogger(__name__)


async def booking_agent(
    state: AgentState,
    db: AsyncSession,
) -> AgentState:
    """Handle booking intent: check slots or create appointment."""
    entities = state.get("extracted_entities", {})
    tenant_id_str = state.get("tenant_id", "")

    try:
        tenant_id = uuid.UUID(tenant_id_str)
    except (ValueError, AttributeError):
        return state

    repo = AppointmentRepository(db)

    # If specific time is requested, try to create the appointment
    requested_dt: str | None = entities.get("requested_datetime")
    agent_id_str: str | None = entities.get("agent_id")

    if requested_dt and agent_id_str:
        try:
            start = datetime.fromisoformat(requested_dt).replace(tzinfo=timezone.utc)
            end = start.replace(hour=start.hour + 1)
            lead_id = state.get("lead_id")
            property_id = entities.get("property_id")

            appt = await repo.create(
                tenant_id=tenant_id,
                data=AppointmentCreate(
                    lead_id=uuid.UUID(lead_id) if lead_id else None,
                    property_id=uuid.UUID(property_id) if property_id else None,
                    agent_id=uuid.UUID(agent_id_str),
                    title=f"Property Viewing – {entities.get('area', 'Dubai')}",
                    start_time=start,
                    end_time=end,
                ),
            )
            state["calendar_slots"] = [
                {
                    "appointment_id": str(appt.id),
                    "start_time": appt.start_time.isoformat(),
                    "end_time": appt.end_time.isoformat(),
                    "status": appt.status.value,
                    "confirmed": True,
                }
            ]
        except Exception as exc:
            logger.error("booking_agent create appointment failed: %s", exc)
            state["calendar_slots"] = []
    else:
        # Return available slots for agent (or any agent if none specified)
        from datetime import date

        requested_date_str: str | None = entities.get("requested_date")
        try:
            requested_date = (
                date.fromisoformat(requested_date_str)
                if requested_date_str
                else date.today()
            )
        except ValueError:
            requested_date = date.today()

        # Use agent_id from entities or state
        agent_id = agent_id_str or state.get("agent_id")
        if agent_id:
            try:
                slots = await repo.get_availability(
                    agent_id=uuid.UUID(agent_id),
                    tenant_id=tenant_id,
                    for_date=requested_date,
                )
                state["calendar_slots"] = [
                    {
                        "start_time": s.start_time.isoformat(),
                        "end_time": s.end_time.isoformat(),
                        "agent_id": str(s.agent_id),
                    }
                    for s in slots[:5]  # Show max 5 slots
                ]
            except Exception as exc:
                logger.error("booking_agent get_availability failed: %s", exc)
                state["calendar_slots"] = []
        else:
            state["calendar_slots"] = []

    return state
