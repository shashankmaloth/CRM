"""
FastAPI application entry point for HCP CRM.
Configures middleware, routes, and startup events.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database.connection import create_tables
from app.routes import interactions, chat

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()

# ─────────────────────────────────────────────────────────────────────────────
# FastAPI App Initialization
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="HCP CRM API",
    description="AI-first CRM for Healthcare Professional Interaction Management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─────────────────────────────────────────────────────────────────────────────
# CORS Middleware
# ─────────────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────────────────
# Startup Event
# ─────────────────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup."""
    logger.info("Starting HCP CRM API...")
    try:
        create_tables()
        logger.info("Database tables created/verified.")
    except Exception as e:
        logger.error(
            f"⚠️  Database connection failed at startup: {e}\n"
            "Check your DATABASE_URL in backend/.env and ensure PostgreSQL is running."
        )
        # Don't crash — let individual requests fail with a clear DB error
    logger.info(f"Using primary LLM model: {settings.PRIMARY_MODEL}")
    logger.info("HCP CRM API is ready!")

# ─────────────────────────────────────────────────────────────────────────────
# Register Routes
# ─────────────────────────────────────────────────────────────────────────────

app.include_router(interactions.router)
app.include_router(chat.router)

# ─────────────────────────────────────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint — shows DB and Groq API status."""
    from app.database.connection import get_engine
    from sqlalchemy import text as sa_text
    db_status = "unknown"
    try:
        with get_engine().connect() as conn:
            conn.execute(sa_text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)[:80]}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "model": settings.PRIMARY_MODEL,
        "database": db_status,
        "groq_key_set": bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY != "your_groq_api_key_here"),
    }


@app.get("/", tags=["Root"])
def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to HCP CRM API",
        "docs": "/docs",
        "health": "/health",
    }
