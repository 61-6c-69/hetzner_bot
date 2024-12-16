from typing import Optional, Any
import json
from redis.asyncio import Redis

from core.settings import (
    REDIS_URL,
    REDIS_PASSWORD,
    REDIS_DB,
    CACHE_TTL_DEFAULT
)


class Redis:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Redis, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize Redis connection"""
        self.redis = Redis.from_url(
            REDIS_URL,
            password=REDIS_PASSWORD,
            db=REDIS_DB,
            decode_responses=True
        )
        self.default_ttl = CACHE_TTL_DEFAULT

    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None

    async def set(
            self,
            key: str,
            value: Any,
            ttl: Optional[int] = None
    ) -> bool:
        """Set value in Redis with optional TTL"""
        try:
            await self.redis.set(
                key,
                json.dumps(value),
                ex=ttl or self.default_ttl
            )
            return True
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        try:
            await self.redis.delete(key)
            return True
        except Exception:
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            return bool(await self.redis.exists(key))
        except Exception:
            return False

    async def increment(self, key: str) -> int:
        """Increment counter"""
        try:
            return await self.redis.incr(key)
        except Exception:
            return 0

    async def decrement(self, key: str) -> int:
        """Decrement counter"""
        try:
            return await self.redis.decr(key)
        except Exception:
            return 0

    async def set_add(self, key: str, value: str) -> bool:
        """Add value to set"""
        try:
            await self.redis.sadd(key, value)
            return True
        except Exception:
            return False

    async def set_remove(self, key: str, value: str) -> bool:
        """Remove value from set"""
        try:
            await self.redis.srem(key, value)
            return True
        except Exception:
            return False

    async def set_members(self, key: str) -> list:
        """Get all members of a set"""
        try:
            return list(await self.redis.smembers(key))
        except Exception:
            return []

    async def set_exists(self, key: str, value: str) -> bool:
        """Check if value exists in set"""
        try:
            return bool(await self.redis.sismember(key, value))
        except Exception:
            return False

    async def hash_set(
            self,
            key: str,
            field: str,
            value: Any,
            ttl: Optional[int] = None
    ) -> bool:
        """Set hash field"""
        try:
            await self.redis.hset(key, field, json.dumps(value))
            if ttl:
                await self.redis.expire(key, ttl)
            return True
        except Exception:
            return False

    async def hash_get(self, key: str, field: str) -> Optional[Any]:
        """Get hash field"""
        try:
            value = await self.redis.hget(key, field)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None

    async def hash_delete(self, key: str, field: str) -> bool:
        """Delete hash field"""
        try:
            await self.redis.hdel(key, field)
            return True
        except Exception:
            return False

    async def hash_exists(self, key: str, field: str) -> bool:
        """Check if hash field exists"""
        try:
            return bool(await self.redis.hexists(key, field))
        except Exception:
            return False

    async def hash_all(self, key: str) -> dict:
        """Get all hash fields"""
        try:
            result = {}
            data = await self.redis.hgetall(key)
            for field, value in data.items():
                result[field] = json.loads(value)
            return result
        except Exception:
            return {}

    async def list_push(
            self,
            key: str,
            value: Any,
            ttl: Optional[int] = None
    ) -> bool:
        """Push value to list"""
        try:
            await self.redis.lpush(key, json.dumps(value))
            if ttl:
                await self.redis.expire(key, ttl)
            return True
        except Exception:
            return False

    async def list_pop(self, key: str) -> Optional[Any]:
        """Pop value from list"""
        try:
            value = await self.redis.lpop(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None

    async def list_range(
            self,
            key: str,
            start: int = 0,
            end: int = -1
    ) -> list:
        """Get range of list"""
        try:
            result = []
            data = await self.redis.lrange(key, start, end)
            for value in data:
                result.append(json.loads(value))
            return result
        except Exception:
            return []

    async def list_length(self, key: str) -> int:
        """Get list length"""
        try:
            return await self.redis.llen(key)
        except Exception:
            return 0

    async def clear_all(self) -> bool:
        """Clear all keys (use with caution)"""
        try:
            await self.redis.flushdb()
            return True
        except Exception:
            return False
