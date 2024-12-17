from database.database import get_db
from database.models import UserRole
from repositories import UserRepository
from utils.auth import is_admin_role
import logging

logger = logging.getLogger(__name__)


async def is_admin(telegram_id: int) -> bool:
    """Check if user is admin"""
    try:
        async for db in get_db():
            user_repo = UserRepository(db)
            user = await user_repo.get_by_telegram_id(telegram_id)
            return user and is_admin_role(user.role)
    except Exception:
        return False


async def promote_to_admin(user_id: int) -> bool:
    """ارتقاء کاربر به ادمین"""
    try:
        async for db in get_db():
            user_repo = UserRepository(db)
            user = await user_repo.get(user_id)
            if user:
                user.role = UserRole.ADMIN
                await user_repo.update(user)
                return True
    except Exception:
        return False
    return False


async def demote_from_admin(user_id: int) -> bool:
    """حذف دسترسی ادمین"""
    try:
        async for db in get_db():
            user_repo = UserRepository(db)
            user = await user_repo.get(user_id)
            if user and user.role == UserRole.ADMIN:
                user.role = UserRole.USER
                await user_repo.update(user)
                return True
    except Exception:
        return False
    return False
