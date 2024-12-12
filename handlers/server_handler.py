from aiogram import types
from aiogram.dispatcher import FSMContext
from utils.hetzner_api import HetznerAPI
from utils.keyboards import (
    os_selection_keyboard,
    server_type_keyboard,
    location_keyboard,
    main_menu_keyboard,
    get_main_keyboard,
    get_server_management_keyboard
)
from models import Server, User
import logging
from utils.hetzner_api import hetzner
from utils.notifications import send_notification, NotificationType

logger = logging.getLogger(__name__)
hetzner = HetznerAPI()


async def list_servers(callback_query: types.CallbackQuery, state: FSMContext):
    """نمایش لیست سرورهای کاربر"""
    await callback_query.answer()

    user = await User.get(telegram_id=callback_query.from_user.id)
    servers = await Server.filter(user=user)

    if not servers:
        await callback_query.message.edit_text(
            "شما هنوز هیچ سروری ندارید! 🤔\n"
            "برای خرید سرور جدید از دکمه 'خرید سرور' استفاده کنید.",
            reply_markup=main_menu_keyboard()
        )
        return

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for server in servers:
        keyboard.add(
            types.InlineKeyboardButton(
                f"🖥 {server.name} ({server.ip})",
                callback_data=f"server_{server.id}"
            )
        )
    keyboard.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu"))

    await callback_query.message.edit_text(
        "لیست سرورهای شما:\n"
        "برای مدیریت هر سرور روی آن کلیک کنید.",
        reply_markup=keyboard
    )


async def server_details(callback_query: types.CallbackQuery, state: FSMContext):
    """نمایش جزئیات و گزینه‌های مدیریت سرور"""
    await callback_query.answer()

    try:
        server_id = int(callback_query.data.split('_')[1])
        server = await Server.get(id=server_id)

        # دریافت اطلاعات سرور از هتزنر
        server_info = await hetzner.get_server_info(str(server.hetzner_id))

        if not server_info:
            await callback_query.message.edit_text(
                "❌ خطا در دریافت اطلاعات سرور. لطفاً دوباره تلاش کنید.",
                reply_markup=get_main_keyboard()
            )
            return

        message = (
            f"🖥 نام سرور: {server.name}\n"
            f"🌐 آی‌پی: {server.ip}\n"
            f"💻 مشخصات: {server.specs.get('description', 'نامشخص')}\n"
            f"⚡️ وضعیت: {server.status}\n"
            f"💰 هزینه ساعتی: {server.hourly_price} یورو\n"
            f"📅 تاریخ ایجاد: {server.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        )

        await callback_query.message.edit_text(
            message,
            reply_markup=get_server_management_keyboard(server.id)
        )
    except Exception as e:
        logger.error(f"Error in server_details: {e}")
        await callback_query.message.edit_text(
            "❌ خطای غیرمنتظره رخ داد. لطفاً دوباره تلاش کنید.",
            reply_markup=get_main_keyboard()
        )


async def power_off(callback_query: types.CallbackQuery, state: FSMContext):
    """خاموش کردن سرور"""
    await callback_query.answer()

    server_id = int(callback_query.data.split('_')[2])
    server = await Server.get(id=server_id)

    try:
        result = await hetzner.power_off(str(server.hetzner_id))
        if result:
            server.status = 'off'
            await server.save()

            # ارسال نوتیفیکیشن
            await send_notification(
                server.user,
                NotificationType.SERVER_STOPPED,
                name=server.name
            )

            await callback_query.message.edit_text(
                "✅ سرور با موفقیت خاموش شد.",
                reply_markup=get_server_management_keyboard(server.id)
            )
        else:
            raise Exception("خطا در خاموش کردن سرور")
    except Exception as e:
        logger.error(f"Error powering off server {server_id}: {str(e)}")
        await callback_query.message.edit_text(
            "❌ خطا در خاموش کردن سرور. لطفاً دوباره تلاش کنید.",
            reply_markup=get_server_management_keyboard(server.id)
        )


async def reset_server(callback_query: types.CallbackQuery, state: FSMContext):
    """ریست کردن سرور"""
    await callback_query.answer()

    server_id = int(callback_query.data.split('_')[2])
    server = await Server.get(id=server_id)

    try:
        result = await hetzner.reset_server(server.hetzner_id)
        if result:
            await callback_query.message.edit_text(
                "✅ سرور با موفقیت ریست شد.\n"
                "لطفاً چند دقیقه صبر کنید تا سرور مجدداً راه‌اندازی شود.",
                reply_markup=get_server_management_keyboard(server.id)
            )
        else:
            raise Exception("خطا در ریست کردن سرور")
    except Exception as e:
        logger.error(f"Error resetting server {server.id}: {str(e)}")
        await callback_query.message.edit_text(
            "❌ خطا در ریست کردن سرور. لطفاً دوباره تلاش کنید.",
            reply_markup=get_server_management_keyboard(server.id)
        )


async def change_os(callback_query: types.CallbackQuery, state: FSMContext):
    """تغییر سیستم عامل سرور"""
    await callback_query.answer()

    server_id = int(callback_query.data.split('_')[2])
    await state.update_data(server_id=server_id)

    await callback_query.message.edit_text(
        "لطفاً سیستم عامل مورد نظر خود را انتخاب کنید:",
        reply_markup=os_selection_keyboard(server_id)
    )


async def select_os(callback_query: types.CallbackQuery, state: FSMContext):
    """پردازش انتخاب سیستم عامل"""
    await callback_query.answer()

    data = await state.get_data()
    server_id = data.get('server_id')
    os_type = callback_query.data.split('_')[2]

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("✅ بله، مطمئنم", callback_data=f"confirm_os_{server_id}_{os_type}"),
        types.InlineKeyboardButton("❌ انصراف", callback_data=f"server_{server_id}")
    )

    await callback_query.message.edit_text(
        "⚠️ هشدار: تغییر سیستم عامل باعث پاک شدن تمام اطلاعات سرور می‌شود.\n"
        "آیا مطمئن هستید؟",
        reply_markup=keyboard
    )


async def start_buy_server(callback_query: types.CallbackQuery, state: FSMContext):
    """شروع فرایند خرید سرور"""
    await callback_query.answer()

    # پاک کردن داده‌های قبلی
    await state.finish()
    await state.set_state('selecting_hardware')

    await callback_query.message.edit_text(
        "🛒 خرید سرور جدید\n\n"
        "لطفاً نوع سرور مورد نظر خود را انتخاب کنید:",
        reply_markup=server_type_keyboard()
    )


async def select_hardware(callback_query: types.CallbackQuery, state: FSMContext):
    """انتخاب سخت‌افزار سرور"""
    await callback_query.answer()

    hardware_type = callback_query.data.split('_')[1]

    try:
        server_types = await hetzner.get_server_types()
        selected_type = next(
            (st for st in server_types if st['name'] == hardware_type),
            None
        )

        if not selected_type:
            raise ValueError("نوع سرور انتخابی معتبر نیست")

        # ذخیره انتخاب کاربر
        await state.update_data(hardware={
            'type': hardware_type,
            'price': selected_type['prices'][0]['price_hourly']['gross']
        })
        await state.set_state('selecting_location')

        await callback_query.message.edit_text(
            "🌍 لط��اً موقعیت جغرافیایی سرور را انتخاب کنید:",
            reply_markup=location_keyboard()
        )
    except Exception as e:
        logger.error(f"Error selecting hardware: {str(e)}")
        await callback_query.message.edit_text(
            "❌ خطا در انتخاب نوع سرور. لطفاً دوباره تلاش کنید.",
            reply_markup=server_type_keyboard()
        )
