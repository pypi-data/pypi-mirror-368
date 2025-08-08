"""
Audit logger utility for simplified audit logging operations.
Provides context managers and batch operations for audit trails.
"""
import uuid
from typing import Optional, Dict, List, Any, Tuple
from contextlib import asynccontextmanager

from services.audit_service import AuditService


class AuditLogger:
    """Utility class for simplified audit logging with context support."""
    
    def __init__(
        self,
        audit_service: AuditService,
        actor: str,
        correlation_id: Optional[str] = None
    ):
        """Initialize audit logger with service and context."""
        self.audit_service = audit_service
        self.actor = actor
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self._entries: List[Dict[str, Any]] = []
    
    async def log(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        changes: Optional[Dict[str, Any]] = None,
        meta_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an audit entry with current context."""
        # Merge correlation ID into metadata
        final_meta_data = meta_data or {}
        final_meta_data["correlation_id"] = self.correlation_id
        
        await self.audit_service.create_audit_entry(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            actor=self.actor,
            changes=changes,
            meta_data=final_meta_data
        )
    
    async def log_batch(
        self,
        entries: List[Tuple[str, str, str, Dict[str, Any]]]
    ) -> None:
        """Log multiple audit entries in batch."""
        for entity_type, entity_id, action, changes in entries:
            await self.log(entity_type, entity_id, action, changes)
    
    async def log_operation_start(
        self,
        operation_type: str,
        operation_id: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log the start of an operation."""
        meta_data = {"operation_status": "started"}
        if details:
            meta_data.update(details)
        
        await self.log("operation", operation_id, f"{operation_type}_started", meta_data=meta_data)
    
    async def log_operation_complete(
        self,
        operation_type: str,
        operation_id: str,
        result: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None
    ) -> None:
        """Log the completion of an operation."""
        meta_data = {"operation_status": "completed"}
        if result:
            meta_data["result"] = result
        if duration_ms:
            meta_data["duration_ms"] = duration_ms
        
        await self.log("operation", operation_id, f"{operation_type}_completed", meta_data=meta_data)
    
    async def log_operation_failed(
        self,
        operation_type: str,
        operation_id: str,
        error: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log the failure of an operation."""
        meta_data = {
            "operation_status": "failed",
            "error": error
        }
        if details:
            meta_data.update(details)
        
        await self.log("operation", operation_id, f"{operation_type}_failed", meta_data=meta_data)
    
    async def __aenter__(self):
        """Enter async context."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context."""
        # Could add automatic logging of context exit here if needed
        pass


@asynccontextmanager
async def audit_context(
    audit_service: AuditService,
    actor: str,
    operation_type: str,
    operation_id: str,
    correlation_id: Optional[str] = None
):
    """Context manager for automatic operation auditing."""
    logger = AuditLogger(audit_service, actor, correlation_id)
    
    # Log operation start
    await logger.log_operation_start(operation_type, operation_id)
    
    try:
        yield logger
        # Log successful completion
        await logger.log_operation_complete(operation_type, operation_id)
    except Exception as e:
        # Log failure
        await logger.log_operation_failed(
            operation_type,
            operation_id,
            str(e),
            {"exception_type": type(e).__name__}
        )
        raise


class BatchAuditLogger:
    """Collect audit entries for batch logging."""
    
    def __init__(self, audit_service: AuditService, actor: str):
        """Initialize batch logger."""
        self.audit_service = audit_service
        self.actor = actor
        self.entries: List[Dict[str, Any]] = []
    
    def add(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        changes: Optional[Dict[str, Any]] = None,
        meta_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add entry to batch."""
        self.entries.append({
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action": action,
            "changes": changes or {},
            "meta_data": meta_data or {}
        })
    
    async def flush(self, correlation_id: Optional[str] = None) -> int:
        """Flush all entries to database."""
        if not self.entries:
            return 0
        
        count = 0
        for entry in self.entries:
            # Add correlation ID if provided
            if correlation_id:
                entry["meta_data"]["correlation_id"] = correlation_id
            
            await self.audit_service.create_audit_entry(
                entity_type=entry["entity_type"],
                entity_id=entry["entity_id"],
                action=entry["action"],
                actor=self.actor,
                changes=entry["changes"],
                meta_data=entry["meta_data"]
            )
            count += 1
        
        # Clear entries after flush
        self.entries.clear()
        return count