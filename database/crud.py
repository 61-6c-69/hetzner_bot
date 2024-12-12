from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api import schemas
from . import models
from typing import Optional, List


async def get_user(db: AsyncSession, user_id: int) -> Optional[models.User]:
    result = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    result = await db.execute(
        select(models.User).where(models.User.email == email)
    )
    return result.scalar_one_or_none()


async def get_servers(db: AsyncSession, user_id: int) -> List[models.Server]:
    result = await db.execute(
        select(models.Server)
        .where(models.Server.user_id == user_id)
        .options(selectinload(models.Server.user))
    )
    return result.scalars().all()


async def create_server(db: AsyncSession, server: schemas.ServerCreate, user_id: int) -> models.Server:
    db_server = models.Server(
        **server.dict(),
        user_id=user_id
    )
    db.add(db_server)
    await db.commit()
    await db.refresh(db_server)
    return db_server
