"""
FastAPI routes for the AI chat interface.
Integrates LangGraph agent for natural language interaction logging.
"""
import logging
import traceback
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.interaction import ChatRequest, ChatResponse
from app.langgraph_agent.agent import run_agent

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    POST /api/chat/

    Process a natural language message through the LangGraph agent.
    The agent classifies intent, routes to the correct tool, uses LLM
    to extract/process data, saves to DB, and returns a structured response.
    """
    logger.info(f"[Chat] Received message: {request.message[:100]}")
    try:
        result = run_agent(request.message, db)
        logger.info(f"[Chat] Agent completed. Intent steps: {len(result.get('agent_steps', []))}")
        return ChatResponse(
            message=result["message"],
            extracted_data=result.get("extracted_data"),
            interaction_id=result.get("interaction_id"),
            suggested_actions=result.get("suggested_actions"),
            agent_steps=result.get("agent_steps"),
        )
    except Exception as e:
        # Log full traceback server-side for debugging
        logger.error(f"[Chat] Agent failed:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent processing failed: {str(e)}",
        )
