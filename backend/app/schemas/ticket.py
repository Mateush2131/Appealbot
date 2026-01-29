from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.enums import TicketStatus, TicketType, TicketPriority

class TicketBase(BaseModel):
    """Base schema for ticket"""
    full_name: str = Field(..., min_length=2, max_length=255)
    contact: str = Field(..., min_length=5, max_length=255)
    type: TicketType
    text: str = Field(..., min_length=10)
    priority: TicketPriority = Field(default=TicketPriority.MEDIUM)

class TicketCreate(TicketBase):
    """Schema for creating a ticket"""
    pass

class TicketUpdate(BaseModel):
    """Schema for updating a ticket"""
    status: Optional[TicketStatus] = None
    admin_comment: Optional[str] = None
    priority: Optional[TicketPriority] = None
    assigned_to: Optional[str] = Field(None, max_length=255)

class TicketOut(TicketBase):
    """Schema for outputting a ticket"""
    id: int
    status: TicketStatus
    admin_comment: Optional[str]
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)