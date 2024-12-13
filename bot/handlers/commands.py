from aiogram import types
from repositories.user_repository import UserRepository
from repositories.server_repository import ServerRepository
from database.database import get_db
from ..main import dp
from handlers.admin_handler import is_admin, promote_to_admin, demote_from_admin


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


@dp.message_handler(commands=['promote'])
async def cmd_promote(message: types.Message):
    """Promote a user to admin"""
    # Check if command sender is admin
    if not await is_admin(message.from_user.id):
        await message.reply("⛔️ شما دسترسی به این دستور را ندارید!")
        return
        
    # Check command format
    args = message.get_args().split()
    if not args:
        await message.reply("❌ لطفا شناسه تلگرام کاربر را وارد کنید!")
        return
        
    try:
        target_telegram_id = int(args[0])
        async for db in get_db():
            user_repo = UserRepository(db)
            user = await user_repo.get_by_telegram_id(target_telegram_id)
            
            if not user:
                await message.reply("❌ کاربر مورد نظر یافت نشد!")
                return
                
            if await promote_to_admin(user.id):
                await message.reply("✅ کاربر با موفقیت به ادمین ارتقا یافت!")
            else:
                await message.reply("❌ خطا در ارتقاء کاربر به ادمین!")
    except ValueError:
        await message.reply("❌ شناسه تلگرام نامعتبر!")
    except Exception as e:
        await message.reply("❌ خطا در اجرای دستور!")


@dp.message_handler(commands=['demote'])
async def cmd_demote(message: types.Message):
    """Remove admin role from a user"""
    # Check if command sender is admin
    if not await is_admin(message.from_user.id):
        await message.reply("⛔️ شما دسترسی به این دستور را ندارید!")
        return
        
    # Check command format
    args = message.get_args().split()
    if not args:
        await message.reply("❌ لطفا شناسه تلگرام کاربر را وارد کنید!")
        return
        
    try:
        target_telegram_id = int(args[0])
        async for db in get_db():
            user_repo = UserRepository(db)
            user = await user_repo.get_by_telegram_id(target_telegram_id)
            
            if not user:
                await message.reply("❌ کاربر مورد نظر یافت نشد!")
                return
                
            if await demote_from_admin(user.id):
                await message.reply("✅ دسترسی ادمین کاربر با موفقیت حذف شد!")
            else:
                await message.reply("❌ خطا در حذف دسترسی ادمین!")
    except ValueError:
        await message.reply("❌ شناسه تلگرام نامعتبر!")
    except Exception as e:
        await message.reply("❌ خطا در اجرای دستور!")
