from typing import Annotated, Optional
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class QualificationScore(TypedDict):
    budget: int
    property_type: int
    purpose: int
    timeline: int
    nationality: int
    pre_approval: int
    locations: int
    contact_preference: int
    total: int
    status: str  # unqualified | in_progress | qualified | handoff


def default_qualification_score() -> QualificationScore:
    return QualificationScore(
        budget=0,
        property_type=0,
        purpose=0,
        timeline=0,
        nationality=0,
        pre_approval=0,
        locations=0,
        contact_preference=0,
        total=0,
        status="unqualified",
    )


class AgentState(TypedDict):
    # Identity
    tenant_id: str
    conversation_id: str
    lead_id: str
    agent_id: Optional[str]

    # Conversation
    messages: Annotated[list[BaseMessage], add_messages]
    language: str           # en | ar | hi | ru
    channel: str            # web | whatsapp | telegram

    # Intent
    current_intent: str     # search | book | calculate | qualify | rag | handoff | smalltalk | unclear
    intent_confidence: float
    clarification_attempts: int

    # Tool outputs
    search_results: list[dict]
    calendar_slots: list[dict]
    calculator_output: Optional[dict]
    rag_chunks: list[dict]

    # Lead context
    qualification_score: QualificationScore
    extracted_entities: dict

    # Control flow
    handoff_triggered: bool
    handoff_reason: Optional[str]
    frustration_count: int
    consecutive_failures: int

    # Guardrails
    guardrail_violations: list[str]
    regeneration_count: int

    # Memory
    session_memory: dict
    lead_memory_context: str

    # Tenant config
    persona_name: str
    guardrail_rules: list[dict]
    tone: str               # warm_professional | formal | casual
