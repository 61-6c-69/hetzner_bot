from repositories.verification_repository import VerificationRepository
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from utils.auth import create_access_token
from database.database import get_db
from utils.sms import sms_service
from api import schemas

router = APIRouter()


@router.post("/request-otp")
async def request_otp(
    data: schemas.PhoneVerification,
    db: AsyncSession = Depends(get_db)
):
    """درخواست کد تایید"""
    phone = data.phone

    # بررسی فرمت شماره موبایل
    if not phone.startswith('+98') and not phone.startswith('09'):
        raise HTTPException(status_code=400, detail="Invalid phone number format")

    # استاندارد کردن فرمت شماره
    if phone.startswith('0'):
        phone = '+98' + phone[1:]

    repo = VerificationRepository(db)
    
    # بررسی وجود کاربر و ایجاد کد
    try:
        code = await repo.create_code(phone)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # ارسال کد از طریق پیامک
    success = await sms_service.send_otp(phone, code)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send OTP")

    return {"message": "OTP sent successfully"}


@router.post("/verify-otp", response_model=schemas.Token)
async def verify_otp(
    data: schemas.OTPVerification,
    db: AsyncSession = Depends(get_db)
):
    """تایید کد و ورود"""
    # تبدیل به فرمت بین‌المللی
    phone = data.phone
    if phone.startswith('09'):
        phone = '+98' + phone[1:]

    repo = VerificationRepository(db)
    
    try:
        # تایید کد
        is_valid, user_id = await repo.verify_code(phone, data.code)

        # دریافت اطلاعات کاربر
        user = await repo.get_user_by_phone(phone)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # ایجاد توکن
        access_token = create_access_token({"sub": str(user.id)})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
