from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app import crud, schemas
from app.database import get_db
from app.enums import TicketStatus, TicketType, TicketPriority

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.post("/", response_model=schemas.TicketOut, summary="Create a ticket")
def create_ticket(
    ticket: schemas.TicketCreate,
    db: Session = Depends(get_db)
):
    """Create a new ticket from user"""
    return crud.create_ticket(db, ticket)

@router.get("/", response_model=List[schemas.TicketOut], summary="Get tickets list")
def read_tickets(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records per page"),
    status: Optional[TicketStatus] = Query(None, description="Filter by status"),
    type: Optional[TicketType] = Query(None, description="Filter by type"),
    priority: Optional[TicketPriority] = Query(None, description="Filter by priority"),
    search: Optional[str] = Query(None, description="Search in text, name or contact"),
    db: Session = Depends(get_db)
):
    """Get list of tickets with filtering and pagination"""
    return crud.get_tickets(
        db,
        skip=skip,
        limit=limit,
        status=status,
        type=type,
        priority=priority,
        search=search
    )

@router.get("/stats", summary="Get tickets statistics")
def get_stats(db: Session = Depends(get_db)):
    """Get statistics about tickets"""
    total = crud.get_ticket_count(db)
    
    # Get count by status
    from app.models import Ticket
    status_counts = {
        status.value: db.query(Ticket).filter(Ticket.status == status).count()
        for status in TicketStatus
    }
    
    return {
        "total": total,
        "statuses": status_counts
    }

@router.get("/{ticket_id}", response_model=schemas.TicketOut, summary="Get ticket by ID")
def read_ticket(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about specific ticket"""
    ticket = crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.patch("/{ticket_id}", response_model=schemas.TicketOut, summary="Update a ticket")
def edit_ticket(
    ticket_id: int,
    ticket_update: schemas.TicketUpdate,
    db: Session = Depends(get_db)
):
    """Update ticket (status, comment, priority, assignment)"""
    ticket = crud.update_ticket(db, ticket_id, ticket_update)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.delete("/{ticket_id}", summary="Delete a ticket")
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Delete a ticket (for administrators)"""
    ticket = crud.delete_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"message": "Ticket successfully deleted"}