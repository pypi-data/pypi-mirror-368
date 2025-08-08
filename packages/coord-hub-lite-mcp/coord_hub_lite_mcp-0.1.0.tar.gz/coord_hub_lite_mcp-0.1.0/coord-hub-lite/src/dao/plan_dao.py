"""Plan Data Access Object"""
from typing import List, Optional, Dict, Any, Set
from datetime import datetime, timezone
import json

from sqlalchemy import select, update, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.base import BaseDAO
from src.database.models import Plan as PlanModel
from src.models.plan import PlanCreate, PlanResponse, PlanStatus


class PlanDAO(BaseDAO[PlanModel]):
    """Data Access Object for Plan operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, PlanModel)
    
    async def create_plan(self, plan_data: PlanCreate) -> PlanResponse:
        """Create a new execution plan"""
        try:
            # Build task tree structure
            task_tree = self._build_plan_tree(plan_data.tasks)
            
            # Create plan model - ID will be auto-generated
            plan = PlanModel(
                name=plan_data.name,
                version=1,  # Start with version 1
                content=plan_data.description,  # Store description as content
                status='active',  # Use string status matching database constraint
                meta_data={
                    **plan_data.metadata,
                    'total_tasks': len(plan_data.tasks),
                    'task_tree': task_tree,
                    'started_at': datetime.now(timezone.utc).isoformat()
                }
            )
            
            await self.add(plan)
            await self.flush()
            
            return await self._to_response(plan)
            
        except Exception as e:
            await self.rollback()
            self.handle_error(e, "create_plan")
    
    async def get_active_plan(self) -> Optional[PlanResponse]:
        """Get the currently active plan"""
        try:
            stmt = (
                select(PlanModel)
                .where(PlanModel.status == 'active')  # Use string status
                .order_by(PlanModel.created_at.desc())
                .limit(1)
            )
            
            result = await self.session.execute(stmt)
            plan = result.scalar_one_or_none()
            
            if plan:
                return await self._to_response(plan)
            return None
            
        except Exception as e:
            self.handle_error(e, "get_active_plan")
    
    async def get_plan_by_id(self, plan_id: int) -> Optional[PlanResponse]:
        """Get a plan by ID"""
        try:
            stmt = select(PlanModel).where(PlanModel.id == plan_id)
            
            result = await self.session.execute(stmt)
            plan = result.scalar_one_or_none()
            
            if plan:
                return await self._to_response(plan)
            return None
            
        except Exception as e:
            self.handle_error(e, "get_plan_by_id")
    
    async def update_plan_progress(self, plan_id: int, completed: int = 0, failed: int = 0) -> PlanResponse:
        """Update plan progress counters"""
        try:
            stmt = select(PlanModel).where(PlanModel.id == plan_id)
            result = await self.session.execute(stmt)
            plan = result.scalar_one_or_none()
            
            if not plan:
                raise ValueError(f"Plan {plan_id} not found")
            
            # Update counters in meta_data
            meta_data = plan.meta_data or {}
            meta_data['completed_tasks'] = meta_data.get('completed_tasks', 0) + completed
            meta_data['failed_tasks'] = meta_data.get('failed_tasks', 0) + failed
            plan.meta_data = meta_data
            
            # Check if plan is complete
            total_tasks = meta_data.get('total_tasks', 0)
            completed_tasks = meta_data.get('completed_tasks', 0)
            failed_tasks = meta_data.get('failed_tasks', 0)
            
            if completed_tasks + failed_tasks >= total_tasks:
                plan.status = 'completed' if failed_tasks == 0 else 'failed'
                meta_data['completed_at'] = datetime.now(timezone.utc).isoformat()
                plan.meta_data = meta_data
            
            await self.flush()
            return await self._to_response(plan)
            
        except Exception as e:
            await self.rollback()
            self.handle_error(e, "update_plan_progress")
    
    async def validate_plan_structure(self, plan_data: PlanCreate) -> List[str]:
        """Validate plan structure for issues like circular dependencies"""
        errors = []
        
        try:
            # Build dependency graph
            task_ids = {task["id"] for task in plan_data.tasks}
            dependency_graph = {
                task["id"]: set(task.get("dependencies", []))
                for task in plan_data.tasks
            }
            
            # Check for missing dependencies
            for task_id, deps in dependency_graph.items():
                for dep in deps:
                    if dep not in task_ids:
                        errors.append(f"Task {task_id} depends on non-existent task {dep}")
            
            # Check for circular dependencies
            def has_cycle(graph: Dict[str, Set[str]]) -> Optional[List[str]]:
                visited = set()
                rec_stack = set()
                path = []
                
                def visit(node: str) -> bool:
                    if node in rec_stack:
                        # Found cycle
                        cycle_start = path.index(node)
                        return path[cycle_start:] + [node]
                    
                    if node in visited:
                        return None
                    
                    visited.add(node)
                    rec_stack.add(node)
                    path.append(node)
                    
                    for neighbor in graph.get(node, []):
                        cycle = visit(neighbor)
                        if cycle:
                            return cycle
                    
                    path.pop()
                    rec_stack.remove(node)
                    return None
                
                for node in graph:
                    if node not in visited:
                        cycle = visit(node)
                        if cycle:
                            return cycle
                
                return None
            
            cycle = has_cycle(dependency_graph)
            if cycle:
                errors.append(f"Circular dependency detected: {' -> '.join(cycle)}")
            
            # Check for orphaned tasks (no path from any root)
            roots = [task_id for task_id, deps in dependency_graph.items() if not deps]
            if not roots:
                errors.append("No root tasks found (tasks with no dependencies)")
            
            return errors
            
        except Exception as e:
            return [f"Validation error: {str(e)}"]
    
    async def soft_delete_plan(self, plan_id: str) -> None:
        """Soft delete a plan"""
        try:
            stmt = (
                update(PlanModel)
                .where(PlanModel.id == plan_id)
                .values(
                    deleted_at=datetime.now(timezone.utc),
                    status=PlanStatus.ARCHIVED
                )
            )
            
            result = await self.session.execute(stmt)
            if result.rowcount == 0:
                raise ValueError(f"Plan {plan_id} not found")
            
            await self.flush()
            
        except Exception as e:
            await self.rollback()
            self.handle_error(e, "soft_delete_plan")
    
    def _build_plan_tree(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build hierarchical task tree from flat task list"""
        # Create task lookup
        task_lookup = {task["id"]: task for task in tasks}
        
        # Build tree structure
        tree = {}
        for task in tasks:
            task_id = task["id"]
            tree[task_id] = {
                "name": task["name"],
                "description": task["description"],
                "status": "pending",
                "dependencies": task.get("dependencies", []),
                "children": []
            }
        
        # Populate children (reverse dependencies)
        for task_id, task_info in tree.items():
            for dep_id in task_info["dependencies"]:
                if dep_id in tree:
                    tree[dep_id]["children"].append(task_id)
        
        return tree
    
    async def _to_response(self, plan: PlanModel) -> PlanResponse:
        """Convert PlanModel to PlanResponse"""
        # Extract data from meta_data
        meta_data = plan.meta_data or {}
        
        return PlanResponse(
            id=str(plan.id),  # Convert integer ID to string
            name=plan.name,
            description=plan.content,  # Map content to description
            status=PlanStatus(plan.status) if plan.status in [s.value for s in PlanStatus] else PlanStatus.ACTIVE,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
            started_at=datetime.fromisoformat(meta_data['started_at']) if 'started_at' in meta_data else None,
            completed_at=datetime.fromisoformat(meta_data['completed_at']) if 'completed_at' in meta_data else None,
            deleted_at=None,  # Not in database model
            total_tasks=meta_data.get('total_tasks', 0),
            completed_tasks=meta_data.get('completed_tasks', 0),
            failed_tasks=meta_data.get('failed_tasks', 0),
            task_tree=meta_data.get('task_tree', {}),
            metadata={k: v for k, v in meta_data.items() if k not in ['total_tasks', 'completed_tasks', 'failed_tasks', 'task_tree', 'started_at', 'completed_at']}
        )