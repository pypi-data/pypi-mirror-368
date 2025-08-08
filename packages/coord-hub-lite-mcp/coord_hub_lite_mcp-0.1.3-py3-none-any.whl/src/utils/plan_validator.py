"""
Validator for plan structures and dependencies.
"""

from typing import Dict, Any, List, Set, Optional
from collections import defaultdict, deque


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class PlanValidator:
    """Validates plan structure, dependencies, and resources."""
    
    def __init__(self):
        """Initialize PlanValidator."""
        self.required_fields = ["name", "version", "tasks"]
        self.required_task_fields = ["id", "title", "dependencies", "required_capabilities"]
    
    async def validate(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform full validation on a plan.
        
        Args:
            plan_data: Plan dictionary to validate
            
        Returns:
            Dict with validation results
        """
        errors = []
        warnings = []
        
        # Validate structure
        structure_errors = self.validate_structure(plan_data)
        errors.extend(structure_errors)
        
        if not structure_errors:  # Only continue if structure is valid
            # Check circular dependencies
            if self.check_circular_dependencies(plan_data):
                errors.append("Circular dependency detected in task graph")
            
            # Validate task references
            ref_errors = self.validate_task_references(plan_data)
            errors.extend(ref_errors)
            
            # Check resource availability
            resource_errors = await self.check_resource_availability(plan_data)
            errors.extend(resource_errors)
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def validate_structure(self, plan_data: Dict[str, Any]) -> List[str]:
        """
        Validate the basic structure of a plan.
        
        Args:
            plan_data: Plan dictionary
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check required top-level fields
        for field in self.required_fields:
            if field not in plan_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate tasks if present
        if "tasks" in plan_data:
            if not isinstance(plan_data["tasks"], list):
                errors.append("Tasks must be a list")
            else:
                for i, task in enumerate(plan_data["tasks"]):
                    task_errors = self._validate_task_structure(task, i)
                    errors.extend(task_errors)
        
        return errors
    
    def _validate_task_structure(self, task: Dict[str, Any], index: int) -> List[str]:
        """Validate individual task structure."""
        errors = []
        
        if not isinstance(task, dict):
            errors.append(f"Task at index {index} must be a dictionary")
            return errors
        
        for field in self.required_task_fields:
            if field not in task:
                errors.append(f"Task at index {index} missing required field: {field}")
        
        # Validate field types
        if "dependencies" in task and not isinstance(task["dependencies"], list):
            errors.append(f"Task at index {index}: dependencies must be a list")
        
        if "required_capabilities" in task and not isinstance(task["required_capabilities"], list):
            errors.append(f"Task at index {index}: required_capabilities must be a list")
        
        return errors
    
    def check_circular_dependencies(self, plan_data: Dict[str, Any]) -> bool:
        """
        Check for circular dependencies in the task graph.
        
        Args:
            plan_data: Plan dictionary
            
        Returns:
            True if circular dependencies exist, False otherwise
        """
        tasks = plan_data.get("tasks", [])
        if not tasks:
            return False
        
        # Build adjacency list
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        task_ids = set()
        
        for task in tasks:
            task_id = task.get("id")
            if not task_id:
                continue
                
            task_ids.add(task_id)
            dependencies = task.get("dependencies", [])
            
            for dep in dependencies:
                graph[dep].append(task_id)
                in_degree[task_id] += 1
        
        # Topological sort to detect cycles
        queue = deque([task_id for task_id in task_ids if in_degree[task_id] == 0])
        visited = 0
        
        while queue:
            current = queue.popleft()
            visited += 1
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # If we haven't visited all tasks, there's a cycle
        return visited < len(task_ids)
    
    def validate_task_references(self, plan_data: Dict[str, Any]) -> List[str]:
        """
        Validate that all task dependencies reference existing tasks.
        
        Args:
            plan_data: Plan dictionary
            
        Returns:
            List of validation errors
        """
        errors = []
        tasks = plan_data.get("tasks", [])
        
        # Collect all task IDs
        task_ids = {task.get("id") for task in tasks if task.get("id")}
        
        # Check each task's dependencies
        for task in tasks:
            task_id = task.get("id", "unknown")
            dependencies = task.get("dependencies", [])
            
            for dep in dependencies:
                if dep not in task_ids:
                    errors.append(f"Task '{task_id}' references non-existent dependency: '{dep}'")
        
        return errors
    
    def build_dependency_graph(self, plan_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Build a dependency graph from plan data.
        
        Args:
            plan_data: Plan dictionary
            
        Returns:
            Dict mapping task IDs to their dependencies
        """
        graph = {}
        tasks = plan_data.get("tasks", [])
        
        for task in tasks:
            task_id = task.get("id")
            if task_id:
                graph[task_id] = task.get("dependencies", [])
        
        return graph
    
    async def check_resource_availability(self, plan_data: Dict[str, Any]) -> List[str]:
        """
        Check if required capabilities/resources are available.
        
        Args:
            plan_data: Plan dictionary
            
        Returns:
            List of validation errors for missing resources
        """
        errors = []
        tasks = plan_data.get("tasks", [])
        
        # Collect all required capabilities
        required_capabilities = set()
        for task in tasks:
            caps = task.get("required_capabilities", [])
            required_capabilities.update(caps)
        
        # Check each capability
        for capability in required_capabilities:
            if not await self.check_capability_exists(capability):
                errors.append(f"Required capability not available: '{capability}'")
        
        return errors
    
    async def check_capability_exists(self, capability: str) -> bool:
        """
        Check if a capability exists in the system.
        
        Args:
            capability: Capability name
            
        Returns:
            True if capability exists, False otherwise
        """
        # For now, assume common capabilities exist
        # This would normally check against a capability registry
        known_capabilities = {
            "python", "nodejs", "docker", "kubernetes", 
            "aws", "azure", "gcp", "terraform", "ansible"
        }
        
        return capability.lower() in known_capabilities