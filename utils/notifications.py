import logging
from datetime import datetime
from enum import Enum
from aiogram import Bot
from typing import Optional, Dict, Any
from database.database import AsyncSessionLocal
from repositories.server_repository import ServerRepository
from repositories.user_repository import UserRepository
from repositories.notification_repository import NotificationRepository
from config import BOT_TOKEN

# Initialize bot
bot = Bot(token=BOT_TOKEN)
logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    SERVER_CREATED = "server_created"
    SERVER_DELETED = "server_deleted"
    SERVER_STARTED = "server_started"
    SERVER_STOPPED = "server_stopped"
    SERVER_ERROR = "server_error"
    SERVER_WARNING = "server_warning"
    LOW_BALANCE = "low_balance"
    LOW_BALANCE_SHUTDOWN = "low_balance_shutdown"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    TICKET_REPLY = "ticket_reply"
    TICKET_STATUS = "ticket_status"


# Message templates for different notification types
messages = {
    NotificationType.SERVER_CREATED: "🖥 سرور جدید ایجاد شد\nن��م: {name}\nنوع: {type}\nقیمت: {price} تومان",
    NotificationType.SERVER_STOPPED: "⚠️ سرور {name} متوقف شد",
    NotificationType.SERVER_WARNING: "⚠️ هشدار سرور {name}:\n{message}",
    NotificationType.LOW_BALANCE: "⚠️ موجودی حساب شما کم است\nموجودی فعلی: {balance} تومان",
    NotificationType.PAYMENT_SUCCESS: "✅ پرداخت موفق\nمبلغ: {amount} تومان\nشناسه پرداخت: {payment_id}",
    NotificationType.TICKET_REPLY: "🎫 پاسخ به تیکت #{ticket_id}\n\n{message}",
    NotificationType.LOW_BALANCE_SHUTDOWN: "🚨 خاموش شدن خودکار سرورها\n\nبه دلیل کمبود موجودی، {servers_count} سرور شما خاموش شدند.\n💰 موجودی فعلی: {current_balance:,} تومان\n💰 هزینه ساعتی: {hourly_cost:,} تومان\n\nبرای روشن کردن مجدد سرورها، لطفاً حساب خود را شارژ کنید.",
    NotificationType.PAYMENT_FAILED: "❌ پرداخت ناموفق\n\n💰 مبلغ: {amount:,} تومان\n⚠️ علت: {reason}",
    NotificationType.TICKET_STATUS: "🔄 تغییر وضعیت تیکت #{ticket_id}\n\nوضعیت جدید: {status}"
}


async def notify_user(user_id: int, message: str, parse_mode: str = 'HTML') -> bool:
    """ارسال نوتیفیکیشن به کاربر"""
    try:
        async with AsyncSessionLocal() as db:
            user_repo = UserRepository(db)
            user = await user_repo.get(user_id)

            if user and user.telegram_id:
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=message,
                    parse_mode=parse_mode
                )
                return True
    except Exception as e:
        logger.error(f"Failed to notify user {user_id}: {e}")
    return False


async def send_notification(
        user,
        type: NotificationType,
        **kwargs: Dict[str, Any]
) -> bool:
    """ارسال نوتیفیکیشن با قالب مشخص"""
    try:
        async with AsyncSessionLocal() as db:
            notification_repo = NotificationRepository(db)
            settings = await notification_repo.get_or_create(user.id)

            # بررسی تنظیمات نوتیفیکیشن کاربر
            if not settings:
                return False

            if type == NotificationType.SERVER_WARNING and not settings.server_notifications:
                return False
            elif type == NotificationType.PAYMENT_SUCCESS and not settings.payment_notifications:
                return False
            elif type == NotificationType.TICKET_REPLY and not settings.ticket_notifications:
                return False
            elif type == NotificationType.LOW_BALANCE and not settings.low_balance_threshold:
                return False

            # ساخت پیام با قالب مناسب
            message = messages[type].format(**kwargs)

            # ارسال به کاربر
            if user.telegram_id:
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=message,
                    parse_mode='HTML'
                )
                return True

    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        return False


async def notify_admins(message: str, file_path: Optional[str] = None):
    """Send notification to all admin users"""
    try:
        async with AsyncSessionLocal() as db:
            user_repo = UserRepository(db)
            admins = await user_repo.get_admins()

            for admin in admins:
                if admin.telegram_id:
                    try:
                        # Send message
                        await bot.send_message(
                            chat_id=admin.telegram_id,
                            text=message,
                            parse_mode='HTML'
                        )

                        # Send file if provided
                        if file_path:
                            with open(file_path, 'rb') as file:
                                await bot.send_document(
                                    chat_id=admin.telegram_id,
                                    document=file
                                )
                    except Exception as e:
                        logger.error(f"Failed to notify admin {admin.id}: {e}")

    except Exception as e:
        logger.error(f"Error in notify_admins: {e}")


async def notify_server_action(server_id: int, action: str, admin_id: int):
    """Notify server owner about admin action"""
    try:
        async with AsyncSessionLocal() as db:
            user_repo = UserRepository(db)
            server_repo = ServerRepository(db)

            server = await server_repo.get(server_id)
            if not server:
                return

            owner = await user_repo.get(server.user_id)
            admin = await user_repo.get(admin_id)

            if owner and owner.telegram_id:
                message = (
                    f"🔔 اقدام مدیر بر روی سرور\n"
                    f"عملیات: {action}\n"
                    f"توسط: {admin.username if admin else 'Unknown'}\n"
                    f"زمان: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
                )

                await notify_user(owner.id, message)
    except Exception as e:
        logger.error(f"Error in notify_server_action: {e}")
