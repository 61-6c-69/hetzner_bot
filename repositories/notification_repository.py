from database.models import NotificationSettings, Base
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.base import BaseRepository
from core.settings import CACHE_TTL_DEFAULT
from typing import Optional, TypeVar
from datetime import timedelta
from sqlalchemy import select

ModelType = TypeVar("ModelType", bound=Base)


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
