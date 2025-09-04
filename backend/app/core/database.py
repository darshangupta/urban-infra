from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import os

# For local development, use SQLite if PostgreSQL is not available
database_url = settings.DATABASE_URL or settings.db_url

# Check if we're in development mode and PostgreSQL is not available
if settings.DEBUG and "postgresql" in database_url:
    try:
        engine = create_engine(database_url, echo=settings.DEBUG)
        # Test connection
        with engine.connect():
            pass
    except Exception:
        # Fall back to SQLite for local development
        database_url = "sqlite:///./urban_infra.db"
        print(f"PostgreSQL not available, using SQLite: {database_url}")

# Create database engine
engine = create_engine(
    database_url,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False} if "sqlite" in database_url else {},
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database initialization
async def init_db():
    """Initialize database and create tables"""
    # Import all models here to ensure they are registered with SQLAlchemy
    from app.models import scenario
    
    # Create all tables
    Base.metadata.create_all(bind=engine)