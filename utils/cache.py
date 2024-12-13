from typing import Any, Optional
from config import REDIS_URL
from redis import Redis
import json


class CacheService:
    def __init__(self):
        self.redis = Redis.from_url(REDIS_URL)
        self.default_ttl = 120  # 2 minutes
        self.max_attempts = 3

    async def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Set a value in cache with TTL"""
        ttl = ttl or self.default_ttl
        self.redis.setex(
            name=key,
            time=ttl,
            value=json.dumps(value)
        )

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        value = self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def delete(self, key: str) -> None:
        """Delete a value from cache"""
        self.redis.delete(key)

    async def increment_attempts(self, key: str) -> int:
        """Increment failed attempts counter"""
        attempts_key = f"{key}:attempts"
        attempts = self.redis.incr(attempts_key)
        if not self.redis.ttl(attempts_key):
            self.redis.expire(attempts_key, self.default_ttl)
        return attempts

    async def get_attempts(self, key: str) -> int:
        """Get number of failed attempts"""
        attempts_key = f"{key}:attempts"
        attempts = self.redis.get(attempts_key)
        return int(attempts) if attempts else 0

    async def clear_attempts(self, key: str) -> None:
        """Clear failed attempts counter"""
        self.redis.delete(f"{key}:attempts")


cache_service = CacheService()
