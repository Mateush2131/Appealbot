from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from app import models, schemas
from app.enums import TicketStatus, TicketType, TicketPriority

def create_ticket(db: Session, ticket: schemas.TicketCreate) -> models.Ticket:
    """Create a new ticket"""
    db_ticket = models.Ticket(
        full_name=ticket.full_name,
        contact=ticket.contact,
        type=ticket.type,
        text=ticket.text,
        priority=ticket.priority
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def get_tickets(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    status: Optional[TicketStatus] = None,
    type: Optional[TicketType] = None,
    priority: Optional[TicketPriority] = None,
    search: Optional[str] = None
) -> list[models.Ticket]:
    """Get list of tickets with filtering"""
    query = db.query(models.Ticket)
    
    # Apply filters
    if status:
        query = query.filter(models.Ticket.status == status)
    if type:
        query = query.filter(models.Ticket.type == type)
    if priority:
        query = query.filter(models.Ticket.priority == priority)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                models.Ticket.full_name.ilike(search_term),
                models.Ticket.text.ilike(search_term),
                models.Ticket.contact.ilike(search_term)
            )
        )
    
    # Return with pagination
    return query.order_by(models.Ticket.created_at.desc()).offset(skip).limit(limit).all()

def get_ticket(db: Session, ticket_id: int) -> Optional[models.Ticket]:
    """Get ticket by ID"""
    return db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

def update_ticket(
    db: Session,
    ticket_id: int,
    ticket_update: schemas.TicketUpdate
) -> Optional[models.Ticket]:
    """Update a ticket"""
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        return None
    
    # Update only provided fields
    update_data = ticket_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(ticket, key, value)
    
    db.commit()
    db.refresh(ticket)
    return ticket

def delete_ticket(db: Session, ticket_id: int) -> Optional[models.Ticket]:
    """Delete a ticket"""
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        return None
    
    db.delete(ticket)
    db.commit()
    return ticket

def get_ticket_count(db: Session) -> int:
    """Get total number of tickets"""
    return db.query(models.Ticket).count()