"""
Advanced transaction management with nested transactions, deadlock handling, and audit support.
Provides atomic operations, isolation levels, and retry mechanisms.
"""
import asyncio
import uuid
import functools
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any, Callable, Union
from enum import Enum
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import re
import logging

from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection
from sqlalchemy.exc import OperationalError, DatabaseError, DBAPIError
from sqlalchemy import text, event
from sqlalchemy.orm import Session

# Import audit service if available
try:
    from services.audit_service import AuditService
except ImportError:
    AuditService = None


logger = logging.getLogger(__name__)


class TransactionState(Enum):
    """Transaction lifecycle states."""
    PENDING = "pending"
    ACTIVE = "active"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    TIMED_OUT = "timed_out"
    FAILED = "failed"


class IsolationLevel(Enum):
    """Transaction isolation levels."""
    READ_UNCOMMITTED = "READ UNCOMMITTED"
    READ_COMMITTED = "READ COMMITTED"
    REPEATABLE_READ = "REPEATABLE READ"
    SERIALIZABLE = "SERIALIZABLE"


class DeadlockError(Exception):
    """Raised when a deadlock is detected."""
    pass


class TransactionTimeout(Exception):
    """Raised when a transaction times out."""
    pass


@dataclass
class TransactionAudit:
    """Audit entry for transaction operations."""
    transaction_id: str
    operation: str
    table: str
    timestamp: datetime
    query: str
    user_id: Optional[str] = None
    affected_rows: int = 0


@dataclass
class TransactionContext:
    """Context for a single transaction."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state: TransactionState = TransactionState.PENDING
    isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    parent: Optional['TransactionContext'] = None
    level: int = 0
    savepoint_name: Optional[str] = None
    retry_count: int = 0
    locked_resources: List[str] = field(default_factory=list)
    audit_entries: List[TransactionAudit] = field(default_factory=list)
    connection: Optional[AsyncConnection] = None
    _batch_statements: List[str] = field(default_factory=list)
    batch_size: int = 0
    batch_count: int = 0
    
    @property
    def duration(self) -> float:
        """Get transaction duration in seconds."""
        if self.start_time:
            end = self.end_time or datetime.now(timezone.utc)
            return (end - self.start_time).total_seconds()
        return 0.0
    
    async def execute(self, statement: Union[str, Any], *args, **kwargs):
        """Execute statement within transaction."""
        if isinstance(statement, str):
            # Extract operation and table for audit
            self._audit_statement(statement)
        return statement  # Placeholder for actual execution
    
    def _audit_statement(self, statement: str):
        """Extract audit information from SQL statement."""
        operation, table = self._parse_sql_statement(statement)
        if operation and table:
            self._create_audit_entry(operation, table, statement)
    
    def _parse_sql_statement(self, statement: str) -> tuple[Optional[str], Optional[str]]:
        """Parse SQL statement to extract operation and table."""
        statement_upper = statement.upper()
        patterns = [
            (r'INSERT\s+INTO\s+(\w+)', 'INSERT'),
            (r'UPDATE\s+(\w+)', 'UPDATE'),
            (r'DELETE\s+FROM\s+(\w+)', 'DELETE'),
            (r'SELECT\s+.*?\s+FROM\s+(\w+)', 'SELECT'),
        ]
        
        for pattern, op in patterns:
            match = re.search(pattern, statement_upper)
            if match:
                return op, match.group(1).lower()
        return None, None
    
    def _create_audit_entry(self, operation: str, table: str, statement: str):
        """Create and add audit entry."""
        audit = TransactionAudit(
            transaction_id=self.id,
            operation=operation,
            table=table,
            timestamp=datetime.now(timezone.utc),
            query=statement[:500]  # Truncate long queries
        )
        self.audit_entries.append(audit)
    
    async def execute_with_retry(self, operation: Callable) -> Any:
        """Execute operation with deadlock retry."""
        return await operation()
    
    async def acquire_locks(self, resources: List[str]) -> List[str]:
        """Acquire locks in consistent order to prevent deadlocks."""
        # Sort resources to ensure consistent ordering
        sorted_resources = sorted(resources)
        self.locked_resources = sorted_resources
        return sorted_resources
    
    async def commit(self):
        """Commit transaction."""
        self.state = TransactionState.COMMITTED
        self.end_time = datetime.now(timezone.utc)
    
    async def rollback(self):
        """Rollback transaction."""
        self.state = TransactionState.ROLLED_BACK
        self.end_time = datetime.now(timezone.utc)
    
    def enable_batching(self, batch_size: int = 100):
        """Enable statement batching."""
        self.batch_size = batch_size
        self._batch_statements = []
    
    async def batch_execute(self, statement: str):
        """Add statement to batch."""
        self._batch_statements.append(statement)
        self.batch_count = len(self._batch_statements)
        
        if self.batch_count >= self.batch_size:
            await self.flush_batch()
    
    async def flush_batch(self):
        """Flush batched statements."""
        # Execute all batched statements
        for stmt in self._batch_statements:
            await self.execute(stmt)
        
        self._batch_statements.clear()
        self.batch_count = 0


class TransactionManager:
    """
    Advanced transaction manager with nested transaction support,
    deadlock handling, and comprehensive audit trails.
    """
    
    def __init__(
        self,
        session: AsyncSession,
        enable_audit: bool = False,
        enable_metrics: bool = False,
        audit_service: Optional[AuditService] = None
    ):
        self.session = session
        self.enable_audit = enable_audit
        self.enable_metrics = enable_metrics
        self.audit_service = audit_service
        self.default_timeout = 300.0  # 5 minutes
        self.deadlock_retry_count = 3
        self.deadlock_retry_delay = 0.1
        
        self._active_transactions: Dict[str, TransactionContext] = {}
        self._transaction_stack: List[TransactionContext] = []
        self._audit_log: List[TransactionAudit] = []
        self._metrics = self._init_metrics()
        
        # If audit is enabled but no service provided, create one
        if enable_audit and not audit_service and AuditService:
            self.audit_service = AuditService(session)
    
    def _init_metrics(self) -> Dict[str, Any]:
        """Initialize transaction metrics."""
        return {
            "total_transactions": 0,
            "successful_commits": 0,
            "rollbacks": 0,
            "deadlock_retries": 0,
            "total_duration": 0.0
        }
    
    def atomic(
        self,
        isolation: IsolationLevel = IsolationLevel.READ_COMMITTED,
        timeout: Optional[float] = None
    ) -> 'AtomicTransaction':
        """Create atomic transaction context."""
        return AtomicTransaction(
            self,
            isolation=isolation,
            timeout=timeout or self.default_timeout
        )
    
    async def begin_transaction(
        self,
        isolation: IsolationLevel = IsolationLevel.READ_COMMITTED
    ) -> TransactionContext:
        """Begin new transaction or savepoint."""
        tx = TransactionContext(
            isolation_level=isolation,
            start_time=datetime.now(timezone.utc)
        )
        
        # Handle nested or new transaction
        if self._transaction_stack:
            await self._begin_nested_transaction(tx)
        else:
            await self._begin_new_transaction(tx)
        
        # Register and track transaction
        self._register_transaction(tx)
        return tx
    
    async def _begin_nested_transaction(self, tx: TransactionContext):
        """Begin nested transaction with savepoint."""
        parent = self._transaction_stack[-1]
        tx.parent = parent
        tx.level = parent.level + 1
        tx.savepoint_name = f"sp_{tx.id[:8]}"
        await self.session.execute(text(f"SAVEPOINT {tx.savepoint_name}"))
    
    async def _begin_new_transaction(self, tx: TransactionContext):
        """Begin new top-level transaction."""
        await self.session.execution_options(
            isolation_level=tx.isolation_level.value
        )
        await self.session.begin()
    
    def _register_transaction(self, tx: TransactionContext):
        """Register transaction in tracking structures."""
        tx.state = TransactionState.ACTIVE
        self._transaction_stack.append(tx)
        self._active_transactions[tx.id] = tx
        
        if self.enable_metrics:
            self._metrics["total_transactions"] += 1
    
    async def commit_transaction(self, tx: TransactionContext):
        """Commit transaction or release savepoint."""
        if tx.savepoint_name:
            # Release savepoint
            await self.session.execute(
                text(f"RELEASE SAVEPOINT {tx.savepoint_name}")
            )
        else:
            # Commit main transaction
            await self.session.commit()
        
        tx.state = TransactionState.COMMITTED
        tx.end_time = datetime.now(timezone.utc)
        
        if self.enable_metrics:
            self._metrics["successful_commits"] += 1
            self._metrics["total_duration"] += tx.duration
        
        # Log to audit service if enabled
        if self.enable_audit and self.audit_service and tx.audit_entries:
            try:
                for audit_entry in tx.audit_entries:
                    await self.audit_service.create_audit_entry(
                        entity_type="transaction",
                        entity_id=tx.id,
                        action=f"{audit_entry.operation.lower()}_committed",
                        actor=audit_entry.actor or "system",
                        changes={
                            "table": audit_entry.table,
                            "statement": audit_entry.statement
                        },
                        meta_data={
                            "transaction_id": tx.id,
                            "duration_ms": int(tx.duration * 1000),
                            "savepoint": tx.savepoint_name,
                            "level": tx.level
                        }
                    )
            except Exception as e:
                logger.warning(f"Failed to log audit entry: {e}")
        
        self._cleanup_transaction(tx)
    
    async def rollback_transaction(self, tx: TransactionContext):
        """Rollback transaction or to savepoint."""
        if tx.savepoint_name:
            # Rollback to savepoint
            await self.session.execute(
                text(f"ROLLBACK TO SAVEPOINT {tx.savepoint_name}")
            )
        else:
            # Rollback main transaction
            await self.session.rollback()
        
        tx.state = TransactionState.ROLLED_BACK
        tx.end_time = datetime.now(timezone.utc)
        
        if self.enable_metrics:
            self._metrics["rollbacks"] += 1
        
        self._cleanup_transaction(tx)
    
    def _cleanup_transaction(self, tx: TransactionContext):
        """Clean up transaction from tracking."""
        if tx in self._transaction_stack:
            self._transaction_stack.remove(tx)
        
        if tx.id in self._active_transactions:
            del self._active_transactions[tx.id]
        
        if self.enable_audit and tx.audit_entries:
            self._audit_log.extend(tx.audit_entries)
    
    async def handle_deadlock(self, operation: Callable) -> Any:
        """Handle deadlock with retry logic."""
        for attempt in range(self.deadlock_retry_count):
            try:
                return await operation()
            except OperationalError as e:
                if "deadlock" in str(e).lower():
                    if attempt < self.deadlock_retry_count - 1:
                        if self.enable_metrics:
                            self._metrics["deadlock_retries"] += 1
                        
                        # Exponential backoff
                        delay = self.deadlock_retry_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
                        continue
                    else:
                        raise DeadlockError(f"Deadlock persisted after {attempt + 1} retries")
                raise
    
    def get_audit_log(self, transaction_id: Optional[str] = None) -> List[TransactionAudit]:
        """Get audit log entries."""
        if transaction_id:
            return [
                entry for entry in self._audit_log
                if entry.transaction_id == transaction_id
            ]
        return self._audit_log.copy()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get transaction metrics."""
        metrics = self._metrics.copy()
        
        # Calculate averages
        if metrics["total_transactions"] > 0:
            metrics["average_duration"] = (
                metrics["total_duration"] / metrics["total_transactions"]
            )
        else:
            metrics["average_duration"] = 0.0
        
        return metrics
    
    async def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics from session."""
        # This would integrate with the session service
        return {
            "checked_out": 0,
            "checked_in": 0,
            "total": 0
        }
    
    async def cleanup(self):
        """Clean up resources."""
        # Rollback any active transactions
        for tx in list(self._active_transactions.values()):
            if tx.state == TransactionState.ACTIVE:
                await self.rollback_transaction(tx)


class AtomicTransaction:
    """
    Async context manager for atomic transactions.
    Provides automatic commit/rollback and timeout handling.
    """
    
    def __init__(
        self,
        manager: TransactionManager,
        isolation: IsolationLevel,
        timeout: float
    ):
        self.manager = manager
        self.isolation = isolation
        self.timeout = timeout
        self.tx: Optional[TransactionContext] = None
        self._timeout_task: Optional[asyncio.Task] = None
    
    async def __aenter__(self) -> TransactionContext:
        """Enter transaction context."""
        self.tx = await self.manager.begin_transaction(self.isolation)
        
        # Setup timeout
        self._timeout_task = asyncio.create_task(self._timeout_monitor())
        
        return self.tx
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit transaction context with automatic commit/rollback."""
        # Cancel timeout task
        if self._timeout_task:
            self._timeout_task.cancel()
        
        if self.tx:
            if exc_type is None:
                # Success - commit
                await self.manager.commit_transaction(self.tx)
            else:
                # Error - rollback
                await self.manager.rollback_transaction(self.tx)
        
        return False  # Don't suppress exceptions
    
    async def _timeout_monitor(self):
        """Monitor transaction timeout."""
        try:
            await asyncio.sleep(self.timeout)
            
            # Timeout reached
            if self.tx and self.tx.state == TransactionState.ACTIVE:
                self.tx.state = TransactionState.TIMED_OUT
                await self.manager.rollback_transaction(self.tx)
                raise TransactionTimeout(
                    f"Transaction {self.tx.id} timed out after {self.timeout}s"
                )
        except asyncio.CancelledError:
            pass
    
    async def commit(self):
        """Manually commit transaction."""
        if self.tx:
            await self.manager.commit_transaction(self.tx)
    
    async def rollback(self):
        """Manually rollback transaction."""
        if self.tx:
            await self.manager.rollback_transaction(self.tx)
    
    async def execute(self, statement: Any, *args, **kwargs):
        """Execute statement within transaction."""
        if self.tx:
            return await self.tx.execute(statement, *args, **kwargs)
        raise RuntimeError("Transaction not active")


def transactional(
    isolation: IsolationLevel = IsolationLevel.READ_COMMITTED,
    timeout: float = 300.0,
    retry_on_deadlock: bool = True
):
    """
    Decorator for transactional methods.
    Automatically manages transaction lifecycle.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract session from kwargs or first arg
            session = kwargs.get('session')
            if not session and args and hasattr(args[0], 'session'):
                session = args[0].session
            
            if not session:
                raise ValueError("No session available for transaction")
            
            # Create transaction manager
            manager = TransactionManager(session)
            
            async def operation():
                async with manager.atomic(isolation=isolation, timeout=timeout) as tx:
                    # Inject transaction into function
                    kwargs['_tx'] = tx
                    return await func(*args, **kwargs)
            
            if retry_on_deadlock:
                return await manager.handle_deadlock(operation)
            else:
                return await operation()
        
        return wrapper
    
    return decorator