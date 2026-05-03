"""Property repository: PostGIS + Qdrant hybrid search."""
from __future__ import annotations

import math
import re
import uuid
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.property import Property, PropertyPurpose, PropertyStatus, PropertyType
from app.schemas.property import PropertyCreate, PropertySearchParams, PropertyUpdate
from app.services import embedding as emb_svc


def _build_slug(title: str, property_id: str) -> str:
    """Generate a URL-safe slug from title + short id."""
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return f"{slug}-{property_id[:8]}"


def _property_to_text(prop: Property) -> str:
    """Build searchable text representation of a property for embedding."""
    parts = [
        prop.title,
        prop.description or "",
        f"{prop.bedrooms}BR" if prop.bedrooms else "",
        f"{prop.property_type.value}" if prop.property_type else "",
        f"AED {prop.price_aed}" if prop.price_aed else "",
        prop.address or "",
    ]
    return " ".join(p for p in parts if p)


def _reciprocal_rank_fusion(
    pg_results: list[Property],
    qdrant_hits: list[dict],
    k: int = 60,
) -> list[Property]:
    """Merge PostGIS and Qdrant results using Reciprocal Rank Fusion."""
    pg_ids = {str(p.id): (rank, p) for rank, p in enumerate(pg_results)}
    qdrant_ids = {h["property_id"]: rank for rank, h in enumerate(qdrant_hits)}

    scores: dict[str, float] = {}
    for pid, (rank, _) in pg_ids.items():
        scores[pid] = scores.get(pid, 0) + 1 / (k + rank)
    for pid, rank in qdrant_ids.items():
        scores[pid] = scores.get(pid, 0) + 1 / (k + rank)

    # Sort by combined score; prefer pg_results objects, fallback to qdrant-only ids
    sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)
    result_map = {str(p.id): p for _, p in pg_ids.values()}

    merged: list[Property] = []
    for pid in sorted_ids:
        if pid in result_map:
            merged.append(result_map[pid])
    return merged


class PropertyRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def search(
        self,
        tenant_id: uuid.UUID,
        params: PropertySearchParams,
        qdrant_hits: list[dict] | None = None,
    ) -> tuple[list[Property], int]:
        """Hybrid PostGIS + Qdrant search. Returns (results, total_count)."""
        stmt = select(Property).where(
            Property.tenant_id == tenant_id,
            Property.status != PropertyStatus.sold,
        )

        # Filters
        if params.property_type:
            stmt = stmt.where(Property.property_type == params.property_type)
        if params.purpose:
            stmt = stmt.where(
                sa.or_(Property.purpose == params.purpose, Property.purpose == PropertyPurpose.both)
            )
        if params.price_min is not None:
            stmt = stmt.where(Property.price_aed >= params.price_min)
        if params.price_max is not None:
            stmt = stmt.where(Property.price_aed <= params.price_max)
        if params.bedrooms is not None:
            stmt = stmt.where(Property.bedrooms == params.bedrooms)
        if params.is_freehold is not None:
            stmt = stmt.where(Property.is_freehold == params.is_freehold)
        if params.is_off_plan is not None:
            stmt = stmt.where(Property.is_off_plan == params.is_off_plan)
        if params.is_golden_visa_eligible is not None:
            stmt = stmt.where(Property.is_golden_visa_eligible == params.is_golden_visa_eligible)

        # Text search on title/description
        if params.q:
            pattern = f"%{params.q}%"
            stmt = stmt.where(
                sa.or_(
                    Property.title.ilike(pattern),
                    Property.description.ilike(pattern),
                    Property.address.ilike(pattern),
                )
            )

        # Geo radius filter — bounding box (fast; exact PostGIS reserved for future)
        if params.lat is not None and params.lng is not None and params.radius_km:
            lat_delta = params.radius_km / 111.0
            lng_delta = params.radius_km / (111.0 * math.cos(math.radians(params.lat)))
            stmt = stmt.where(
                Property.latitude.between(params.lat - lat_delta, params.lat + lat_delta),
                Property.longitude.between(params.lng - lng_delta, params.lng + lng_delta),
            )

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        # Sort
        if params.sort == "price_asc":
            stmt = stmt.order_by(Property.price_aed.asc().nullslast())
        elif params.sort == "price_desc":
            stmt = stmt.order_by(Property.price_aed.desc().nullslast())
        elif params.sort == "newest":
            stmt = stmt.order_by(Property.created_at.desc())
        else:
            stmt = stmt.order_by(Property.created_at.desc())

        offset = (params.page - 1) * params.limit
        stmt = stmt.offset(offset).limit(params.limit)

        rows = (await self.db.execute(stmt)).scalars().all()
        pg_results = list(rows)

        # Merge with Qdrant hits if provided
        if qdrant_hits and params.sort == "relevance":
            merged = _reciprocal_rank_fusion(pg_results, qdrant_hits)
            return merged, total

        return pg_results, total

    async def get_by_id(self, property_id: uuid.UUID, tenant_id: uuid.UUID) -> Property | None:
        stmt = select(Property).where(
            Property.id == property_id, Property.tenant_id == tenant_id
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_by_slug(self, slug: str, tenant_id: uuid.UUID) -> Property | None:
        stmt = select(Property).where(
            Property.slug == slug, Property.tenant_id == tenant_id
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def create(self, tenant_id: uuid.UUID, data: PropertyCreate) -> Property:
        prop_id = uuid.uuid4()
        slug = _build_slug(data.title, str(prop_id))

        prop = Property(
            id=prop_id,
            tenant_id=tenant_id,
            slug=slug,
            **data.model_dump(exclude_none=True),
        )

        # Set PostGIS geometry if lat/lng provided
        if data.latitude is not None and data.longitude is not None:
            prop.geom = f"SRID=4326;POINT({data.longitude} {data.latitude})"  # type: ignore[assignment]

        self.db.add(prop)
        await self.db.flush()
        await self.db.refresh(prop)

        # Async embed + upsert to Qdrant (fire and forget)
        text = _property_to_text(prop)
        await emb_svc.upsert_property(
            property_id=str(prop.id),
            tenant_id=str(tenant_id),
            text=text,
            payload={
                "title": prop.title,
                "property_type": prop.property_type.value if prop.property_type else None,
                "price_aed": float(prop.price_aed) if prop.price_aed else None,
                "bedrooms": prop.bedrooms,
            },
        )
        return prop

    async def update(
        self, prop: Property, data: PropertyUpdate
    ) -> Property:
        updates = data.model_dump(exclude_none=True)
        for key, val in updates.items():
            setattr(prop, key, val)

        if "latitude" in updates and "longitude" in updates:
            prop.geom = f"SRID=4326;POINT({updates['longitude']} {updates['latitude']})"  # type: ignore[assignment]

        await self.db.flush()
        await self.db.refresh(prop)

        # Re-embed
        await emb_svc.upsert_property(
            property_id=str(prop.id),
            tenant_id=str(prop.tenant_id),
            text=_property_to_text(prop),
            payload={"title": prop.title},
        )
        return prop

    async def archive(self, prop: Property) -> None:
        prop.status = PropertyStatus.sold  # type: ignore[assignment]
        await self.db.flush()

    async def get_similar(
        self, property_id: uuid.UUID, tenant_id: uuid.UUID, limit: int = 6
    ) -> list[Property]:
        """Find similar properties via Qdrant vector similarity."""
        hits = await emb_svc.search_properties(
            query_text=str(property_id),
            tenant_id=str(tenant_id),
            limit=limit + 1,
        )
        ids = [
            uuid.UUID(h["property_id"]) for h in hits if h["property_id"] != str(property_id)
        ][:limit]
        if not ids:
            return []
        stmt = select(Property).where(Property.id.in_(ids), Property.tenant_id == tenant_id)
        return list((await self.db.execute(stmt)).scalars().all())
