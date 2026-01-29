from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import tickets_router
from app.models import ticket  # Import model for table creation

# Create FastAPI instance
app = FastAPI(
    title="Support Service API for Educational Organizations",
    description="Module for receiving and processing user requests",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration (for frontend connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(tickets_router)

@app.get("/", tags=["Info"])
def root():
    """API health check"""
    return {
        "message": "Support Service API is running",
        "docs": "/docs",
        "endpoints": {
            "create_ticket": "POST /tickets/",
            "get_tickets": "GET /tickets/",
            "get_ticket": "GET /tickets/{id}",
            "update_ticket": "PATCH /tickets/{id}",
            "delete_ticket": "DELETE /tickets/{id}",
            "stats": "GET /tickets/stats"
        }
    }

@app.get("/health", tags=["Info"])
def health_check():
    """Service health check"""
    return {"status": "healthy"}