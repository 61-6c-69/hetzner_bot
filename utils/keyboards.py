from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_IDS


def get_main_keyboard(user_id: int | None = None) -> ReplyKeyboardMarkup:
    """دریافت کیبورد اصلی"""
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2,
        one_time_keyboard=False,
        selective=False,
        input_field_placeholder=""
    )

    # دکمه‌های عمومی
    keyboard.add(
        KeyboardButton(
            text="🖥 سرورهای من",
            request_contact=False,
            request_location=False
        ),
        KeyboardButton(
            text="💰 موجودی",
            request_contact=False,
            request_location=False
        ),
        KeyboardButton(
            text="🛒 خرید سرور",
            request_contact=False,
            request_location=False
        ),
        KeyboardButton(
            text="📊 آمار",
            request_contact=False,
            request_location=False
        ),
        KeyboardButton(
            text="⚙️ تنظیمات",
            request_contact=False,
            request_location=False
        ),
        KeyboardButton(
            text="📞 پشتیبانی",
            request_contact=False,
            request_location=False
        )
    )

    # دکمه‌های ادمین
    if user_id in ADMIN_IDS:
        keyboard.add(
            KeyboardButton(
                text="👥 کاربران",
                request_contact=False,
                request_location=False
            ),
            KeyboardButton(
                text="🎫 تیکت‌ها",
                request_contact=False,
                request_location=False
            ),
            KeyboardButton(
                text="📢 ارسال اعلان",
                request_contact=False,
                request_location=False
            ),
            KeyboardButton(
                text="📊 آمار کلی",
                request_contact=False,
                request_location=False
            )
        )

    return keyboard


def get_server_keyboard(server_id: int) -> InlineKeyboardMarkup:
    """دریافت کیبورد مدیریت سرور"""
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton(
            text="🔄 روشن/خاموش",
            callback_data=f"server_power:{server_id}",
            url=None,
            switch_inline_query=None,
            switch_inline_query_current_chat=None,
            pay=False
        ),
        InlineKeyboardButton(
            text="🔄 ریستارت",
            callback_data=f"server_restart:{server_id}",
            url=None,
            switch_inline_query=None,
            switch_inline_query_current_chat=None,
            pay=False
        ),
        InlineKeyboardButton(
            text="🔒 تغییر پسورد",
            callback_data=f"server_password:{server_id}",
            url=None,
            switch_inline_query=None,
            switch_inline_query_current_chat=None,
            pay=False
        ),
        InlineKeyboardButton(
            text="🌐 تغییر IP",
            callback_data=f"server_ip:{server_id}",
            url=None,
            switch_inline_query=None,
            switch_inline_query_current_chat=None,
            pay=False
        ),
        InlineKeyboardButton(
            text="📊 مانیتورینگ",
            callback_data=f"server_monitoring:{server_id}",
            url=None,
            switch_inline_query=None,
            switch_inline_query_current_chat=None,
            pay=False
        ),
        InlineKeyboardButton(
            text="❌ حذف",
            callback_data=f"server_delete:{server_id}",
            url=None,
            switch_inline_query=None,
            switch_inline_query_current_chat=None,
            pay=False
        )
    )

    return keyboard


def get_payment_keyboard(payment_id: int) -> InlineKeyboardMarkup:
    """دریافت کیبورد پرداخت"""
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton(
            text="💳 پرداخت",
            callback_data=f"pay:{payment_id}",
            url=None,
            switch_inline_query=None,
            switch_inline_query_current_chat=None,
            pay=False
        ),
        InlineKeyboardButton(
            text="❌ انصراف",
            callback_data=f"cancel_payment:{payment_id}",
            url=None,
            switch_inline_query=None,
            switch_inline_query_current_chat=None,
            pay=False
        )
    )

    return keyboard


def get_server_management_keyboard(server_id: int) -> InlineKeyboardMarkup:
    """دریافت کیبورد مدیریت سرور"""
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton(
            text="🔌 خاموش/روشن",
            callback_data=f"power_{server_id}",
            url=None,
            switch_inline_query=None,
            switch_inline_query_current_chat=None,
            pay=False
        ),
        InlineKeyboardButton(
            text="🔄 ریستارت",
            callback_data=f"restart_{server_id}",
            url=None,
            switch_inline_query=None,
            switch_inline_query_current_chat=None,
            pay=False
        ),
        InlineKeyboardButton(
            text="🔒 تغییر پسورد",
            callback_data=f"password_{server_id}",
            url=None,
            switch_inline_query=None,
            switch_inline_query_current_chat=None,
            pay=False
        ),
        InlineKeyboardButton(
            text="🌐 تغییر IP",
            callback_data=f"ip_{server_id}",
            url=None,
            switch_inline_query=None,
            switch_inline_query_current_chat=None,
            pay=False
        ),
        InlineKeyboardButton(
            text="📊 مانیتورینگ",
            callback_data=f"monitoring_{server_id}",
            url=None,
            switch_inline_query=None,
            switch_inline_query_current_chat=None,
            pay=False
        ),
        InlineKeyboardButton(
            text="🔙 بازگشت",
            callback_data="servers_list",
            url=None,
            switch_inline_query=None,
            switch_inline_query_current_chat=None,
            pay=False
        )
    )

    return keyboard


def os_selection_keyboard(server_id: int) -> InlineKeyboardMarkup:
    """دریافت کیبورد انتخاب سیستم‌عامل"""
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton("Ubuntu 20.04", callback_data=f"os_{server_id}_ubuntu20"),
        InlineKeyboardButton("Ubuntu 22.04", callback_data=f"os_{server_id}_ubuntu22"),
        InlineKeyboardButton("Debian 10", callback_data=f"os_{server_id}_debian10"),
        InlineKeyboardButton("Debian 11", callback_data=f"os_{server_id}_debian11"),
        InlineKeyboardButton("CentOS 7", callback_data=f"os_{server_id}_centos7"),
        InlineKeyboardButton("CentOS 8", callback_data=f"os_{server_id}_centos8"),
        InlineKeyboardButton("🔙 بازگشت", callback_data=f"server_type_{server_id}")
    )

    return keyboard


def server_type_keyboard() -> InlineKeyboardMarkup:
    """دریافت کیبورد انتخاب نوع سرور"""
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton("🟢 اقتصادی", callback_data="type_cx11"),
        InlineKeyboardButton("🔵 متوسط", callback_data="type_cx21"),
        InlineKeyboardButton("🟣 حرفه‌ای", callback_data="type_cx31"),
        InlineKeyboardButton("🔴 سازمانی", callback_data="type_cx41"),
        InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")
    )

    return keyboard


def location_keyboard(server_type: str) -> InlineKeyboardMarkup:
    """دریافت کیبورد انتخاب لوکیشن"""
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton("🇩🇪 نورنبرگ", callback_data=f"location_{server_type}_nbg1"),
        InlineKeyboardButton("🇩🇪 فرانکفورت", callback_data=f"location_{server_type}_fsn1"),
        InlineKeyboardButton("🇫🇮 هلسینکی", callback_data=f"location_{server_type}_hel1"),
        InlineKeyboardButton("🇺🇸 اشبرن", callback_data=f"location_{server_type}_ash"),
        InlineKeyboardButton("🔙 بازگشت", callback_data="server_types")
    )

    return keyboard


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """دریافت کیبورد منوی اصلی"""
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton("🖥 سرورهای من", callback_data="my_servers"),
        InlineKeyboardButton("🛒 خرید سرور", callback_data="buy_server"),
        InlineKeyboardButton("💰 موجودی", callback_data="balance"),
        InlineKeyboardButton("📊 آمار", callback_data="stats"),
        InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings"),
        InlineKeyboardButton("📞 پشتیبانی", callback_data="support")
    )

    return keyboard
