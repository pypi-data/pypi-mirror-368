"""Utilities for working with task metadata"""
from typing import Dict, Any, Optional, List, Set
from src.models.metadata_schemas import TaskMetadata


def parse_metadata(raw_metadata: Dict[str, Any]) -> TaskMetadata:
    """Parse raw metadata into structured schema"""
    return TaskMetadata(**raw_metadata)


def merge_metadata(
    existing: Dict[str, Any],
    updates: Dict[str, Any],
    preserve_fields: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Merge metadata updates while preserving specified fields"""
    if preserve_fields is None:
        preserve_fields = ["parent_task_id", "created_at", "completion_time"]
    
    result = existing.copy()
    
    for key, value in updates.items():
        if key not in preserve_fields or key not in existing:
            result[key] = value
    
    return result


def validate_dependencies(
    task_id: int,
    dependencies: List[int]
) -> List[str]:
    """Validate dependency list for issues"""
    errors = []
    
    if task_id in dependencies:
        errors.append("Task cannot depend on itself")
    
    if len(dependencies) != len(set(dependencies)):
        errors.append("Duplicate dependencies found")
    
    return errors


def extract_keywords(text: str) -> List[str]:
    """Extract keywords from task description for capability matching"""
    # Common technical keywords to look for
    keywords_map = {
        "python": ["python", "py", "pytest", "fastapi", "django", "flask"],
        "javascript": ["javascript", "js", "typescript", "ts", "react", "vue", "angular", "node"],
        "docker": ["docker", "container", "dockerfile", "compose"],
        "database": ["database", "db", "sql", "postgres", "mysql", "mongodb", "redis"],
        "api": ["api", "rest", "graphql", "endpoint", "swagger", "openapi"],
        "frontend": ["frontend", "ui", "ux", "html", "css", "styling"],
        "backend": ["backend", "server", "service", "microservice"],
        "testing": ["test", "testing", "unit test", "integration test", "e2e"],
        "security": ["security", "auth", "authentication", "authorization", "jwt", "oauth"],
        "devops": ["devops", "ci", "cd", "pipeline", "deployment", "kubernetes", "k8s"]
    }
    
    text_lower = text.lower()
    found_keywords = []
    
    for category, terms in keywords_map.items():
        for term in terms:
            if term in text_lower:
                found_keywords.append(category)
                break
    
    return list(set(found_keywords))


def calculate_task_priority_score(
    task: Dict[str, Any],
    is_on_critical_path: bool = False,
    blocked_task_count: int = 0
) -> float:
    """Calculate priority score for task scheduling"""
    # Base scores by priority
    priority_scores = {
        "critical": 100,
        "high": 75,
        "medium": 50,
        "low": 25
    }
    
    score = priority_scores.get(task.get("priority", "medium"), 50)
    
    # Boost if on critical path
    if is_on_critical_path:
        score *= 1.5
    
    # Boost based on blocked tasks
    score += blocked_task_count * 10
    
    # Penalty if already has many dependencies
    metadata = parse_metadata(task.get("metadata", {}))
    score -= len(metadata.depends_on) * 5
    
    return score


async def find_circular_dependencies(
    task_graph: Dict[int, List[int]],
    start_task: int,
    visited: Optional[Set[int]] = None,
    path: Optional[List[int]] = None
) -> Optional[List[int]]:
    """
    Find circular dependencies in task graph
    
    Args:
        task_graph: Dict mapping task_id to list of dependency_ids
        start_task: Task to start checking from
        visited: Set of visited tasks (for optimization)
        path: Current path being explored
        
    Returns:
        List of task IDs forming a cycle, or None if no cycle
    """
    if visited is None:
        visited = set()
    if path is None:
        path = []
    
    if start_task in path:
        # Found cycle - return the cycle portion
        cycle_start = path.index(start_task)
        return path[cycle_start:] + [start_task]
    
    if start_task in visited:
        return None
    
    visited.add(start_task)
    path.append(start_task)
    
    for dependency in task_graph.get(start_task, []):
        cycle = await find_circular_dependencies(task_graph, dependency, visited, path.copy())
        if cycle:
            return cycle
    
    return None


def format_metadata_for_display(metadata: Dict[str, Any]) -> str:
    """Format metadata for human-readable display"""
    parsed = parse_metadata(metadata)
    lines = []
    
    if parsed.parent_task_id:
        lines.append(f"Parent Task: #{parsed.parent_task_id}")
    
    if parsed.phase:
        lines.append(f"Phase: {parsed.phase}")
    
    if parsed.depends_on:
        lines.append(f"Depends on: {', '.join(f'#{id}' for id in parsed.depends_on)}")
    
    if parsed.blocks:
        lines.append(f"Blocks: {', '.join(f'#{id}' for id in parsed.blocks)}")
    
    if parsed.exclusive_files:
        lines.append(f"Exclusive files: {len(parsed.exclusive_files)} files")
    
    if parsed.parallel_group:
        lines.append(f"Parallel group: {parsed.parallel_group}")
    
    if parsed.review_required:
        lines.append("Review required: Yes")
    
    if parsed.estimated_hours:
        lines.append(f"Estimated: {parsed.estimated_hours} hours")
    
    if parsed.blocker_reason:
        lines.append(f"Blocked: {parsed.blocker_reason}")
    
    return "\n".join(lines)