"""Qualification agent node: 8-dimension lead scoring."""
from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage

from app.agents.state import AgentState, QualificationScore

logger = logging.getLogger(__name__)

FRUSTRATION_SIGNALS = [
    "this is useless",
    "not helpful",
    "terrible",
    "give up",
    "waste of time",
    "not working",
    "forget it",
    "bye",
    "whatever",
]


def qualification_agent(state: AgentState) -> AgentState:
    """Score 8 qualification dimensions from extracted entities."""
    entities = state.get("extracted_entities", {})
    score = state.get("qualification_score", {}).copy()

    score["budget"] = _score_budget(
        entities.get("budget_min_aed"), entities.get("budget_max_aed")
    )
    score["property_type"] = 10 if entities.get("property_type") else 0
    score["purpose"] = 10 if entities.get("purpose") else 0
    score["timeline"] = _score_timeline(entities.get("timeline_months"))
    score["nationality"] = 10 if entities.get("nationality") else 0
    score["pre_approval"] = 10 if entities.get("pre_approved") is not None else 0
    score["locations"] = min(10, len(entities.get("preferred_locations", [])) * 5)
    score["contact_preference"] = 10 if entities.get("contact_preference") else 0

    total = sum(
        v for k, v in score.items()
        if k not in ("total", "status") and isinstance(v, int)
    )
    score["total"] = total
    score["status"] = (
        "qualified" if total >= 70
        else "in_progress" if total > 0
        else "unqualified"
    )

    state["qualification_score"] = score  # type: ignore[typeddict-item]

    # Detect frustration from last user message
    last_msg = _get_last_user_text(state)
    if last_msg and any(sig in last_msg.lower() for sig in FRUSTRATION_SIGNALS):
        state["frustration_count"] = state.get("frustration_count", 0) + 1

    return state


def _get_last_user_text(state: AgentState) -> str:
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, HumanMessage):
            return msg.content
    return ""


def _score_budget(min_aed, max_aed) -> int:
    if max_aed or min_aed:
        return 10
    return 0


def _score_timeline(months) -> int:
    if months is None:
        return 0
    if months <= 1:
        return 10
    if months <= 3:
        return 8
    if months <= 6:
        return 6
    if months <= 12:
        return 4
    return 2
