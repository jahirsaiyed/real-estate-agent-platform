"""Conversations API — REST + WebSocket streaming chat."""
from __future__ import annotations

import json
import time
import uuid
from typing import Annotated

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from langchain_core.messages import HumanMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import run_turn
from app.agents.state import AgentState, default_qualification_score
from app.api.v1.deps import get_current_user, get_db, get_redis
from app.models.conversation import ConversationChannel, ConversationLanguage, ConversationStatus
from app.models.message import MessageRole
from app.models.user import User
from app.repositories.conversation import ConversationRepository, MessageRepository
from app.schemas.conversation import (
    ConversationCreate,
    ConversationListItem,
    ConversationResponse,
    ConversationUpdate,
    MessageCreate,
    MessageListResponse,
    MessageResponse,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    data: ConversationCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ConversationResponse:
    repo = ConversationRepository(db)
    conv = await repo.create(current_user.tenant_id, data)
    await db.commit()
    await db.refresh(conv)
    return ConversationResponse.model_validate(conv)


@router.get("", response_model=list[ConversationListItem])
async def list_conversations(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    status_filter: ConversationStatus | None = Query(default=None, alias="status"),
    channel: ConversationChannel | None = None,
    lead_id: uuid.UUID | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[ConversationListItem]:
    repo = ConversationRepository(db)
    rows, _ = await repo.list(
        current_user.tenant_id,
        status=status_filter,
        channel=channel,
        lead_id=lead_id,
        page=page,
        limit=limit,
    )
    return [ConversationListItem.model_validate(r) for r in rows]


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ConversationResponse:
    repo = ConversationRepository(db)
    conv = await repo.get_by_id(conversation_id, current_user.tenant_id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return ConversationResponse.model_validate(conv)


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: uuid.UUID,
    data: ConversationUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ConversationResponse:
    repo = ConversationRepository(db)
    conv = await repo.get_by_id(conversation_id, current_user.tenant_id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    if data.status:
        await repo.update_status(conv, data.status, data.handoff_agent_id)
        await db.commit()
        await db.refresh(conv)
    return ConversationResponse.model_validate(conv)


@router.get("/{conversation_id}/messages", response_model=MessageListResponse)
async def get_messages(
    conversation_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
) -> MessageListResponse:
    conv_repo = ConversationRepository(db)
    conv = await conv_repo.get_by_id(conversation_id, current_user.tenant_id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    msg_repo = MessageRepository(db)
    messages, total = await msg_repo.get_messages(conversation_id, current_user.tenant_id, page, limit)
    return MessageListResponse(
        items=[MessageResponse.model_validate(m) for m in messages],
        total=total,
        page=page,
        limit=limit,
    )


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: uuid.UUID,
    data: MessageCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    redis: Annotated[aioredis.Redis, Depends(get_redis)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MessageResponse:
    """REST fallback for sending a message (WebSocket preferred for streaming)."""
    conv_repo = ConversationRepository(db)
    conv = await conv_repo.get_by_id(conversation_id, current_user.tenant_id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    msg_repo = MessageRepository(db)

    # Persist user message
    user_msg = await msg_repo.create_message(
        conversation_id=conversation_id,
        tenant_id=current_user.tenant_id,
        role=MessageRole.user,
        content=data.content,
    )
    await db.commit()

    # Run agent graph
    recent_msgs = await msg_repo.get_recent_messages(conversation_id, current_user.tenant_id, limit=20)
    lc_messages = [
        HumanMessage(content=m.content) if m.role == MessageRole.user
        else _make_ai_message(m.content)
        for m in recent_msgs
    ]

    state: AgentState = {
        "tenant_id": str(current_user.tenant_id),
        "conversation_id": str(conversation_id),
        "lead_id": str(conv.lead_id) if conv.lead_id else "",
        "agent_id": None,
        "messages": lc_messages,
        "language": data.language.value,
        "channel": conv.channel.value,
        "current_intent": "",
        "intent_confidence": 0.0,
        "clarification_attempts": 0,
        "search_results": [],
        "calendar_slots": [],
        "calculator_output": None,
        "rag_chunks": [],
        "qualification_score": default_qualification_score(),
        "extracted_entities": {},
        "handoff_triggered": False,
        "handoff_reason": None,
        "frustration_count": 0,
        "consecutive_failures": 0,
        "guardrail_violations": [],
        "regeneration_count": 0,
        "session_memory": {},
        "lead_memory_context": "",
        "persona_name": "Layla",
        "guardrail_rules": [],
        "tone": "warm_professional",
    }

    t0 = time.monotonic()
    result = await run_turn(state, db=db, redis=redis)
    latency = int((time.monotonic() - t0) * 1000)

    # Get assistant response
    from langchain_core.messages import AIMessage
    assistant_content = ""
    for msg in reversed(result.get("messages", [])):
        if isinstance(msg, AIMessage):
            assistant_content = msg.content
            break

    # Persist assistant message
    tokens_used = None  # Could parse from LLM response metadata
    asst_msg = await msg_repo.create_message(
        conversation_id=conversation_id,
        tenant_id=current_user.tenant_id,
        role=MessageRole.assistant,
        content=assistant_content,
        latency_ms=latency,
        tokens_used=tokens_used,
        guardrail_triggered=bool(result.get("guardrail_violations")),
    )
    await db.commit()

    # Trigger handoff status update if needed
    if result.get("handoff_triggered"):
        await conv_repo.update_status(conv, ConversationStatus.handoff)
        await db.commit()

    return MessageResponse.model_validate(asst_msg)


@router.post("/{conversation_id}/handoff", status_code=status.HTTP_200_OK)
async def trigger_handoff(
    conversation_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    repo = ConversationRepository(db)
    conv = await repo.get_by_id(conversation_id, current_user.tenant_id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    await repo.update_status(conv, ConversationStatus.handoff)
    await db.commit()
    return {"status": "handoff_initiated", "conversation_id": str(conversation_id)}


@router.post("/{conversation_id}/resolve", status_code=status.HTTP_200_OK)
async def resolve_conversation(
    conversation_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    repo = ConversationRepository(db)
    conv = await repo.get_by_id(conversation_id, current_user.tenant_id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    await repo.update_status(conv, ConversationStatus.resolved)
    await db.commit()
    return {"status": "resolved", "conversation_id": str(conversation_id)}


# ──────────────────────────────────────────────
# WebSocket streaming chat
# ──────────────────────────────────────────────

ws_router = APIRouter(prefix="/chat", tags=["chat"])


@ws_router.websocket("/stream/{conversation_id}")
async def websocket_chat(
    websocket: WebSocket,
    conversation_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    redis: Annotated[aioredis.Redis, Depends(get_redis)],
) -> None:
    """WebSocket endpoint for streaming AI chat responses.

    Auth: send token as query param ?token=<jwt> or first WS message.
    """
    await websocket.accept()

    try:
        # Auth: expect first message as {"token": "..."}
        auth_data = await websocket.receive_json()
        token = auth_data.get("token", "")

        from app.core.security import decode_token
        from sqlalchemy import select
        from app.models.user import User

        try:
            payload = decode_token(token)
        except ValueError:
            await websocket.send_json({"type": "error", "error": "Invalid token"})
            await websocket.close(code=4001)
            return

        user_id = payload.get("sub")
        result_user = await db.execute(select(User).where(User.id == user_id))
        current_user = result_user.scalar_one_or_none()
        if not current_user or not current_user.is_active:
            await websocket.send_json({"type": "error", "error": "Unauthorized"})
            await websocket.close(code=4001)
            return

        conv_repo = ConversationRepository(db)
        conv = await conv_repo.get_by_id(conversation_id, current_user.tenant_id)
        if not conv:
            await websocket.send_json({"type": "error", "error": "Conversation not found"})
            await websocket.close(code=4004)
            return

        msg_repo = MessageRepository(db)

        while True:
            try:
                incoming = await websocket.receive_json()
                user_text = incoming.get("content", "").strip()
                language = incoming.get("language", conv.language.value)

                if not user_text:
                    continue

                # Persist user message
                await msg_repo.create_message(
                    conversation_id=conversation_id,
                    tenant_id=current_user.tenant_id,
                    role=MessageRole.user,
                    content=user_text,
                )
                await db.commit()

                # Build state from recent history
                recent_msgs = await msg_repo.get_recent_messages(
                    conversation_id, current_user.tenant_id, limit=20
                )
                lc_messages = [
                    HumanMessage(content=m.content) if m.role == MessageRole.user
                    else _make_ai_message(m.content)
                    for m in recent_msgs
                ]

                state: AgentState = {
                    "tenant_id": str(current_user.tenant_id),
                    "conversation_id": str(conversation_id),
                    "lead_id": str(conv.lead_id) if conv.lead_id else "",
                    "agent_id": None,
                    "messages": lc_messages,
                    "language": language,
                    "channel": conv.channel.value,
                    "current_intent": "",
                    "intent_confidence": 0.0,
                    "clarification_attempts": 0,
                    "search_results": [],
                    "calendar_slots": [],
                    "calculator_output": None,
                    "rag_chunks": [],
                    "qualification_score": default_qualification_score(),
                    "extracted_entities": {},
                    "handoff_triggered": False,
                    "handoff_reason": None,
                    "frustration_count": 0,
                    "consecutive_failures": 0,
                    "guardrail_violations": [],
                    "regeneration_count": 0,
                    "session_memory": {},
                    "lead_memory_context": "",
                    "persona_name": "Layla",
                    "guardrail_rules": [],
                    "tone": "warm_professional",
                }

                t0 = time.monotonic()
                graph_result = await run_turn(state, db=db, redis=redis)
                latency = int((time.monotonic() - t0) * 1000)

                from langchain_core.messages import AIMessage as LCAIMessage
                assistant_content = ""
                for msg in reversed(graph_result.get("messages", [])):
                    if isinstance(msg, LCAIMessage):
                        assistant_content = msg.content
                        break

                # Persist assistant message
                await msg_repo.create_message(
                    conversation_id=conversation_id,
                    tenant_id=current_user.tenant_id,
                    role=MessageRole.assistant,
                    content=assistant_content,
                    latency_ms=latency,
                    guardrail_triggered=bool(graph_result.get("guardrail_violations")),
                )
                await db.commit()

                # Send response over WebSocket
                await websocket.send_json({
                    "type": "done",
                    "content": assistant_content,
                    "tool_outputs": {
                        "search_results": graph_result.get("search_results", []),
                        "calendar_slots": graph_result.get("calendar_slots", []),
                    },
                    "qualification_update": graph_result.get("qualification_score"),
                    "handoff_triggered": graph_result.get("handoff_triggered", False),
                })

                if graph_result.get("handoff_triggered"):
                    await conv_repo.update_status(conv, ConversationStatus.handoff)
                    await db.commit()
                    await websocket.close()
                    return

            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        try:
            await websocket.send_json({"type": "error", "error": str(exc)})
        except Exception:
            pass


def _make_ai_message(content: str):
    from langchain_core.messages import AIMessage
    return AIMessage(content=content)
