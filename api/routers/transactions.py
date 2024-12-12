from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from api.database import get_db
from api.models import User
from api.schemas import Transaction, TransactionCreate
from api.utils import get_current_user

router = APIRouter()

@router.post("/", response_model=Transaction)
async def create_transaction(
    transaction: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    async with db.begin():
        db_transaction = Transaction(
            user_id=current_user.id,
            amount=transaction.amount,
            description=transaction.description,
            status='pending'
        )
        db.add(db_transaction)
        await db.commit()
        await db.refresh(db_transaction)
    return db_transaction 