import os
import time
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.exc import OperationalError

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Fix for Neon DB compatibility: Replace postgres:// with postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create database engine with connection pooling and keepalive settings
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,  # Check connection health before use
    pool_recycle=300,  # Recycle connections every 5 minutes
    pool_size=20,  # Number of connections to maintain
    max_overflow=30,  # Additional connections when pool is exhausted
    connect_args={
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
        "sslmode": "require",  # Force SSL
    },
)


def create_db_and_tables():
    """Create all database tables defined in SQLModel models."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency function that yields a database session for FastAPI with retry logic."""
    max_retries = 3
    retry_delay = 1  # seconds

    for attempt in range(max_retries):
        try:
            with Session(engine) as session:
                yield session
                return  # Success, exit the function
        except OperationalError as e:
            if attempt < max_retries - 1:
                print(f"Database connection failed (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"Retrying in {retry_delay} second(s)...")
                time.sleep(retry_delay)
            else:
                print(f"Database connection failed after {max_retries} attempts: {e}")
                raise  # Re-raise the exception after all retries exhausted
