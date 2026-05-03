"""Inbound webhooks: WhatsApp Business API + Telegram Bot."""
from __future__ import annotations

import logging
import uuid

import redis.asyncio as aioredis
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, status
from langchain_core.messages import HumanMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import run_turn
from app.agents.state import AgentState, default_qualification_score
from app.api.v1.deps import get_db, get_redis
from app.models.conversation import ConversationChannel, ConversationLanguage, ConversationStatus
from app.models.message import MessageRole
from app.repositories.conversation import ConversationRepository, MessageRepository
from app.repositories.lead import LeadRepository
from app.schemas.conversation import ConversationCreate
from app.schemas.lead import LeadCreate
from app.services.notification import (
    parse_telegram_webhook,
    parse_whatsapp_webhook,
    send_telegram_text,
    send_whatsapp_text,
    verify_whatsapp_signature,
)
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


# ──────────────────────────────────────────────
# WhatsApp webhook
# ──────────────────────────────────────────────

@router.get("/whatsapp")
async def whatsapp_verify(
    hub_mode: str = Query(alias="hub.mode"),
    hub_challenge: str = Query(alias="hub.challenge"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
) -> int:
    """Meta webhook verification endpoint."""
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        return int(hub_challenge)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification failed")


@router.post("/whatsapp", status_code=status.HTTP_200_OK)
async def whatsapp_incoming(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
) -> dict:
    """Receive and process WhatsApp Business API messages."""
    body_bytes = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    if not verify_whatsapp_signature(body_bytes, signature):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature")

    body = await request.json()
    messages = parse_whatsapp_webhook(body)

    for msg in messages:
        if msg["type"] != "text" or not msg["text"]:
            continue
        background_tasks.add_task(
            _process_channel_message,
            phone=msg["from"],
            text=msg["text"],
            channel=ConversationChannel.whatsapp,
            external_thread_id=msg["from"],
            db=db,
            redis=redis,
        )

    return {"status": "ok"}


# ──────────────────────────────────────────────
# Telegram webhook
# ──────────────────────────────────────────────

@router.post("/telegram", status_code=status.HTTP_200_OK)
async def telegram_incoming(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
) -> dict:
    """Receive and process Telegram Bot updates."""
    body = await request.json()
    msg = parse_telegram_webhook(body)

    if msg and msg.get("text"):
        background_tasks.add_task(
            _process_channel_message,
            phone=str(msg["from_id"]),
            text=msg["text"],
            channel=ConversationChannel.telegram,
            external_thread_id=str(msg["chat_id"]),
            db=db,
            redis=redis,
            telegram_chat_id=msg["chat_id"],
        )

    return {"status": "ok"}


# ──────────────────────────────────────────────
# Shared processing logic
# ──────────────────────────────────────────────

async def _process_channel_message(
    phone: str,
    text: str,
    channel: ConversationChannel,
    external_thread_id: str,
    db: AsyncSession,
    redis: aioredis.Redis,
    telegram_chat_id: int | None = None,
) -> None:
    """Find or create lead+conversation, run agent graph, reply to channel."""
    # Use first tenant (MVP single-tenant; multi-tenant: resolve from phone routing)
    from sqlalchemy import select
    from app.models.tenant import Tenant

    tenant_result = await db.execute(select(Tenant).where(Tenant.is_active == True).limit(1))
    tenant = tenant_result.scalar_one_or_none()
    if not tenant:
        logger.error("No active tenant found for webhook processing")
        return

    tenant_id = tenant.id

    lead_repo = LeadRepository(db)
    conv_repo = ConversationRepository(db)
    msg_repo = MessageRepository(db)

    # Find or create lead by phone
    lead = await lead_repo.get_by_phone(phone, tenant_id)
    if not lead:
        lead = await lead_repo.create(
            tenant_id,
            LeadCreate(
                phone=phone,
                source_channel=channel.value,  # type: ignore[arg-type]
            ),
        )
        await db.flush()

    # Find or create conversation
    conv = await conv_repo.get_by_external_thread(external_thread_id, channel, tenant_id)
    if not conv:
        conv = await conv_repo.create(
            tenant_id,
            ConversationCreate(
                channel=channel,
                lead_id=lead.id,
                external_thread_id=external_thread_id,
            ),
        )
        await db.flush()

    # Persist user message
    await msg_repo.create_message(
        conversation_id=conv.id,
        tenant_id=tenant_id,
        role=MessageRole.user,
        content=text,
    )
    await db.flush()

    # Load recent history
    recent_msgs = await msg_repo.get_recent_messages(conv.id, tenant_id, limit=20)
    lc_messages = [
        HumanMessage(content=m.content) if m.role == MessageRole.user
        else _make_ai_message(m.content)
        for m in recent_msgs
    ]

    state: AgentState = {
        "tenant_id": str(tenant_id),
        "conversation_id": str(conv.id),
        "lead_id": str(lead.id),
        "agent_id": None,
        "messages": lc_messages,
        "language": "en",
        "channel": channel.value,
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

    try:
        result = await run_turn(state, db=db, redis=redis)
    except Exception as exc:
        logger.error("Agent graph failed for %s channel: %s", channel.value, exc)
        await db.rollback()
        return

    from langchain_core.messages import AIMessage
    assistant_content = ""
    for msg_item in reversed(result.get("messages", [])):
        if isinstance(msg_item, AIMessage):
            assistant_content = msg_item.content
            break

    if not assistant_content:
        await db.rollback()
        return

    # Persist assistant message
    await msg_repo.create_message(
        conversation_id=conv.id,
        tenant_id=tenant_id,
        role=MessageRole.assistant,
        content=assistant_content,
        guardrail_triggered=bool(result.get("guardrail_violations")),
    )

    # Handoff
    if result.get("handoff_triggered"):
        await conv_repo.update_status(conv, ConversationStatus.handoff)

    await db.commit()

    # Send reply to channel
    if channel == ConversationChannel.whatsapp:
        await send_whatsapp_text(phone, assistant_content)
    elif channel == ConversationChannel.telegram and telegram_chat_id:
        await send_telegram_text(telegram_chat_id, assistant_content)


def _make_ai_message(content: str):
    from langchain_core.messages import AIMessage
    return AIMessage(content=content)
