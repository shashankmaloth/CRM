"""
Database connection and session management using SQLAlchemy.
Engine is created lazily so it always reads the current .env value.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Base class for all ORM models — must be module-level
Base = declarative_base()

# Module-level references, populated on first use
_engine = None
_SessionLocal = None


def get_engine():
    """Return (and lazily create) the SQLAlchemy engine."""
    global _engine
    if _engine is None:
        from app.config import get_settings
        settings = get_settings()
        _engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            echo=settings.DEBUG,
        )
    return _engine


def get_session_factory():
    """Return (and lazily create) the session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine(),
        )
    return _SessionLocal


def get_db():
    """
    FastAPI dependency that provides a database session.
    Ensures the session is closed after each request.
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables defined in models."""
    from app.models import interaction  # noqa: F401 — registers the model
    Base.metadata.create_all(bind=get_engine())
