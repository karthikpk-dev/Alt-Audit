from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from typing import Generator
from .config import settings

# Database URL from config
DATABASE_URL = settings.database_url

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,  # Recycle connections every 5 minutes
    pool_size=10,      # Number of connections to maintain
    max_overflow=20,   # Additional connections that can be created
    echo=False  # Set to True for SQL query logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db() -> Generator:
    """
    Dependency to get database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        try:
            db.close()
        except Exception:
            # Ignore errors when closing the session
            pass


def create_tables():
    """
    Create all tables in the database.
    This is used for initial setup and testing.
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Drop all tables in the database.
    This is used for testing and cleanup.
    """
    Base.metadata.drop_all(bind=engine)
