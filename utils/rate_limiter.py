from typing import Optional
from datetime import datetime
from utils.cache import cache_service
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        self.cache = cache_service
        self.default_limit = 100  # Default requests per window
        self.default_window = 60  # Default window in seconds

    async def is_allowed(
        self,
        key: str,
        limit: Optional[int] = None,
        window: Optional[int] = None
    ) -> bool:
        """Check if request is allowed under rate limit"""
        limit = limit or self.default_limit
        window = window or self.default_window
        
        cache_key = f"rate_limit:{key}"
        
        try:
            # Get current count
            count = await self.cache.get(cache_key) or 0
            
            if count >= limit:
                logger.warning(f"Rate limit exceeded for {key}")
                return False
            
            # Increment counter
            await self.cache.set(
                cache_key,
                count + 1,
                ttl=window
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limiter error: {str(e)}")
            return True  # Allow on error to prevent blocking legitimate requests

    async def get_remaining(
        self,
        key: str,
        limit: Optional[int] = None
    ) -> int:
        """Get remaining requests in current window"""
        limit = limit or self.default_limit
        
        try:
            count = await self.cache.get(f"rate_limit:{key}") or 0
            return max(0, limit - count)
        except Exception as e:
            logger.error(f"Error getting rate limit remaining: {str(e)}")
            return 0

    async def reset(self, key: str) -> None:
        """Reset rate limit for a key"""
        try:
            await self.cache.delete(f"rate_limit:{key}")
        except Exception as e:
            logger.error(f"Error resetting rate limit: {str(e)}")


# Rate limits for different operations
class RateLimits:
    # Server operations
    SERVER_SYNC = 30       # Syncs per minute per server
    SERVER_METRICS = 12    # Metrics requests per minute per server
    SERVER_ACTION = 10     # Actions (start/stop/etc) per minute per server
    
    # API operations
    API_GENERAL = 1000     # General API requests per minute per IP
    API_WRITE = 100       # Write operations per minute per IP
    
    # User operations
    USER_LOGIN = 5        # Login attempts per minute per IP
    USER_REGISTER = 3     # Registration attempts per minute per IP


rate_limiter = RateLimiter() 