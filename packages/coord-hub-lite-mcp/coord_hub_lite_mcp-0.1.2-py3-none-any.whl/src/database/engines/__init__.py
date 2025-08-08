"""
Database engine abstraction layer.

Provides a unified interface for SQLite and PostgreSQL databases,
enabling seamless migration from development to production.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union
import os
from urllib.parse import urlparse


class DatabaseEngine(ABC):
    """Abstract base class for database engines."""
    
    def __init__(self, connection_string: str):
        """Initialize engine with connection string."""
        self.connection_string = connection_string
        self._connection = None
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish database connection."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to database."""
        pass
    
    @abstractmethod
    async def execute(self, query: str, *args) -> None:
        """Execute a query without returning results."""
        pass
    
    @abstractmethod
    async def execute_many(self, query: str, args_list: List[Tuple]) -> None:
        """Execute a query multiple times with different parameters."""
        pass
    
    @abstractmethod
    async def fetch_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Execute query and fetch one result."""
        pass
    
    @abstractmethod
    async def fetch_all(self, query: str, *args) -> List[Dict[str, Any]]:
        """Execute query and fetch all results."""
        pass
    
    @abstractmethod
    async def begin_transaction(self) -> None:
        """Begin a database transaction."""
        pass
    
    @abstractmethod
    async def commit_transaction(self) -> None:
        """Commit the current transaction."""
        pass
    
    @abstractmethod
    async def rollback_transaction(self) -> None:
        """Rollback the current transaction."""
        pass
    
    @abstractmethod
    async def json_query(self, table: str, column: str, path: str, value: Any) -> List[Dict[str, Any]]:
        """Query JSON data in a database-specific way."""
        pass


def create_engine(connection_string: str) -> DatabaseEngine:
    """Create appropriate engine based on connection string."""
    parsed = urlparse(connection_string)
    scheme = parsed.scheme.lower()
    
    if scheme == "sqlite":
        from .sqlite import SQLiteEngine
        return SQLiteEngine(connection_string)
    elif scheme in ("postgresql", "postgres"):
        from .postgresql import PostgreSQLEngine
        return PostgreSQLEngine(connection_string)
    else:
        raise ValueError(f"Unsupported database scheme: {scheme}")


def create_engine_from_env() -> DatabaseEngine:
    """Create engine from DATABASE_URL environment variable."""
    database_url = os.environ.get("DATABASE_URL", "sqlite:///coord_hub_lite.db")
    return create_engine(database_url)


class EngineManager:
    """Manages database engine switching at runtime."""
    
    def __init__(self):
        """Initialize engine manager."""
        self.current_engine: Optional[DatabaseEngine] = None
    
    def set_engine(self, connection_string: str) -> None:
        """Set the current engine."""
        self.current_engine = create_engine(connection_string)
    
    async def switch_engine(self, connection_string: str) -> None:
        """Switch to a new engine, closing the old one."""
        if self.current_engine and self.current_engine.is_connected():
            await self.current_engine.disconnect()
        
        self.current_engine = create_engine(connection_string)
        await self.current_engine.connect()