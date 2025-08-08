"""
Advanced session management service with pooling and lifecycle control.
Provides factory pattern, connection pooling optimization, and metrics.
"""
import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import time

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import OperationalError, DatabaseError
from sqlalchemy import text


class SessionState(Enum):
    """Session lifecycle states."""
    LAZY = "lazy"
    ACTIVE = "active"
    IN_TRANSACTION = "in_transaction"
    CLOSED = "closed"
    TIMED_OUT = "timed_out"
    ROLLED_BACK = "rolled_back"
    ERROR = "error"


@dataclass
class PoolConfig:
    """Database connection pool configuration."""
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: float = 30.0
    pool_recycle: int = 3600
    pool_pre_ping: bool = True
    echo_pool: bool = False


@dataclass
class SessionMetrics:
    """Session usage metrics."""
    total_sessions_created: int = 0
    total_queries_executed: int = 0
    active_sessions: int = 0
    total_session_time: float = 0.0
    failed_sessions: int = 0
    timed_out_sessions: int = 0


class EnhancedAsyncSession:
    """Enhanced async session with state tracking and metrics."""
    
    def __init__(self, session: AsyncSession, session_id: str):
        self._session = session
        self.session_id = session_id
        self.state = SessionState.ACTIVE
        self.created_at = datetime.now(timezone.utc)
        self.query_count = 0
        self._closed = False
    
    async def execute(self, statement: Any, *args, **kwargs):
        """Execute statement with metrics tracking."""
        if self.state == SessionState.CLOSED:
            raise RuntimeError("Session is closed")
        
        if self.state == SessionState.LAZY:
            self.state = SessionState.ACTIVE
        
        self.query_count += 1
        return await self._session.execute(statement, *args, **kwargs)
    
    async def begin(self):
        """Begin transaction."""
        await self._session.begin()
        self.state = SessionState.IN_TRANSACTION
    
    async def commit(self):
        """Commit transaction."""
        try:
            await self._session.commit()
            if self.state == SessionState.IN_TRANSACTION:
                self.state = SessionState.ACTIVE
        except DatabaseError:
            self.state = SessionState.ROLLED_BACK
            raise
    
    async def rollback(self):
        """Rollback transaction."""
        await self._session.rollback()
        self.state = SessionState.ROLLED_BACK
    
    async def close(self):
        """Close session and cleanup."""
        if not self._closed:
            if self._session is not None:
                await self._session.close()
            self._closed = True
            # Only set to CLOSED if not already in a terminal state
            if self.state not in (SessionState.TIMED_OUT, SessionState.ERROR):
                self.state = SessionState.CLOSED
    
    @property
    def duration(self) -> float:
        """Get session duration in seconds."""
        return (datetime.now(timezone.utc) - self.created_at).total_seconds()


class SessionFactory:
    """Factory for creating database sessions with pooling."""
    
    def __init__(self, engine: AsyncEngine, service: 'SessionService'):
        self._engine = engine
        self._service = service
        self._sessionmaker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
    
    async def create(self) -> EnhancedAsyncSession:
        """Create new session from pool."""
        session_id = str(uuid.uuid4())
        async_session = self._sessionmaker()
        enhanced_session = EnhancedAsyncSession(async_session, session_id)
        
        # Register with service
        self._service._register_session(enhanced_session)
        
        return enhanced_session
    
    def create_lazy(self) -> EnhancedAsyncSession:
        """Create lazy session (connection deferred)."""
        session_id = str(uuid.uuid4())
        # Create session but don't connect yet
        session = EnhancedAsyncSession(None, session_id)
        session.state = SessionState.LAZY
        session._sessionmaker = self._sessionmaker
        
        # Override execute to lazy-init
        original_execute = session.execute
        
        async def lazy_execute(statement, *args, **kwargs):
            if session._session is None:
                session._session = session._sessionmaker()
            return await original_execute(statement, *args, **kwargs)
        
        session.execute = lazy_execute
        self._service._register_session(session)
        
        return session


class SessionService:
    """
    Advanced session management service.
    Handles pooling, lifecycle, metrics, and health checks.
    """
    
    def __init__(
        self,
        database_url: str,
        pool_config: Optional[PoolConfig] = None,
        session_timeout: float = 3600.0  # 1 hour default
    ):
        self.database_url = database_url
        self.pool_config = pool_config or PoolConfig()
        self.session_timeout = session_timeout
        
        # Create engine and initialize components
        self._engine = self._create_engine()
        self._factory = SessionFactory(self._engine, self)
        self._active_sessions: Dict[str, EnhancedAsyncSession] = {}
        self._metrics = SessionMetrics()
        self._cleanup_task = None
        
        # Start cleanup task
        self._start_cleanup_task()
    
    def _create_engine(self) -> AsyncEngine:
        """Create async engine with appropriate pooling configuration."""
        # SQLite doesn't support traditional pooling parameters
        if self.database_url.startswith("sqlite"):
            return create_async_engine(
                self.database_url,
                echo=False,
                pool_recycle=self.pool_config.pool_recycle,
                pool_pre_ping=self.pool_config.pool_pre_ping
            )
        else:
            return create_async_engine(
                self.database_url,
                echo=False,
                pool_size=self.pool_config.pool_size,
                max_overflow=self.pool_config.max_overflow,
                pool_timeout=self.pool_config.pool_timeout,
                pool_recycle=self.pool_config.pool_recycle,
                pool_pre_ping=self.pool_config.pool_pre_ping
            )
    
    def _start_cleanup_task(self):
        """Start background task for session cleanup."""
        async def cleanup_loop():
            while True:
                await asyncio.sleep(60)  # Check every minute
                await self._cleanup_timed_out_sessions()
        
        try:
            loop = asyncio.get_running_loop()
            self._cleanup_task = loop.create_task(cleanup_loop())
        except RuntimeError:
            # No event loop running yet (e.g., during testing)
            self._cleanup_task = None
    
    async def _cleanup_timed_out_sessions(self):
        """Clean up timed out sessions."""
        now = datetime.now(timezone.utc)
        timed_out = []
        
        for session_id, session in self._active_sessions.items():
            if session.duration > self.session_timeout:
                timed_out.append(session_id)
                session.state = SessionState.TIMED_OUT
                await session.close()
                self._metrics.timed_out_sessions += 1
        
        for session_id in timed_out:
            self._active_sessions.pop(session_id, None)
    
    def _register_session(self, session: EnhancedAsyncSession):
        """Register active session."""
        self._active_sessions[session.session_id] = session
        self._metrics.total_sessions_created += 1
        self._metrics.active_sessions = len(self._active_sessions)
    
    def _unregister_session(self, session_id: str):
        """Unregister closed session."""
        if session_id in self._active_sessions:
            session = self._active_sessions.pop(session_id)
            self._metrics.total_session_time += session.duration
            self._metrics.active_sessions = len(self._active_sessions)
    
    async def create_session(self) -> EnhancedAsyncSession:
        """Create new database session."""
        try:
            session = await self._factory.create()
            return session
        except OperationalError as e:
            if "QueuePool limit" in str(e):
                raise OperationalError(
                    "QueuePool limit of size {} overflow {} reached".format(
                        self.pool_config.pool_size,
                        self.pool_config.max_overflow
                    ),
                    None, None
                )
            raise
    
    def get_factory(self) -> SessionFactory:
        """Get session factory for custom session creation."""
        return self._factory
    
    async def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        pool = self._engine.pool
        return {
            "size": pool.size() if hasattr(pool, 'size') else 0,
            "overflow": pool.overflow() if hasattr(pool, 'overflow') else 0,
            "checked_in": pool.checkedin() if hasattr(pool, 'checkedin') else 0,
            "checked_out": pool.checkedout() if hasattr(pool, 'checkedout') else 0,
            "active_sessions": len(self._active_sessions),
            "available_connections": (
                pool.size() - pool.checkedout() 
                if hasattr(pool, 'size') and hasattr(pool, 'checkedout') 
                else 0
            )
        }
    
    def reset_metrics(self):
        """Reset session metrics."""
        self._metrics = SessionMetrics()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get session usage metrics."""
        return {
            "total_sessions_created": self._metrics.total_sessions_created,
            "total_queries_executed": self._calculate_total_queries(),
            "active_sessions": self._metrics.active_sessions,
            "average_session_duration": self._calculate_average_duration(),
            "failed_sessions": self._metrics.failed_sessions,
            "timed_out_sessions": self._metrics.timed_out_sessions
        }
    
    def _calculate_average_duration(self) -> float:
        """Calculate average session duration."""
        if self._metrics.total_sessions_created > 0:
            return self._metrics.total_session_time / self._metrics.total_sessions_created
        return 0.0
    
    def _calculate_total_queries(self) -> int:
        """Calculate total queries including active sessions."""
        total = self._metrics.total_queries_executed
        for session in self._active_sessions.values():
            total += session.query_count
        return total
    
    async def health_check(self) -> bool:
        """Check database connection health."""
        try:
            async with self._engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except OperationalError:
            return False
    
    async def shutdown(self):
        """Shutdown service and cleanup resources."""
        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        # Close all active sessions
        for session in list(self._active_sessions.values()):
            await session.close()
        
        # Dispose engine
        await self._engine.dispose()


# Convenience function for dependency injection
async def get_session_service(
    database_url: Optional[str] = None,
    pool_config: Optional[PoolConfig] = None
) -> SessionService:
    """
    Get or create session service instance.
    Can be used with FastAPI dependency injection.
    """
    if not hasattr(get_session_service, "_instance"):
        url = database_url or "sqlite+aiosqlite:///./db.sqlite"
        get_session_service._instance = SessionService(url, pool_config)
    
    return get_session_service._instance