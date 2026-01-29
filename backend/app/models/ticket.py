from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from datetime import datetime
from app.database import Base
from app.enums import TicketStatus, TicketType, TicketPriority

class Ticket(Base):
    """Model for storing support tickets"""
    __tablename__ = "tickets"

    # Basic fields
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # User information
    full_name = Column(String(255), nullable=False)
    contact = Column(String(255), nullable=False)
    
    # Ticket content
    type = Column(Enum(TicketType), nullable=False)
    text = Column(Text, nullable=False)
    
    # Status and comments
    status = Column(Enum(TicketStatus), default=TicketStatus.NEW)
    admin_comment = Column(Text, nullable=True)
    
    # Additional fields (enhancements)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM)
    assigned_to = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<Ticket(id={self.id}, status={self.status}, type={self.type})>"