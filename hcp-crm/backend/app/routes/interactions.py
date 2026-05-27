"""
FastAPI routes for HCP interactions.
Handles structured form submissions and CRUD operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.connection import get_db
from app.schemas.interaction import (
    InteractionCreate,
    InteractionUpdate,
    InteractionResponse,
)
from app.services.interaction_service import InteractionService

router = APIRouter(prefix="/api/interactions", tags=["Interactions"])


@router.post("/log-interaction", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
def log_interaction(data: InteractionCreate, db: Session = Depends(get_db)):
    """
    POST /api/interactions/log-interaction
    
    Create a new interaction from structured form data.
    This endpoint is used by the "Structured Form" tab.
    """
    interaction = InteractionService.create_interaction(db, data)
    return interaction


@router.get("/interactions/{hcp_name}", response_model=List[InteractionResponse])
def get_interactions_by_hcp(hcp_name: str, db: Session = Depends(get_db)):
    """
    GET /api/interactions/interactions/{hcp_name}
    
    Fetch all interactions for a specific HCP.
    Supports partial name matching (case-insensitive).
    """
    interactions = InteractionService.get_interactions_by_hcp(db, hcp_name)
    return interactions


@router.get("/", response_model=List[InteractionResponse])
def get_all_interactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    GET /api/interactions/
    
    Fetch all interactions with pagination.
    Used for displaying the interaction table on the dashboard.
    """
    interactions = InteractionService.get_all_interactions(db, skip, limit)
    return interactions


@router.get("/{interaction_id}", response_model=InteractionResponse)
def get_interaction(interaction_id: int, db: Session = Depends(get_db)):
    """
    GET /api/interactions/{interaction_id}
    
    Fetch a single interaction by ID.
    """
    interaction = InteractionService.get_interaction(db, interaction_id)
    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interaction with ID {interaction_id} not found"
        )
    return interaction


@router.put("/edit-interaction/{interaction_id}", response_model=InteractionResponse)
def edit_interaction(
    interaction_id: int,
    data: InteractionUpdate,
    db: Session = Depends(get_db)
):
    """
    PUT /api/interactions/edit-interaction/{interaction_id}
    
    Update an existing interaction.
    Supports partial updates — only provided fields are changed.
    """
    interaction = InteractionService.update_interaction(db, interaction_id, data)
    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interaction with ID {interaction_id} not found"
        )
    return interaction


@router.delete("/{interaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interaction(interaction_id: int, db: Session = Depends(get_db)):
    """
    DELETE /api/interactions/{interaction_id}
    
    Delete an interaction by ID.
    """
    success = InteractionService.delete_interaction(db, interaction_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interaction with ID {interaction_id} not found"
        )
    return None


@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    GET /api/interactions/dashboard/stats
    
    Fetch dashboard statistics including:
    - Total interactions
    - Sentiment breakdown
    - Upcoming follow-ups
    - Recent interactions
    """
    stats = InteractionService.get_dashboard_stats(db)
    return stats
