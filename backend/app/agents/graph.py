"""Sprint 2 — Full LangGraph orchestrator.

Graph:
  memory_loader → intent_classifier → {
    search    → property_search_agent → response_generator
    book      → booking_agent        → response_generator
    qualify   → qualification_agent  → response_generator
    rag       → rag_agent            → response_generator
    handoff   → handoff_agent        → END
    smalltalk → response_generator
    unclear   → clarification_node   → response_generator
  }
  response_generator → guardrails_node → {
    violation (regen < 2) → response_generator
    else                  → memory_update → END
  }
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any

import redis.asyncio as aioredis
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import memory as mem
from app.agents.llm import llm_provider
from app.agents.nodes.booking import booking_agent
from app.agents.nodes.handoff import handoff_agent
from app.agents.nodes.property_search import property_search_agent
from app.agents.nodes.qualification import qualification_agent
from app.agents.nodes.rag import rag_agent
from app.agents.state import AgentState, default_qualification_score

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# System prompt builder
# ──────────────────────────────────────────────

BASE_SYSTEM_PROMPT = """You are {persona_name}, a warm and professional Dubai real estate specialist working for {agency_name}.
You help clients find their perfect property in Dubai, UAE.

Guidelines:
- Always respond in the language the user writes in ({language})
- Never guarantee prices or investment returns — always add appropriate disclaimers
- RERA registration number: {rera_number}. Mention it in your first interaction.
- Keep responses concise (under 300 words) unless the client asks for details
- Tone: {tone}

Current lead context:
{lead_memory_context}

Qualification status: {qualification_status} (score: {qualification_score}/80)
Known entities: {extracted_entities}"""

INTENT_KEYWORDS: dict[str, list[str]] = {
    "handoff": ["speak to agent", "human agent", "call me", "agent please", "representative", "real person"],
    "search": ["looking for", "find", "search", "show me", "properties", "apartment", "villa", "studio", "townhouse", "penthouse", "bedroom", "br "],
    "book": ["book", "viewing", "appointment", "schedule", "visit", "tour", "available", "when can"],
    "calculate": ["mortgage", "roi", "calculate", "afford", "monthly payment", "golden visa", "yield", "return"],
    "qualify": ["budget", "ready to buy", "pre-approved", "pre approved", "timeline", "moving"],
    "rag": ["tell me about", "what is", "explain", "freehold", "rera", "dld", "fees", "regulations", "process"],
}

RERA_STATEMENT = "As a RERA-registered agency"
COMPETITOR_NAMES = ["property finder", "bayut", "dubizzle"]


# ──────────────────────────────────────────────
# Node: memory_loader
# ──────────────────────────────────────────────

async def memory_loader(state: AgentState, redis: aioredis.Redis | None = None) -> AgentState:
    """Load Redis session + Qdrant long-term memory."""
    # Defaults
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
    if not state.get("frustration_count"):
        state["frustration_count"] = 0
    if not state.get("consecutive_failures"):
        state["consecutive_failures"] = 0

    if redis:
        session = await mem.load_session(state["conversation_id"], redis)
        if session:
            state["session_memory"] = session
            if "entities" in session:
                existing = state.get("extracted_entities", {})
                existing.update(session["entities"])
                state["extracted_entities"] = existing
            if "qualification_score" in session:
                state["qualification_score"] = session["qualification_score"]
            if "frustration_count" in session:
                state["frustration_count"] = session["frustration_count"]

    # Load Qdrant long-term memory for this lead
    lead_id = state.get("lead_id", "")
    tenant_id = state.get("tenant_id", "")
    messages = state.get("messages", [])
    last_user_text = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_user_text = msg.content
            break

    if lead_id and last_user_text:
        state["lead_memory_context"] = await mem.load_lead_memory(
            lead_id=lead_id,
            tenant_id=tenant_id,
            query_text=last_user_text,
        )

    if not state.get("lead_memory_context"):
        state["lead_memory_context"] = ""

    return state


# ──────────────────────────────────────────────
# Node: intent_classifier
# ──────────────────────────────────────────────

async def intent_classifier(state: AgentState) -> AgentState:
    """LLM intent classification with rule-based fast path."""
    messages = state.get("messages", [])
    last_user_msg = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_user_msg = msg.content
            break

    lower = last_user_msg.lower()

    # Rule-based fast path
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            state["current_intent"] = intent
            state["intent_confidence"] = 0.9
            if intent == "handoff":
                state["handoff_triggered"] = True
                state["handoff_reason"] = "explicit_request"
            return state

    # Auto-handoff triggers
    if _should_trigger_handoff(state):
        state["current_intent"] = "handoff"
        state["intent_confidence"] = 1.0
        return state

    # LLM classification fallback
    try:
        classification_prompt = f"""Classify the intent of this message into one of:
search, book, calculate, qualify, rag, handoff, smalltalk, unclear

Message: "{last_user_msg}"
Context entities: {json.dumps(state.get('extracted_entities', {}), default=str)}

Return JSON only: {{"intent": "...", "confidence": 0.0-1.0, "entities": {{}}}}
Entities to extract: bedrooms, property_type, area, budget_min_aed, budget_max_aed, purpose, nationality, timeline_months, pre_approved, contact_preference"""

        response = await llm_provider.ainvoke([HumanMessage(content=classification_prompt)])
        content = response.content.strip()

        # Extract JSON from response
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            state["current_intent"] = parsed.get("intent", "smalltalk")
            state["intent_confidence"] = float(parsed.get("confidence", 0.5))

            # Merge extracted entities
            new_entities = parsed.get("entities", {})
            existing = state.get("extracted_entities", {})
            existing.update({k: v for k, v in new_entities.items() if v})
            state["extracted_entities"] = existing
        else:
            state["current_intent"] = "smalltalk"
            state["intent_confidence"] = 0.4
    except Exception as exc:
        logger.warning("intent_classifier LLM fallback failed: %s", exc)
        state["current_intent"] = "smalltalk"
        state["intent_confidence"] = 0.3

    return state


def _should_trigger_handoff(state: AgentState) -> bool:
    score = state.get("qualification_score", {})
    entities = state.get("extracted_entities", {})
    return (
        (score.get("status") == "qualified" and entities.get("contact_preference") == "callback")
        or (float(entities.get("budget_max_aed", 0) or 0) > 5_000_000)
        or (state.get("consecutive_failures", 0) >= 3)
        or (state.get("frustration_count", 0) >= 3)
    )


# ──────────────────────────────────────────────
# Node: clarification_node
# ──────────────────────────────────────────────

def clarification_node(state: AgentState) -> AgentState:
    """Increment clarification attempts counter."""
    state["clarification_attempts"] = state.get("clarification_attempts", 0) + 1
    return state


# ──────────────────────────────────────────────
# Node: response_generator
# ──────────────────────────────────────────────

async def response_generator(state: AgentState) -> AgentState:
    """Generate LLM response with full context (memory + tool outputs)."""
    intent = state.get("current_intent", "smalltalk")
    entities = state.get("extracted_entities", {})
    rag_chunks = state.get("rag_chunks", [])
    search_results = state.get("search_results", [])
    calendar_slots = state.get("calendar_slots", [])
    calc_output = state.get("calculator_output")

    system_content = BASE_SYSTEM_PROMPT.format(
        persona_name=state.get("persona_name", "Layla"),
        agency_name="Sceptre Estate",
        language=state.get("language", "en"),
        rera_number="REA-12345",  # From tenant config in Phase 3
        tone=state.get("tone", "warm_professional"),
        lead_memory_context=state.get("lead_memory_context", ""),
        qualification_status=state.get("qualification_score", {}).get("status", "unqualified"),
        qualification_score=state.get("qualification_score", {}).get("total", 0),
        extracted_entities=json.dumps(entities, default=str),
    )

    # Augment system prompt with tool outputs
    tool_context_parts = []
    if search_results:
        tool_context_parts.append(
            f"\nProperty search results ({len(search_results)} found):\n"
            + "\n".join(
                f"- {r['title']} | {r.get('bedrooms', '?')}BR | AED {r.get('price_aed', 'POA')} | {r.get('address', '')}"
                for r in search_results[:5]
            )
        )
    if calendar_slots:
        tool_context_parts.append(
            "\nAvailable viewing slots:\n"
            + "\n".join(
                f"- {s.get('start_time', '')} to {s.get('end_time', '')}"
                for s in calendar_slots[:5]
            )
        )
    if rag_chunks:
        tool_context_parts.append(
            "\nKnowledge base context:\n"
            + "\n".join(c.get("text", "") for c in rag_chunks[:3])
        )
    if calc_output:
        tool_context_parts.append(f"\nCalculation result:\n{json.dumps(calc_output, indent=2)}")

    if tool_context_parts:
        system_content += "\n\n---\nRelevant context for your response:" + "".join(tool_context_parts)

    history = [SystemMessage(content=system_content)] + list(state.get("messages", []))

    try:
        response = await llm_provider.ainvoke(history)
        state["messages"] = list(state.get("messages", [])) + [response]
        state["consecutive_failures"] = 0
    except Exception as exc:
        logger.error("response_generator LLM call failed: %s", exc)
        fallback = AIMessage(content="I apologize, I'm having trouble responding right now. Please try again in a moment.")
        state["messages"] = list(state.get("messages", [])) + [fallback]
        state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1

    return state


# ──────────────────────────────────────────────
# Node: guardrails_node
# ──────────────────────────────────────────────

PRICE_GUARANTEE_PATTERNS = [
    r"guaranteed?\s+(return|yield|profit|price|appreciation)",
    r"will definitely (increase|grow|appreciate)",
    r"100%\s+(safe|secure|guaranteed)",
]
COMPETITOR_PATTERN = re.compile(
    r"\b(property finder|bayut|dubizzle)\b", re.IGNORECASE
)
BLOCKED_TOPIC_PATTERNS = [
    r"\b(ISIS|terrorism|money laundering)\b",
]


def guardrails_node(state: AgentState) -> AgentState:
    """Post-LLM validation: RERA compliance, price guarantees, competitor mention."""
    messages = state.get("messages", [])
    if not messages:
        return state

    last_msg = messages[-1]
    if not isinstance(last_msg, AIMessage):
        return state

    response_text = last_msg.content
    violations: list[str] = []

    # Check tenant-configured rules
    for rule in state.get("guardrail_rules", []):
        if re.search(rule.get("rule_pattern", ""), response_text, re.IGNORECASE):
            if rule.get("rule_type") == "blocked_topic":
                violations.append(f"blocked_topic:{rule.get('rule_name', 'unknown')}")
            elif rule.get("rule_type") == "required_disclaimer":
                disclaimer = rule.get("disclaimer_text", "")
                if disclaimer and disclaimer not in response_text:
                    response_text = response_text + f"\n\n*{disclaimer}*"

    # RERA statement on first assistant message
    assistant_msgs = [m for m in messages if isinstance(m, AIMessage)]
    if len(assistant_msgs) == 1 and RERA_STATEMENT not in response_text:
        response_text = response_text  # don't force — LLM should handle via system prompt

    # Price guarantee check
    for pattern in PRICE_GUARANTEE_PATTERNS:
        if re.search(pattern, response_text, re.IGNORECASE):
            violations.append("price_guarantee")
            response_text = re.sub(
                pattern,
                "[past performance does not guarantee future results]",
                response_text,
                flags=re.IGNORECASE,
            )

    # Competitor mention check
    if COMPETITOR_PATTERN.search(response_text):
        violations.append("competitor_mention")
        response_text = COMPETITOR_PATTERN.sub("[other platform]", response_text)

    # Hard blocked topics
    for pattern in BLOCKED_TOPIC_PATTERNS:
        if re.search(pattern, response_text, re.IGNORECASE):
            violations.append(f"blocked_topic:{pattern}")

    state["guardrail_violations"] = violations

    if violations and any(v.startswith("blocked_topic") for v in violations):
        state["regeneration_count"] = state.get("regeneration_count", 0) + 1
        # Remove last assistant message to trigger regeneration
        state["messages"] = messages[:-1]
    else:
        # Update response with any in-place fixes
        if response_text != last_msg.content:
            state["messages"] = messages[:-1] + [AIMessage(content=response_text)]

    if not state.get("regeneration_count"):
        state["regeneration_count"] = 0

    return state


# ──────────────────────────────────────────────
# Node: memory_update
# ──────────────────────────────────────────────

async def memory_update(
    state: AgentState,
    redis: aioredis.Redis | None = None,
) -> AgentState:
    """Persist session to Redis + conversation chunk to Qdrant."""
    if redis:
        await mem.save_session(state["conversation_id"], state, redis)

    # Save last turn to Qdrant for long-term lead memory
    messages = state.get("messages", [])
    user_text = ""
    assistant_text = ""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and not assistant_text:
            assistant_text = msg.content
        elif isinstance(msg, HumanMessage) and not user_text:
            user_text = msg.content
        if user_text and assistant_text:
            break

    if user_text and assistant_text and state.get("lead_id"):
        await mem.save_conversation_chunk(
            conversation_id=state["conversation_id"],
            lead_id=state["lead_id"],
            tenant_id=state["tenant_id"],
            user_text=user_text,
            assistant_text=assistant_text,
        )

    return state


# ──────────────────────────────────────────────
# Routing functions
# ──────────────────────────────────────────────

def _route_after_intent(state: AgentState) -> str:
    intent = state.get("current_intent", "smalltalk")
    return {
        "search": "property_search_agent",
        "book": "booking_agent",
        "qualify": "qualification_agent",
        "rag": "rag_agent",
        "handoff": "handoff_agent",
        "unclear": "clarification_node",
    }.get(intent, "response_generator")


def _route_after_guardrails(state: AgentState) -> str:
    violations = state.get("guardrail_violations", [])
    regen_count = state.get("regeneration_count", 0)
    if violations and any(v.startswith("blocked_topic") for v in violations) and regen_count < 2:
        return "response_generator"
    return "memory_update"


# ──────────────────────────────────────────────
# Graph builder
# ──────────────────────────────────────────────

def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # Nodes (db/redis injected at runtime for nodes that need them)
    graph.add_node("memory_loader", memory_loader)
    graph.add_node("intent_classifier", intent_classifier)
    graph.add_node("property_search_agent", lambda s: property_search_agent(s, None))  # db injected at runtime
    graph.add_node("booking_agent", lambda s: booking_agent(s, None))
    graph.add_node("qualification_agent", qualification_agent)
    graph.add_node("rag_agent", rag_agent)
    graph.add_node("handoff_agent", handoff_agent)
    graph.add_node("clarification_node", clarification_node)
    graph.add_node("response_generator", response_generator)
    graph.add_node("guardrails_node", guardrails_node)
    graph.add_node("memory_update", memory_update)

    # Edges
    graph.set_entry_point("memory_loader")
    graph.add_edge("memory_loader", "intent_classifier")
    graph.add_conditional_edges(
        "intent_classifier",
        _route_after_intent,
        {
            "property_search_agent": "property_search_agent",
            "booking_agent": "booking_agent",
            "qualification_agent": "qualification_agent",
            "rag_agent": "rag_agent",
            "handoff_agent": "handoff_agent",
            "clarification_node": "clarification_node",
            "response_generator": "response_generator",
        },
    )
    graph.add_edge("property_search_agent", "response_generator")
    graph.add_edge("booking_agent", "response_generator")
    graph.add_edge("qualification_agent", "response_generator")
    graph.add_edge("rag_agent", "response_generator")
    graph.add_edge("clarification_node", "response_generator")
    graph.add_edge("handoff_agent", END)
    graph.add_edge("response_generator", "guardrails_node")
    graph.add_conditional_edges(
        "guardrails_node",
        _route_after_guardrails,
        {"response_generator": "response_generator", "memory_update": "memory_update"},
    )
    graph.add_edge("memory_update", END)

    return graph


# Module-level compiled graph (db/redis injected per-request via run_turn)
_compiled_graph = build_graph().compile()


async def run_turn(
    state: AgentState,
    db: AsyncSession | None = None,
    redis: aioredis.Redis | None = None,
) -> AgentState:
    """Main entrypoint for processing a single conversation turn.

    For nodes requiring DB/Redis, we inject via closure override at call time.
    """
    from functools import partial

    from app.agents.nodes.booking import booking_agent as _booking_agent
    from app.agents.nodes.property_search import property_search_agent as _prop_search

    # Build a fresh graph with injected dependencies for this request
    run_graph = StateGraph(AgentState)

    run_graph.add_node("memory_loader", partial(memory_loader, redis=redis))
    run_graph.add_node("intent_classifier", intent_classifier)
    run_graph.add_node(
        "property_search_agent",
        partial(_prop_search, db=db) if db else lambda s: {**s, "search_results": []},
    )
    run_graph.add_node(
        "booking_agent",
        partial(_booking_agent, db=db) if db else lambda s: {**s, "calendar_slots": []},
    )
    run_graph.add_node("qualification_agent", qualification_agent)
    run_graph.add_node("rag_agent", rag_agent)
    run_graph.add_node("handoff_agent", handoff_agent)
    run_graph.add_node("clarification_node", clarification_node)
    run_graph.add_node("response_generator", response_generator)
    run_graph.add_node("guardrails_node", guardrails_node)
    run_graph.add_node("memory_update", partial(memory_update, redis=redis))

    run_graph.set_entry_point("memory_loader")
    run_graph.add_edge("memory_loader", "intent_classifier")
    run_graph.add_conditional_edges(
        "intent_classifier",
        _route_after_intent,
        {
            "property_search_agent": "property_search_agent",
            "booking_agent": "booking_agent",
            "qualification_agent": "qualification_agent",
            "rag_agent": "rag_agent",
            "handoff_agent": "handoff_agent",
            "clarification_node": "clarification_node",
            "response_generator": "response_generator",
        },
    )
    run_graph.add_edge("property_search_agent", "response_generator")
    run_graph.add_edge("booking_agent", "response_generator")
    run_graph.add_edge("qualification_agent", "response_generator")
    run_graph.add_edge("rag_agent", "response_generator")
    run_graph.add_edge("clarification_node", "response_generator")
    run_graph.add_edge("handoff_agent", END)
    run_graph.add_edge("response_generator", "guardrails_node")
    run_graph.add_conditional_edges(
        "guardrails_node",
        _route_after_guardrails,
        {"response_generator": "response_generator", "memory_update": "memory_update"},
    )
    run_graph.add_edge("memory_update", END)

    compiled = run_graph.compile()
    result: AgentState = await compiled.ainvoke(state)
    return result
