"""Handoff agent node: trigger human escalation."""
from __future__ import annotations

import logging

from langchain_core.messages import AIMessage

from app.agents.state import AgentState

logger = logging.getLogger(__name__)

HANDOFF_MESSAGES = {
    "en": "I'm connecting you with one of our specialists now. They'll be with you shortly. Is there anything specific you'd like them to know before the call?",
    "ar": "أقوم بتحويلك الآن إلى أحد متخصصينا. سيكون معك قريباً. هل هناك شيء محدد تريد أن يعرفه قبل الاتصال؟",
    "hi": "मैं अभी आपको हमारे एक विशेषज्ञ से जोड़ रहा हूँ। वे जल्द ही आपके साथ होंगे।",
    "ru": "Я соединяю вас с одним из наших специалистов. Они скоро будут с вами.",
}


def handoff_agent(state: AgentState) -> AgentState:
    """Prepare handoff message and mark conversation for human agent pickup."""
    language = state.get("language", "en")
    handoff_msg = HANDOFF_MESSAGES.get(language, HANDOFF_MESSAGES["en"])

    state["handoff_triggered"] = True
    state["messages"] = list(state.get("messages", [])) + [
        AIMessage(content=handoff_msg)
    ]

    logger.info(
        "Handoff triggered for conversation %s, reason: %s",
        state.get("conversation_id"),
        state.get("handoff_reason", "unknown"),
    )
    return state
