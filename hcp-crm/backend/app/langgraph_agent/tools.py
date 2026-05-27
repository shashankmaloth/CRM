"""
LangGraph Tools for HCP CRM Agent.
Each tool handles a specific CRM operation with LLM assistance.
"""
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.models.interaction import Interaction
from app.langgraph_agent.llm_service import llm_service

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Tool 1: LogInteractionTool
# ─────────────────────────────────────────────────────────────────────────────

def log_interaction_tool(raw_text: str, db: Session) -> dict:
    """
    Tool 1: LogInteractionTool
    
    Accepts raw natural language text, uses LLM to extract structured data,
    generates a summary, and saves the interaction to the database.
    
    Args:
        raw_text: Natural language description of the interaction
        db: SQLAlchemy database session
    
    Returns:
        dict with saved interaction data and AI-generated fields
    """
    logger.info(f"[LogInteractionTool] Processing: {raw_text[:100]}...")

    # Step 1: Use LLM to extract structured data
    extracted = llm_service.extract_interaction(raw_text)
    logger.info(f"[LogInteractionTool] Extracted: {extracted}")

    # Step 2: Parse datetime fields safely
    interaction_datetime = None
    follow_up_date = None

    if extracted.get("datetime"):
        try:
            interaction_datetime = datetime.fromisoformat(
                extracted["datetime"].replace("Z", "+00:00")
            )
        except (ValueError, AttributeError):
            interaction_datetime = None

    if extracted.get("follow_up_date"):
        try:
            follow_up_date = datetime.fromisoformat(
                extracted["follow_up_date"].replace("Z", "+00:00")
            )
        except (ValueError, AttributeError):
            follow_up_date = None

    # Step 3: Create and save the interaction record
    interaction = Interaction(
        hcp_name=extracted.get("hcp_name") or "Unknown HCP",
        specialty=extracted.get("specialty"),
        hospital=extracted.get("hospital"),
        interaction_type=extracted.get("interaction_type"),
        datetime=interaction_datetime,
        products=extracted.get("products"),
        notes=extracted.get("notes") or raw_text,
        summary=extracted.get("summary"),
        sentiment=extracted.get("sentiment", "neutral"),
        follow_up_date=follow_up_date,
    )

    db.add(interaction)
    db.commit()
    db.refresh(interaction)

    logger.info(f"[LogInteractionTool] Saved interaction ID: {interaction.id}")
    return {
        "tool": "LogInteractionTool",
        "status": "success",
        "interaction": interaction.to_dict(),
        "message": f"Interaction logged successfully with ID {interaction.id}"
    }


# ─────────────────────────────────────────────────────────────────────────────
# Tool 2: EditInteractionTool
# ─────────────────────────────────────────────────────────────────────────────

def edit_interaction_tool(interaction_id: int, updates: dict, db: Session) -> dict:
    """
    Tool 2: EditInteractionTool
    
    Fetches an existing interaction by ID, applies updates, and saves.
    Supports partial updates — only provided fields are changed.
    
    Args:
        interaction_id: ID of the interaction to update
        updates: Dictionary of fields to update
        db: SQLAlchemy database session
    
    Returns:
        dict with updated interaction data
    """
    logger.info(f"[EditInteractionTool] Editing interaction ID: {interaction_id}")

    # Fetch existing record
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        return {
            "tool": "EditInteractionTool",
            "status": "error",
            "message": f"Interaction with ID {interaction_id} not found"
        }

    # Apply updates for each provided field
    updatable_fields = [
        "hcp_name", "specialty", "hospital", "interaction_type",
        "products", "notes", "summary", "sentiment"
    ]

    for field in updatable_fields:
        if field in updates and updates[field] is not None:
            setattr(interaction, field, updates[field])

    # Handle datetime fields separately
    if "datetime" in updates and updates["datetime"]:
        try:
            interaction.datetime = datetime.fromisoformat(
                str(updates["datetime"]).replace("Z", "+00:00")
            )
        except (ValueError, AttributeError):
            pass

    if "follow_up_date" in updates and updates["follow_up_date"]:
        try:
            interaction.follow_up_date = datetime.fromisoformat(
                str(updates["follow_up_date"]).replace("Z", "+00:00")
            )
        except (ValueError, AttributeError):
            pass

    db.commit()
    db.refresh(interaction)

    logger.info(f"[EditInteractionTool] Updated interaction ID: {interaction.id}")
    return {
        "tool": "EditInteractionTool",
        "status": "success",
        "interaction": interaction.to_dict(),
        "message": f"Interaction {interaction_id} updated successfully"
    }


# ─────────────────────────────────────────────────────────────────────────────
# Tool 3: GetInteractionHistoryTool
# ─────────────────────────────────────────────────────────────────────────────

def get_interaction_history_tool(hcp_name: str, db: Session, limit: int = 20) -> dict:
    """
    Tool 3: GetInteractionHistoryTool
    
    Fetches all interactions for a given HCP, sorted by date (newest first).
    Supports partial name matching (case-insensitive).
    
    Args:
        hcp_name: Name of the HCP to search for
        db: SQLAlchemy database session
        limit: Maximum number of records to return
    
    Returns:
        dict with list of interactions sorted by date
    """
    logger.info(f"[GetInteractionHistoryTool] Fetching history for: {hcp_name}")

    # Case-insensitive partial match
    from sqlalchemy import nullslast
    interactions = (
        db.query(Interaction)
        .filter(Interaction.hcp_name.ilike(f"%{hcp_name}%"))
        .order_by(nullslast(Interaction.datetime.desc()), Interaction.created_at.desc())
        .limit(limit)
        .all()
    )

    interaction_list = [i.to_dict() for i in interactions]

    logger.info(f"[GetInteractionHistoryTool] Found {len(interaction_list)} interactions")
    return {
        "tool": "GetInteractionHistoryTool",
        "status": "success",
        "hcp_name": hcp_name,
        "count": len(interaction_list),
        "interactions": interaction_list,
        "message": f"Found {len(interaction_list)} interactions for {hcp_name}"
    }


# ─────────────────────────────────────────────────────────────────────────────
# Tool 4: SuggestNextActionTool
# ─────────────────────────────────────────────────────────────────────────────

def suggest_next_action_tool(hcp_name: str, db: Session) -> dict:
    """
    Tool 4: SuggestNextActionTool
    
    Fetches recent interactions for an HCP and uses LLM to suggest
    follow-up strategies, product pitch ideas, and risk alerts.
    
    Args:
        hcp_name: Name of the HCP
        db: SQLAlchemy database session
    
    Returns:
        dict with AI-generated action suggestions
    """
    logger.info(f"[SuggestNextActionTool] Generating suggestions for: {hcp_name}")

    # Get recent interactions (last 5)
    interactions = (
        db.query(Interaction)
        .filter(Interaction.hcp_name.ilike(f"%{hcp_name}%"))
        .order_by(Interaction.created_at.desc())
        .limit(5)
        .all()
    )

    if not interactions:
        return {
            "tool": "SuggestNextActionTool",
            "status": "warning",
            "hcp_name": hcp_name,
            "suggestions": [
                "Schedule an introductory visit",
                "Research HCP's specialty and prescribing patterns",
                "Prepare product samples and literature"
            ],
            "message": f"No prior interactions found for {hcp_name}. Showing default suggestions."
        }

    # Use most recent interaction for context
    latest = interactions[0].to_dict()
    suggestions = llm_service.suggest_next_actions(latest)

    return {
        "tool": "SuggestNextActionTool",
        "status": "success",
        "hcp_name": hcp_name,
        "based_on_interaction_id": latest["id"],
        "suggestions": suggestions,
        "message": f"Generated {len(suggestions)} action suggestions for {hcp_name}"
    }


# ─────────────────────────────────────────────────────────────────────────────
# Tool 5: SummarizeInteractionsTool
# ─────────────────────────────────────────────────────────────────────────────

def summarize_interactions_tool(hcp_name: str, db: Session) -> dict:
    """
    Tool 5: SummarizeInteractionsTool
    
    Fetches all interactions for an HCP and generates a comprehensive
    AI summary highlighting trends, sentiment, and opportunities.
    
    Args:
        hcp_name: Name of the HCP
        db: SQLAlchemy database session
    
    Returns:
        dict with AI-generated comprehensive summary
    """
    logger.info(f"[SummarizeInteractionsTool] Summarizing interactions for: {hcp_name}")

    interactions = (
        db.query(Interaction)
        .filter(Interaction.hcp_name.ilike(f"%{hcp_name}%"))
        .order_by(Interaction.created_at.asc())
        .all()
    )

    if not interactions:
        return {
            "tool": "SummarizeInteractionsTool",
            "status": "warning",
            "hcp_name": hcp_name,
            "summary": f"No interactions found for {hcp_name}.",
            "stats": {},
            "message": "No interactions to summarize"
        }

    interaction_list = [i.to_dict() for i in interactions]

    # Calculate basic stats
    sentiments = [i["sentiment"] for i in interaction_list if i.get("sentiment")]
    sentiment_counts = {
        "positive": sentiments.count("positive"),
        "neutral": sentiments.count("neutral"),
        "negative": sentiments.count("negative"),
    }

    products_mentioned = set()
    for i in interaction_list:
        if i.get("products"):
            for p in i["products"].split(","):
                products_mentioned.add(p.strip())

    # Generate AI summary
    ai_summary = llm_service.summarize_interactions(interaction_list)

    return {
        "tool": "SummarizeInteractionsTool",
        "status": "success",
        "hcp_name": hcp_name,
        "total_interactions": len(interaction_list),
        "sentiment_breakdown": sentiment_counts,
        "products_discussed": list(products_mentioned),
        "summary": ai_summary,
        "message": f"Summary generated for {len(interaction_list)} interactions with {hcp_name}"
    }
