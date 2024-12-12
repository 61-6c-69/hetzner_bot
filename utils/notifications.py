import logging
from enum import Enum
from aiogram import Bot
from typing import Optional, Dict, Any
from database.models import User, NotificationSettings, Server
from config import BOT_TOKEN
from sqlalchemy import select
from database.database import AsyncSessionLocal
from datetime import datetime

# Initialize bot
bot = Bot(token=BOT_TOKEN)
logger = logging.getLogger(__name__)


class NotificationType(Enum):
    SERVER_CREATED = "server_created"
    SERVER_STOPPED = "server_stopped"
    SERVER_WARNING = "server_warning"
    LOW_BALANCE = "low_balance"
    PAYMENT_SUCCESS = "payment_success"
    TICKET_REPLY = "ticket_reply"


# Message templates for different notification types
messages = {
    NotificationType.SERVER_CREATED: "🖥 سرور جدید ایجاد شد\nنام: {name}\nنوع: {type}\nقیمت: {price} تومان",
    NotificationType.SERVER_STOPPED: "⚠️ سرور {name} متوقف شد",
    NotificationType.SERVER_WARNING: "⚠️ هشدار سرور {name}:\n{message}",
    NotificationType.LOW_BALANCE: "⚠️ موجودی حساب شما کم است\nموجودی فعلی: {balance} تومان",
    NotificationType.PAYMENT_SUCCESS: "✅ پرداخت موفق\nمبلغ: {amount} تومان\nشناسه پرداخت: {payment_id}",
    NotificationType.TICKET_REPLY: "🎫 پاسخ به تیکت #{ticket_id}\n\n{message}"
}


async def notify_user(user_id: int, message: str, parse_mode: str = 'HTML') -> bool:
    """ارسال نوتیفیکیشن به کاربر"""
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()

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
        user: User,
        type: NotificationType,
        **kwargs: Dict[str, Any]
) -> bool:
    """Send a notification to a user based on type and settings"""
    try:
        async with AsyncSessionLocal() as db:
            # Get notification settings
            result = await db.execute(
                select(NotificationSettings)
                .where(NotificationSettings.user_id == user.id)
            )
            settings = result.scalar_one_or_none()

            # Check if notifications are enabled for this type
            if not settings:
                return False

            if type == NotificationType.SERVER_CREATED and not settings.server_notifications:
                return False
            elif type == NotificationType.SERVER_STOPPED and not settings.server_notifications:
                return False
            elif type == NotificationType.SERVER_WARNING and not settings.server_notifications:
                return False
            elif type == NotificationType.LOW_BALANCE and not settings.payment_notifications:
                return False
            elif type == NotificationType.PAYMENT_SUCCESS and not settings.payment_notifications:
                return False
            elif type == NotificationType.TICKET_REPLY and not settings.ticket_notifications:
                return False

            # Get message template
            message_template = messages.get(type)
            if not message_template:
                logger.error(f"Unknown notification type: {type}")
                return False

            try:
                message = message_template.format(**kwargs)
            except KeyError as e:
                logger.error(f"Missing required parameter for notification type {type}: {e}")
                return False

            return await notify_user(user.id, message)

    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        return False


async def notify_low_balance(user_id: int, current_balance: float):
    """Send low balance notification if threshold is reached"""
    try:
        async with AsyncSessionLocal() as db:
            # Get notification settings
            result = await db.execute(
                select(NotificationSettings)
                .where(NotificationSettings.user_id == user_id)
            )
            settings = result.scalar_one_or_none()

            if not settings or not settings.payment_notifications:
                return

            if current_balance < settings.low_balance_threshold:
                # Get user
                user_result = await db.execute(
                    select(User).where(User.id == user_id)
                )
                user = user_result.scalar_one_or_none()

                if user:
                    await send_notification(
                        user,
                        NotificationType.LOW_BALANCE,
                        balance=current_balance
                    )

                    # Update last notification time to prevent spam
                    settings.last_low_balance_notification = datetime.utcnow()
                    await db.commit()
    except Exception as e:
        logger.error(f"Error in notify_low_balance for user {user_id}: {e}")


async def notify_admins(message: str, file_path: Optional[str] = None):
    """Send notification to all admin users"""
    try:
        async with AsyncSessionLocal() as db:
            # Get all admin users
            result = await db.execute(
                select(User).where(User.is_superuser == True)
            )
            admins = result.scalars().all()

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
            # Get server and owner
            result = await db.execute(
                select(User)
                .join(Server)
                .where(Server.id == server_id)
            )
            owner = result.scalar_one_or_none()

            if owner and owner.telegram_id:
                # Get admin info
                admin_result = await db.execute(
                    select(User).where(User.id == admin_id)
                )
                admin = admin_result.scalar_one_or_none()

                message = (
                    f"🔔 اقدام مدیر بر روی سرور\n"
                    f"عملیات: {action}\n"
                    f"توسط: {admin.username if admin else 'Unknown'}\n"
                    f"زمان: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
                )

                await notify_user(owner.id, message)
    except Exception as e:
        logger.error(f"Error in notify_server_action: {e}")
