from aiogram.dispatcher.filters import Command
from aiogram import types
from ..main import dp
from repositories.user_repository import UserRepository
from repositories.notification_repository import NotificationRepository
from database.database import get_db


@dp.message_handler(commands=['auth'])
async def auth_command(message: types.Message):
    """دستور احراز هویت"""
    async for db in get_db():
        user_repo = UserRepository(db)
        user = await user_repo.get_by_telegram_id(message.from_user.id)
        
        if user:
            await message.reply(
                "✅ شما قبلاً احراز هویت شده‌اید.\n"
                f"شماره موبایل: {user.phone}"
            )
        else:
            await message.reply(
                "برای احراز هویت، لطفاً شماره موبایل خود را به صورت زیر ارسال کنید:\n"
                "/phone 09123456789"
            )


@dp.message_handler(Command("phone"))
async def phone_command(message: types.Message):
    """دریافت شماره موبایل"""
    try:
        phone = message.get_args()
        if not phone or not phone.startswith('09') or len(phone) != 11:
            raise ValueError("شماره موبایل نامعتبر است")
            
        async for db in get_db():
            user_repo = UserRepository(db)
            notif_repo = NotificationRepository(db)
            
            # بررسی تکراری نبودن شماره
            existing_user = await user_repo.get_by_phone(phone)
            if existing_user:
                await message.reply("❌ این شماره موبایل قبلاً ثبت شده است")
                return
                
            # ایجاد کاربر جدید
            user = await user_repo.create(
                telegram_id=message.from_user.id,
                phone=phone,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
            
            # ایجاد تنظیمات اعلان‌ها
            await notif_repo.create_settings(
                user_id=user.id,
                server_notifications=True,
                payment_notifications=True,
                ticket_notifications=True,
                low_balance_threshold=50000
            )
            
            await message.reply(
                "✅ ثبت‌نام شما با موفقیت انجام شد.\n"
                "اکنون می‌توانید از امکانات ربات استفاده کنید."
            )
            
    except ValueError as e:
        await message.reply(str(e))
    except Exception as e:
        await message.reply("❌ خطا در ثبت‌نام. لطفاً دوباره تلاش کنید.")
