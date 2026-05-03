"""Property search agent node: hybrid PostGIS + Qdrant search."""
from __future__ import annotations

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.state import AgentState
from app.repositories.property import PropertyRepository
from app.schemas.property import PropertySearchParams
from app.services import embedding as emb_svc

logger = logging.getLogger(__name__)


async def property_search_agent(
    state: AgentState,
    db: AsyncSession,
) -> AgentState:
    """Execute hybrid property search and populate state['search_results']."""
    entities = state.get("extracted_entities", {})
    tenant_id_str = state.get("tenant_id", "")

    try:
        tenant_id = uuid.UUID(tenant_id_str)
    except (ValueError, AttributeError):
        state["search_results"] = []
        return state

    # Build search params from extracted entities
    params = PropertySearchParams(
        q=entities.get("query_text"),
        property_type=entities.get("property_type"),
        purpose=entities.get("purpose"),
        price_min=entities.get("budget_min_aed"),
        price_max=entities.get("budget_max_aed"),
        bedrooms=entities.get("bedrooms"),
        area=entities.get("area"),
        is_freehold=entities.get("is_freehold"),
        is_off_plan=entities.get("is_off_plan"),
        is_golden_visa_eligible=entities.get("is_golden_visa_eligible"),
        lat=entities.get("lat"),
        lng=entities.get("lng"),
        radius_km=entities.get("radius_km"),
        sort="relevance",
        limit=10,
    )

    # Run semantic search for relevance ranking
    query_text = _build_search_query(entities)
    qdrant_hits = await emb_svc.search_properties(
        query_text=query_text,
        tenant_id=tenant_id_str,
        limit=20,
    )

    repo = PropertyRepository(db)
    results, total = await repo.search(tenant_id, params, qdrant_hits=qdrant_hits)

    state["search_results"] = [
        {
            "id": str(r.id),
            "title": r.title,
            "property_type": r.property_type.value if r.property_type else None,
            "price_aed": float(r.price_aed) if r.price_aed else None,
            "bedrooms": r.bedrooms,
            "bathrooms": r.bathrooms,
            "area_sqft": float(r.area_sqft) if r.area_sqft else None,
            "address": r.address,
            "is_off_plan": r.is_off_plan,
            "is_freehold": r.is_freehold,
            "images": r.images or [],
            "slug": r.slug,
        }
        for r in results
    ]

    return state


def _build_search_query(entities: dict) -> str:
    """Build a natural-language query string from extracted entities."""
    parts = []
    if entities.get("bedrooms"):
        parts.append(f"{entities['bedrooms']} bedroom")
    if entities.get("property_type"):
        parts.append(entities["property_type"])
    if entities.get("area"):
        parts.append(entities["area"])
    if entities.get("purpose"):
        parts.append(f"for {entities['purpose']}")
    if entities.get("budget_max_aed"):
        parts.append(f"under AED {entities['budget_max_aed']}")
    if entities.get("query_text"):
        parts.append(entities["query_text"])
    return " ".join(parts) or "Dubai property"
