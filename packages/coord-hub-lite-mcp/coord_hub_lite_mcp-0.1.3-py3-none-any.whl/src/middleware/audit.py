"""
Audit middleware for request tracking and automatic logging.
Captures request/response details and integrates with audit service.
"""
import uuid
import time
import traceback
from datetime import datetime, timezone
from typing import Callable, Optional, Dict, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from services.audit_service import AuditService
from utils.audit_logger import AuditLogger


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic request/response auditing."""
    
    def __init__(
        self,
        app,
        get_session: Optional[Callable] = None,
        enable_request_logging: bool = True,
        enable_response_logging: bool = True,
        enable_error_logging: bool = True,
        log_request_body: bool = False,
        log_response_body: bool = False
    ):
        """Initialize audit middleware with configuration."""
        super().__init__(app)
        self.get_session = get_session
        self.enable_request_logging = enable_request_logging
        self.enable_response_logging = enable_response_logging
        self.enable_error_logging = enable_error_logging
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and log audit information."""
        # Generate correlation ID for request tracking
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        # Extract agent ID from headers
        agent_id = request.headers.get("x-agent-id", "system")
        request.state.agent_id = agent_id
        
        # Track timing
        start_time = time.time()
        
        # Log request if enabled
        if self.enable_request_logging and self.get_session:
            await self._log_request(request, correlation_id, agent_id)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log response if enabled
            if self.enable_response_logging and self.get_session:
                await self._log_response(
                    request, response, correlation_id, agent_id, duration_ms
                )
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log error if enabled
            if self.enable_error_logging and self.get_session:
                await self._log_error(
                    request, e, correlation_id, agent_id, duration_ms
                )
            
            # Re-raise exception
            raise
    
    async def _log_request(
        self,
        request: Request,
        correlation_id: str,
        agent_id: str
    ) -> None:
        """Log incoming request."""
        try:
            async with self.get_session() as session:
                audit_service = AuditService(session)
                
                meta_data = {
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "path": str(request.url.path),
                    "query_params": dict(request.query_params),
                    "headers": dict(request.headers),
                    "client_host": request.client.host if request.client else None
                }
                
                # Optionally include request body
                if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
                    try:
                        body = await request.body()
                        request._body = body  # Cache for later use
                        meta_data["body_size"] = len(body)
                    except:
                        pass
                
                await audit_service.create_audit_entry(
                    entity_type="http_request",
                    entity_id=correlation_id,
                    action="received",
                    actor=agent_id,
                    changes={},
                    meta_data=meta_data
                )
        except Exception as e:
            # Don't fail request if audit logging fails
            pass
    
    async def _log_response(
        self,
        request: Request,
        response: Response,
        correlation_id: str,
        agent_id: str,
        duration_ms: int
    ) -> None:
        """Log outgoing response."""
        try:
            async with self.get_session() as session:
                audit_service = AuditService(session)
                
                meta_data = {
                    "correlation_id": correlation_id,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "method": request.method,
                    "path": str(request.url.path)
                }
                
                # Optionally include response headers
                if hasattr(response, "headers"):
                    meta_data["response_headers"] = dict(response.headers)
                
                await audit_service.create_audit_entry(
                    entity_type="http_response",
                    entity_id=correlation_id,
                    action="sent",
                    actor=agent_id,
                    changes={},
                    meta_data=meta_data
                )
        except Exception as e:
            # Don't fail response if audit logging fails
            pass
    
    async def _log_error(
        self,
        request: Request,
        error: Exception,
        correlation_id: str,
        agent_id: str,
        duration_ms: int
    ) -> None:
        """Log request error."""
        try:
            async with self.get_session() as session:
                audit_service = AuditService(session)
                
                await audit_service.log_error(
                    entity_type="http_request",
                    entity_id=correlation_id,
                    error_type=type(error).__name__,
                    error_message=str(error),
                    actor=agent_id,
                    stack_trace=traceback.format_exc(),
                    context={
                        "method": request.method,
                        "path": str(request.url.path),
                        "duration_ms": duration_ms
                    }
                )
        except Exception as e:
            # Don't fail if error logging fails
            pass


def create_audit_middleware(
    get_session: Callable,
    **kwargs
) -> AuditMiddleware:
    """Factory function to create audit middleware with session provider."""
    return lambda app: AuditMiddleware(app, get_session=get_session, **kwargs)