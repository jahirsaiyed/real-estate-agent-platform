"""Embedding service: generates vectors and manages Qdrant collections."""
from __future__ import annotations

import logging
import uuid

from openai import AsyncOpenAI
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.core.config import settings

logger = logging.getLogger(__name__)

_openai_client: AsyncOpenAI | None = None
_qdrant_client: AsyncQdrantClient | None = None


def get_openai_client() -> AsyncOpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY or "placeholder")
    return _openai_client


def get_qdrant_client() -> AsyncQdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        kwargs: dict = {"url": settings.QDRANT_URL}
        if settings.QDRANT_API_KEY:
            kwargs["api_key"] = settings.QDRANT_API_KEY
        _qdrant_client = AsyncQdrantClient(**kwargs)
    return _qdrant_client


async def embed_text(text: str) -> list[float]:
    """Embed a single text string. Returns zero vector on error (graceful degradation)."""
    if not settings.OPENAI_API_KEY:
        return [0.0] * settings.EMBEDDING_DIMS
    try:
        client = get_openai_client()
        response = await client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=text[:8191],  # OpenAI token limit
        )
        return response.data[0].embedding
    except Exception as exc:
        logger.warning("embed_text failed: %s", exc)
        return [0.0] * settings.EMBEDDING_DIMS


async def ensure_collections() -> None:
    """Create Qdrant collections if they don't exist. Called at startup."""
    client = get_qdrant_client()
    collections = {
        settings.QDRANT_COLLECTION_PROPERTIES: settings.EMBEDDING_DIMS,
        settings.QDRANT_COLLECTION_CONVERSATIONS: settings.EMBEDDING_DIMS,
        settings.QDRANT_COLLECTION_KB: settings.EMBEDDING_DIMS,
    }
    try:
        existing = {c.name for c in (await client.get_collections()).collections}
        for name, dims in collections.items():
            if name not in existing:
                await client.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(size=dims, distance=Distance.COSINE),
                )
                logger.info("Created Qdrant collection: %s", name)
    except Exception as exc:
        logger.warning("ensure_collections failed: %s", exc)


async def upsert_property(
    property_id: str,
    tenant_id: str,
    text: str,
    payload: dict,
) -> None:
    """Embed property text and upsert into Qdrant."""
    vector = await embed_text(text)
    client = get_qdrant_client()
    try:
        await client.upsert(
            collection_name=settings.QDRANT_COLLECTION_PROPERTIES,
            points=[
                PointStruct(
                    id=str(uuid.uuid5(uuid.NAMESPACE_DNS, property_id)),
                    vector=vector,
                    payload={"property_id": property_id, "tenant_id": tenant_id, **payload},
                )
            ],
        )
    except Exception as exc:
        logger.warning("upsert_property failed for %s: %s", property_id, exc)


async def search_properties(
    query_text: str,
    tenant_id: str,
    limit: int = 20,
) -> list[dict]:
    """Semantic property search via Qdrant."""
    vector = await embed_text(query_text)
    client = get_qdrant_client()
    try:
        results = await client.search(
            collection_name=settings.QDRANT_COLLECTION_PROPERTIES,
            query_vector=vector,
            query_filter=Filter(
                must=[FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))]
            ),
            limit=limit,
            with_payload=True,
        )
        return [
            {"property_id": r.payload["property_id"], "score": r.score, **r.payload}
            for r in results
        ]
    except Exception as exc:
        logger.warning("search_properties failed: %s", exc)
        return []


async def upsert_conversation_chunk(
    chunk_id: str,
    conversation_id: str,
    lead_id: str,
    tenant_id: str,
    text: str,
) -> None:
    """Store a conversation chunk for long-term lead memory."""
    vector = await embed_text(text)
    client = get_qdrant_client()
    try:
        await client.upsert(
            collection_name=settings.QDRANT_COLLECTION_CONVERSATIONS,
            points=[
                PointStruct(
                    id=str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id)),
                    vector=vector,
                    payload={
                        "chunk_id": chunk_id,
                        "conversation_id": conversation_id,
                        "lead_id": lead_id,
                        "tenant_id": tenant_id,
                        "text": text,
                    },
                )
            ],
        )
    except Exception as exc:
        logger.warning("upsert_conversation_chunk failed: %s", exc)


async def search_lead_memory(
    query_text: str,
    lead_id: str,
    tenant_id: str,
    limit: int = 3,
) -> list[dict]:
    """Retrieve relevant past conversation chunks for a lead."""
    vector = await embed_text(query_text)
    client = get_qdrant_client()
    try:
        results = await client.search(
            collection_name=settings.QDRANT_COLLECTION_CONVERSATIONS,
            query_vector=vector,
            query_filter=Filter(
                must=[
                    FieldCondition(key="lead_id", match=MatchValue(value=lead_id)),
                    FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id)),
                ]
            ),
            limit=limit,
            with_payload=True,
        )
        return [r.payload for r in results]
    except Exception as exc:
        logger.warning("search_lead_memory failed: %s", exc)
        return []


async def search_knowledge_base(
    query_text: str,
    tenant_id: str,
    limit: int = 5,
) -> list[dict]:
    """RAG: retrieve relevant knowledge base chunks."""
    vector = await embed_text(query_text)
    client = get_qdrant_client()
    try:
        results = await client.search(
            collection_name=settings.QDRANT_COLLECTION_KB,
            query_vector=vector,
            query_filter=Filter(
                must=[FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))]
            ),
            limit=limit,
            with_payload=True,
        )
        return [{"text": r.payload.get("text", ""), "score": r.score, **r.payload} for r in results]
    except Exception as exc:
        logger.warning("search_knowledge_base failed: %s", exc)
        return []
