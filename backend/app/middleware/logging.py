import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import log_api_request, log_api_response, get_logger

logger = get_logger("middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all API requests and responses in structured format"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Extract user info if available
        user_id = None
        tenant_id = None
        if hasattr(request.state, "user"):
            user_id = str(request.state.user.id)
            tenant_id = request.state.user.tenant_id
        
        # Get client IP
        client_ip = request.client.host if request.client else None
        
        # Log request
        start_time = time.time()
        
        log_api_request(
            method=request.method,
            path=str(request.url.path),
            user_id=user_id,
            tenant_id=tenant_id,
            request_id=request_id,
            client_ip=client_ip,
            user_agent=request.headers.get("user-agent"),
            query_params=dict(request.query_params) if request.query_params else None
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate response time
            process_time = (time.time() - start_time) * 1000
            
            # Log response
            log_api_response(
                method=request.method,
                path=str(request.url.path),
                status_code=response.status_code,
                response_time_ms=process_time,
                user_id=user_id,
                tenant_id=tenant_id,
                request_id=request_id
            )
            
            # Add request ID to response headers for tracking
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Calculate response time for failed requests
            process_time = (time.time() - start_time) * 1000
            
            # Log error response
            logger.error(
                f"Request failed: {str(e)}",
                extra={
                    "event_type": "api_error",
                    "method": request.method,
                    "path": str(request.url.path),
                    "user_id": user_id,
                    "tenant_id": tenant_id,
                    "request_id": request_id,
                    "response_time_ms": process_time,
                    "error": str(e)
                },
                exc_info=True
            )
            
            # Re-raise the exception to be handled by FastAPI
            raise