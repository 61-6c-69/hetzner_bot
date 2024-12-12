from sqlalchemy import select
from database.models import Server, User
from database.database import AsyncSessionLocal

async def handle_servers_list(message: types.Message):
    async with AsyncSessionLocal() as db:
        # Get user
        result = await db.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.reply("لطفا ابتدا حساب کاربری خود را متصل کنید.")
            return
            
        # Get servers
        result = await db.execute(
            select(Server).where(Server.user_id == user.id)
        )
        servers = result.scalars().all()
        
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