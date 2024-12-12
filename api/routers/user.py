from database.models import User, NotificationSettings
from fastapi import APIRouter, Depends, HTTPException
from utils.auth import get_current_user
from pydantic import BaseModel
from config import REDIS_URL
from redis import Redis

router = APIRouter()
redis_client = Redis.from_url(REDIS_URL)


class TelegramConnect(BaseModel):
    code: str


class NotificationSettingsUpdate(BaseModel):
    server_notifications: bool
    payment_notifications: bool
    ticket_notifications: bool
    low_balance_threshold: int


@router.post("/telegram-connect")
async def connect_telegram(
        data: TelegramConnect,
        current_user: User = Depends(get_current_user)
):
    """اتصال اکانت تلگرام"""
    # بررسی کد در ردیس
    telegram_id = redis_client.get(f"telegram_connect:{data.code}")
    if not telegram_id:
        raise HTTPException(status_code=400, detail="کد نامعتبر است")

    # ذخیره شناسه تلگرام
    current_user.telegram_id = int(telegram_id)
    await current_user.save()

    # حذف کد از ردیس
    redis_client.delete(f"telegram_connect:{data.code}")

    return {"message": "اکانت تلگرام با موفقیت متصل شد"}


@router.get("/notification-settings")
async def get_notification_settings(user: User = Depends(get_current_user)):
    """دریافت تنظیمات اعلان‌ها"""
    settings = await NotificationSettings.get_or_create(user=user)
    return settings[0]


@router.post("/notification-settings")
async def update_notification_settings(
        settings: NotificationSettingsUpdate,
        user: User = Depends(get_current_user)
):
    """بروزرسانی تنظیمات اعلان‌ها"""
    user_settings = await NotificationSettings.get_or_create(user=user)
    user_settings = user_settings[0]

    await user_settings.update_from_dict(settings.dict()).save()
    return user_settings
