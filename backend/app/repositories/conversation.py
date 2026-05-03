"""Conversation and message repositories."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation, ConversationChannel, ConversationLanguage, ConversationStatus
from app.models.message import Message, MessageRole
from app.schemas.conversation import ConversationCreate, MessageCreate


class ConversationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, tenant_id: uuid.UUID, data: ConversationCreate) -> Conversation:
        conv = Conversation(
            tenant_id=tenant_id,
            channel=data.channel,
            language=data.language,
            lead_id=data.lead_id,
            external_thread_id=data.external_thread_id,
        )
        self.db.add(conv)
        await self.db.flush()
        await self.db.refresh(conv)
        return conv

    async def get_by_id(self, conv_id: uuid.UUID, tenant_id: uuid.UUID) -> Conversation | None:
        stmt = select(Conversation).where(
            Conversation.id == conv_id,
            Conversation.tenant_id == tenant_id,
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_by_external_thread(
        self, external_thread_id: str, channel: ConversationChannel, tenant_id: uuid.UUID
    ) -> Conversation | None:
        stmt = select(Conversation).where(
            Conversation.external_thread_id == external_thread_id,
            Conversation.channel == channel,
            Conversation.tenant_id == tenant_id,
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def list(
        self,
        tenant_id: uuid.UUID,
        status: ConversationStatus | None = None,
        channel: ConversationChannel | None = None,
        lead_id: uuid.UUID | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Conversation], int]:
        stmt = select(Conversation).where(Conversation.tenant_id == tenant_id)
        if status:
            stmt = stmt.where(Conversation.status == status)
        if channel:
            stmt = stmt.where(Conversation.channel == channel)
        if lead_id:
            stmt = stmt.where(Conversation.lead_id == lead_id)

        total = (await self.db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
        stmt = stmt.order_by(Conversation.updated_at.desc())
        stmt = stmt.offset((page - 1) * limit).limit(limit)
        rows = list((await self.db.execute(stmt)).scalars().all())
        return rows, total

    async def update_status(
        self,
        conv: Conversation,
        status: ConversationStatus,
        handoff_agent_id: uuid.UUID | None = None,
    ) -> Conversation:
        conv.status = status  # type: ignore[assignment]
        if status == ConversationStatus.handoff:
            conv.handoff_at = datetime.now(timezone.utc)  # type: ignore[assignment]
            if handoff_agent_id:
                conv.handoff_agent_id = handoff_agent_id  # type: ignore[assignment]
        elif status == ConversationStatus.resolved:
            conv.resolved_at = datetime.now(timezone.utc)  # type: ignore[assignment]
        await self.db.flush()
        await self.db.refresh(conv)
        return conv

    async def update_sentiment(
        self, conv: Conversation, sentiment_score: float, frustration_count: int
    ) -> None:
        conv.sentiment_score = sentiment_score  # type: ignore[assignment]
        conv.frustration_count = frustration_count  # type: ignore[assignment]
        await self.db.flush()


class MessageRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_message(
        self,
        conversation_id: uuid.UUID,
        tenant_id: uuid.UUID,
        role: MessageRole,
        content: str,
        tool_name: str | None = None,
        tool_input: dict | None = None,
        tool_output: dict | None = None,
        tokens_used: int | None = None,
        latency_ms: int | None = None,
        guardrail_triggered: bool = False,
        guardrail_reason: str | None = None,
    ) -> Message:
        msg = Message(
            conversation_id=conversation_id,
            tenant_id=tenant_id,
            role=role,
            content=content,
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=tool_output,
            tokens_used=tokens_used,
            latency_ms=latency_ms,
            guardrail_triggered=guardrail_triggered,
            guardrail_reason=guardrail_reason,
        )
        self.db.add(msg)
        await self.db.flush()
        await self.db.refresh(msg)
        return msg

    async def get_messages(
        self,
        conversation_id: uuid.UUID,
        tenant_id: uuid.UUID,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[Message], int]:
        stmt = select(Message).where(
            Message.conversation_id == conversation_id,
            Message.tenant_id == tenant_id,
        )
        total = (await self.db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
        stmt = stmt.order_by(Message.created_at.asc()).offset((page - 1) * limit).limit(limit)
        rows = list((await self.db.execute(stmt)).scalars().all())
        return rows, total

    async def get_recent_messages(
        self,
        conversation_id: uuid.UUID,
        tenant_id: uuid.UUID,
        limit: int = 20,
    ) -> list[Message]:
        stmt = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.tenant_id == tenant_id,
            )
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        rows = list((await self.db.execute(stmt)).scalars().all())
        return list(reversed(rows))
