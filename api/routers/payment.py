from repositories.transaction_repository import TransactionRepository
from repositories.user_repository import UserRepository
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from utils.payment import PaymentHandler
from utils.auth import get_current_user
from database.database import get_db
from config import API_URL
from api import schemas

router = APIRouter()


@router.get("/transactions", response_model=list[schemas.TransactionResponse])
async def list_transactions(
        current_user: schemas.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    repo = TransactionRepository(db)
    return await repo.get_user_transactions(current_user.id)


@router.get("/balance")
async def get_balance(
        current_user: schemas.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)
    balance = await repo.get_balance(current_user.id)
    return {"balance": balance}


@router.post("/")
async def create_payment_link(
        amount: int,
        current_user: schemas.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    transaction_repo = TransactionRepository(db)
    payment_handler = PaymentHandler()

    try:
        # Create pending transaction
        transaction = await transaction_repo.create(
            user_id=current_user.id,
            amount=amount,
            status='pending'
        )

        # Create payment link
        payment_link = await payment_handler.create_payment(
            amount=amount,
            description=f"شارژ حساب کاربری {current_user.username}",
            callback_url=f"{API_URL}/payments/verify?transaction_id={transaction.id}",
            transaction=transaction
        )

        return {"payment_link": payment_link}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/verify")
async def verify_payment(
        status: str,
        authority: str,
        db: AsyncSession = Depends(get_db)
):
    transaction_repo = TransactionRepository(db)
    payment_handler = PaymentHandler()

    # Get transaction
    transaction = await transaction_repo.get_by_payment_id(authority)
    if not transaction or transaction.status != 'pending':
        raise HTTPException(status_code=400, detail="Invalid transaction")

    if status == "OK":
        # Verify payment
        if await payment_handler.verify_payment(authority):
            # Update transaction status
            await transaction_repo.update_status(transaction.id, 'completed')
            return {"message": "Payment successful"}

    # Payment failed
    await transaction_repo.update_status(transaction.id, 'failed')
    raise HTTPException(status_code=400, detail="Payment failed")
