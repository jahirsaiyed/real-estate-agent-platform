"""Leads API — CRUD + qualification score."""
from __future__ import annotations

import math
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_db, require_role
from app.models.lead import LeadQualificationStatus
from app.models.user import User, UserRole
from app.repositories.lead import LeadRepository
from app.schemas.lead import (
    LeadAssignRequest,
    LeadCreate,
    LeadListResponse,
    LeadResponse,
    LeadSummary,
    LeadUpdate,
    QualificationScoreResponse,
)
from app.services.crm import sync_lead_to_crm

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("", response_model=LeadListResponse)
async def list_leads(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    qualification_status: LeadQualificationStatus | None = Query(default=None),
    channel: str | None = None,
    agent_id: uuid.UUID | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> LeadListResponse:
    repo = LeadRepository(db)
    rows, total = await repo.list(
        current_user.tenant_id,
        status=qualification_status,
        channel=channel,
        agent_id=agent_id,
        page=page,
        limit=limit,
    )
    return LeadListResponse(
        items=[LeadSummary.model_validate(r) for r in rows],
        total=total,
        page=page,
        limit=limit,
        pages=math.ceil(total / limit) if total else 1,
    )


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    data: LeadCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> LeadResponse:
    repo = LeadRepository(db)
    lead = await repo.create(current_user.tenant_id, data)
    await db.commit()
    await db.refresh(lead)
    return LeadResponse.model_validate(lead)


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> LeadResponse:
    repo = LeadRepository(db)
    lead = await repo.get_by_id(lead_id, current_user.tenant_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return LeadResponse.model_validate(lead)


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: uuid.UUID,
    data: LeadUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> LeadResponse:
    repo = LeadRepository(db)
    lead = await repo.get_by_id(lead_id, current_user.tenant_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    lead = await repo.update(lead, data)
    await db.commit()
    await db.refresh(lead)
    return LeadResponse.model_validate(lead)


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.tenant_admin, UserRole.superadmin))],
) -> None:
    repo = LeadRepository(db)
    lead = await repo.get_by_id(lead_id, current_user.tenant_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    await db.delete(lead)
    await db.commit()


@router.get("/{lead_id}/score", response_model=QualificationScoreResponse)
async def get_lead_score(
    lead_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> QualificationScoreResponse:
    repo = LeadRepository(db)
    lead = await repo.get_by_id(lead_id, current_user.tenant_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return repo.build_qualification_response(lead, {})


@router.post("/{lead_id}/assign", response_model=LeadResponse)
async def assign_lead(
    lead_id: uuid.UUID,
    data: LeadAssignRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.tenant_admin, UserRole.superadmin))],
) -> LeadResponse:
    repo = LeadRepository(db)
    lead = await repo.get_by_id(lead_id, current_user.tenant_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    lead = await repo.assign_agent(lead, data.agent_id)
    await db.commit()
    await db.refresh(lead)
    return LeadResponse.model_validate(lead)


@router.post("/{lead_id}/crm-sync", status_code=status.HTTP_200_OK)
async def sync_lead_crm(
    lead_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Force CRM sync for a lead."""
    repo = LeadRepository(db)
    lead = await repo.get_by_id(lead_id, current_user.tenant_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    crm_id = await sync_lead_to_crm(
        {
            "full_name": lead.full_name,
            "email": lead.email,
            "phone": lead.phone,
            "source_channel": lead.source_channel.value if lead.source_channel else "web",
            "budget_max_aed": float(lead.budget_max_aed) if lead.budget_max_aed else None,
        }
    )
    if crm_id:
        lead.crm_contact_id = crm_id  # type: ignore[assignment]
        await db.commit()

    return {"synced": bool(crm_id), "crm_contact_id": crm_id}
