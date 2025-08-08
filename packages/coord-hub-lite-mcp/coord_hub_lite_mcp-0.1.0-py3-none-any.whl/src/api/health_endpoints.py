"""
Health check and metrics endpoints for coord-hub-lite.
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from src.monitoring.health import HealthChecker, HealthStatus
from src.monitoring.metrics import MetricsCollector, get_global_collector


# Global instances (will be initialized by the app)
_health_checker: Optional[HealthChecker] = None
_metrics_collector: Optional[MetricsCollector] = None


def set_health_checker(checker: HealthChecker):
    """Set the global health checker instance."""
    global _health_checker
    _health_checker = checker


def set_metrics_collector(collector: MetricsCollector):
    """Set the global metrics collector instance."""
    global _metrics_collector
    _metrics_collector = collector


async def health_check(health_checker: Optional[HealthChecker] = None) -> Dict[str, Any]:
    """
    Basic health check endpoint.
    Returns 200 with basic status information.
    """
    checker = health_checker or _health_checker
    
    try:
        if checker:
            result = await checker.check_all()
            status = result.overall_status.value
        else:
            status = "unknown"
            
        return {
            "status": status,
            "service": "coord-hub-lite",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "coord-hub-lite",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }


async def readiness_check(health_checker: Optional[HealthChecker] = None) -> Dict[str, Any]:
    """
    Readiness check endpoint for Kubernetes.
    Returns whether the service is ready to handle requests.
    """
    checker = health_checker or _health_checker
    
    try:
        if not checker:
            return {
                "ready": False,
                "status": "no_health_checker",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        result = await checker.check_all()
        
        # Service is ready if overall status is not unhealthy
        is_ready = result.overall_status != HealthStatus.UNHEALTHY
        
        # Check critical components (database)
        for component in result.components:
            if component.component == "database" and component.status == HealthStatus.UNHEALTHY:
                is_ready = False
                break
                
        return {
            "ready": is_ready,
            "status": result.overall_status.value,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "ready": False,
            "status": "error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }


async def health_details(health_checker: Optional[HealthChecker] = None) -> Dict[str, Any]:
    """
    Detailed health check endpoint.
    Returns comprehensive health information for all components.
    """
    checker = health_checker or _health_checker
    
    try:
        if not checker:
            return {
                "overall_status": "unknown",
                "components": {},
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": "Health checker not configured"
            }
            
        result = await checker.check_all()
        
        # Convert components to dict format
        components_dict = {}
        for component in result.components:
            components_dict[component.component] = {
                "status": component.status.value,
                "details": component.details
            }
            
        return {
            "overall_status": result.overall_status.value,
            "components": components_dict,
            "timestamp": result.timestamp.isoformat(),
            "service": "coord-hub-lite"
        }
        
    except Exception as e:
        return {
            "overall_status": "error",
            "components": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }


def metrics_endpoint(metrics_collector: Optional[MetricsCollector] = None) -> str:
    """
    Prometheus metrics endpoint.
    Returns metrics in Prometheus text format.
    """
    collector = metrics_collector or _metrics_collector or get_global_collector()
    
    try:
        return collector.get_prometheus_text()
    except Exception as e:
        # Return empty metrics on error
        return f"# Error generating metrics: {e}\n"


def create_health_endpoints(app, health_checker: HealthChecker, metrics_collector: MetricsCollector):
    """
    Register health check endpoints with the application.
    This is a helper function for integration with web frameworks.
    """
    # Set global instances
    set_health_checker(health_checker)
    set_metrics_collector(metrics_collector)
    
    # Return endpoint mappings for the framework to register
    return {
        "/health": health_check,
        "/health/ready": readiness_check,
        "/health/details": health_details,
        "/metrics": metrics_endpoint
    }