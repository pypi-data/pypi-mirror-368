"""
Database session management for async SQLAlchemy.
Provides session factory and context managers.
"""
import os
from typing import AsyncGenerator
from pathlib import Path
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession, 
    create_async_engine, 
    async_sessionmaker
)
from sqlalchemy import text


# Get database URL from environment or use default
# For testing, use SQLite if no DATABASE_URL is set
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite+aiosqlite:///./test.db"  # Use SQLite for local testing
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before use
)

# Create session factory
async_session_maker = async_sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session as async generator.
    Use in FastAPI dependency injection or with async for.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_async_session() -> AsyncSession:
    """
    Get database session as async context manager.
    Use with async with statement.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database (create tables, etc.)"""
    from src.database.models import Base
    from sqlalchemy import text
    
    # Create all tables defined in models
    async with engine.begin() as conn:
        # Import all models to ensure they're registered with Base.metadata
        from src.database.models import Task, Agent, TaskEvent, Plan, AgentSession, AuditLog, SystemMetric
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        
        # Test the connection
        result = await conn.execute(text("SELECT 1"))
        if result.scalar() != 1:
            raise Exception("Database initialization failed - connection test failed")


async def close_db():
    """Close database connections"""
    await engine.dispose()


# ---- Runtime reconfiguration helpers ----

def build_sqlite_url(db_file: str) -> str:
    """Build a SQLAlchemy async SQLite URL from a file path.
    
    Args:
        db_file: Path to the SQLite database file
    Returns:
        SQLAlchemy async URL string
    """
    abs_path = Path(db_file).expanduser().resolve()
    # Four slashes after scheme for absolute paths on POSIX
    return f"sqlite+aiosqlite:///{abs_path}"


def get_current_database_url() -> str:
    """Return the current engine URL as string (with password if any)."""
    try:
        return engine.url.render_as_string(hide_password=False)
    except Exception:
        return os.getenv("DATABASE_URL", "")


async def reconfigure_database(new_url: str) -> None:
    """Hot-swap the database engine and session factory at runtime.
    
    This disposes the existing engine, creates a new engine using the
    provided URL, rebuilds the session maker, persists the URL to the
    environment, initializes schema (create_all), and validates connectivity.
    
    Args:
        new_url: SQLAlchemy async URL to connect to
    """
    global engine, async_session_maker, DATABASE_URL

    # Update module-level URL and environment for future imports
    DATABASE_URL = new_url
    os.environ["DATABASE_URL"] = new_url

    # Dispose existing connections
    try:
        await engine.dispose()
    except Exception:
        # Ignore dispose failures; we'll replace engine anyway
        pass

    # Create a new engine
    engine = create_async_engine(
        new_url,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )

    # Rebuild the session maker
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    # Ensure schema exists
    await init_db()

    # Quick connectivity check
    async with async_session_maker() as _session:
        await _session.execute(text("SELECT 1"))