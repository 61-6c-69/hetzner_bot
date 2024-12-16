from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from datetime import datetime, timedelta
from database.database import get_db
from database.models import User, UserRole
from jose import JWTError, jwt
from sqlalchemy import select
from fastapi import status

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/verify-otp")


async def get_current_user(
        db: AsyncSession = Depends(get_db),
        token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    return user


def is_admin_role(role: str) -> bool:
    """Check if the given role is admin"""
    return role == UserRole.ADMIN


async def check_admin_access(user_id: int, db: AsyncSession) -> bool:
    """Check if user has admin access"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    return user is not None and is_admin_role(user.role)


async def get_current_admin_user(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> User:
    """Get current user with admin check"""
    if not is_admin_role(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def create_access_token(data: dict) -> str:
    """ایجاد توکن دسترسی"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
