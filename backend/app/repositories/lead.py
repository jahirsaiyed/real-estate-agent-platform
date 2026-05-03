"""Lead repository."""
from __future__ import annotations

import uuid
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead, LeadQualificationStatus
from app.schemas.lead import LeadCreate, LeadUpdate, QualificationDimension, QualificationScoreResponse


class LeadRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, tenant_id: uuid.UUID, data: LeadCreate) -> Lead:
        lead = Lead(tenant_id=tenant_id, **data.model_dump(exclude_none=True))
        self.db.add(lead)
        await self.db.flush()
        await self.db.refresh(lead)
        return lead

    async def get_by_id(self, lead_id: uuid.UUID, tenant_id: uuid.UUID) -> Lead | None:
        stmt = select(Lead).where(Lead.id == lead_id, Lead.tenant_id == tenant_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_by_phone(self, phone: str, tenant_id: uuid.UUID) -> Lead | None:
        stmt = select(Lead).where(Lead.phone == phone, Lead.tenant_id == tenant_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_by_external_thread(
        self, external_thread_id: str, tenant_id: uuid.UUID
    ) -> Lead | None:
        """Find lead linked to a WhatsApp/Telegram thread via conversation join."""
        from app.models.conversation import Conversation
        stmt = (
            select(Lead)
            .join(Conversation, Conversation.lead_id == Lead.id)
            .where(
                Conversation.external_thread_id == external_thread_id,
                Lead.tenant_id == tenant_id,
            )
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def list(
        self,
        tenant_id: uuid.UUID,
        status: LeadQualificationStatus | None = None,
        channel: str | None = None,
        agent_id: uuid.UUID | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Lead], int]:
        stmt = select(Lead).where(Lead.tenant_id == tenant_id)
        if status:
            stmt = stmt.where(Lead.qualification_status == status)
        if channel:
            stmt = stmt.where(Lead.source_channel == channel)
        if agent_id:
            stmt = stmt.where(Lead.assigned_agent_id == agent_id)

        total = (await self.db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
        stmt = stmt.order_by(Lead.created_at.desc()).offset((page - 1) * limit).limit(limit)
        rows = list((await self.db.execute(stmt)).scalars().all())
        return rows, total

    async def update(self, lead: Lead, data: LeadUpdate) -> Lead:
        updates = data.model_dump(exclude_none=True)
        for key, val in updates.items():
            setattr(lead, key, val)
        await self.db.flush()
        await self.db.refresh(lead)
        return lead

    async def assign_agent(self, lead: Lead, agent_id: uuid.UUID) -> Lead:
        lead.assigned_agent_id = agent_id  # type: ignore[assignment]
        await self.db.flush()
        await self.db.refresh(lead)
        return lead

    async def update_qualification(
        self,
        lead: Lead,
        score: int,
        status: LeadQualificationStatus,
        entities: dict,
    ) -> Lead:
        lead.qualification_score = score  # type: ignore[assignment]
        lead.qualification_status = status  # type: ignore[assignment]

        # Persist extracted entities to lead fields
        if "budget_min_aed" in entities and entities["budget_min_aed"]:
            lead.budget_min_aed = Decimal(str(entities["budget_min_aed"]))  # type: ignore[assignment]
        if "budget_max_aed" in entities and entities["budget_max_aed"]:
            lead.budget_max_aed = Decimal(str(entities["budget_max_aed"]))  # type: ignore[assignment]
        if "preferred_locations" in entities:
            lead.preferred_locations = entities["preferred_locations"]  # type: ignore[assignment]
        if "property_type" in entities and entities["property_type"]:
            try:
                from app.models.lead import LeadPropertyType
                lead.property_type = LeadPropertyType(entities["property_type"])  # type: ignore[assignment]
            except ValueError:
                pass
        if "purpose" in entities and entities["purpose"]:
            try:
                from app.models.lead import LeadPurpose
                lead.purpose = LeadPurpose(entities["purpose"])  # type: ignore[assignment]
            except ValueError:
                pass
        if "pre_approved" in entities:
            lead.pre_approved = entities["pre_approved"]  # type: ignore[assignment]
        if "timeline_months" in entities and entities["timeline_months"]:
            lead.timeline_months = int(entities["timeline_months"])  # type: ignore[assignment]
        if "contact_preference" in entities and entities["contact_preference"]:
            try:
                from app.models.lead import LeadContactPreference
                lead.contact_preference = LeadContactPreference(entities["contact_preference"])  # type: ignore[assignment]
            except ValueError:
                pass

        await self.db.flush()
        await self.db.refresh(lead)
        return lead

    def build_qualification_response(self, lead: Lead, entities: dict) -> QualificationScoreResponse:
        """Build the qualification scorecard response from a lead + entities."""
        dims: dict[str, QualificationDimension] = {
            "budget": QualificationDimension(
                score=min(10, 10 if (lead.budget_min_aed or lead.budget_max_aed) else 0),
                value=f"AED {lead.budget_min_aed}–{lead.budget_max_aed}" if lead.budget_max_aed else None,
            ),
            "property_type": QualificationDimension(
                score=10 if lead.property_type else 0,
                value=lead.property_type.value if lead.property_type else None,
            ),
            "purpose": QualificationDimension(
                score=10 if lead.purpose else 0,
                value=lead.purpose.value if lead.purpose else None,
            ),
            "timeline": QualificationDimension(
                score=_score_timeline(lead.timeline_months),
                value=f"{lead.timeline_months} months" if lead.timeline_months else None,
            ),
            "nationality": QualificationDimension(
                score=10 if lead.nationality else 0,
                value=lead.nationality,
            ),
            "pre_approval": QualificationDimension(
                score=10 if lead.pre_approved is not None else 0,
                value=str(lead.pre_approved) if lead.pre_approved is not None else None,
            ),
            "locations": QualificationDimension(
                score=min(10, len(lead.preferred_locations) * 5) if lead.preferred_locations else 0,
                value=", ".join(lead.preferred_locations) if lead.preferred_locations else None,
            ),
            "contact_preference": QualificationDimension(
                score=10 if lead.contact_preference else 0,
                value=lead.contact_preference.value if lead.contact_preference else None,
            ),
        }
        return QualificationScoreResponse(
            total_score=lead.qualification_score,
            status=lead.qualification_status.value,
            dimensions=dims,
        )


def _score_timeline(months: int | None) -> int:
    if months is None:
        return 0
    if months <= 1:
        return 10
    if months <= 3:
        return 8
    if months <= 6:
        return 6
    if months <= 12:
        return 4
    return 2
