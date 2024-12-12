from repositories.user_repository import UserRepository
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from utils.auth import get_current_user
from database.database import get_db
from utils.redis import Redis
from api import schemas

router = APIRouter()
redis = Redis()


@router.post("/telegram-connect")
async def connect_telegram(
        data: schemas.TelegramConnect,
        current_user: schemas.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)

    # Check code in Redis
    telegram_id = await redis.get(f"telegram_connect:{data.code}")
    if not telegram_id:
        raise HTTPException(status_code=400, detail="Invalid code")

    # Update user's telegram ID
    user = await user_repo.update(
        current_user.id,
        telegram_id=int(telegram_id)
    )

    # Delete code from Redis
    await redis.delete(f"telegram_connect:{data.code}")

    return {"message": "Telegram account connected successfully"}


@router.get("/me", response_model=schemas.User)
async def get_current_user_info(
    current_user: schemas.User = Depends(get_current_user)
):
    return current_user


@router.patch("/me/settings", response_model=schemas.User)
async def update_user_settings(
    settings: schemas.UserSettingsUpdate,
    current_user: schemas.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)
    updated_user = await repo.update_settings(current_user.id, settings)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.get("/me/notifications", response_model=schemas.NotificationSettings)
async def get_notification_settings(
    current_user: schemas.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)
    settings = await repo.get_notification_settings(current_user.id)
    if not settings:
        raise HTTPException(status_code=404, detail="Notification settings not found")
    return settings
