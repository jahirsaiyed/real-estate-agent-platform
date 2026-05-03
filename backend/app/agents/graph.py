"""Sprint 1 skeleton LangGraph agent graph.

Nodes: memory_loader → intent_classifier → response_generator → guardrails_node → memory_update
All nodes except response_generator are stubs in Sprint 1.
"""
from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agents.llm import llm_provider
from app.agents.state import AgentState, default_qualification_score
from langgraph.graph import END, StateGraph

SYSTEM_PROMPT = """You are Layla, a warm and professional Dubai real estate specialist.
You help clients find their perfect property in Dubai, UAE.
Always respond in the language the user writes in.
Never guarantee prices or investment returns — always add appropriate disclaimers."""

INTENT_KEYWORDS: dict[str, list[str]] = {
    "handoff": ["speak to agent", "human agent", "call me", "agent please", "representative"],
    "search": ["looking for", "find", "search", "show me", "properties", "apartment", "villa"],
    "book": ["book", "viewing", "appointment", "schedule", "visit", "tour"],
    "calculate": ["mortgage", "roi", "calculate", "afford", "payment", "visa eligibility"],
    "qualify": ["budget", "bedroom", "ready to buy", "pre-approved"],
}


def memory_loader(state: AgentState) -> AgentState:
    """Stub: In Sprint 2+ will load Redis session + Qdrant long-term memory."""
    if not state.get("session_memory"):
        state["session_memory"] = {}
    if not state.get("lead_memory_context"):
        state["lead_memory_context"] = ""
    if not state.get("qualification_score"):
        state["qualification_score"] = default_qualification_score()
    if not state.get("extracted_entities"):
        state["extracted_entities"] = {}
    if not state.get("guardrail_rules"):
        state["guardrail_rules"] = []
    if not state.get("persona_name"):
        state["persona_name"] = "Layla"
    if not state.get("tone"):
        state["tone"] = "warm_professional"
    return state


def intent_classifier(state: AgentState) -> AgentState:
    """Rule-based intent classification with LLM fallback stub."""
    messages = state.get("messages", [])
    last_user_msg = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_user_msg = msg.content.lower()
            break

    # Rule-based fast path
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(kw in last_user_msg for kw in keywords):
            state["current_intent"] = intent
            state["intent_confidence"] = 0.9
            if intent == "handoff":
                state["handoff_triggered"] = True
                state["handoff_reason"] = "explicit_request"
            return state

    # Default to smalltalk for Sprint 1
    state["current_intent"] = "smalltalk"
    state["intent_confidence"] = 0.5
    return state


async def response_generator(state: AgentState) -> AgentState:
    """Generate response via LLMProvider."""
    system_msg = SystemMessage(content=SYSTEM_PROMPT)
    history = [system_msg] + list(state.get("messages", []))

    response = await llm_provider.ainvoke(history)
    state["messages"] = list(state.get("messages", [])) + [response]
    return state


def guardrails_node(state: AgentState) -> AgentState:
    """Stub: Pass-through in Sprint 1. Sprint 2+ adds regex checks + RERA compliance."""
    state["guardrail_violations"] = []
    if not state.get("regeneration_count"):
        state["regeneration_count"] = 0
    return state


def memory_update(state: AgentState) -> AgentState:
    """Stub: In Sprint 2+ will persist to Redis + Qdrant."""
    return state


def _route_after_guardrails(state: AgentState) -> str:
    violations = state.get("guardrail_violations", [])
    regen_count = state.get("regeneration_count", 0)
    if violations and any(v.startswith("blocked_topic") for v in violations) and regen_count < 2:
        return "response_generator"
    return "memory_update"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("memory_loader", memory_loader)
    graph.add_node("intent_classifier", intent_classifier)
    graph.add_node("response_generator", response_generator)
    graph.add_node("guardrails_node", guardrails_node)
    graph.add_node("memory_update", memory_update)

    graph.set_entry_point("memory_loader")
    graph.add_edge("memory_loader", "intent_classifier")
    graph.add_edge("intent_classifier", "response_generator")
    graph.add_edge("response_generator", "guardrails_node")
    graph.add_conditional_edges(
        "guardrails_node",
        _route_after_guardrails,
        {"response_generator": "response_generator", "memory_update": "memory_update"},
    )
    graph.add_edge("memory_update", END)

    return graph


compiled_graph = build_graph().compile()


async def run_turn(state: AgentState) -> AgentState:
    """Main entrypoint for processing a single conversation turn."""
    result: AgentState = await compiled_graph.ainvoke(state)
    return result
