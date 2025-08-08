"""FastMCP server implementation for Coord-Hub-Lite."""
import asyncio
import importlib
import inspect
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, List, Optional

from fastmcp import FastMCP, Context
from sqlalchemy import text

from src.config import Settings, get_settings
from src.database.session import engine, get_async_session, init_db
from src.middleware.error_handler import ErrorHandlingMiddleware
from src.middleware.logging import LoggingMiddleware, get_logger
from src.middleware.auth import AuthMiddleware
from src.middleware.mcp_auth import initialize_mcp_auth_middleware
from src.auth.api_keys import APIKeyManager, JWTTokenManager
from src.auth.permissions import PermissionManager
# NO AUTHENTICATION - Local MCP server

# Logger instance
logger = get_logger(__name__)


async def lifespan(settings: Settings) -> AsyncGenerator[None, None]:
    """Manage server lifespan - startup and shutdown.
    
    Args:
        settings: Application settings
        
    Yields:
        None during server operation
    """
    # Startup
    logger.info("Starting Coord-Hub-Lite server", 
                host=settings.host, 
                port=settings.port,
                environment=settings.environment)
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")
        
        # Yield control back to server
        yield
        
    except Exception as e:
        logger.error("Failed to initialize server", error=str(e), exc_info=True)
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down Coord-Hub-Lite server")
        
        try:
            # Close database connections
            await engine.dispose()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error("Error during shutdown", error=str(e), exc_info=True)


async def check_database_health() -> bool:
    """Check if database is accessible and healthy.
    
    Returns:
        True if database is healthy, False otherwise
    """
    try:
        async with get_async_session() as session:
            # Simple health check query
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return False


# NO AUTH REQUIRED
async def health_check(context: Optional[Context] = None) -> Dict[str, Any]:
    """Health check endpoint for monitoring.
    
    Args:
        context: MCP context for logging
    
    Returns:
        Health status information
    """
    try:
        if context:
            await context.info("Performing health check")
        
        # Check database health
        db_healthy = await check_database_health()
        
        if context:
            if db_healthy:
                await context.debug("Database health check passed")
            else:
                await context.warning("Database health check failed")
        
        overall_status = "healthy" if db_healthy else "degraded"
        
        result_data = {
            "status": overall_status,
            "service": "coord-hub-lite",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "0.1.0",
            "database": "connected" if db_healthy else "disconnected",
            "checks": {
                "database": db_healthy
            }
        }
        
        if context:
            await context.info(f"Health check completed: {overall_status}")
        
        return {
            "success": True,
            "data": result_data
        }
        
    except Exception as e:
        error_msg = f"Health check failed: {str(e)}"
        if context:
            await context.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }


async def register_tools(server: FastMCP) -> None:
    """Register all available tools with the server.
    
    Args:
        server: FastMCP server instance
    """
    from fastmcp.tools import FunctionTool
    
    # Enhanced tool definitions with metadata
    tool_definitions = [
        {
            "module": "src.tools.database_setup_tools",
            "functions": [
                {
                    "name": "initialize_database_tool",
                    "description": "Initialize a SQLite database at a user path, persist DATABASE_URL to .env, and hot-reload the server to use it.",
                    "tags": {"database", "init", "setup"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                }
            ]
        },
        {
            "module": "src.tools.task_tools", 
            "functions": [
                {
                    "name": "create_task",
                    "description": "Creates a new task with automatic validation. USE: When starting new work items. RETURNS: Task ID for tracking. ENFORCES: Quality gates and status workflow.",
                    "tags": {"task-management", "create", "coordination"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": False
                    }
                },
                {
                    "name": "update_task_status",
                    "description": "Transitions task to new status with state validation. USE: After completing work phases. BLOCKS: Invalid transitions like skipping review. RETURNS: Updated task or error.",
                    "tags": {"task-management", "update", "status"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                }
            ]
        },
        {
            "module": "src.tools.agent_tools",
            "functions": [
                {
                    "name": "register_agent_tool",
                    "description": "Registers agent with capabilities for task assignment. USE: Before assigning work to agents. TRACKS: Agent type, capabilities, availability. RETURNS: Agent registration confirmation.",
                    "tags": {"agent-management", "registration", "capabilities"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                },
                {
                    "name": "find_available_agent_tool",
                    "description": "Discovers agents ready for task assignment. USE: Before batch_assign_tasks. FILTERS: By capability and availability. RETURNS: List of assignable agents.",
                    "tags": {"agent-management", "search", "availability"},
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                }
            ]
        },
        {
            "module": "src.tools.assignment_tools",
            "functions": [
                {
                    "name": "assign_task_tool",
                    "description": "Assigns single task to specific agent with validation. USE: For targeted assignment. VALIDATES: Agent capabilities match task. RETURNS: Assignment confirmation or rejection.",
                    "tags": {"assignment", "coordination", "validation"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": False
                    }
                },
                {
                    "name": "get_task_tree_tool",
                    "description": "Visualizes all tasks with status, assignments, and dependencies. USE: To monitor project progress. SHOWS: Task hierarchy, agent workload, completion stats. RETURNS: Tree structure with metadata.",
                    "tags": {"visualization", "dependencies", "analysis"},
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                }
            ]
        },
        {
            "module": "src.tools.plan_tools",
            "functions": [
                {
                    "name": "upload_plan",
                    "description": "Imports project plan and auto-creates tasks. USE: Project initialization from structured plan. VALIDATES: Plan format. OPTION: auto_create_tasks flag. RETURNS: Plan ID or validation errors.",
                    "tags": {"planning", "upload", "validation"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": False
                    }
                },
                {
                    "name": "validate_plan",
                    "description": "Checks plan structure without creating tasks. USE: Before upload_plan to preview. PERFORMS: Dry run validation. RETURNS: Validation report with issues.",
                    "tags": {"planning", "validation", "analysis"},
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                }
            ]
        },
        {
            "module": "src.tools.dependency_tools",
            "functions": [
                {
                    "name": "set_task_dependencies",
                    "description": "Establishes task execution order with cycle detection. USE: After task creation. PREVENTS: Circular dependencies. RETURNS: Dependency graph or cycle error.",
                    "tags": {"dependencies", "task-management", "validation"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                },
                {
                    "name": "get_ready_tasks",
                    "description": "Finds tasks with satisfied dependencies ready to execute. USE: For work scheduling. FILTERS: No blocking dependencies. RETURNS: Immediately executable tasks.",
                    "tags": {"dependencies", "task-management", "scheduling"},
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                },
                {
                    "name": "check_circular_dependencies",
                    "description": "Tests if new dependencies create cycles. USE: Before set_task_dependencies. VALIDATES: Acyclic graph maintained. RETURNS: Safe/unsafe with cycle path.",
                    "tags": {"dependencies", "validation", "analysis"},
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                },
                {
                    "name": "get_dependency_graph",
                    "description": "Visualizes task dependency relationships. USE: Understanding execution order. FORMATS: Tree, DOT, Mermaid. RETURNS: Graph representation.",
                    "tags": {"dependencies", "visualization", "analysis"},
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                },
                {
                    "name": "get_blocked_tasks",
                    "description": "Identifies tasks waiting on incomplete dependencies. USE: Finding bottlenecks. SHOWS: Blocking task chains. RETURNS: Blocked tasks with blockers.",
                    "tags": {"dependencies", "task-management", "analysis"},
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                }
            ]
        },
        {
            "module": "src.tools.file_ownership_tools",
            "functions": [
                {
                    "name": "set_file_ownership",
                    "description": "Reserves files exclusively for a task. USE: Prevent parallel edit conflicts. LOCKS: File paths to single task. RETURNS: Ownership confirmation.",
                    "tags": {"file-ownership", "concurrency", "coordination"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                },
                {
                    "name": "get_file_ownership_map",
                    "description": "Shows which tasks own which files. USE: Before file modifications. DISPLAYS: File-Task mapping. RETURNS: Ownership registry.",
                    "tags": {"file-ownership", "analysis", "monitoring"},
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                },
                {
                    "name": "release_file_ownership",
                    "description": "Frees file locks when task completes. USE: After task completion/failure. UNLOCKS: Reserved files. RETURNS: Released file list.",
                    "tags": {"file-ownership", "coordination", "cleanup"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                },
                {
                    "name": "get_available_files",
                    "description": "Get list of files not currently owned by any active task",
                    "tags": {"file-ownership", "discovery", "scheduling"},
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                },
                {
                    "name": "transfer_file_ownership",
                    "description": "Transfer file ownership between tasks during handoffs",
                    "tags": {"file-ownership", "coordination", "workflow"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": False
                    }
                }
            ]
        },
        {
            "module": "src.tools.review_workflow_tools",
            "functions": [
                {
                    "name": "submit_task_for_review",
                    "description": "Initiates review process with artifacts. USE: After executor completes work. ASSIGNS: Reviewer based on type. RETURNS: Review request ID.",
                    "tags": {"review", "workflow", "completion"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": False
                    }
                },
                {
                    "name": "submit_review_decision",
                    "description": "Records review outcome (approved/needs_fixes/rejected). USE: After code review. TRIGGERS: Status transitions. RETURNS: Decision confirmation.",
                    "tags": {"review", "decision", "workflow"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": False
                    }
                },
                {
                    "name": "get_tasks_pending_review",
                    "description": "Lists all tasks awaiting review. USE: Reviewer workload check. FILTERS: By reviewer, type. RETURNS: Review queue.",
                    "tags": {"review", "query", "workflow"},
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                },
                {
                    "name": "get_review_history",
                    "description": "Get complete review history for a task",
                    "tags": {"review", "history", "audit"},
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                },
                {
                    "name": "resubmit_after_fixes",
                    "description": "Resubmit task for review after addressing feedback",
                    "tags": {"review", "fixes", "workflow"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": False
                    }
                },
                {
                    "name": "escalate_review",
                    "description": "Escalate review to higher-level reviewer",
                    "tags": {"review", "escalation", "workflow"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": False
                    }
                }
            ]
        },
        {
            "module": "src.tools.completion_handler_tools",
            "functions": [
                {
                    "name": "handle_task_completion",
                    "description": "Processes successful task completion with follow-ups. USE: Task succeeded. TRIGGERS: Dependent task activation. RETURNS: Completion report.",
                    "tags": {"completion", "workflow", "automation"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": False
                    }
                },
                {
                    "name": "handle_task_failure",
                    "description": "Manages task failure with recovery options. USE: Task failed. OPTIONS: Retry, reassign, escalate. RETURNS: Failure analysis.",
                    "tags": {"failure", "recovery", "workflow"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": False
                    }
                },
                {
                    "name": "check_project_completion",
                    "description": "Check if all tasks in a project are complete",
                    "tags": {"project", "completion", "monitoring"},
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                },
                {
                    "name": "trigger_phase_transition",
                    "description": "Trigger transition between project phases",
                    "tags": {"phase", "workflow", "automation"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": False
                    }
                },
                {
                    "name": "retry_failed_task",
                    "description": "Retry a failed task with optional modifications",
                    "tags": {"retry", "failure", "recovery"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": False
                    }
                }
            ]
        },
        {
            "module": "src.tools.workflow_automation_tools",
            "functions": [
                {
                    "name": "auto_assign_ready_tasks",
                    "description": "Automatically assign ready tasks to available agents",
                    "tags": {"automation", "assignment", "scheduling"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": False
                    }
                },
                {
                    "name": "process_completion_workflow",
                    "description": "Process full completion workflow including reviews",
                    "tags": {"workflow", "completion", "automation"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": False
                    }
                },
                {
                    "name": "create_task_batch",
                    "description": "Create multiple related tasks with dependencies",
                    "tags": {"batch", "creation", "automation"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": False
                    }
                },
                {
                    "name": "cascade_task_cancellation",
                    "description": "Cancel task and optionally cascade to dependents",
                    "tags": {"cancellation", "cascade", "workflow"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": True,
                        "idempotentHint": False
                    }
                },
                {
                    "name": "rebalance_agent_workload",
                    "description": "Rebalance task assignments across agents",
                    "tags": {"workload", "optimization", "automation"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": False
                    }
                }
            ]
        },
        {
            "module": "src.tools.parallel_execution_tools",
            "functions": [
                {
                    "name": "identify_parallel_groups",
                    "description": "Identify groups of tasks that can execute in parallel",
                    "tags": {"parallel", "analysis", "optimization"},
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                },
                {
                    "name": "schedule_parallel_execution",
                    "description": "Schedule tasks for parallel execution with constraints",
                    "tags": {"parallel", "scheduling", "execution"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": False
                    }
                },
                {
                    "name": "detect_parallelization_opportunities",
                    "description": "Detect opportunities to parallelize sequential tasks",
                    "tags": {"parallel", "optimization", "analysis"},
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                },
                {
                    "name": "coordinate_parallel_agents",
                    "description": "Coordinate agents working on parallel tasks",
                    "tags": {"parallel", "coordination", "synchronization"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": False
                    }
                },
                {
                    "name": "monitor_parallel_progress",
                    "description": "Monitor progress of parallel task execution",
                    "tags": {"parallel", "monitoring", "progress"},
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                }
            ]
        },
        {
            "module": "src.tools.artifact_tools",
            "functions": [
                {
                    "name": "upload_artifact",
                    "description": "Stores TDD artifacts (RED/GREEN), review feedback, test results. USE: Sub-agents upload work outputs. REQUIRED: For status transitions. RETURNS: Artifact ID.",
                    "tags": {"artifact", "quality", "tdd", "compliance"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": False
                    }
                },
                {
                    "name": "get_task_artifacts",
                    "description": "Retrieves all artifacts for a task. USE: Reviewers fetch TDD outputs for validation. FILTERS: By artifact type. RETURNS: Chronological artifact list.",
                    "tags": {"artifact", "audit", "compliance", "retrieval"},
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                },
                {
                    "name": "validate_compliance",
                    "description": "Checks if task has required artifacts for current status. USE: Before approval/completion. VALIDATES: TDD artifacts, review feedback. RETURNS: Compliance status with missing items.",
                    "tags": {"compliance", "validation", "quality", "audit"},
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                }
            ]
        },
        {
            "module": "src.tools.batch_tools",
            "functions": [
                {
                    "name": "batch_create_tasks",
                    "description": "Creates multiple tasks atomically in single transaction. USE: For parallel work decomposition (up to 4 simultaneous). SUPPORTS: Dependencies via temp_id. RETURNS: All task IDs or rollback.",
                    "tags": {"batch", "parallel", "creation", "atomic"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": False
                    }
                },
                {
                    "name": "batch_assign_tasks",
                    "description": "Assigns multiple tasks to available executors simultaneously. USE: To maximize parallel execution (4 slots). PERFORMS: Round-robin distribution. RETURNS: Task-Agent mapping.",
                    "tags": {"batch", "assignment", "parallel", "scheduling"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": False
                    }
                },
                {
                    "name": "batch_update_status",
                    "description": "Updates multiple task statuses in atomic transaction. USE: For bulk status changes. ENSURES: All succeed or all rollback. RETURNS: Success/failure per task.",
                    "tags": {"batch", "status", "atomic", "transaction"},
                    "annotations": {
                        "readOnlyHint": False,
                        "destructiveHint": False,
                        "idempotentHint": False
                    }
                },
                {
                    "name": "get_ready_tasks",
                    "description": "Finds tasks with satisfied dependencies ready to execute. USE: For work scheduling. FILTERS: No blocking dependencies. RETURNS: Immediately executable tasks.",
                    "tags": {"scheduling", "dependencies", "parallel", "ready"},
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                },
                {
                    "name": "parallel_task_status",
                    "description": "Reports current parallel execution capacity and utilization. USE: Before batch operations. SHOWS: Available slots (max 4), busy agents. RETURNS: Capacity metrics.",
                    "tags": {"parallel", "status", "capacity", "monitoring"},
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True
                    }
                }
            ]
        }
    ]
    
    # Track registered tools
    registered_count = 0
    
    for tool_module in tool_definitions:
        try:
            # Import the module
            module = importlib.import_module(tool_module["module"])
            
            # Register each tool with enhanced metadata
            for func_def in tool_module["functions"]:
                func_name = func_def["name"]
                if hasattr(module, func_name):
                    func = getattr(module, func_name)
                    
                    # Check if function has 'context' parameter
                    sig = inspect.signature(func)
                    has_context = 'context' in sig.parameters
                    
                    # Create tool from function with enhanced metadata
                    tool = FunctionTool.from_function(
                        func,
                        name=func_name,
                        description=func_def.get("description"),
                        tags=func_def.get("tags", set()),
                        annotations=func_def.get("annotations", {}),
                        exclude_args=["context"] if has_context else []
                    )
                    server.add_tool(tool)
                    registered_count += 1
                    logger.debug(f"Registered enhanced tool: {func_name}")
                else:
                    logger.warning(f"Tool {func_name} not found in {tool_module['module']}")
            
        except ImportError as e:
            logger.error(f"Failed to import tool module: {tool_module['module']}", error=str(e))
        except Exception as e:
            logger.error(f"Error registering tools from {tool_module['module']}", error=str(e))
    
    # Register health check as a tool with enhanced metadata
    health_tool = FunctionTool.from_function(
        health_check,
        name="health_check",
        description="Validates service and database connectivity. USE: Before operations. CHECKS: Database, API availability. RETURNS: Health status (healthy/degraded).",
        tags={"monitoring", "health", "status"},
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "title": "Service Health Check"
        },
        exclude_args=["context"]
    )
    server.add_tool(health_tool)
    registered_count += 1
    
    logger.info(f"Registered {registered_count} tools")


async def create_server(settings: Settings) -> FastMCP:
    """Create and configure the FastMCP server.
    
    Args:
        settings: Application settings
        
    Returns:
        Configured FastMCP server instance
    """
    # Initialize MCP authentication middleware BEFORE creating tools
    # Create the required managers for AuthMiddleware
    api_key_manager = APIKeyManager()
    token_manager = JWTTokenManager(secret_key="dev-secret-key-change-in-production")
    permission_manager = PermissionManager()
    
    # Initialize AuthMiddleware with its dependencies
    auth_middleware = AuthMiddleware(
        api_key_manager=api_key_manager,
        token_manager=token_manager,
        permission_manager=permission_manager
    )
    initialize_mcp_auth_middleware(auth_middleware)
    logger.info("MCP authentication middleware initialized")
    
    # Create server instance
    server = FastMCP("coord-hub-lite")
    
    # Add middleware in order (outermost first)
    server.add_middleware(ErrorHandlingMiddleware(include_traceback=True))
    server.add_middleware(LoggingMiddleware(include_payloads=True, max_payload_length=1000))
    
    # Register all tools
    await register_tools(server)
    
    logger.info("Server created and configured",
                middleware_count=2,
                environment=settings.environment)
    
    return server


async def main():
    """Main entry point for the server."""
    # Force development mode for testing
    import os
    os.environ['MCP_DEV_MODE'] = 'true'
    
    # Get settings
    settings = get_settings()
    
    # Configure logging based on settings
    import logging as std_logging
    std_logging.basicConfig(level=getattr(std_logging, settings.log_level))
    
    # Create server
    server = await create_server(settings)
    
    # Run server with lifespan management
    # Handle startup
    logger.info("Starting Coord-Hub-Lite server", 
                host=settings.host, 
                port=settings.port,
                environment=settings.environment)
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")
        
        # Start server using stdio transport for MCP
        logger.info("Server starting with stdio transport for MCP")
        
        # Run the server with stdio transport - this will block until interrupted
        await server.run_stdio_async()
            
    except Exception as e:
        logger.error("Failed to initialize server", error=str(e), exc_info=True)
        raise
        
    finally:
        # Shutdown
        logger.info("Shutting down Coord-Hub-Lite server")
        
        try:
            # Close database connections
            await engine.dispose()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error("Error during shutdown", error=str(e), exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())


def cli():
    """Console entrypoint for packaging (sync wrapper)."""
    asyncio.run(main())