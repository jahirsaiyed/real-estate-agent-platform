"""Properties API — CRUD + hybrid search."""
from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_db, require_role
from app.models.property import PropertyPurpose, PropertyStatus, PropertyType
from app.models.user import User, UserRole
from app.repositories.property import PropertyRepository
from app.schemas.property import (
    PropertyCreate,
    PropertyListResponse,
    PropertyResponse,
    PropertySearchParams,
    PropertySummary,
    PropertyUpdate,
)
from app.services import embedding as emb_svc

router = APIRouter(prefix="/properties", tags=["properties"])


@router.get("/search", response_model=PropertyListResponse)
async def search_properties(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    q: str | None = Query(default=None),
    property_type: PropertyType | None = None,
    purpose: PropertyPurpose | None = None,
    price_min: float | None = None,
    price_max: float | None = None,
    bedrooms: int | None = None,
    area: str | None = None,
    radius_km: float | None = None,
    lat: float | None = None,
    lng: float | None = None,
    is_freehold: bool | None = None,
    is_off_plan: bool | None = None,
    is_golden_visa_eligible: bool | None = None,
    sort: str = "relevance",
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> PropertyListResponse:
    params = PropertySearchParams(
        q=q,
        property_type=property_type,
        purpose=purpose,
        price_min=price_min,
        price_max=price_max,
        bedrooms=bedrooms,
        area=area,
        radius_km=radius_km,
        lat=lat,
        lng=lng,
        is_freehold=is_freehold,
        is_off_plan=is_off_plan,
        is_golden_visa_eligible=is_golden_visa_eligible,
        sort=sort,
        page=page,
        limit=limit,
    )

    # Run semantic search for relevance
    qdrant_hits = None
    if sort == "relevance" and q:
        qdrant_hits = await emb_svc.search_properties(
            query_text=q, tenant_id=str(current_user.tenant_id), limit=50
        )

    repo = PropertyRepository(db)
    results, total = await repo.search(current_user.tenant_id, params, qdrant_hits=qdrant_hits)

    import math
    pages = math.ceil(total / limit) if total else 1

    return PropertyListResponse(
        items=[PropertySummary.model_validate(r) for r in results],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PropertyResponse:
    repo = PropertyRepository(db)
    prop = await repo.get_by_id(property_id, current_user.tenant_id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    return PropertyResponse.model_validate(prop)


@router.get("/slug/{slug}", response_model=PropertyResponse)
async def get_property_by_slug(
    slug: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PropertyResponse:
    repo = PropertyRepository(db)
    prop = await repo.get_by_slug(slug, current_user.tenant_id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    return PropertyResponse.model_validate(prop)


@router.post("", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
async def create_property(
    data: PropertyCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.tenant_admin, UserRole.agent, UserRole.superadmin))],
) -> PropertyResponse:
    repo = PropertyRepository(db)
    async with db.begin_nested():
        prop = await repo.create(current_user.tenant_id, data)
    await db.commit()
    await db.refresh(prop)
    return PropertyResponse.model_validate(prop)


@router.patch("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: uuid.UUID,
    data: PropertyUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.tenant_admin, UserRole.agent, UserRole.superadmin))],
) -> PropertyResponse:
    repo = PropertyRepository(db)
    prop = await repo.get_by_id(property_id, current_user.tenant_id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    async with db.begin_nested():
        prop = await repo.update(prop, data)
    await db.commit()
    await db.refresh(prop)
    return PropertyResponse.model_validate(prop)


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_property(
    property_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.tenant_admin, UserRole.superadmin))],
) -> None:
    repo = PropertyRepository(db)
    prop = await repo.get_by_id(property_id, current_user.tenant_id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    await repo.archive(prop)
    await db.commit()


@router.get("/{property_id}/similar", response_model=list[PropertySummary])
async def get_similar_properties(
    property_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(default=6, ge=1, le=20),
) -> list[PropertySummary]:
    repo = PropertyRepository(db)
    results = await repo.get_similar(property_id, current_user.tenant_id, limit=limit)
    return [PropertySummary.model_validate(r) for r in results]
