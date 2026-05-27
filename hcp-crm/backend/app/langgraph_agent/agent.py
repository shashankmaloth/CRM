"""
LangGraph Agent for HCP CRM.

Architecture fix: SQLAlchemy Session objects cannot be serialized by LangGraph's
checkpointer. Solution: db session is passed as a closure variable into each node
function at graph-build time, NOT stored in the state dict.

The graph is built fresh per request (lightweight — no checkpointing needed).
"""
import logging
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

from app.langgraph_agent.llm_service import llm_service
from app.langgraph_agent.tools import (
    log_interaction_tool,
    edit_interaction_tool,
    get_interaction_history_tool,
    suggest_next_action_tool,
    summarize_interactions_tool,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Agent State — NO db session here (avoids serialization errors)
# ─────────────────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    """
    Serializable state that flows through LangGraph nodes.
    db session is intentionally excluded — injected via closure instead.
    """
    user_message: str
    intent: Optional[str]
    hcp_name: Optional[str]
    interaction_id: Optional[int]
    tool_result: Optional[dict]
    response_message: str
    suggested_actions: Optional[list]
    steps: list


# ─────────────────────────────────────────────────────────────────────────────
# Graph Builder — creates a fresh graph with db injected via closure
# ─────────────────────────────────────────────────────────────────────────────

def build_agent_graph(db: Session) -> StateGraph:
    """
    Build and compile the LangGraph workflow for a single request.
    The db session is captured in each node's closure — never stored in state.

    Graph flow:
        START → classify_intent → [conditional route] → execute_* → END
    """

    # ── Node 1: Classify Intent ──────────────────────────────────────────────
    def classify_intent_node(state: AgentState) -> AgentState:
        logger.info("[Agent] Classifying intent...")
        try:
            intent_data = llm_service.understand_intent(state["user_message"])
        except Exception as e:
            logger.error(f"[Agent] Intent classification failed: {e}")
            intent_data = {
                "intent": "log_interaction",
                "hcp_name": None,
                "interaction_id": None,
                "confidence": 0.5,
            }

        return {
            **state,
            "intent": intent_data.get("intent", "log_interaction"),
            "hcp_name": intent_data.get("hcp_name"),
            "interaction_id": intent_data.get("interaction_id"),
            "steps": state["steps"] + [{
                "node": "classify_intent",
                "intent": intent_data.get("intent"),
                "hcp_name": intent_data.get("hcp_name"),
                "confidence": intent_data.get("confidence", 0.5),
            }],
        }

    # ── Routing function ─────────────────────────────────────────────────────
    def route_to_tool(state: AgentState) -> str:
        intent = state.get("intent") or "log_interaction"
        routing_map = {
            "log_interaction": "execute_log_interaction",
            "edit_interaction": "execute_edit_interaction",
            "get_history": "execute_get_history",
            "suggest_actions": "execute_suggest_actions",
            "summarize": "execute_summarize",
            "general": "execute_log_interaction",
        }
        target = routing_map.get(intent, "execute_log_interaction")
        logger.info(f"[Agent] Routing intent '{intent}' → {target}")
        return target

    # ── Node 2: Log Interaction ──────────────────────────────────────────────
    def execute_log_interaction_node(state: AgentState) -> AgentState:
        logger.info("[Agent] Executing LogInteractionTool")
        try:
            result = log_interaction_tool(state["user_message"], db)
        except Exception as e:
            logger.error(f"[LogInteractionTool] Error: {e}", exc_info=True)
            result = {"status": "error", "message": str(e)}

        new_steps = state["steps"] + [{"node": "execute_log_interaction", "result": result.get("status")}]

        if result.get("status") == "success":
            interaction = result["interaction"]
            response = (
                f"✅ Interaction logged successfully!\n\n"
                f"**HCP:** {interaction.get('hcp_name', 'N/A')}\n"
                f"**Hospital:** {interaction.get('hospital', 'N/A')}\n"
                f"**Products:** {interaction.get('products', 'N/A')}\n"
                f"**Sentiment:** {interaction.get('sentiment', 'N/A')}\n\n"
                f"**Summary:** {interaction.get('summary', 'N/A')}\n\n"
                f"*Interaction ID: {interaction.get('id')}*"
            )
            # Generate follow-up suggestions
            suggestions = []
            try:
                if interaction.get("hcp_name"):
                    suggestions = llm_service.suggest_next_actions(interaction)
            except Exception as e:
                logger.warning(f"[Agent] Suggestions failed (non-fatal): {e}")

            return {
                **state,
                "tool_result": result,
                "response_message": response,
                "suggested_actions": suggestions,
                "steps": new_steps,
            }
        else:
            return {
                **state,
                "tool_result": result,
                "response_message": f"❌ Failed to log interaction: {result.get('message', 'Unknown error')}",
                "steps": new_steps,
            }

    # ── Node 3: Edit Interaction ─────────────────────────────────────────────
    def execute_edit_interaction_node(state: AgentState) -> AgentState:
        logger.info("[Agent] Executing EditInteractionTool")

        if not state.get("interaction_id"):
            return {
                **state,
                "response_message": (
                    "I need an interaction ID to edit. "
                    "Please specify which interaction to update "
                    "(e.g., 'Edit interaction #5, change follow-up to next Friday')."
                ),
                "steps": state["steps"] + [{"node": "execute_edit_interaction", "result": "missing_id"}],
            }

        try:
            extracted = llm_service.extract_interaction(state["user_message"])
            updates = {k: v for k, v in extracted.items() if v is not None and k != "summary"}
            result = edit_interaction_tool(state["interaction_id"], updates, db)
        except Exception as e:
            logger.error(f"[EditInteractionTool] Error: {e}", exc_info=True)
            result = {"status": "error", "message": str(e)}

        if result.get("status") == "success":
            response = f"✅ Interaction #{state['interaction_id']} updated successfully!"
        else:
            response = f"❌ {result.get('message', 'Update failed')}"

        return {
            **state,
            "tool_result": result,
            "response_message": response,
            "steps": state["steps"] + [{"node": "execute_edit_interaction", "result": result.get("status")}],
        }

    # ── Node 4: Get History ──────────────────────────────────────────────────
    def execute_get_history_node(state: AgentState) -> AgentState:
        logger.info("[Agent] Executing GetInteractionHistoryTool")
        hcp_name = state.get("hcp_name") or "Unknown"

        try:
            result = get_interaction_history_tool(hcp_name, db)
        except Exception as e:
            logger.error(f"[GetInteractionHistoryTool] Error: {e}", exc_info=True)
            result = {"status": "error", "count": 0, "interactions": [], "message": str(e)}

        if result.get("status") == "success" and result.get("count", 0) > 0:
            interactions = result["interactions"]
            lines = []
            for i, item in enumerate(interactions[:5], 1):
                date_str = (item.get("datetime") or item.get("created_at") or "")[:10] or "N/A"
                lines.append(
                    f"{i}. **{item.get('interaction_type', 'Interaction')}** on {date_str} — "
                    f"{item.get('products', 'No products')} — Sentiment: {item.get('sentiment', 'N/A')}"
                )
            response = (
                f"📋 Found **{result['count']} interactions** with {hcp_name}:\n\n"
                + "\n".join(lines)
                + (f"\n\n*...and {result['count'] - 5} more*" if result["count"] > 5 else "")
            )
        else:
            response = f"No interactions found for **{hcp_name}**."

        return {
            **state,
            "tool_result": result,
            "response_message": response,
            "steps": state["steps"] + [{"node": "execute_get_history", "result": result.get("status")}],
        }

    # ── Node 5: Suggest Actions ──────────────────────────────────────────────
    def execute_suggest_actions_node(state: AgentState) -> AgentState:
        logger.info("[Agent] Executing SuggestNextActionTool")
        hcp_name = state.get("hcp_name") or "Unknown"

        try:
            result = suggest_next_action_tool(hcp_name, db)
        except Exception as e:
            logger.error(f"[SuggestNextActionTool] Error: {e}", exc_info=True)
            result = {
                "status": "error",
                "suggestions": ["Schedule a follow-up meeting", "Send product literature"],
                "message": str(e),
            }

        suggestions = result.get("suggestions", [])
        suggestions_text = "\n".join([f"• {s}" for s in suggestions])
        response = f"💡 **Suggested next actions for {hcp_name}:**\n\n{suggestions_text}"

        return {
            **state,
            "tool_result": result,
            "response_message": response,
            "suggested_actions": suggestions,
            "steps": state["steps"] + [{"node": "execute_suggest_actions", "result": result.get("status")}],
        }

    # ── Node 6: Summarize ────────────────────────────────────────────────────
    def execute_summarize_node(state: AgentState) -> AgentState:
        logger.info("[Agent] Executing SummarizeInteractionsTool")
        hcp_name = state.get("hcp_name") or "Unknown"

        try:
            result = summarize_interactions_tool(hcp_name, db)
        except Exception as e:
            logger.error(f"[SummarizeInteractionsTool] Error: {e}", exc_info=True)
            result = {"status": "error", "message": str(e)}

        if result.get("status") == "success":
            stats = result.get("sentiment_breakdown", {})
            products = ", ".join(result.get("products_discussed", [])) or "None"
            response = (
                f"📊 **Interaction Summary for {hcp_name}**\n\n"
                f"**Total Interactions:** {result.get('total_interactions', 0)}\n"
                f"**Products Discussed:** {products}\n"
                f"**Sentiment:** ✅ {stats.get('positive', 0)} positive | "
                f"⚪ {stats.get('neutral', 0)} neutral | "
                f"❌ {stats.get('negative', 0)} negative\n\n"
                f"**AI Analysis:**\n{result.get('summary', 'N/A')}"
            )
        else:
            response = result.get("message", "Could not generate summary.")

        return {
            **state,
            "tool_result": result,
            "response_message": response,
            "steps": state["steps"] + [{"node": "execute_summarize", "result": result.get("status")}],
        }

    # ── Assemble the graph ───────────────────────────────────────────────────
    workflow = StateGraph(AgentState)

    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("execute_log_interaction", execute_log_interaction_node)
    workflow.add_node("execute_edit_interaction", execute_edit_interaction_node)
    workflow.add_node("execute_get_history", execute_get_history_node)
    workflow.add_node("execute_suggest_actions", execute_suggest_actions_node)
    workflow.add_node("execute_summarize", execute_summarize_node)

    workflow.set_entry_point("classify_intent")

    workflow.add_conditional_edges(
        "classify_intent",
        route_to_tool,
        {
            "execute_log_interaction": "execute_log_interaction",
            "execute_edit_interaction": "execute_edit_interaction",
            "execute_get_history": "execute_get_history",
            "execute_suggest_actions": "execute_suggest_actions",
            "execute_summarize": "execute_summarize",
        },
    )

    workflow.add_edge("execute_log_interaction", END)
    workflow.add_edge("execute_edit_interaction", END)
    workflow.add_edge("execute_get_history", END)
    workflow.add_edge("execute_suggest_actions", END)
    workflow.add_edge("execute_summarize", END)

    return workflow.compile()


# ─────────────────────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────────────────────

def run_agent(user_message: str, db: Session) -> dict:
    """
    Build and run the LangGraph agent for a single request.

    A fresh graph is compiled per request so the db session is safely
    captured in each node's closure without touching LangGraph state.

    Args:
        user_message: Natural language input from the user
        db: SQLAlchemy database session (injected by FastAPI)

    Returns:
        dict with response message, extracted data, interaction_id,
        suggested_actions, and agent_steps
    """
    logger.info(f"[Agent] Processing: {user_message[:100]}...")

    # Build graph with db captured in closures
    graph = build_agent_graph(db)

    # Initial state — fully serializable
    initial_state: AgentState = {
        "user_message": user_message,
        "intent": None,
        "hcp_name": None,
        "interaction_id": None,
        "tool_result": None,
        "response_message": "",
        "suggested_actions": None,
        "steps": [],
    }

    try:
        final_state = graph.invoke(initial_state)
    except Exception as e:
        logger.error(f"[Agent] Graph execution failed: {e}", exc_info=True)
        raise RuntimeError(f"Agent execution failed: {e}") from e

    # Safely extract interaction id from tool result
    tool_result = final_state.get("tool_result") or {}
    interaction = tool_result.get("interaction") if isinstance(tool_result, dict) else None
    interaction_id = interaction.get("id") if isinstance(interaction, dict) else None

    return {
        "message": final_state.get("response_message") or "Request processed.",
        "extracted_data": interaction,
        "interaction_id": interaction_id,
        "suggested_actions": final_state.get("suggested_actions"),
        "agent_steps": final_state.get("steps", []),
    }
