from api.models import PhoneVerification, TokenResponse, OTPVerification
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, HTTPException
from database.models import User, OTPCode
from datetime import datetime, timedelta
from utils.sms import sms_service
from jose import jwt
import logging
import random
import string

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/verify-otp")


def generate_otp():
    """تولید کد تصادفی 6 رقمی"""
    return ''.join(random.choices(string.digits, k=6))


@router.post("/request-otp")
async def request_otp(data: PhoneVerification):
    """درخواست کد تایید"""
    phone = data.phone

    # بررسی فرمت شماره موبایل
    if not phone.startswith('+98') and not phone.startswith('09'):
        raise HTTPException(status_code=400, detail="Invalid phone number format")

    # استاندارد کردن فرمت شماره
    if phone.startswith('0'):
        phone = '+98' + phone[1:]

    # بررسی وجود کاربر در تلگرام
    user = await User.get_or_none(phone=phone)
    if not user or not user.telegram_id:
        raise HTTPException(
            status_code=403,
            detail="Please register through Telegram bot first"
        )

    # حذف کدهای قبلی
    await OTPCode.filter(phone=phone, is_used=False).delete()

    # تولید و ذخیره کد جدید
    code = generate_otp()
    await OTPCode.create(
        phone=phone,
        code=code
    )

    # ارسال کد از طریق پیامک
    success = await sms_service.send_otp(phone, code)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send OTP")

    return {"message": "OTP sent successfully"}


@router.post("/verify-phone")
async def verify_phone(phone: PhoneVerification):
    """ارسال کد تایید به شماره موبایل"""
    # بررسی فرمت شماره موبایل
    if not phone.phone.startswith('09') or len(phone.phone) != 11:
        raise HTTPException(status_code=400, detail="Invalid phone number")

    # تبدیل به فرمت بین‌المللی
    international_phone = '+98' + phone.phone[1:]

    # تولید و ارسال کد
    code = ''.join(random.choices(string.digits, k=5))

    # ذخیره کد در دیتابیس
    await OTPCode.create(
        phone=international_phone,
        code=code
    )

    # ارسال کد از طریق پیامک
    try:
        await sms_service.send_otp(international_phone, code)
    except Exception as e:
        logging.error(f"Failed to send OTP: {e}")
        raise HTTPException(status_code=500, detail="Failed to send OTP")

    return {"message": "OTP sent successfully"}


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(data: OTPVerification):
    """تایید کد و ورود/ثبت‌نام"""
    # تبدیل به فرم�� بین‌المللی
    phone = data.phone
    if phone.startswith('09'):
        phone = '+98' + phone[1:]

    # بررسی کد
    otp = await OTPCode.get_or_none(
        phone=phone,
        code=data.code,
        is_used=False,
        created_at__gte=datetime.utcnow() - timedelta(minutes=2)
    )

    if not otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    otp.is_used = True
    await otp.save()

    # پیدا کردن یا ایجاد کاربر
    user = await User.get_or_none(phone=phone)
    if not user:
        # ایجاد کاربر جدید
        user = await User.create(
            phone=phone,
            first_name="کاربر جدید",
            last_name=None,
            username=None
        )
    # ایجاد توکن
    access_token = jwt.encode(
        {
            "sub": str(user.id),
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
