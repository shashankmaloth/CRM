"""
Pydantic schemas for request/response validation.
Compatible with Pydantic v2.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class InteractionCreate(BaseModel):
    """Schema for creating a new interaction via structured form."""
    hcp_name: str = Field(..., min_length=1, description="Full name of the HCP")
    specialty: Optional[str] = None
    hospital: Optional[str] = None
    interaction_type: Optional[str] = None
    datetime: Optional[datetime] = None
    products: Optional[str] = None
    notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "hcp_name": "Dr. Priya Rao",
                "specialty": "Endocrinology",
                "hospital": "Apollo Hospital",
                "interaction_type": "Visit",
                "datetime": "2026-04-30T10:00:00",
                "products": "Metformin XR, Januvia",
                "notes": "Doctor showed interest in new diabetes drug.",
                "follow_up_date": "2026-05-07T10:00:00"
            }
        }
    }


class InteractionUpdate(BaseModel):
    """Schema for updating an existing interaction (all fields optional)."""
    hcp_name: Optional[str] = None
    specialty: Optional[str] = None
    hospital: Optional[str] = None
    interaction_type: Optional[str] = None
    datetime: Optional[datetime] = None
    products: Optional[str] = None
    notes: Optional[str] = None
    summary: Optional[str] = None
    sentiment: Optional[str] = None
    follow_up_date: Optional[datetime] = None


class InteractionResponse(BaseModel):
    """Schema for interaction API responses."""
    id: int
    hcp_name: str
    specialty: Optional[str] = None
    hospital: Optional[str] = None
    interaction_type: Optional[str] = None
    datetime: Optional[datetime] = None
    products: Optional[str] = None
    notes: Optional[str] = None
    summary: Optional[str] = None
    sentiment: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    """Schema for conversational chat input."""
    message: str = Field(..., min_length=1, description="Natural language interaction description")
    session_id: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Met Dr. Rao at Apollo Hospital today. Discussed Januvia for diabetes. She was very interested. Follow up next Monday."
            }
        }
    }


class ChatResponse(BaseModel):
    """Schema for chat API responses."""
    message: str
    extracted_data: Optional[Any] = None
    interaction_id: Optional[int] = None
    suggested_actions: Optional[List[str]] = None
    agent_steps: Optional[List[Any]] = None
