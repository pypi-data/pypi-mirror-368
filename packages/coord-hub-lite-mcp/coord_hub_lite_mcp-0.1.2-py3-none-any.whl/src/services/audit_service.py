"""
Audit service for comprehensive logging of all system operations.
Provides centralized audit trail management with support for:
- Agent actions and decisions
- Resource modifications
- MCP tool invocations
- Error categorization
- Query capabilities
"""
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_
from sqlalchemy.orm import selectinload

from src.database.models import AuditLog


class AuditService:
    """Service for managing audit logs and tracking system operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize audit service with database session."""
        self.session = session
    
    async def create_audit_entry(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        actor: str,
        changes: Optional[Dict[str, Any]] = None,
        meta_data: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Create a new audit log entry."""
        entry = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            actor=actor,
            changes=changes or {},
            meta_data=meta_data or {}
        )
        
        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        
        return entry
    
    async def log_agent_action(
        self,
        agent_id: str,
        action: str,
        target_entity_type: Optional[str] = None,
        target_entity_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log an agent action with optional target entity."""
        meta_data = details or {}
        
        if target_entity_type and target_entity_id:
            meta_data.update({
                "target_entity_type": target_entity_type,
                "target_entity_id": target_entity_id
            })
        
        return await self.create_audit_entry(
            entity_type="agent",
            entity_id=agent_id,
            action=action,
            actor=agent_id,
            changes={},
            meta_data=meta_data
        )
    
    async def log_resource_modification(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        actor: str,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> AuditLog:
        """Log resource modification with before/after states."""
        changes = {}
        
        # Calculate changes if both states provided
        if before_state and after_state:
            for key, new_value in after_state.items():
                old_value = before_state.get(key)
                if old_value != new_value:
                    changes[key] = {"old": old_value, "new": new_value}
        
        meta_data = {}
        if correlation_id:
            meta_data["correlation_id"] = correlation_id
        
        return await self.create_audit_entry(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            actor=actor,
            changes=changes,
            meta_data=meta_data
        )
    
    async def log_mcp_tool_invocation(
        self,
        tool_name: str,
        agent_id: str,
        parameters: Dict[str, Any],
        result: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None
    ) -> AuditLog:
        """Log MCP tool invocation with parameters and results."""
        meta_data = {
            "parameters": parameters,
            "result": result or {},
            "duration_ms": duration_ms
        }
        
        return await self.create_audit_entry(
            entity_type="mcp_tool",
            entity_id=tool_name,
            action="invoked",
            actor=agent_id,
            changes={},
            meta_data=meta_data
        )
    
    async def log_error(
        self,
        entity_type: str,
        entity_id: str,
        error_type: str,
        error_message: str,
        actor: str,
        stack_trace: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log error with categorization and context."""
        meta_data = {
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {}
        }
        
        if stack_trace:
            meta_data["stack_trace"] = stack_trace
        
        return await self.create_audit_entry(
            entity_type=entity_type,
            entity_id=entity_id,
            action="error",
            actor=actor,
            changes={},
            meta_data=meta_data
        )
    
    async def query_audit_log(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        actor: Optional[str] = None,
        action: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """Query audit log with various filters."""
        query = select(AuditLog)
        
        # Build filter conditions
        conditions = []
        
        if entity_type:
            conditions.append(AuditLog.entity_type == entity_type)
        
        if entity_id:
            conditions.append(AuditLog.entity_id == entity_id)
        
        if actor:
            conditions.append(AuditLog.actor == actor)
        
        if action:
            conditions.append(AuditLog.action == action)
        
        if start_time:
            conditions.append(AuditLog.timestamp >= start_time)
        
        if end_time:
            conditions.append(AuditLog.timestamp <= end_time)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Apply ordering, limit and offset
        query = query.order_by(AuditLog.timestamp.desc())
        query = query.limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def apply_retention_policy(self, days_to_keep: int = 90) -> int:
        """Apply retention policy by deleting old audit logs."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
        
        # Delete old audit logs
        delete_stmt = delete(AuditLog).where(AuditLog.timestamp < cutoff_date)
        result = await self.session.execute(delete_stmt)
        await self.session.commit()
        
        return result.rowcount
    
    async def get_audit_summary(
        self,
        entity_type: str,
        entity_id: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get audit summary for a specific entity."""
        entries = await self.query_audit_log(
            entity_type=entity_type,
            entity_id=entity_id,
            limit=limit
        )
        
        summary = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "total_entries": len(entries),
            "actions": {},
            "actors": {},
            "first_action": None,
            "last_action": None
        }
        
        if entries:
            # Count actions and actors
            for entry in entries:
                summary["actions"][entry.action] = summary["actions"].get(entry.action, 0) + 1
                summary["actors"][entry.actor] = summary["actors"].get(entry.actor, 0) + 1
            
            # Get first and last actions
            summary["first_action"] = {
                "action": entries[-1].action,
                "actor": entries[-1].actor,
                "timestamp": entries[-1].timestamp.isoformat()
            }
            summary["last_action"] = {
                "action": entries[0].action,
                "actor": entries[0].actor,
                "timestamp": entries[0].timestamp.isoformat()
            }
        
        return summary