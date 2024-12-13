from aiogram import types
from repositories.user_repository import UserRepository
from repositories.server_repository import ServerRepository
from database.database import get_db
from ..main import dp


@dp.message_handler(commands=['status'])
async def cmd_status(message: types.Message):
    """نمایش وضعیت سرورها"""
    async for db in get_db():
        user_repo = UserRepository(db)
        server_repo = ServerRepository(db)
        
        user = await user_repo.get_by_telegram_id(message.from_user.id)
        if not user:
            await message.reply("لطفا ابتدا حساب کاربری خود را متصل کنید.")
            return
            
        servers = await server_repo.get_user_servers(user.id)
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
    async for db in get_db():
        user_repo = UserRepository(db)
        user = await user_repo.get_by_telegram_id(message.from_user.id)
        
        if not user:
            await message.reply("لطفا ابتدا حساب کاربری خود را متصل کنید.")
            return
            
        balance = await user_repo.get_balance(user.id)
        await message.reply(f"💰 موجودی شما: {balance:,} تومان")
