from datetime import datetime
from tortoise.exceptions import DoesNotExist
from models import User, Transaction, NotificationSettings

async def get_or_create_user(tg_user):
    """دریافت یا ایجاد کاربر جدید"""
    try:
        user = await User.get(telegram_id=tg_user.id)
    except DoesNotExist:
        user = await User.create(
            telegram_id=tg_user.id,
            username=tg_user.username or f"user_{tg_user.id}",
            password_hash="",  # باید بعداً توسط کاربر تنظیم شود
            email="",  # باید بعداً توسط کاربر تنظیم شود
            phone="",  # باید بعداً توسط کاربر تنظیم شود
            role="user",
            is_active=True
        )
        # ایجاد تنظیمات اعلان‌ها برای کاربر جدید
        await NotificationSettings.create(
            user=user,
            server_notifications=True,
            payment_notifications=True,
            ticket_notifications=True,
            low_balance_threshold=10
        )
    
    return user

async def get_user_balance(telegram_id: int) -> float:
    """دریافت موجودی کاربر از تراکنش‌ها"""
    try:
        user = await User.get(telegram_id=telegram_id)
        # Calculate balance from transactions
        transactions = await Transaction.filter(user_id=user.id, status='completed')
        balance = 0.0
        for tx in transactions:
            if tx.type in ['deposit']:
                balance += float(tx.amount)
            elif tx.type in ['withdrawal', 'server_charge', 'ip_change']:
                balance -= float(tx.amount)
        return balance
    except DoesNotExist:
        return 0.0

async def add_transaction(user_id: int, amount: float, type: str, description: str, payment_id: str = None) -> Transaction:
    """ثبت تراکنش جدید"""
    return await Transaction.create(
        user_id=user_id,
        amount=amount,
        type=type,
        status='pending',
        payment_id=payment_id,
        description=description
    )

async def complete_transaction(payment_id: str) -> Transaction:
    """تکمیل تراکنش"""
    try:
        transaction = await Transaction.get(payment_id=payment_id)
        if transaction.status != 'completed':
            transaction.status = 'completed'
            # به‌روزرسانی موجودی کاربر
            user = await User.get(id=transaction.user_id)
            if transaction.type == 'deposit':
                user.balance += transaction.amount
            elif transaction.type == 'withdraw':
                user.balance -= transaction.amount
            await user.save()
            await transaction.save()
        return transaction
    except DoesNotExist:
        raise ValueError("تراکنش مورد نظر یافت نشد")

async def cancel_transaction(payment_id: str) -> Transaction:
    """لغو تراکنش"""
    try:
        transaction = await Transaction.get(payment_id=payment_id)
        if transaction.status == 'pending':
            transaction.status = 'failed'
            await transaction.save()
        return transaction
    except DoesNotExist:
        raise ValueError("تراکنش مورد نظر یافت نشد")

async def get_user_transactions(user_id: int, limit: int = 10) -> list[Transaction]:
    """دریافت لیست تراکنش‌های کاربر"""
    return await Transaction.filter(user_id=user_id).order_by('-created_at').limit(limit)

async def update_user_profile(telegram_id: int, **kwargs) -> User:
    """به‌روزرسانی پروفایل کاربر"""
    try:
        user = await User.get(telegram_id=telegram_id)
        for key, value in kwargs.items():
            setattr(user, key, value)
        await user.save()
        return user
    except DoesNotExist:
        raise ValueError("کاربر مورد نظر یافت نشد")

async def get_notification_settings(user_id: int) -> NotificationSettings:
    """دریافت تنظیمات اعلان‌های کاربر"""
    try:
        return await NotificationSettings.get(user_id=user_id)
    except DoesNotExist:
        raise ValueError("تنظیمات اعلان برای کاربر یافت نشد") 