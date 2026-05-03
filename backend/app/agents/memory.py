"""Redis session memory + Qdrant long-term memory helpers."""
from __future__ import annotations

import json
import logging
import uuid

import redis.asyncio as aioredis

from app.agents.state import AgentState, default_qualification_score
from app.core.config import settings
from app.services import embedding as emb_svc

logger = logging.getLogger(__name__)

SESSION_KEY_PREFIX = "session:"
SESSION_TTL = settings.SESSION_TTL_SECONDS


async def load_session(
    conversation_id: str,
    redis: aioredis.Redis,
) -> dict:
    """Load short-term session state from Redis."""
    try:
        raw = await redis.get(f"{SESSION_KEY_PREFIX}{conversation_id}")
        if raw:
            return json.loads(raw)
    except Exception as exc:
        logger.warning("load_session failed for %s: %s", conversation_id, exc)
    return {}


async def save_session(
    conversation_id: str,
    state: AgentState,
    redis: aioredis.Redis,
) -> None:
    """Persist session state to Redis with TTL."""
    session_data = {
        "entities": state.get("extracted_entities", {}),
        "qualification_score": state.get("qualification_score", default_qualification_score()),
        "frustration_count": state.get("frustration_count", 0),
        "consecutive_failures": state.get("consecutive_failures", 0),
        "language": state.get("language", "en"),
    }
    try:
        await redis.setex(
            f"{SESSION_KEY_PREFIX}{conversation_id}",
            SESSION_TTL,
            json.dumps(session_data, default=str),
        )
    except Exception as exc:
        logger.warning("save_session failed for %s: %s", conversation_id, exc)


async def load_lead_memory(
    lead_id: str,
    tenant_id: str,
    query_text: str,
) -> str:
    """Retrieve relevant past conversation chunks from Qdrant for context."""
    if not lead_id:
        return ""
    try:
        chunks = await emb_svc.search_lead_memory(
            query_text=query_text,
            lead_id=lead_id,
            tenant_id=tenant_id,
            limit=3,
        )
        if not chunks:
            return ""
        parts = [f"[Past context] {c.get('text', '')}" for c in chunks if c.get("text")]
        return "\n".join(parts)
    except Exception as exc:
        logger.warning("load_lead_memory failed for lead %s: %s", lead_id, exc)
        return ""


async def save_conversation_chunk(
    conversation_id: str,
    lead_id: str,
    tenant_id: str,
    user_text: str,
    assistant_text: str,
) -> None:
    """Save conversation turn to Qdrant for future lead memory retrieval."""
    if not lead_id:
        return
    chunk_text = f"User: {user_text}\nAssistant: {assistant_text}"
    chunk_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{conversation_id}:{user_text[:50]}"))
    try:
        await emb_svc.upsert_conversation_chunk(
            chunk_id=chunk_id,
            conversation_id=conversation_id,
            lead_id=lead_id,
            tenant_id=tenant_id,
            text=chunk_text,
        )
    except Exception as exc:
        logger.warning("save_conversation_chunk failed: %s", exc)
