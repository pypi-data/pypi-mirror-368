"""
Tree builder utility for creating hierarchical task visualizations.
Builds JSON-serializable tree structures from task relationships.
"""
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from src.database.models import Task


class TreeBuilder:
    """Utility for building task dependency trees."""
    
    def build_tree(
        self,
        tasks: List[Task],
        root_id: Optional[int] = None,
        status_filter: Optional[List[str]] = None,
        include_metadata: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Build a hierarchical tree from a list of tasks.
        
        Args:
            tasks: List of Task objects with relationships loaded
            root_id: ID of root task to start from
            status_filter: Only include tasks with these statuses
            include_metadata: Whether to include task metadata
            
        Returns:
            Tree structure as nested dict, None if root not found
        """
        # Create task lookup
        task_map = {task.id: task for task in tasks}
        
        # Find root task
        if root_id:
            root = task_map.get(root_id)
            if not root:
                return None
        else:
            # Find tasks with no dependencies (roots)
            roots = [t for t in tasks if not t.dependencies]
            if not roots:
                return None
            root = roots[0]
        
        # Build tree recursively
        return self._build_node(root, task_map, status_filter, include_metadata, set())
    
    def build_forest(
        self,
        tasks: List[Task],
        status_filter: Optional[List[str]] = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Build multiple trees (forest) from tasks with no common root.
        
        Args:
            tasks: List of all tasks
            status_filter: Only include tasks with these statuses
            include_metadata: Whether to include metadata
            
        Returns:
            List of tree structures
        """
        # Find all root tasks (no dependencies)
        roots = [t for t in tasks if not t.dependencies]
        
        # Apply status filter to roots if specified
        if status_filter:
            roots = [r for r in roots if r.status in status_filter]
        
        # Create task lookup
        task_map = {task.id: task for task in tasks}
        
        # Build tree for each root
        forest = []
        for root in roots:
            tree = self._build_node(root, task_map, status_filter, include_metadata, set())
            if tree:  # Only add non-empty trees
                forest.append(tree)
        
        return forest
    
    def _build_node(
        self,
        task: Task,
        task_map: Dict[int, Task],
        status_filter: Optional[List[str]],
        include_metadata: bool,
        visited: Set[int]
    ) -> Optional[Dict[str, Any]]:
        """
        Recursively build a node and its children.
        
        Args:
            task: Current task node
            task_map: Lookup map of all tasks
            status_filter: Status filter to apply
            include_metadata: Whether to include metadata
            visited: Set of visited task IDs to prevent cycles
            
        Returns:
            Node dict or None if filtered out
        """
        # Check status filter
        if status_filter and task.status not in status_filter:
            return None
        
        # Prevent infinite recursion
        if task.id in visited:
            return {
                'id': task.id,
                'title': task.title,
                'circular_reference': True,
                'children': []
            }
        
        visited.add(task.id)
        
        # Build node
        node = {
            'id': task.id,
            'title': task.title,
            'status': task.status,
            'agent_id': task.agent_id,
            'priority': task.priority,
            'created_at': task.created_at.isoformat() if task.created_at else None,
            'updated_at': task.updated_at.isoformat() if task.updated_at else None,
            'children': []
        }
        
        # Add metadata if requested
        if include_metadata and task.meta_data:
            node['metadata'] = task.meta_data
        
        # Add completion time if completed
        if task.completed_at:
            node['completed_at'] = task.completed_at.isoformat()
        
        # Build children (dependents)
        for dependent in task.dependents:
            if dependent.id in task_map:
                child_node = self._build_node(
                    dependent, 
                    task_map, 
                    status_filter, 
                    include_metadata,
                    visited.copy()  # New visited set for each branch
                )
                if child_node:
                    node['children'].append(child_node)
        
        return node
    
    def has_circular_dependencies(self, tasks: List[Task]) -> bool:
        """
        Check if the task graph has circular dependencies.
        
        Args:
            tasks: List of tasks to check
            
        Returns:
            True if circular dependencies exist
        """
        # Build adjacency list
        graph = {}
        for task in tasks:
            graph[task.id] = [dep.id for dep in task.dependencies]
        
        # Track visited and recursion stack
        visited = set()
        rec_stack = set()
        
        def has_cycle(task_id: int) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)
            
            # Check all dependencies
            for dep_id in graph.get(task_id, []):
                if dep_id not in visited:
                    if has_cycle(dep_id):
                        return True
                elif dep_id in rec_stack:
                    return True
            
            rec_stack.remove(task_id)
            return False
        
        # Check each unvisited task
        for task_id in graph:
            if task_id not in visited:
                if has_cycle(task_id):
                    return True
        
        return False
    
    def get_task_stats(self, tree: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate statistics from a task tree.
        
        Args:
            tree: Tree structure from build_tree
            
        Returns:
            Statistics dict
        """
        stats = {
            'total_tasks': 0,
            'by_status': {},
            'by_agent': {},
            'unassigned': 0,
            'max_depth': 0
        }
        
        def traverse(node: Dict[str, Any], depth: int = 0):
            stats['total_tasks'] += 1
            stats['max_depth'] = max(stats['max_depth'], depth)
            
            # Count by status
            status = node.get('status')
            if status:
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
            # Count by agent
            agent_id = node.get('agent_id')
            if agent_id:
                stats['by_agent'][agent_id] = stats['by_agent'].get(agent_id, 0) + 1
            else:
                stats['unassigned'] += 1
            
            # Traverse children
            for child in node.get('children', []):
                traverse(child, depth + 1)
        
        if tree:
            traverse(tree)
        
        return stats