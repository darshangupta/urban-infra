from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import os

# Always use DATABASE_URL (prioritize Supabase)
database_url = settings.db_url

print(f"Using database: {database_url[:50]}{'...' if len(database_url) > 50 else ''}")

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