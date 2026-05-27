"""
Service layer for interaction CRUD operations.
Bridges routes and database/agent layers.
"""
import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.interaction import Interaction
from app.schemas.interaction import InteractionCreate, InteractionUpdate

logger = logging.getLogger(__name__)


class InteractionService:
    """Handles all database operations for interactions."""

    @staticmethod
    def create_interaction(db: Session, data: InteractionCreate) -> Interaction:
        """
        Create a new interaction from structured form data.
        No LLM involved — direct save from validated schema.
        """
        interaction = Interaction(
            hcp_name=data.hcp_name,
            specialty=data.specialty,
            hospital=data.hospital,
            interaction_type=data.interaction_type,
            datetime=data.datetime,
            products=data.products,
            notes=data.notes,
            follow_up_date=data.follow_up_date,
            sentiment="neutral",  # Default for structured form
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        logger.info(f"[Service] Created interaction ID: {interaction.id}")
        return interaction

    @staticmethod
    def get_interaction(db: Session, interaction_id: int) -> Optional[Interaction]:
        """Fetch a single interaction by ID."""
        return db.query(Interaction).filter(Interaction.id == interaction_id).first()

    @staticmethod
    def get_interactions_by_hcp(
        db: Session, hcp_name: str, skip: int = 0, limit: int = 50
    ) -> List[Interaction]:
        """
        Fetch all interactions for a given HCP.
        Uses case-insensitive partial match.
        """
        return (
            db.query(Interaction)
            .filter(Interaction.hcp_name.ilike(f"%{hcp_name}%"))
            .order_by(Interaction.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_all_interactions(
        db: Session, skip: int = 0, limit: int = 100
    ) -> List[Interaction]:
        """Fetch all interactions with pagination."""
        return (
            db.query(Interaction)
            .order_by(Interaction.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_interaction(
        db: Session, interaction_id: int, data: InteractionUpdate
    ) -> Optional[Interaction]:
        """
        Update an existing interaction with partial data.
        Only non-None fields are updated.
        """
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if not interaction:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(interaction, field, value)

        db.commit()
        db.refresh(interaction)
        logger.info(f"[Service] Updated interaction ID: {interaction.id}")
        return interaction

    @staticmethod
    def delete_interaction(db: Session, interaction_id: int) -> bool:
        """Delete an interaction by ID."""
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if not interaction:
            return False
        db.delete(interaction)
        db.commit()
        logger.info(f"[Service] Deleted interaction ID: {interaction_id}")
        return True

    @staticmethod
    def get_dashboard_stats(db: Session) -> dict:
        """
        Compute dashboard statistics for the frontend.
        Returns counts and breakdowns.
        """
        from sqlalchemy import func

        total = db.query(func.count(Interaction.id)).scalar()
        positive = db.query(func.count(Interaction.id)).filter(
            Interaction.sentiment == "positive"
        ).scalar()
        negative = db.query(func.count(Interaction.id)).filter(
            Interaction.sentiment == "negative"
        ).scalar()
        neutral = db.query(func.count(Interaction.id)).filter(
            Interaction.sentiment == "neutral"
        ).scalar()

        # Upcoming follow-ups
        upcoming = db.query(func.count(Interaction.id)).filter(
            Interaction.follow_up_date >= datetime.now()
        ).scalar()

        # Recent interactions (last 5)
        recent = (
            db.query(Interaction)
            .order_by(Interaction.created_at.desc())
            .limit(5)
            .all()
        )

        return {
            "total_interactions": total,
            "sentiment_breakdown": {
                "positive": positive,
                "neutral": neutral,
                "negative": negative,
            },
            "upcoming_followups": upcoming,
            "recent_interactions": [i.to_dict() for i in recent],
        }
