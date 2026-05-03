"""RAG agent node: semantic search over knowledge base."""
from __future__ import annotations

import logging

from app.agents.state import AgentState
from app.services import embedding as emb_svc

logger = logging.getLogger(__name__)


async def rag_agent(state: AgentState) -> AgentState:
    """Retrieve relevant knowledge base chunks to augment response."""
    messages = state.get("messages", [])
    tenant_id = state.get("tenant_id", "")

    # Build query from last user message
    last_user_text = ""
    for msg in reversed(messages):
        if hasattr(msg, "type") and msg.type == "human":
            last_user_text = msg.content
            break
        if hasattr(msg, "__class__") and msg.__class__.__name__ == "HumanMessage":
            last_user_text = msg.content
            break

    if not last_user_text or not tenant_id:
        state["rag_chunks"] = []
        return state

    try:
        chunks = await emb_svc.search_knowledge_base(
            query_text=last_user_text,
            tenant_id=tenant_id,
            limit=5,
        )
        state["rag_chunks"] = chunks
    except Exception as exc:
        logger.warning("rag_agent failed: %s", exc)
        state["rag_chunks"] = []

    return state
