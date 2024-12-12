from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from handlers import auth_handler, server_handler, payment_handler, admin_handler
from config import BOT_TOKEN
from utils.keyboards import main_menu_keyboard
import logging
import asyncio

# تنظیم لاگینگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


# تعریف حالت‌ها
class BotStates(StatesGroup):
    selecting_action = State()
    selecting_server = State()
    selecting_os = State()
    selecting_location = State()
    selecting_hardware = State()
    confirming_purchase = State()
    processing_payment = State()


async def start_command(message: types.Message, state: FSMContext):
    """شروع کار با ربات و ثبت نام کاربر"""
    user = await auth_handler.get_or_create_user(message.from_user)
    await message.reply(
        f"سلام {user.first_name} عزیز! 👋\n"
        "به ربات مدیریت سرورهای هتزنر خوش آمدید.\n"
        "از منوی زیر گزینه مورد نظر خود را انتخاب کنید:",
        reply_markup=main_menu_keyboard()
    )
    await BotStates.selecting_action.set()


async def error_handler(update: types.Update, exception: Exception):
    """مدیریت خطاها"""
    logger.error(f"خطا {exception} برای آپدیت {update} رخ داد")
    if update.message:
        await update.message.reply("متأسفانه خطایی رخ داد. لطفاً دوباره تلاش کنید.")


async def main():
    """راه‌اندازی ربات"""
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    # ثبت هندلرها
    dp.register_message_handler(start_command, commands=['start'], state='*')

    # هندلرهای اصلی
    dp.register_callback_query_handler(
        server_handler.list_servers,
        lambda c: c.data == 'servers',
        state=BotStates.selecting_action
    )
    dp.register_callback_query_handler(
        server_handler.start_buy_server,
        lambda c: c.data == 'buy_server',
        state=BotStates.selecting_action
    )
    dp.register_callback_query_handler(
        payment_handler.increase_balance,
        lambda c: c.data == 'increase_balance',
        state=BotStates.selecting_action
    )
    dp.register_callback_query_handler(
        payment_handler.show_transactions,
        lambda c: c.data == 'transactions',
        state=BotStates.selecting_action
    )

    # هندلرهای مدیریت سرور
    dp.register_callback_query_handler(
        server_handler.server_details,
        lambda c: c.data.startswith('server_'),
        state=BotStates.selecting_server
    )
    dp.register_callback_query_handler(
        server_handler.power_off,
        lambda c: c.data.startswith('power_off_'),
        state=BotStates.selecting_server
    )
    dp.register_callback_query_handler(
        server_handler.reset_server,
        lambda c: c.data.startswith('reset_'),
        state=BotStates.selecting_server
    )
    dp.register_callback_query_handler(
        server_handler.change_os,
        lambda c: c.data.startswith('change_os_'),
        state=BotStates.selecting_server
    )

    # هندلرهای انتخاب سیستم‌عامل و سخت‌افزار
    dp.register_callback_query_handler(
        server_handler.select_os,
        lambda c: c.data.startswith('os_'),
        state=BotStates.selecting_os
    )
    dp.register_callback_query_handler(
        server_handler.select_location,
        lambda c: c.data.startswith('location_'),
        state=BotStates.selecting_location
    )
    dp.register_callback_query_handler(
        server_handler.select_hardware,
        lambda c: c.data.startswith('hw_'),
        state=BotStates.selecting_hardware
    )

    # هندلرهای تأیید خرید و پرداخت
    dp.register_callback_query_handler(
        server_handler.confirm_purchase,
        lambda c: c.data.startswith('confirm_'),
        state=BotStates.confirming_purchase
    )
    dp.register_callback_query_handler(
        payment_handler.process_payment,
        lambda c: c.data.startswith('pay_'),
        state=BotStates.processing_payment
    )

    # هندلرهای پنل ادمین
    dp.register_message_handler(admin_handler.admin_panel, commands=['admin'])
    dp.register_callback_query_handler(
        admin_handler.admin_users,
        lambda c: c.data == 'admin_users'
    )
    dp.register_callback_query_handler(
        admin_handler.admin_servers,
        lambda c: c.data == 'admin_servers'
    )
    dp.register_callback_query_handler(
        admin_handler.admin_transactions,
        lambda c: c.data == 'admin_transactions'
    )
    dp.register_callback_query_handler(
        admin_handler.admin_settings,
        lambda c: c.data == 'admin_settings'
    )

    # هندلر خطا
    dp.register_errors_handler(error_handler)

    # شروع پردازش آپدیت‌ها
    try:
        await dp.start_polling()
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
