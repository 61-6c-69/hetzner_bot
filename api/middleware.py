from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from utils.rate_limiter import rate_limiter, RateLimits
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        path = request.url.path
        method = request.method

        # Define rate limit based on path and method
        rate_limit = self._get_rate_limit(path, method)
        
        # Generate rate limit key
        key = f"{client_ip}:{path}"

        # Check rate limit
        if not await rate_limiter.is_allowed(key, limit=rate_limit):
            remaining = await rate_limiter.get_remaining(key, limit=rate_limit)
            
            # Add rate limit headers
            headers = {
                "X-RateLimit-Limit": str(rate_limit),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": "60"  # Reset after 1 minute
            }
            
            raise HTTPException(
                status_code=429,
                detail="Too many requests",
                headers=headers
            )

        # Get remaining requests for headers
        remaining = await rate_limiter.get_remaining(key, limit=rate_limit)
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = "60"
        
        return response

    def _get_rate_limit(self, path: str, method: str) -> int:
        """Get rate limit based on path and method"""
        
        # Server operations
        if path.startswith("/servers"):
            if method == "GET":
                return RateLimits.SERVER_METRICS
            return RateLimits.SERVER_ACTION
            
        # User authentication
        if path.startswith("/auth"):
            if "login" in path:
                return RateLimits.USER_LOGIN
            if "register" in path:
                return RateLimits.USER_REGISTER
            
        # Write operations
        if method in ["POST", "PUT", "PATCH", "DELETE"]:
            return RateLimits.API_WRITE
            
        # Default rate limit for general API usage
        return RateLimits.API_GENERAL 