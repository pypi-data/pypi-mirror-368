"""
Health checking functionality for coord-hub-lite.
"""

import asyncio
import time
import shutil
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass

try:
    import psutil
except ImportError:
    psutil = None  # Handle gracefully if not installed


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    UNHEALTHY = "unhealthy"


@dataclass
class ComponentHealth:
    """Health status of a single component."""
    component: str
    status: HealthStatus
    details: Dict[str, Any]
    
    
@dataclass 
class HealthCheckResult:
    """Overall health check result."""
    overall_status: HealthStatus
    components: List[ComponentHealth]
    timestamp: datetime


class HealthChecker:
    """Performs health checks on various system components."""
    
    def __init__(
        self,
        db_session=None,
        timeout_seconds: float = 5.0,
        cache_ttl_seconds: float = 30.0,
        disk_threshold_percent: float = 20.0,
        memory_threshold_percent: float = 85.0
    ):
        self.db_session = db_session
        self.timeout_seconds = timeout_seconds
        self.cache_ttl_seconds = cache_ttl_seconds
        self.disk_threshold_percent = disk_threshold_percent
        self.memory_threshold_percent = memory_threshold_percent
        self._cache: Dict[str, tuple[ComponentHealth, datetime]] = {}
        
    async def check_database(self) -> ComponentHealth:
        """Check database connectivity and response time."""
        cache_key = "database"
        
        # Check cache
        if cache_key in self._cache:
            result, timestamp = self._cache[cache_key]
            if datetime.now(timezone.utc) - timestamp < timedelta(seconds=self.cache_ttl_seconds):
                return result
                
        start_time = time.time()
        
        try:
            if self.db_session:
                # Simple query to test connectivity
                result = await self.db_session.execute("SELECT 1")
                result.scalar()
                
            response_time_ms = (time.time() - start_time) * 1000
            
            health = ComponentHealth(
                component="database",
                status=HealthStatus.HEALTHY,
                details={
                    "response_time_ms": round(response_time_ms, 2)
                }
            )
            
        except Exception as e:
            health = ComponentHealth(
                component="database",
                status=HealthStatus.UNHEALTHY,
                details={
                    "error": str(e),
                    "response_time_ms": (time.time() - start_time) * 1000
                }
            )
            
        # Cache the result
        self._cache[cache_key] = (health, datetime.now(timezone.utc))
        return health
        
    async def check_disk_space(self) -> ComponentHealth:
        """Check available disk space."""
        try:
            usage = shutil.disk_usage("/")
            
            total_gb = usage.total / (1024**3)
            free_gb = usage.free / (1024**3)
            percent_free = (usage.free / usage.total) * 100
            
            if percent_free < 10:
                status = HealthStatus.UNHEALTHY
            elif percent_free < self.disk_threshold_percent:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
                
            return ComponentHealth(
                component="disk",
                status=status,
                details={
                    "total_gb": round(total_gb, 2),
                    "free_gb": round(free_gb, 2),
                    "percent_free": round(percent_free, 2)
                }
            )
            
        except Exception as e:
            return ComponentHealth(
                component="disk",
                status=HealthStatus.UNHEALTHY,
                details={"error": str(e)}
            )
            
    async def check_memory(self) -> ComponentHealth:
        """Check memory usage."""
        if psutil is None:
            return ComponentHealth(
                component="memory",
                status=HealthStatus.DEGRADED,
                details={"warning": "psutil not installed, memory check unavailable"}
            )
            
        try:
            memory = psutil.virtual_memory()
            
            total_gb = memory.total / (1024**3)
            available_gb = memory.available / (1024**3)
            percent_used = memory.percent
            
            if percent_used > 95:
                status = HealthStatus.UNHEALTHY
            elif percent_used > self.memory_threshold_percent:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
                
            return ComponentHealth(
                component="memory",
                status=status,
                details={
                    "total_gb": round(total_gb, 2),
                    "available_gb": round(available_gb, 2),
                    "percent_used": round(percent_used, 2)
                }
            )
            
        except Exception as e:
            return ComponentHealth(
                component="memory",
                status=HealthStatus.UNHEALTHY,
                details={"error": str(e)}
            )
            
    async def check_all(self) -> HealthCheckResult:
        """Run all health checks with timeout."""
        components = []
        checks = [
            ("database", self.check_database()),
            ("disk", self.check_disk_space()),
            ("memory", self.check_memory())
        ]
        
        for component_name, check_coro in checks:
            try:
                result = await asyncio.wait_for(
                    check_coro,
                    timeout=self.timeout_seconds
                )
                components.append(result)
            except asyncio.TimeoutError:
                components.append(
                    ComponentHealth(
                        component=component_name,
                        status=HealthStatus.UNHEALTHY,
                        details={"error": f"Health check timeout after {self.timeout_seconds}s"}
                    )
                )
            except Exception as e:
                components.append(
                    ComponentHealth(
                        component=component_name,
                        status=HealthStatus.UNHEALTHY,
                        details={"error": str(e)}
                    )
                )
                
        # Determine overall status (worst status wins)
        overall_status = HealthStatus.HEALTHY
        for component in components:
            if component.status == HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.UNHEALTHY
                break
            elif component.status == HealthStatus.DEGRADED and overall_status != HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.DEGRADED
                
        return HealthCheckResult(
            overall_status=overall_status,
            components=components,
            timestamp=datetime.now(timezone.utc)
        )