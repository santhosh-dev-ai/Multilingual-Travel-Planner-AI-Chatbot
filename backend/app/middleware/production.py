"""
Production Middleware - Error handling, logging, rate limiting
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Callable, Optional
import time
import logging
from datetime import datetime
from collections import defaultdict

from app.models.responses import ErrorResponse


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """
    Log all incoming requests and responses
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        
        # Extract request info
        request = Request(scope, receive)
        method = request.method
        path = request.url.path
        client = request.client.host if request.client else "unknown"
        
        logger.info(f"Request: {method} {path} from {client}")
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                duration = time.time() - start_time
                logger.info(
                    f"Response: {method} {path} - {status_code} - {duration:.3f}s"
                )
            await send(message)
        
        await self.app(scope, receive, send_wrapper)


class ErrorHandlerMiddleware:
    """
    Centralized error handling with consistent responses
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        try:
            await self.app(scope, receive, send)
        except HTTPException as e:
            # FastAPI HTTP exceptions
            error_response = ErrorResponse(
                error=e.__class__.__name__,
                message=str(e.detail),
                path=scope["path"],
                timestamp=datetime.utcnow()
            )
            
            response = JSONResponse(
                status_code=e.status_code,
                content=error_response.model_dump()
            )
            
            await response(scope, receive, send)
            
        except Exception as e:
            # Unexpected errors
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            
            error_response = ErrorResponse(
                error="InternalServerError",
                message="An unexpected error occurred",
                details={"error_type": e.__class__.__name__},
                path=scope["path"],
                timestamp=datetime.utcnow()
            )
            
            response = JSONResponse(
                status_code=500,
                content=error_response.model_dump()
            )
            
            await response(scope, receive, send)


class RateLimitMiddleware:
    """
    Simple rate limiting middleware
    In production, use Redis for distributed rate limiting
    """
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000
    ):
        self.app = app
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # Track requests per IP
        self.minute_requests = defaultdict(list)
        self.hour_requests = defaultdict(list)
    
    def _clean_old_requests(self, client_ip: str):
        """Remove requests outside time windows"""
        now = time.time()
        minute_ago = now - 60
        hour_ago = now - 3600
        
        # Clean minute window
        self.minute_requests[client_ip] = [
            t for t in self.minute_requests[client_ip] if t > minute_ago
        ]
        
        # Clean hour window
        self.hour_requests[client_ip] = [
            t for t in self.hour_requests[client_ip] if t > hour_ago
        ]
    
    def _is_rate_limited(self, client_ip: str) -> tuple[bool, str]:
        """Check if client is rate limited"""
        self._clean_old_requests(client_ip)
        
        minute_count = len(self.minute_requests[client_ip])
        hour_count = len(self.hour_requests[client_ip])
        
        if minute_count >= self.requests_per_minute:
            return True, "Rate limit exceeded: Too many requests per minute"
        
        if hour_count >= self.requests_per_hour:
            return True, "Rate limit exceeded: Too many requests per hour"
        
        return False, ""
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Extract client IP
        client = scope.get("client")
        client_ip = client[0] if client else "unknown"
        
        # Check rate limit
        is_limited, message = self._is_rate_limited(client_ip)
        
        if is_limited:
            error_response = ErrorResponse(
                error="RateLimitExceeded",
                message=message,
                path=scope["path"],
                timestamp=datetime.utcnow()
            )
            
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=error_response.model_dump(),
                headers={
                    "Retry-After": "60"
                }
            )
            
            await response(scope, receive, send)
            return
        
        # Record request
        now = time.time()
        self.minute_requests[client_ip].append(now)
        self.hour_requests[client_ip].append(now)
        
        await self.app(scope, receive, send)


class CacheControlMiddleware:
    """
    Add cache control headers for appropriate responses
    """
    
    def __init__(self, app):
        self.app = app
        
        # Define cache strategies per route pattern
        self.cache_rules = {
            "/api/destinations": "public, max-age=300",  # 5 minutes
            "/api/weather": "public, max-age=600",  # 10 minutes
            "/static": "public, max-age=86400",  # 1 day
            "/health": "no-cache",
        }
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        path = scope["path"]
        
        # Determine cache control
        cache_control = "no-cache"
        for pattern, control in self.cache_rules.items():
            if path.startswith(pattern):
                cache_control = control
                break
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"cache-control", cache_control.encode()))
                message["headers"] = headers
            await send(message)
        
        await self.app(scope, receive, send_wrapper)


# Utility functions for dependency injection

def get_current_user(request: Request) -> Optional[str]:
    """
    Extract current user from request
    In production, implement proper authentication
    """
    # Check for user_id in headers or session
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        user_id = request.cookies.get("user_id")
    return user_id


def get_session_id(request: Request) -> Optional[str]:
    """Extract session ID from request"""
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        session_id = request.cookies.get("session_id")
    return session_id


def require_user() -> Callable:
    """
    Dependency that requires authenticated user
    """
    def _require_user(request: Request) -> str:
        user_id = get_current_user(request)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        return user_id
    
    return _require_user
