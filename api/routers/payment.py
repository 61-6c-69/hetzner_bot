from fastapi import APIRouter, Depends, HTTPException
from database.models import User, Transaction
from api.models import TransactionResponse
from utils.payment import PaymentHandler
from utils.auth import get_current_user
from config import API_URL
from typing import List


router = APIRouter()


@router.get("/transactions", response_model=List[TransactionResponse])
async def list_transactions(user: User = Depends(get_current_user)):
    """لیست تراکنش‌ها"""
    transactions = await Transaction.filter(user=user).order_by('-created_at')
    return transactions


@router.get("/balance")
async def get_balance(user: User = Depends(get_current_user)):
    """دریافت موجودی"""
    balance = await user.get_balance()
    return {"balance": balance}


@router.post("/")
async def create_payment_link(
        amount: int,
        current_user: User = Depends(get_current_user)
):
    """ایجاد لینک پرداخت"""
    try:
        # ایجاد تراکنش در وضعیت pending
        transaction = await Transaction.create(
            user=current_user,
            amount=amount,
            status='pending'
        )

        payment_handler = PaymentHandler()
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
async def verify_payment_callback(
        status: str,
        authority: str,
        transaction_id: int
):
    """کالبک تایید پرداخت"""
    try:
        transaction = await Transaction.get_or_none(id=transaction_id)
        if not transaction or transaction.status != 'pending':
            raise HTTPException(status_code=400, detail="تراکنش نامعتبر است")

        if status == "OK":
            payment_handler = PaymentHandler()
            success = await payment_handler.verify_payment(
                transaction=transaction,
                authority=authority
            )

            if success:
                return {"message": "پرداخت با موفقیت انجام شد"}

        raise HTTPException(status_code=400, detail="پرداخت ناموفق")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
