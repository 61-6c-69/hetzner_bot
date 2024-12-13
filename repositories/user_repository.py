from database.models import User, Transaction, Base, NotificationSettings
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, TypeVar
from datetime import datetime, timedelta
from sqlalchemy import select, func
from api import schemas

from repositories.base import BaseRepository

ModelType = TypeVar("ModelType", bound=Base)


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
        self.cache_ttl = timedelta(minutes=30)

    async def get_by_phone(self, phone: str) -> Optional[User]:
        """Get user by phone number"""
        cache_key = self._get_cache_key(f"phone:{phone}")

        cached_user = await self._get_from_cache(cache_key)
        if cached_user:
            return cached_user

        result = await self.db.execute(
            select(User).where(User.phone == phone)
        )
        user = result.scalar_one_or_none()

        if user:
            await self._set_cache(cache_key, user)

        return user

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        cache_key = self._get_cache_key(f"telegram:{telegram_id}")

        cached_user = await self._get_from_cache(cache_key)
        if cached_user:
            return cached_user

        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if user:
            await self._set_cache(cache_key, user)

        return user

    async def create(
            self,
            phone: str,
            username: Optional[str] = None,
            email: Optional[str] = None,
            telegram_id: Optional[int] = None,
            password_hash: Optional[str] = None
    ) -> User:
        """Create a new user"""
        user = User(
            phone=phone,
            username=username,
            email=email,
            telegram_id=telegram_id,
            password_hash=password_hash,
            is_active=True,
            created_at=datetime.utcnow()
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(
            self,
            user_id: int,
            **kwargs
    ) -> Optional[User]:
        """Update user fields"""
        user = await self.get(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            await self.db.commit()
            await self.db.refresh(user)

            # Update cache
            cache_key = self._get_cache_key(str(user_id))
            await self._set_cache(cache_key, user)

            # Update phone cache if phone is updated
            if 'phone' in kwargs:
                phone_cache_key = self._get_cache_key(f"phone:{kwargs['phone']}")
                await self._set_cache(phone_cache_key, user)

            # Update telegram cache if telegram_id is updated
            if 'telegram_id' in kwargs:
                telegram_cache_key = self._get_cache_key(f"telegram:{kwargs['telegram_id']}")
                await self._set_cache(telegram_cache_key, user)

        return user

    async def get_balance(self, user_id: int) -> float:
        """Get user's current balance"""
        result = await self.db.execute(
            select(func.sum(Transaction.amount))
            .where(
                Transaction.user_id == user_id,
                Transaction.status == 'completed'
            )
        )
        balance = result.scalar()
        return float(balance if balance is not None else 0.0)

    async def list_users(
            self,
            skip: int = 0,
            limit: int = 50,
            active_only: bool = True
    ) -> List[User]:
        """Get list of users"""
        query = select(User)
        if active_only:
            query = query.where(User.is_active == True)
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_telegram_users(self) -> List[User]:
        """Get users with Telegram ID"""
        result = await self.db.execute(
            select(User).where(User.telegram_id.isnot(None))
        )
        return list(result.scalars().all())

    async def deactivate(self, user_id: int) -> Optional[User]:
        """Deactivate a user"""
        return await self.update(user_id, is_active=False)

    async def activate(self, user_id: int) -> Optional[User]:
        """Activate a user"""
        return await self.update(user_id, is_active=True)

    async def connect_telegram(
            self,
            user_id: int,
            telegram_id: int
    ) -> Optional[User]:
        """Connect Telegram account to user"""
        return await self.update(user_id, telegram_id=telegram_id)

    async def disconnect_telegram(self, user_id: int) -> Optional[User]:
        """Disconnect Telegram account from user"""
        return await self.update(user_id, telegram_id=None)

    async def get_user_stats(self, user_id: int) -> dict:
        """Get user statistics"""
        # Get total transactions
        transactions_result = await self.db.execute(
            select(
                func.count(Transaction.id).label('total_transactions'),
                func.sum(Transaction.amount).label('total_amount')
            )
            .where(
                Transaction.user_id == user_id,
                Transaction.status == 'completed'
            )
        )
        row = transactions_result.first()

        return {
            'total_transactions': row.total_transactions if row else 0,
            'total_amount': float(row.total_amount if row and row.total_amount else 0.0)
        }

    async def update_telegram_id(
            self,
            user_id: int,
            telegram_id: int
    ) -> Optional[User]:
        """Update user's telegram ID"""
        user = await self.get(user_id)
        if user:
            user.telegram_id = telegram_id
            await self.db.commit()
            await self.db.refresh(user)
        return user

    async def update_settings(
            self,
            user_id: int,
            settings: schemas.UserSettingsUpdate
    ) -> Optional[User]:
        """Update user settings"""
        user = await self.get(user_id)
        if not user:
            return None

        # Update user fields if provided
        if settings.first_name is not None:
            user.first_name = settings.first_name
        if settings.last_name is not None:
            user.last_name = settings.last_name
        if settings.email is not None:
            user.email = settings.email
        if settings.phone is not None:
            user.phone = settings.phone
        if settings.telegram_id is not None:
            user.telegram_id = settings.telegram_id

        # Update notification settings if provided
        if settings.notification_settings:
            result = await self.db.execute(
                select(NotificationSettings)
                .where(NotificationSettings.user_id == user_id)
            )
            notification_settings = result.scalar_one_or_none()

            if notification_settings:
                for key, value in settings.notification_settings.dict(exclude_unset=True).items():
                    setattr(notification_settings, key, value)
            else:
                notification_settings = NotificationSettings(
                    user_id=user_id,
                    **settings.notification_settings.dict()
                )
                self.db.add(notification_settings)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_notification_settings(
            self,
            user_id: int
    ) -> Optional[NotificationSettings]:
        """Get user's notification settings"""
        result = await self.db.execute(
            select(NotificationSettings)
            .where(NotificationSettings.user_id == user_id)
        )
        return result.scalar_one_or_none()
