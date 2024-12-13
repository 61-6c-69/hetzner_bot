from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from repositories.user_repository import UserRepository
from repositories.session_repository import SessionRepository
from database.database import get_db
from aiogram import types


class AuthMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        # بررسی دسترسی کاربر
        user = await check_user_session(message.from_user.id)
        if not user and message.get_command() not in ['/start']:
            await message.reply("⚠️ لطفا ابتدا حساب خود را متصل کنید")
            raise CancelHandler()


async def check_user_session(telegram_id: int):
    async for db in get_db():
        session_repo = SessionRepository(db)
        user_repo = UserRepository(db)
        
        # Check active session
        session = await session_repo.get_active_session(telegram_id)
        if not session:
            return None
            
        # Get user
        return await user_repo.get(session.user_id)
