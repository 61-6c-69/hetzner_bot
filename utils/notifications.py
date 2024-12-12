import logging
from enum import Enum
from aiogram import Bot
from typing import Optional, Dict, Any
from database.models import User, NotificationSettings
from config import BOT_TOKEN

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

async def notify_user(user_id: int, message: str, parse_mode: str = 'HTML') -> bool:
    """ارسال نوتیفیکیشن به کاربر"""
    try:
        user = await User.get(id=user_id)
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

async def send_notification(user: User, type: NotificationType, **kwargs: Dict[str, Any]) -> bool:
    """ارسال اعلان به کاربر با در نظر گرفتن تنظیمات"""
    try:
        if not user or not user.telegram_id:
            return False
            
        # بررسی تنظیمات اعلان‌های کاربر
        settings = await NotificationSettings.get_or_create(user=user)
        settings = settings[0]  # get_or_create returns tuple (obj, created)
        
        # بررسی نوع اعلان و تنظیمات مربوطه
        should_send = True
        
        if type in [NotificationType.SERVER_CREATED, NotificationType.SERVER_STOPPED, NotificationType.SERVER_WARNING]:
            should_send = settings.server_notifications
        elif type == NotificationType.PAYMENT_SUCCESS:
            should_send = settings.payment_notifications
        elif type == NotificationType.TICKET_REPLY:
            should_send = settings.ticket_notifications
        elif type == NotificationType.LOW_BALANCE:
            balance = kwargs.get('amount', 0)
            should_send = balance <= settings.low_balance_threshold
            
        if not should_send:
            return False
            
        # تنظیم متن اعلان بر اساس نوع آن
        messages = {
            NotificationType.SERVER_CREATED: "✅ سرور جدید شما با موفقیت ایجاد شد\nنام: {name}\nIP: {ip}",
            NotificationType.SERVER_STOPPED: "⚠️ سرور {name} متوقف شد",
            NotificationType.SERVER_WARNING: "⚠️ هشدار برای سرور {server_name}\n{resource}: {usage}%",
            NotificationType.LOW_BALANCE: "⚠️ موجودی حساب شما کمتر از {amount:,} تومان است",
            NotificationType.PAYMENT_SUCCESS: "💰 پرداخت {amount:,} تومانی شما با موفقیت انجام شد",
            NotificationType.TICKET_REPLY: "📨 پاسخ جدید برای تیکت #{ticket_id} ثبت شد"
        }
        
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