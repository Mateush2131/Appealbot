from enum import Enum

class TicketStatus(str, Enum):
    """Ticket statuses"""
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class TicketType(str, Enum):
    """Ticket types"""
    QUESTION = "QUESTION"
    COMPLAINT = "COMPLAINT"
    SUGGESTION = "SUGGESTION"

class TicketPriority(str, Enum):
    """Ticket priorities"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"