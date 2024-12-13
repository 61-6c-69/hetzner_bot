from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import TelegramSession
from typing import Optional


class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_session(self, telegram_id: int) -> Optional[TelegramSession]:
        """دریافت نشست فعال تلگرام"""
        result = await self.db.execute(
            select(TelegramSession)
            .where(
                TelegramSession.telegram_id == telegram_id,
                TelegramSession.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def create_session(
        self,
        telegram_id: int,
        user_id: int
    ) -> TelegramSession:
        """ایجاد نشست جدید"""
        # غیرفعال کردن نشست‌های قبلی
        await self.deactivate_sessions(telegram_id)
        
        session = TelegramSession(
            telegram_id=telegram_id,
            user_id=user_id,
            is_active=True
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def deactivate_sessions(self, telegram_id: int) -> None:
        """غیرفعال کردن همه نشست‌های کاربر"""
        result = await self.db.execute(
            select(TelegramSession)
            .where(
                TelegramSession.telegram_id == telegram_id,
                TelegramSession.is_active == True
            )
        )
        sessions = result.scalars().all()
        
        for session in sessions:
            session.is_active = False
            
        await self.db.commit()

    async def delete_session(self, telegram_id: int) -> None:
        """حذف نشست"""
        result = await self.db.execute(
            select(TelegramSession)
            .where(TelegramSession.telegram_id == telegram_id)
        )
        session = result.scalar_one_or_none()
        
        if session:
            await self.db.delete(session)
            await self.db.commit() 