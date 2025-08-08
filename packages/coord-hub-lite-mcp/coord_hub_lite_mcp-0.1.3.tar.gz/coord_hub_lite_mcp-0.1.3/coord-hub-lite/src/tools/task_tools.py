"""Task management tools for MCP using FastMCP framework - NO AUTHENTICATION"""
from typing import Optional, Dict, Any, List
from fastmcp import Context

from src.services.task_service import TaskService
from src.models.task import TaskStatus, TaskPriority
from src.database.session import get_async_session


# Create task tool - NO AUTH REQUIRED
async def create_task(
    title: str,
    description: str,
    status: str = "pending",
    priority: str = "medium",
    parent_task_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    requires_documentation: bool = False,
    documentation_paths: Optional[List[str]] = None,
    documentation_context: Optional[str] = None,
    context: Optional[Context] = None
) -> Dict[str, Any]:
    """Create a new task in the system.
    
    Args:
        context: MCP context
        title: Task title (required)
        description: Task description (required)
        status: Initial task status (default: pending)
        priority: Task priority level (default: medium)
        parent_task_id: Parent task ID if this is a subtask
        metadata: Additional metadata as key-value pairs
        requires_documentation: Whether this task requires documentation files
        documentation_paths: List of file paths to documentation
        documentation_context: Context about the documentation requirements
        
    Returns:
        Dict with success status and created task data or error message
    """
    try:
        # Log the operation
        if context:
            await context.info(f"Creating task: {title}")
        
        # Validate inputs before calling service
        if not title or not title.strip():
            error_msg = "Title cannot be empty"
            if context:
                await context.error(error_msg)
            raise ValueError(error_msg)
        
        if not description or not description.strip():
            error_msg = "Description cannot be empty"
            if context:
                await context.error(error_msg)
            raise ValueError(error_msg)
        
        # Use real database session
        async with get_async_session() as session:
            service = TaskService(session)
            
            if context:
                await context.debug(f"Creating task with status={status}, priority={priority}")
            
            # Create the task
            task_response = await service.create_task(
                session=session,
                title=title,
                description=description,
                status=status,
                priority=priority,
                parent_task_id=parent_task_id,
                metadata=metadata or {},
                requires_documentation=requires_documentation,
                documentation_paths=documentation_paths or [],
                documentation_context=documentation_context
            )
        
        # Log success
        if context:
            await context.info(f"Successfully created task with ID: {task_response.id}")
        
        # Return structured response
        return {
            "success": True,
            "task": task_response.model_dump()
        }
        
    except ValueError as e:
        # Handle validation errors
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        # Handle unexpected errors
        return {
            "success": False,
            "error": f"Failed to create task: {str(e)}"
        }


# Update task status tool
# NO AUTH REQUIRED
async def update_task_status(
    task_id: str,
    status: str,
    metadata: Optional[Dict[str, Any]] = None,
    context: Optional[Context] = None
) -> Dict[str, Any]:
    """Update the status of an existing task.
    
    Args:
        context: MCP context
        task_id: ID of the task to update (required)
        status: New status value (required)
        metadata: Additional metadata to add/update
        
    Returns:
        Dict with success status and updated task data or error message
    """
    try:
        # Log the operation
        if context:
            await context.info(f"Updating task {task_id} status to {status}")
        
        # Validate task_id
        if not task_id:
            error_msg = "Task ID cannot be empty"
            if context:
                await context.error(error_msg)
            raise ValueError(error_msg)
        
        # Validate status before calling service
        if status not in [s.value for s in TaskStatus]:
            error_msg = f"Invalid status: {status}"
            if context:
                await context.error(error_msg)
            raise ValueError(error_msg)
        
        # Use real database session
        async with get_async_session() as session:
            service = TaskService(session)
            
            if context:
                await context.debug(f"Updating task {task_id} in database")
            
            # Update the task status
            task_response = await service.update_task_status(
                session=session,
                task_id=task_id,
                status=status,
                metadata=metadata or {}
            )
        
        # Log success
        if context:
            await context.info(f"Successfully updated task {task_id} to status {status}")
        
        # Return structured response
        return {
            "success": True,
            "task": task_response.model_dump()
        }
        
    except ValueError as e:
        # Handle validation errors
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        # Handle unexpected errors
        return {
            "success": False,
            "error": f"Failed to update task status: {str(e)}"
        }


# Tool metadata for FastMCP registration
CREATE_TASK_METADATA = {
    "name": "create_task",
    "description": "Create a new task in the coordination system with title, description, and optional metadata",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Task title (required)",
                "minLength": 1,
                "maxLength": 255
            },
            "description": {
                "type": "string", 
                "description": "Detailed task description (required)",
                "minLength": 1
            },
            "status": {
                "type": "string",
                "description": "Initial task status",
                "enum": ["pending", "in_progress", "completed", "failed", "cancelled", "blocked"],
                "default": "pending"
            },
            "priority": {
                "type": "string",
                "description": "Task priority level",
                "enum": ["low", "medium", "high", "critical"],
                "default": "medium"
            },
            "parent_task_id": {
                "type": "string",
                "description": "Parent task ID if this is a subtask",
                "nullable": True
            },
            "metadata": {
                "type": "object",
                "description": "Additional metadata as key-value pairs",
                "additionalProperties": True,
                "default": {}
            },
            "requires_documentation": {
                "type": "boolean",
                "description": "Whether this task requires documentation files",
                "default": False
            },
            "documentation_paths": {
                "type": "array",
                "description": "List of file paths to required documentation",
                "items": {"type": "string"},
                "default": []
            },
            "documentation_context": {
                "type": "string",
                "description": "Context about why this documentation is needed",
                "nullable": True
            }
        },
        "required": ["title", "description"]
    }
}

UPDATE_TASK_STATUS_METADATA = {
    "name": "update_task_status",
    "description": "Update the status of an existing task with validation",
    "parameters": {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "ID of the task to update (required)"
            },
            "status": {
                "type": "string",
                "description": "New task status (required)",
                "enum": ["pending", "in_progress", "completed", "failed", "cancelled", "blocked"]
            },
            "metadata": {
                "type": "object",
                "description": "Additional metadata to add/update",
                "additionalProperties": True,
                "default": {}
            }
        },
        "required": ["task_id", "status"]
    }
}