"""
Metrics collection for coord-hub-lite using Prometheus client.
"""

from typing import Dict, Any, Optional
from collections import defaultdict
import time

try:
    from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Provide dummy classes for testing
    class Counter:
        def labels(self, **kwargs): return self
        def inc(self, amount=1): pass
    
    class Histogram:
        def labels(self, **kwargs): return self
        def observe(self, amount): pass
        
    class Gauge:
        def labels(self, **kwargs): return self
        def set(self, value): pass
        
    class CollectorRegistry:
        pass


# Module-level metrics instances
task_metrics = None
agent_metrics = None  
request_metrics = None


class MetricsCollector:
    """Collects and exposes metrics for monitoring."""
    
    def __init__(self, use_prometheus: bool = True):
        self.use_prometheus = use_prometheus and PROMETHEUS_AVAILABLE
        self.registry = CollectorRegistry() if self.use_prometheus else None
        
        # Internal counters for testing
        self._tasks_created = defaultdict(int)
        self._tasks_completed = defaultdict(int)
        self._agents_active = defaultdict(int)
        self._http_requests = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        self._errors = defaultdict(int)
        self._plans_uploaded = defaultdict(int)
        
        # Initialize Prometheus metrics if available
        if self.use_prometheus:
            self._init_prometheus_metrics()
            
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metric instances."""
        # Task metrics
        self.prom_tasks_created = Counter(
            'tasks_created_total',
            'Total number of tasks created',
            ['type'],
            registry=self.registry
        )
        self.prom_tasks_completed = Counter(
            'tasks_completed_total', 
            'Total number of tasks completed',
            ['type'],
            registry=self.registry
        )
        self.prom_task_duration = Histogram(
            'task_duration_seconds',
            'Task execution duration in seconds',
            ['type'],
            registry=self.registry
        )
        
        # Agent metrics
        self.prom_agents_active = Gauge(
            'agents_active',
            'Number of active agents',
            ['type'],
            registry=self.registry
        )
        
        # HTTP metrics
        self.prom_http_requests = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['endpoint', 'method', 'status'],
            registry=self.registry
        )
        self.prom_http_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['endpoint', 'method'],
            registry=self.registry
        )
        
        # Error metrics
        self.prom_errors = Counter(
            'errors_total',
            'Total number of errors',
            ['type'],
            registry=self.registry
        )
        
        # Business metrics
        self.prom_plans_uploaded = Counter(
            'plans_uploaded_total',
            'Total number of plans uploaded',
            ['type'],
            registry=self.registry
        )
        
    def increment_task_created(self, task_type: str):
        """Increment task creation counter."""
        self._tasks_created[task_type] += 1
        
        if self.use_prometheus:
            self.prom_tasks_created.labels(type=task_type).inc()
            
    def increment_task_completed(self, task_type: str, duration_seconds: float):
        """Increment task completion counter and record duration."""
        self._tasks_completed[task_type] += 1
        
        if self.use_prometheus:
            self.prom_tasks_completed.labels(type=task_type).inc()
            self.prom_task_duration.labels(type=task_type).observe(duration_seconds)
            
    def set_agents_active(self, agent_type: str, count: int):
        """Set the number of active agents."""
        self._agents_active[agent_type] = count
        
        if self.use_prometheus:
            self.prom_agents_active.labels(type=agent_type).set(count)
            
    def increment_request(self, endpoint: str, method: str, status: int, duration: float):
        """Record HTTP request metrics."""
        self._http_requests[endpoint][method][str(status)] += 1
        
        if self.use_prometheus:
            self.prom_http_requests.labels(
                endpoint=endpoint,
                method=method,
                status=str(status)
            ).inc()
            self.prom_http_duration.labels(
                endpoint=endpoint,
                method=method
            ).observe(duration)
            
    def increment_error(self, error_type: str, error_message: str = None):
        """Increment error counter."""
        self._errors[error_type] += 1
        
        if self.use_prometheus:
            self.prom_errors.labels(type=error_type).inc()
            
    def increment_plan_uploaded(self, plan_type: str):
        """Increment plan upload counter."""
        self._plans_uploaded[plan_type] += 1
        
        if self.use_prometheus:
            self.prom_plans_uploaded.labels(type=plan_type).inc()
            
    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics as a dictionary."""
        return {
            "tasks_created_total": dict(self._tasks_created),
            "tasks_completed_total": dict(self._tasks_completed),
            "agents_active": dict(self._agents_active),
            "http_requests_total": {
                endpoint: {
                    method: dict(statuses)
                    for method, statuses in methods.items()
                }
                for endpoint, methods in self._http_requests.items()
            },
            "errors_total": dict(self._errors),
            "plans_uploaded_total": dict(self._plans_uploaded)
        }
        
    def get_prometheus_text(self) -> str:
        """Get metrics in Prometheus text format."""
        if self.use_prometheus and self.registry:
            return generate_latest(self.registry).decode('utf-8')
        else:
            # Generate a simple text format for testing
            lines = []
            
            # Tasks created
            lines.append("# HELP tasks_created_total Total tasks created")
            lines.append("# TYPE tasks_created_total counter")
            for task_type, count in self._tasks_created.items():
                lines.append(f'tasks_created_total{{type="{task_type}"}} {count}')
                
            # Tasks completed  
            lines.append("# HELP tasks_completed_total Total tasks completed")
            lines.append("# TYPE tasks_completed_total counter")
            for task_type, count in self._tasks_completed.items():
                lines.append(f'tasks_completed_total{{type="{task_type}"}} {count}')
                
            # Agents active
            lines.append("# HELP agents_active Number of active agents")
            lines.append("# TYPE agents_active gauge")
            for agent_type, count in self._agents_active.items():
                lines.append(f'agents_active{{type="{agent_type}"}} {count}')
                
            return "\n".join(lines) + "\n"


# Initialize global metrics collector
_global_collector = MetricsCollector(use_prometheus=False)  # Will be configured by app

# Export convenience functions
def get_global_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return _global_collector


def set_global_collector(collector: MetricsCollector):
    """Set the global metrics collector instance."""
    global _global_collector
    _global_collector = collector