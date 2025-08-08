"""MCP Tools for Coord-Hub-Lite"""
try:
    from src.tools.task_tools import (
        create_task,
        update_task_status,
        CREATE_TASK_METADATA,
        UPDATE_TASK_STATUS_METADATA
    )
    _task_tools_available = True
except ImportError:
    _task_tools_available = False

from src.tools.plan_tools import upload_plan, validate_plan

# Export all tools
__all__ = [
    # Plan tools
    "upload_plan",
    "validate_plan",
]

# Add task tools if available
if _task_tools_available:
    __all__.extend([
        # Functions
        "create_task",
        "update_task_status",
        # Metadata
        "CREATE_TASK_METADATA",
        "UPDATE_TASK_STATUS_METADATA"
    ])

# Tool registry for FastMCP
TOOL_REGISTRY = {
    "upload_plan": upload_plan,
    "validate_plan": validate_plan,
}

if _task_tools_available:
    TOOL_REGISTRY.update({
        "create_task": (create_task, CREATE_TASK_METADATA),
        "update_task_status": (update_task_status, UPDATE_TASK_STATUS_METADATA)
    })