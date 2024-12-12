from database.models import User, NotificationSettings
from aiogram.dispatcher.filters import Command
from tortoise.exceptions import DoesNotExist
from aiogram import types
from ..main import dp


@dp.message_handler(commands=['auth'])
async def auth_command(message: types.Message):
    """دستور احراز هویت"""
    try:
        user = await User.get(telegram_id=message.from_user.id)
        await message.reply(
            "✅ شما قبلاً احراز هویت شده‌اید.\n"
            f"شماره موبایل: {user.phone}"
        )
    except DoesNotExist:
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
            
        # بررسی تکراری نبودن شماره
        existing_user = await User.get_or_none(phone=phone)
        if existing_user:
            await message.reply("❌ این شماره موبایل قبلاً ثبت شده است")
            return
            
        # ایجاد کاربر جدید
        user = await User.create(
            telegram_id=message.from_user.id,
            phone=phone,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        # ایجاد تنظیمات اعلان‌ها
        await NotificationSettings.create(
            user=user,
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
