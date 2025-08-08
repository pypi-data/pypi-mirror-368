"""
SQLite database engine implementation.

Provides async SQLite support with JSON query capabilities
and WAL mode for better concurrency.
"""

import aiosqlite
import json
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse
from . import DatabaseEngine


class SQLiteEngine(DatabaseEngine):
    """SQLite database engine with async support."""
    
    def __init__(self, connection_string: str):
        """Initialize SQLite engine."""
        super().__init__(connection_string)
        # Parse connection string to get database path
        parsed = urlparse(connection_string)
        if parsed.netloc:
            # Network location specified
            self.db_path = f"{parsed.netloc}{parsed.path}"
        else:
            # No network location, path-only
            path = parsed.path
            if path == '/:memory:':
                self.db_path = ':memory:'
            elif path.startswith('/') and len(path) > 1:
                # Absolute path (sqlite:///abs/path)
                self.db_path = path
            else:
                # Relative path (sqlite://relpath)
                self.db_path = path.lstrip('/')
        self._in_transaction = False
    
    async def connect(self) -> None:
        """Establish SQLite connection with WAL mode."""
        self._connection = await aiosqlite.connect(self.db_path)
        self._connection.row_factory = aiosqlite.Row
        
        # Enable WAL mode for better concurrency (not available for :memory: databases)
        if self.db_path != ':memory:':
            await self._connection.execute("PRAGMA journal_mode=WAL")
            await self._connection.commit()
    
    async def disconnect(self) -> None:
        """Close SQLite connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None
    
    def is_connected(self) -> bool:
        """Check if connected to SQLite."""
        return self._connection is not None
    
    async def execute(self, query: str, *args) -> None:
        """Execute a query without returning results."""
        if not self._connection:
            raise RuntimeError("Not connected to database")
        
        # Handle both single argument and multiple arguments
        if len(args) == 1 and isinstance(args[0], (tuple, list)):
            await self._connection.execute(query, args[0])
        elif args:
            await self._connection.execute(query, args)
        else:
            await self._connection.execute(query)
        
        # Only commit if not in an explicit transaction
        if not self._in_transaction:
            await self._connection.commit()
    
    async def execute_many(self, query: str, args_list: List[Tuple]) -> None:
        """Execute a query multiple times with different parameters."""
        if not self._connection:
            raise RuntimeError("Not connected to database")
        
        await self._connection.executemany(query, args_list)
        
        # Only commit if not in an explicit transaction
        if not self._in_transaction:
            await self._connection.commit()
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Execute query and fetch one result."""
        if not self._connection:
            raise RuntimeError("Not connected to database")
        
        # Handle argument unpacking
        if len(args) == 1 and isinstance(args[0], (tuple, list)):
            cursor = await self._connection.execute(query, args[0])
        elif args:
            cursor = await self._connection.execute(query, args)
        else:
            cursor = await self._connection.execute(query)
        
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    async def fetch_all(self, query: str, *args) -> List[Dict[str, Any]]:
        """Execute query and fetch all results."""
        if not self._connection:
            raise RuntimeError("Not connected to database")
        
        # Handle argument unpacking
        if len(args) == 1 and isinstance(args[0], (tuple, list)):
            cursor = await self._connection.execute(query, args[0])
        elif args:
            cursor = await self._connection.execute(query, args)
        else:
            cursor = await self._connection.execute(query)
        
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def begin_transaction(self) -> None:
        """Begin a database transaction."""
        if not self._connection:
            raise RuntimeError("Not connected to database")
        
        # Store the current isolation level and start explicit transaction
        self._in_transaction = True
        await self._connection.execute("BEGIN")
    
    async def commit_transaction(self) -> None:
        """Commit the current transaction."""
        if not self._connection:
            raise RuntimeError("Not connected to database")
        
        await self._connection.commit()
        self._in_transaction = False
    
    async def rollback_transaction(self) -> None:
        """Rollback the current transaction."""
        if not self._connection:
            raise RuntimeError("Not connected to database")
        
        await self._connection.rollback()
        self._in_transaction = False
    
    async def json_query(self, table: str, column: str, path: str, value: Any) -> List[Dict[str, Any]]:
        """
        Query JSON data using SQLite JSON functions.
        
        Args:
            table: Table name
            column: JSON column name
            path: JSON path (e.g., "$.name" or "$.items[0].id")
            value: Value to match
        
        Returns:
            List of matching rows
        """
        if not self._connection:
            raise RuntimeError("Not connected to database")
        
        # SQLite uses json_extract for JSON queries
        query = f"SELECT * FROM {table} WHERE json_extract({column}, ?) = ?"
        
        # Convert value to JSON string if needed
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        return await self.fetch_all(query, path, value)