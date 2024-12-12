from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from redis import asyncio as aioredis
from database.models import Base
from datetime import timedelta
from sqlalchemy import select
import pickle

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
        self.redis = aioredis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
        self.cache_ttl = timedelta(minutes=15)  # default TTL

    def _get_cache_key(self, key: str) -> str:
        """ساخت کلید یکتا برای cache"""
        return f"{self.model.__tablename__}:{key}"

    async def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """دریافت داده از cache"""
        data = await self.redis.get(cache_key)
        if data:
            return pickle.loads(await self.redis.get(cache_key))
        return None

    async def _set_cache(self, cache_key: str, value: Any):
        """ذخیره داده در cache"""
        await self.redis.set(
            cache_key,
            pickle.dumps(value),
            ex=int(self.cache_ttl.total_seconds())
        )

    async def _delete_cache(self, cache_key: str):
        """حذف داده از cache"""
        await self.redis.delete(cache_key)

    async def get(self, id: int) -> Optional[ModelType]:
        cache_key = self._get_cache_key(f"id:{id}")

        # سعی در دریافت از cache
        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        # دریافت از دیتابیس
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        item = result.scalar_one_or_none()

        if item:
            await self._set_cache(cache_key, item)

        return item

    async def get_all(self) -> List[ModelType]:
        cache_key = self._get_cache_key("all")

        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        result = await self.db.execute(select(self.model))
        items = result.scalars().all()

        await self._set_cache(cache_key, items)
        return items

    async def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.db.add(instance)
        await self.db.commit()
        await self.db.refresh(instance)

        # حذف cache های مرتبط
        await self._delete_cache(self._get_cache_key("all"))

        return instance

    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        instance = await self.get(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await self.db.commit()
            await self.db.refresh(instance)

            # بروزرسانی cache
            cache_key = self._get_cache_key(f"id:{id}")
            await self._set_cache(cache_key, instance)
            await self._delete_cache(self._get_cache_key("all"))

        return instance

    async def delete(self, id: int) -> bool:
        instance = await self.get(id)
        if instance:
            await self.db.delete(instance)
            await self.db.commit()

            # حذف از cache
            await self._delete_cache(self._get_cache_key(f"id:{id}"))
            await self._delete_cache(self._get_cache_key("all"))

            return True
        return False
