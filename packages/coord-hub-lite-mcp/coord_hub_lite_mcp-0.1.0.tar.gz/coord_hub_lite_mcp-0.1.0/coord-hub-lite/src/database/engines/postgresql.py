"""
PostgreSQL database engine implementation.

Provides async PostgreSQL support with connection pooling
and JSONB query capabilities.
"""

import asyncpg
import json
from typing import Any, Dict, List, Optional, Tuple
from . import DatabaseEngine


class PostgreSQLEngine(DatabaseEngine):
    """PostgreSQL database engine with async support."""
    
    def __init__(self, connection_string: str):
        """Initialize PostgreSQL engine."""
        super().__init__(connection_string)
        self._pool = None
        self._prepared_statements = {}
    
    async def connect(self) -> None:
        """Establish PostgreSQL connection with pool."""
        self._pool = await asyncpg.create_pool(
            self.connection_string,
            min_size=5,
            max_size=20,
            max_queries=50000,
            max_inactive_connection_lifetime=300
        )
    
    async def disconnect(self) -> None:
        """Close PostgreSQL connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None
    
    def is_connected(self) -> bool:
        """Check if connected to PostgreSQL."""
        return self._pool is not None
    
    async def execute(self, query: str, *args) -> None:
        """Execute a query without returning results."""
        if not self._pool:
            raise RuntimeError("Not connected to database")
        
        async with self._pool.acquire() as conn:
            await conn.execute(query, *args)
    
    async def execute_many(self, query: str, args_list: List[Tuple]) -> None:
        """Execute a query multiple times with different parameters."""
        if not self._pool:
            raise RuntimeError("Not connected to database")
        
        async with self._pool.acquire() as conn:
            # PostgreSQL uses executemany for batch operations
            await conn.executemany(query, args_list)
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Execute query and fetch one result."""
        if not self._pool:
            raise RuntimeError("Not connected to database")
        
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            if row:
                return dict(row)
            return None
    
    async def fetch_all(self, query: str, *args) -> List[Dict[str, Any]]:
        """Execute query and fetch all results."""
        if not self._pool:
            raise RuntimeError("Not connected to database")
        
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def begin_transaction(self) -> None:
        """Begin a database transaction."""
        if not self._pool:
            raise RuntimeError("Not connected to database")
        
        # For transactions, we need to manage connection manually
        # This is a simplified approach - in production, you'd want
        # to track the transaction connection
        self._transaction_conn = await self._pool.acquire()
        self._transaction = self._transaction_conn.transaction()
        await self._transaction.start()
    
    async def commit_transaction(self) -> None:
        """Commit the current transaction."""
        if hasattr(self, '_transaction') and self._transaction:
            await self._transaction.commit()
            await self._pool.release(self._transaction_conn)
            self._transaction = None
            self._transaction_conn = None
    
    async def rollback_transaction(self) -> None:
        """Rollback the current transaction."""
        if hasattr(self, '_transaction') and self._transaction:
            await self._transaction.rollback()
            await self._pool.release(self._transaction_conn)
            self._transaction = None
            self._transaction_conn = None
    
    async def json_query(self, table: str, column: str, path: str, value: Any) -> List[Dict[str, Any]]:
        """
        Query JSONB data using PostgreSQL operators.
        
        Args:
            table: Table name
            column: JSONB column name
            path: JSON path (e.g., "name" for top-level, "items.0.id" for nested)
            value: Value to match
        
        Returns:
            List of matching rows
        """
        if not self._pool:
            raise RuntimeError("Not connected to database")
        
        # PostgreSQL uses ->> operator for JSONB text extraction
        # For simple paths, we use direct access
        if '.' not in path and not path.startswith('$'):
            query = f"SELECT * FROM {table} WHERE {column}->>${'$1'} = $2"
            return await self.fetch_all(query, path, str(value))
        else:
            # For complex paths, use jsonb_path_query
            json_path = path if path.startswith('$') else f'$.{path}'
            query = f"SELECT * FROM {table} WHERE jsonb_path_query_first({column}, ${1}) = $2"
            
            # Convert value to JSONB format
            if isinstance(value, str):
                jsonb_value = f'"{value}"'
            else:
                jsonb_value = json.dumps(value)
            
            return await self.fetch_all(query, json_path, jsonb_value)
    
    async def prepare_statement(self, name: str, query: str) -> None:
        """Prepare a statement for repeated execution."""
        if not self._pool:
            raise RuntimeError("Not connected to database")
        
        async with self._pool.acquire() as conn:
            stmt = await conn.prepare(query)
            self._prepared_statements[name] = stmt