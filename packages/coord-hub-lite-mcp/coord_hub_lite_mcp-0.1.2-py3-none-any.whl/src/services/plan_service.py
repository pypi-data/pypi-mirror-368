"""
Service layer for plan management operations.
"""

import json
import yaml
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


class PlanService:
    """Service for managing plans - parsing, versioning, and persistence."""
    
    # Class-level storage for persistence across instances
    _plans = {}
    _tasks = {}
    
    def __init__(self):
        """Initialize PlanService with in-memory storage."""
        # Using class-level in-memory storage for now
        self.plans = PlanService._plans
        self.tasks = PlanService._tasks
    
    async def parse_plan(self, plan_data: str) -> Dict[str, Any]:
        """
        Parse plan data from JSON or YAML format.
        
        Args:
            plan_data: String containing plan data in JSON or YAML format
            
        Returns:
            Parsed plan dictionary
        """
        # Try JSON first
        json_error = None
        try:
            return json.loads(plan_data)
        except json.JSONDecodeError as e:
            json_error = str(e)
        
        # Try YAML
        try:
            parsed = yaml.safe_load(plan_data)
            # YAML can parse almost anything, so check if we got a dict
            if not isinstance(parsed, dict):
                raise ValueError(f"Invalid plan format. Expected dict, got {type(parsed).__name__}")
            return parsed
        except yaml.YAMLError as e:
            # If both failed, report JSON error first as it's more common
            raise ValueError(f"Invalid plan format. JSON error: {json_error}, YAML error: {e}")
    
    async def save_text_plan(self, plan_text: str) -> str:
        """
        Save a text plan to storage.
        
        Args:
            plan_text: Plain text plan
            
        Returns:
            Plan ID
        """
        # Generate plan ID
        plan_id = str(uuid.uuid4())
        
        # Create simple plan record
        plan_record = {
            "id": plan_id,
            "content": plan_text,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Save to in-memory storage
        self.plans[plan_id] = plan_record
        
        return plan_id
    
    async def save_plan(self, plan_data: Dict[str, Any]) -> str:
        """
        Save a plan to the database with version management.
        
        Args:
            plan_data: Plan dictionary
            
        Returns:
            Plan ID
        """
        # Check for existing plans with same name
        existing_plans = [p for p in self.plans.values() if p.get("name") == plan_data["name"]]
        
        # Auto-increment version if plan with same name exists
        if existing_plans:
            latest_version = max(p.get("version", 0) for p in existing_plans)
            plan_data["version"] = latest_version + 1
        else:
            # Ensure version is set
            if "version" not in plan_data:
                plan_data["version"] = 1
        
        # Generate plan ID
        plan_id = str(uuid.uuid4())
        
        # Add metadata
        plan_data["id"] = plan_id
        plan_data["created_at"] = datetime.now(timezone.utc).isoformat()
        plan_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        # Save to in-memory storage
        self.plans[plan_id] = plan_data.copy()
        
        return plan_id
    
    async def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a plan by ID.
        
        Args:
            plan_id: Plan ID
            
        Returns:
            Plan data or None if not found
        """
        return self.plans.get(plan_id)
    
    async def extract_tasks(self, plan_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract task definitions from a plan.
        
        Args:
            plan_data: Plan dictionary
            
        Returns:
            List of task dictionaries
        """
        tasks = plan_data.get("tasks", [])
        
        # Enrich tasks with plan information
        enriched_tasks = []
        for task in tasks:
            enriched_task = task.copy()
            enriched_task["plan_id"] = plan_data.get("id")
            enriched_task["plan_name"] = plan_data.get("name")
            enriched_tasks.append(enriched_task)
        
        return enriched_tasks
    
    async def create_tasks_from_plan(self, plan_data: Dict[str, Any]) -> List[str]:
        """
        Create tasks in the database from plan definitions.
        
        Args:
            plan_data: Plan dictionary
            
        Returns:
            List of created task IDs
        """
        tasks = await self.extract_tasks(plan_data)
        task_ids = []
        
        for task in tasks:
            # Generate unique task ID
            task_id = str(uuid.uuid4())
            
            # Create task record
            task_record = {
                "id": task_id,
                "plan_task_id": task["id"],  # Original ID from plan
                "title": task["title"],
                "description": task.get("description", ""),
                "dependencies": task.get("dependencies", []),
                "required_capabilities": task.get("required_capabilities", []),
                "plan_id": plan_data.get("id"),
                "status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Save to in-memory storage
            self.tasks[task_id] = task_record
            task_ids.append(task_id)
        
        return task_ids

