from aiogram import types
from database.models import User, Server
from ..main import dp


@dp.message_handler(commands=['status'])
async def cmd_status(message: types.Message):
    """نمایش وضعیت سرورها"""
    user = await User.get(telegram_id=message.from_user.id)
    servers = await Server.filter(user=user)

    if not servers:
        await message.reply("شما هنوز هیچ سروری ندارید!")
        return

    text = "📊 وضعیت سرورهای شما:\n\n"
    for server in servers:
        text += f"🖥 {server.name}\n"
        text += f"🌐 IP: {server.ip}\n"
        text += f"💻 OS: {server.os}\n"
        text += f"📡 وضعیت: {server.status}\n"
        text += "➖➖➖➖➖➖\n"

    await message.reply(text)


@dp.message_handler(commands=['balance'])
async def cmd_balance(message: types.Message):
    """نمایش موجودی"""
    user = await User.get(telegram_id=message.from_user.id)
    balance = await user.get_balance()
    await message.reply(f"💰 موجودی شما: {balance:,} تومان")
