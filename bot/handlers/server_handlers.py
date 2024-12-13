from aiogram import types
from repositories.server_repository import ServerRepository
from repositories.user_repository import UserRepository
from database.database import get_db


async def handle_servers_list(message: types.Message):
    """لیست سرورهای کاربر"""
    async for db in get_db():
        user_repo = UserRepository(db)
        server_repo = ServerRepository(db)

        # Get user
        user = await user_repo.get_by_telegram_id(message.from_user.id)
        if not user:
            await message.reply("لطفا ابتدا حساب کاربری خود را متصل کنید.")
            return

        # Get servers
        servers = await server_repo.get_user_servers(user.id)
        if not servers:
            await message.reply("شما هیچ سروری ندارید.")
            return

        response = "لیست سرورهای شما:\n\n"
        for server in servers:
            response += f"🖥 {server.name}\n"
            response += f"💾 {server.type}\n"
            response += f"🌍 {server.location}\n"
            response += f"💰 {server.hourly_price} تومان/ساعت\n"
            response += f"🟢 {server.status}\n\n"

        await message.reply(response)
