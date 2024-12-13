import logging
import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from database.models import User, Server, Transaction
from config import BOT_TOKEN, ADMIN_IDS, ZARINPAL_MERCHANT, ZARINPAL_CALLBACK_URL

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

ZARINPAL_API = "https://api.zarinpal.com/pg/v4/payment"


async def notify_admins(message: str, keyboard=None):
    """ارسال پیام به همه ادمین‌ها"""
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                message,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        except Exception as e:
            logging.error(f"Failed to notify admin {admin_id}: {e}")


@dp.message_handler(lambda message: message.text == "💰 افزایش موجودی")
async def increase_balance(message: types.Message):
    """افزایش موجودی"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    amounts = [
        ("50,000 تومان", "50000"),
        ("100,000 تومان", "100000"),
        ("200,000 تومان", "200000"),
        ("500,000 تومان", "500000"),
    ]
    buttons = [
        types.InlineKeyboardButton(text=text, callback_data=f"pay_{amount}")
        for text, amount in amounts
    ]
    markup.add(*buttons)

    await message.reply(
        "💳 مبلغ مورد نظر برای افزایش موجودی را انتخاب کنید:",
        reply_markup=markup
    )


@dp.callback_query_handler(lambda c: c.data.startswith('pay_'))
async def process_payment(callback_query: types.CallbackQuery):
    amount = int(callback_query.data.split('_')[1])
    user = await User.get_or_none(telegram_id=callback_query.from_user.id)

    if not user:
        return await callback_query.answer("لطفا ابتدا ثبت‌نام کنید")

    # ایجاد تراکنش در دیتابیس
    transaction = await Transaction.create(
        user=user,
        amount=amount,
        description=f"افزایش موجودی از طریق ربات",
        status='pending'
    )

    # درخواست به زرین‌پال
    response = requests.post(
        f"{ZARINPAL_API}/request",
        json={
            "merchant_id": ZARINPAL_MERCHANT,
            "amount": amount * 10,  # تبدیل به ریال
            "description": f"افزایش موجودی کاربر {user.phone}",
            "callback_url": f"{ZARINPAL_CALLBACK_URL}/payments/verify/{transaction.id}",
            "metadata": {"mobile": user.phone}
        }
    )
    data = response.json()

    if data['data']['code'] == 100:
        # ذخیره authority
        transaction.payment_id = data['data']['authority']
        await transaction.save()

        # ایجاد دکمه پرداخت
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(
                "پرداخت",
                url=f"https://www.zarinpal.com/pg/StartPay/{data['data']['authority']}"
            )
        )

        await callback_query.message.edit_text(
            f"🔰 لینک پرداخت {amount:,} تومان ایجاد شد.\n"
            "برای پرداخت روی دکمه زیر کلیک کنید.",
            reply_markup=markup
        )
    else:
        await callback_query.message.edit_text("❌ خطا در ایجاد لینک پرداخت")


@dp.message_handler(lambda message: message.text == "💰 موجودی")
async def show_balance(message: types.Message):
    """نمایش موجودی"""
    user = await User.get_or_none(telegram_id=message.from_user.id)
    if not user:
        return await message.reply("لطفا ابتدا ثبت‌نام کنید")

    balance = await user.get_balance()
    await message.reply(
        f"💰 موجودی شما: {balance:,} تومان\n\n"
        "برای افزایش موجودی از دکمه 'افزایش موجودی' استفاده کنید."
    )


class ServerStates(StatesGroup):
    choosing_type = State()
    choosing_location = State()
    choosing_os = State()
    confirming = State()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """Handles /start command"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("ارسال شماره تماس", request_contact=True))

    await message.reply(
        "به ربات مدیریت سرور خوش آمدید!\n"
        "لطفاً برای شروع، شماره تماس خود را با کلیک بر روی دکمه زیر ارسال کنید.",
        reply_markup=markup
    )


@dp.message_handler(content_types=['contact'])
async def handle_contact(message: types.Message):
    """Handles user's shared contact"""
    if not message.contact.user_id == message.from_user.id:
        await message.reply("لطفاً شماره موبایل خودتان را ارسال کنید")
        return

    phone = message.contact.phone_number
    if not phone.startswith('+'):
        phone = '+' + phone

    # پیدا کردن کاربر با این شماره
    user = await User.get_or_none(phone=phone)
    if user:
        # اگر کاربر وجود داشت، telegram_id رو آپدیت می‌کنیم
        user.telegram_id = message.from_user.id
        await user.save()
        await message.reply(
            "اطلاعات شما با موفقیت به‌روزرسانی شد",
            reply_markup=get_main_keyboard()
        )
    else:
        # ایجاد کاربر جدید با تلگرام
        await User.create(
            phone=phone,
            telegram_id=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username
        )
        await message.reply(
            "ثبت‌نام شما با موفق��ت انجام شد",
            reply_markup=get_main_keyboard()
        )


@dp.message_handler(lambda message: message.text == "🖥 سرورهای من")
async def list_servers(message: types.Message):
    """نمایش لیست سرورها"""
    user = await User.get_or_none(telegram_id=message.from_user.id)
    if not user:
        return await message.reply("لطفاً ابتدا ثبت‌نام کنید")

    servers = await Server.filter(user=user)
    if not servers:
        return await message.reply("شما هنوز سروری ندارید")

    text = "📋 لیست سرورهای شما:\n\n"
    for server in servers:
        text += f"🔹 نام: {server.name}\n"
        text += f"📍 IP: {server.ip}\n"
        text += f"💻 OS: {server.os}\n"
        text += f"⚡️ وضعیت: {server.status}\n"
        text += "➖➖➖➖➖➖➖➖\n"

    await message.reply(text)


def get_main_keyboard():
    """دکمه‌های اصلی ربات"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🖥 سرورهای من"),
        types.KeyboardButton("💰 موجودی"),
        types.KeyboardButton("💰 افزایش موجودی"),
        types.KeyboardButton("تراکنش‌ها")
    )
    return markup


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
