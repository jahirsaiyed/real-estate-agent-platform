"""Conversation and message schemas."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.conversation import ConversationChannel, ConversationLanguage, ConversationStatus


class ConversationCreate(BaseModel):
    channel: ConversationChannel = ConversationChannel.web
    language: ConversationLanguage = ConversationLanguage.en
    lead_id: uuid.UUID | None = None
    external_thread_id: str | None = None


class ConversationResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    lead_id: uuid.UUID | None
    channel: str
    status: str
    language: str
    sentiment_score: float | None
    frustration_count: int
    handoff_reason: str | None
    handoff_at: datetime | None
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationListItem(BaseModel):
    id: uuid.UUID
    channel: str
    status: str
    language: str
    lead_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationUpdate(BaseModel):
    status: ConversationStatus | None = None
    handoff_agent_id: uuid.UUID | None = None


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)
    language: ConversationLanguage = ConversationLanguage.en
    attachments: list[Any] = Field(default_factory=list)


class MessageResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    tool_name: str | None
    tool_output: dict | None
    tokens_used: int | None
    latency_ms: int | None
    guardrail_triggered: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageListResponse(BaseModel):
    items: list[MessageResponse]
    total: int
    page: int
    limit: int


class ChatStreamChunk(BaseModel):
    """Sent over WebSocket to client during streaming."""
    type: str  # "token" | "tool_result" | "qualification_update" | "done" | "error"
    content: str | None = None
    tool_outputs: dict | None = None
    qualification_update: dict | None = None
    error: str | None = None
