"""
Connection pool manager for database engines.

Provides a unified interface for connection pooling across
different database engines with health checks and metrics.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from src.database.engines import DatabaseEngine


@dataclass
class PoolConnection:
    """Represents a pooled connection."""
    connection: Any
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)
    in_use: bool = False
    
    def mark_used(self):
        """Mark connection as used."""
        self.last_used = datetime.now()


class ConnectionPoolManager:
    """Manages a pool of database connections."""
    
    def __init__(
        self,
        engine: DatabaseEngine,
        min_size: int = 1,
        max_size: int = 10,
        max_idle_time: int = 3600,
        health_check_interval: int = 60
    ):
        """
        Initialize connection pool manager.
        
        Args:
            engine: Database engine to use
            min_size: Minimum number of connections
            max_size: Maximum number of connections
            max_idle_time: Maximum idle time in seconds
            health_check_interval: Health check interval in seconds
        """
        self.engine = engine
        self.min_size = min_size
        self.max_size = max_size
        self.max_idle_time = max_idle_time
        self.health_check_interval = health_check_interval
        
        self._pool: List[PoolConnection] = []
        self._available: asyncio.Queue = asyncio.Queue()
        self._semaphore = asyncio.Semaphore(max_size)
        self._closed = False
        self._health_check_task = None
        
        # Metrics
        self._total_created = 0
        self._total_destroyed = 0
        self._total_acquisitions = 0
        self._total_releases = 0
    
    async def initialize(self) -> None:
        """Initialize the connection pool."""
        # Create minimum number of connections
        for _ in range(self.min_size):
            conn = await self._create_connection()
            self._pool.append(conn)
            await self._available.put(conn)
        
        # Start health check task
        self._health_check_task = asyncio.create_task(self._health_check_loop())
    
    async def _create_connection(self) -> PoolConnection:
        """Create a new connection."""
        # For SQLite, we create a new engine instance
        # For PostgreSQL, the engine already manages its own pool
        if self.engine.__class__.__name__ == "SQLiteEngine":
            # Create new SQLite connection
            from src.database.engines.sqlite import SQLiteEngine
            new_engine = SQLiteEngine(self.engine.connection_string)
            await new_engine.connect()
            conn = PoolConnection(connection=new_engine)
        else:
            # For PostgreSQL, we'll use the existing pool
            conn = PoolConnection(connection=self.engine)
        
        self._total_created += 1
        return conn
    
    async def acquire(self) -> Any:
        """Acquire a connection from the pool."""
        if self._closed:
            raise RuntimeError("Pool is closed")
        
        # Wait for available slot
        await self._semaphore.acquire()
        
        try:
            # Try to get available connection with timeout
            conn = await asyncio.wait_for(
                self._available.get(),
                timeout=0.1
            )
            conn.in_use = True
            conn.mark_used()
            self._total_acquisitions += 1
            return conn.connection
        except asyncio.TimeoutError:
            # No available connection, create new one if under max
            if len(self._pool) < self.max_size:
                conn = await self._create_connection()
                conn.in_use = True
                self._pool.append(conn)
                self._total_acquisitions += 1
                return conn.connection
            else:
                # Release semaphore and raise timeout
                self._semaphore.release()
                raise asyncio.TimeoutError("No available connections")
    
    async def release(self, connection: Any) -> None:
        """Release a connection back to the pool."""
        # Find the pool connection
        for conn in self._pool:
            if conn.connection == connection:
                conn.in_use = False
                await self._available.put(conn)
                self._semaphore.release()
                self._total_releases += 1
                return
        
        # Connection not found, might be from external source
        self._semaphore.release()
    
    async def close(self) -> None:
        """Close all connections and shutdown pool."""
        self._closed = True
        
        # Cancel health check
        if self._health_check_task:
            self._health_check_task.cancel()
        
        # Close all connections
        for conn in self._pool:
            if hasattr(conn.connection, 'disconnect'):
                await conn.connection.disconnect()
            self._total_destroyed += 1
        
        self._pool.clear()
    
    async def check_health(self) -> bool:
        """Check health of all connections."""
        all_healthy = True
        
        for conn in self._pool:
            if not conn.in_use:
                try:
                    # Simple health check - execute a lightweight query
                    if hasattr(conn.connection, 'fetch_one'):
                        await conn.connection.fetch_one("SELECT 1")
                except Exception:
                    all_healthy = False
                    # Remove unhealthy connection
                    self._pool.remove(conn)
                    self._total_destroyed += 1
                    
                    # Create replacement if below minimum
                    if len(self._pool) < self.min_size:
                        new_conn = await self._create_connection()
                        self._pool.append(new_conn)
                        await self._available.put(new_conn)
        
        return all_healthy
    
    async def _health_check_loop(self) -> None:
        """Background task for periodic health checks."""
        while not self._closed:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self.check_health()
                
                # Clean up idle connections beyond min_size
                now = datetime.now()
                for conn in list(self._pool):
                    if (not conn.in_use and 
                        len(self._pool) > self.min_size and
                        (now - conn.last_used).total_seconds() > self.max_idle_time):
                        
                        self._pool.remove(conn)
                        if hasattr(conn.connection, 'disconnect'):
                            await conn.connection.disconnect()
                        self._total_destroyed += 1
                        
            except asyncio.CancelledError:
                break
            except Exception:
                # Log error in production
                pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get pool metrics."""
        active_connections = sum(1 for conn in self._pool if conn.in_use)
        idle_connections = sum(1 for conn in self._pool if not conn.in_use)
        
        return {
            "total_connections": len(self._pool),
            "active_connections": active_connections,
            "idle_connections": idle_connections,
            "min_size": self.min_size,
            "max_size": self.max_size,
            "total_created": self._total_created,
            "total_destroyed": self._total_destroyed,
            "total_acquisitions": self._total_acquisitions,
            "total_releases": self._total_releases
        }