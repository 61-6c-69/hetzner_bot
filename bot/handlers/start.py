from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram import types
from repositories.user_repository import UserRepository
from database.database import get_db
from bot import dp


@dp.message_handler(CommandStart(deep_link=True))
async def bot_start_with_link(message: types.Message):
    """پردازش دستور start با پارامتر"""
    deep_link_args = message.get_args()
    try:
        # جدا کردن ID کاربر از کد
        user_id = deep_link_args.split('_')[0]

        async for db in get_db():
            user_repo = UserRepository(db)

            # پیدا کردن کاربر در دیتابیس
            user = await user_repo.get(int(user_id))
            if not user:
                await message.reply("❌ کاربر مورد نظر یافت نشد!")
                return

            # چک کردن اینکه آیا این تلگرام قبلا به حساب دیگری متصل شده
            existing_user = await user_repo.get_by_telegram_id(message.from_user.id)
            if existing_user:
                await message.reply(
                    "❌ این اکانت تلگرام قبلاً به یک حساب کاربری دیگر متصل شده است!\n"
                    "لطفاً ابتدا از حساب قبلی خود خارج شوید."
                )
                return

            # چک کردن اینکه آیا این حساب قبلا به تلگرام دیگری متصل شده
            if user.telegram_id:
                await message.reply(
                    "❌ این حساب کاربری قبلاً به یک اکانت تلگرام دیگر متصل شده است!\n"
                    "برای تغییر اکانت تلگرام، ابتدا از پنل کاربری اتصال قبلی را حذف کنید."
                )
                return

            # ذخیره telegram_id
            await user_repo.update(user.id, telegram_id=message.from_user.id)

            await message.reply(
                "✅ حساب کاربری شما با موفقیت متصل شد!\n"
                "از این پس اعلان‌های مربوط به سرورها را دریافت خواهید کرد."
            )

    except Exception as e:
        await message.reply("❌ خطا در اتصال حساب کاربری!")


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    """پردازش دستور start معمولی"""
    async for db in get_db():
        user_repo = UserRepository(db)
        
        # چک کردن اینکه آیا کاربر قبلا متصل شده
        existing_user = await user_repo.get_by_telegram_id(message.from_user.id)
        if existing_user:
            await message.reply(
                "✅ شما قبلاً به حساب کاربری خود متصل شده‌اید.\n"
                "می‌توانید از امکانات ربات استفاده کنید."
            )
            return

        await message.reply(
            "👋 به ربات پنل هتزنر خوش آمدید!\n"
            "برای اتصال حساب کاربری خود، از طریق پنل کاربری اقدام کنید."
        )
