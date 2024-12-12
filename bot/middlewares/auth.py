from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from database.models import User
from aiogram import types


class AuthMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        # بررسی دسترسی کاربر
        user = await User.get_or_none(telegram_id=message.from_user.id)
        if not user and message.get_command() not in ['/start']:
            await message.reply("⚠️ لطفا ابتدا حساب خود را متصل کنید")
            raise CancelHandler()
