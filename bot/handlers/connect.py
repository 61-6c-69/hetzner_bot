import random
import string

from aiogram import types

from bot import dp
from utils.price_cache import redis_client


@dp.message_handler(commands=['connect'])
async def connect_command(message: types.Message):
    """دستور اتصال اکانت"""
    # تولید کد تصادفی
    code = ''.join(random.choices(string.digits, k=6))

    # ذخیره در ردیس با TTL 5 دقیقه
    await redis_client.setex(
        f"telegram_connect:{code}",
        300,  # 5 minutes
        str(message.from_user.id)
    )

    await message.reply(
        "🔗 کد اتصال حساب کاربری:\n\n"
        f"<code>{code}</code>\n\n"
        "این کد را در پنل کاربری خود وارد کنید.\n"
        "⚠️ کد فقط به مدت 5 دقیقه معتبر است.",
        parse_mode="HTML"
    )
