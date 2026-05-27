"""
SQLAlchemy ORM model for HCP Interactions.
Maps to the 'interactions' table in PostgreSQL.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from app.database.connection import Base


class Interaction(Base):
    """
    Represents a logged interaction between a field rep and an HCP.
    """
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # HCP Details
    hcp_name = Column(String(255), nullable=False, index=True)
    specialty = Column(String(255), nullable=True)
    hospital = Column(String(255), nullable=True)

    # Interaction Details
    interaction_type = Column(String(50), nullable=True)  # Visit / Call / Meeting
    datetime = Column(DateTime(timezone=True), nullable=True)
    products = Column(Text, nullable=True)   # Comma-separated or JSON string
    notes = Column(Text, nullable=True)

    # AI-Generated Fields
    summary = Column(Text, nullable=True)    # LLM-generated summary
    sentiment = Column(String(50), nullable=True)  # positive / neutral / negative

    # Follow-up
    follow_up_date = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    def to_dict(self) -> dict:
        """Convert model instance to dictionary for API responses."""
        return {
            "id": self.id,
            "hcp_name": self.hcp_name,
            "specialty": self.specialty,
            "hospital": self.hospital,
            "interaction_type": self.interaction_type,
            "datetime": self.datetime.isoformat() if self.datetime else None,
            "products": self.products,
            "notes": self.notes,
            "summary": self.summary,
            "sentiment": self.sentiment,
            "follow_up_date": self.follow_up_date.isoformat() if self.follow_up_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
