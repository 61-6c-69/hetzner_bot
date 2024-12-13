from utils.notifications import send_notification, NotificationType
from repositories.user_repository import UserRepository
from repositories.server_repository import ServerRepository
from utils.hetzner_api import hetzner
from database.database import get_db
from aiogram import types
from ..main import dp


@dp.message_handler(lambda message: message.text == "🖥 سرور جدید")
async def new_server(message: types.Message):
    async for db in get_db():
        user_repo = UserRepository(db)
        
        user = await user_repo.get_by_telegram_id(message.from_user.id)
        if not user:
            await message.reply("لطفا ابتدا حساب کاربری خود را متصل کنید.")
            return
            
        balance = await user_repo.get_balance(user.id)
        
        # دریافت لیست قیمت‌ها
        prices = await hetzner.get_prices()
        min_price = min(p['hourly'] for p in prices)  # کمترین قیمت ساعتی
        
        if balance < min_price:
            return await message.reply(
                f"❌ موجودی شما کافی نیست.\n"
                f"💰 موجودی فعلی: {balance:,} تومان\n"
                f"💰 حداقل موجودی مورد نیاز: {min_price:,} تومان\n\n"
                "لطفاً ابتدا حساب خود را شارژ کنید."
            )
        
        # نمایش منوی انتخاب نوع سرور
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        for server_type in prices:
            btn_text = (
                f"{server_type['name']} - {server_type['specs']}\n"
                f"💰 {server_type['hourly']:,} تومان/ساعت"
            )
            keyboard.add(
                types.InlineKeyboardButton(
                    text=btn_text,
                    callback_data=f"select_server:{server_type['id']}"
                )
            )
        
        await message.reply(
            "🖥 لطفاً نوع سرور مورد نظر خود را انتخاب کنید:",
            reply_markup=keyboard
        )


@dp.callback_query_handler(lambda c: c.data.startswith('select_server:'))
async def server_selected(callback_query: types.CallbackQuery):
    server_type = callback_query.data.split(':')[1]
    
    async for db in get_db():
        user_repo = UserRepository(db)
        server_repo = ServerRepository(db)
        
        user = await user_repo.get_by_telegram_id(callback_query.from_user.id)
        if not user:
            await callback_query.message.edit_text("لطفا ابتدا حساب کاربری خود را متصل کنید.")
            return
        
        # ایجاد سرور در هتزنر
        try:
            server = await hetzner.create_server(
                type=server_type,
                user_id=user.id
            )
            
            # ذخیره در دیتابیس
            db_server = await server_repo.create(
                user_id=user.id,
                hetzner_id=server['id'],
                name=server['name'],
                ip=server['public_net']['ipv4']['ip'],
                status='running',
                os=server['image']['name'],
                specs=server['server_type']
            )
            
            # ارسال نوتیفیکیشن
            await send_notification(
                user.id,
                NotificationType.SERVER_CREATED,
                name=db_server.name,
                ip=db_server.ip
            )
            
            await callback_query.message.edit_text(
                f"✅ سرور شما با موفقیت ایجاد شد!\n\n"
                f"🖥 نام: {db_server.name}\n"
                f"🌐 IP: {db_server.ip}\n"
                f"💾 OS: {db_server.os}"
            )
            
        except Exception as e:
            await callback_query.message.edit_text(
                "❌ خطا در ایجاد سرور. لطفاً دوباره تلاش کنید."
            ) 