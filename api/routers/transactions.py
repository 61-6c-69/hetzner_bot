from repositories.transaction_repository import TransactionRepository
from repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from utils.payment import payment_handler
from utils.auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from database.database import get_db
from database.models import TransactionStatus
from typing import List
from api import schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.TransactionResponse])
async def list_transactions(
        current_user: schemas.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    repo = TransactionRepository(db)
    return await repo.get_user_transactions(current_user.id)


@router.post("/deposit", response_model=schemas.TransactionResponse)
async def create_deposit(
        deposit: schemas.DepositCreate,
        current_user: schemas.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    repo = TransactionRepository(db)

    # Process payment
    payment_result = await payment_handler.create_payment(
        amount=deposit.amount,
        description=deposit.description or "شارژ حساب کاربری"
    )

    # Create transaction
    transaction = await repo.create_deposit(
        user_id=current_user.id,
        amount=deposit.amount,
        payment_id=payment_result['payment_id'],
        description=deposit.description
    )

    return {
        "payment_url": payment_result.get('payment_url'),
        "transaction_id": transaction.id
    }


@router.get("/verify")
async def verify_payment(
        authority: str,
        status: str,
        db: AsyncSession = Depends(get_db)
):
    repo = TransactionRepository(db)

    # Get transaction
    transaction = await repo.get_by_payment_id(authority)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if status == "OK":
        # Verify payment with payment handler
        if await payment_handler.verify_payment(authority, transaction.amount):
            # Update transaction status
            await repo.update_status(authority, TransactionStatus.COMPLETED)
            return {"message": "Payment successful"}

    # Payment failed
    await repo.update_status(authority, TransactionStatus.FAILED)
    raise HTTPException(status_code=400, detail="Payment failed")


@router.get("/balance")
async def get_balance(
        current_user: schemas.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)
    balance = await repo.get_balance(current_user.id)
    return {"balance": balance}
