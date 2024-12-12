from typing import List, Optional, Any, TypeVar, Generic, Type, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database.models import NotificationSettings, Base
from datetime import timedelta, datetime
import pickle
import redis
from core.settings import CACHE_TTL_DEFAULT

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.cache_ttl = timedelta(minutes=5)

    def _get_cache_key(self, key: str) -> str:
        return f"{self.model.__name__}:{key}"

    async def _get_from_cache(self, cache_key: str) -> Any:
        data = self.redis.get(cache_key)
        if data:
            return pickle.loads(cast(bytes, data))
        return None

    async def _set_cache(self, cache_key: str, value: Any):
        self.redis.set(
            cache_key,
            pickle.dumps(value),
            ex=int(self.cache_ttl.total_seconds())
        )

    async def get(self, id: int) -> Optional[ModelType]:
        cache_key = self._get_cache_key(str(id))

        cached_item = await self._get_from_cache(cache_key)
        if cached_item:
            return cached_item

        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        item = result.scalar_one_or_none()

        if item:
            await self._set_cache(cache_key, item)

        return item


class NotificationRepository(BaseRepository[NotificationSettings]):
    def __init__(self, db: AsyncSession):
        super().__init__(NotificationSettings, db)
        self.cache_ttl = timedelta(seconds=CACHE_TTL_DEFAULT)

    async def get_by_user_id(self, user_id: int) -> Optional[NotificationSettings]:
        """Get notification settings by user ID"""
        cache_key = self._get_cache_key(f"user:{user_id}")

        cached_settings = await self._get_from_cache(cache_key)
        if cached_settings:
            return cached_settings

        result = await self.db.execute(
            select(NotificationSettings)
            .where(NotificationSettings.user_id == user_id)
        )
        settings = result.scalar_one_or_none()

        if settings:
            await self._set_cache(cache_key, settings)

        return settings

    async def get_or_create(self, user_id: int) -> NotificationSettings:
        """Get or create notification settings for a user"""
        settings = await self.get_by_user_id(user_id)
        if not settings:
            settings = NotificationSettings(
                user_id=user_id,
                server_notifications=True,
                payment_notifications=True,
                ticket_notifications=True,
                low_balance_threshold=50000
            )
            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(settings)

            # Update cache
            cache_key = self._get_cache_key(f"user:{user_id}")
            await self._set_cache(cache_key, settings)

        return settings

    async def update(
            self,
            user_id: int,
            server_notifications: Optional[bool] = None,
            payment_notifications: Optional[bool] = None,
            ticket_notifications: Optional[bool] = None,
            low_balance_threshold: Optional[int] = None
    ) -> Optional[NotificationSettings]:
        """Update notification settings"""
        settings = await self.get_by_user_id(user_id)
        if settings:
            if server_notifications is not None:
                settings.server_notifications = server_notifications
            if payment_notifications is not None:
                settings.payment_notifications = payment_notifications
            if ticket_notifications is not None:
                settings.ticket_notifications = ticket_notifications
            if low_balance_threshold is not None:
                settings.low_balance_threshold = low_balance_threshold

            await self.db.commit()
            await self.db.refresh(settings)

            # Update cache
            cache_key = self._get_cache_key(f"user:{user_id}")
            await self._set_cache(cache_key, settings)

        return settings

    async def delete(self, user_id: int) -> bool:
        """Delete notification settings"""
        settings = await self.get_by_user_id(user_id)
        if settings:
            await self.db.delete(settings)
            await self.db.commit()

            # Clear cache
            cache_key = self._get_cache_key(f"user:{user_id}")
            await self.redis.delete(cache_key)

            return True
        return False
