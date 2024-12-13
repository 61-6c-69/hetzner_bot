from utils.notifications import notify_user
from config import ADMIN_IDS
from aiogram import types
import logging

logger = logging.getLogger(__name__)


async def handle_error(update: types.Update, error: Exception):
    """مدیریت پیشرفته خطاها"""
    error_text = f"Update {update} caused error: {error}"
    logger.error(error_text)

    # اطلاع به ادمین‌ها
    error_message = (
        "❌ خطای جدید:\n"
        f"خطا: {error}\n"
        f"آپدیت: {update}"
    )

    for admin_id in ADMIN_IDS:
        try:
            await notify_user(admin_id, error_message)
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")

    # پاسخ به کاربر
    if update.message:
        await update.message.reply(
            "❌ متأسفانه خطایی رخ داد.\n"
            "لطفاً دوباره تلاش کنید."
        )
