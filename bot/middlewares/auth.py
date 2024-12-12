from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from database.models import User, TelegramSession
from database.database import AsyncSessionLocal
from aiogram import types
from sqlalchemy import select


class AuthMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        # بررسی دسترسی کاربر
        user = await check_user_session(message.from_user.id)
        if not user and message.get_command() not in ['/start']:
            await message.reply("⚠️ لطفا ابتدا حساب خود را متصل کنید")
            raise CancelHandler()


async def check_user_session(telegram_id: int) -> User:
    async with AsyncSessionLocal() as db:
        # Check active session
        result = await db.execute(
            select(TelegramSession)
            .where(
                TelegramSession.telegram_id == telegram_id,
                TelegramSession.is_active == True
            )
        )
        session = result.scalar_one_or_none()
        
        if not session:
            return None
            
        # Get user
        result = await db.execute(
            select(User).where(User.id == session.user_id)
        )
        return result.scalar_one_or_none()
