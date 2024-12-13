from aiogram import types
from repositories.transaction_repository import TransactionRepository
from repositories.user_repository import UserRepository
from database.database import get_db


async def handle_transactions_list(message: types.Message):
    """لیست تراکنش‌های کاربر"""
    async for db in get_db():
        user_repo = UserRepository(db)
        tx_repo = TransactionRepository(db)

        # Get user
        user = await user_repo.get_by_telegram_id(message.from_user.id)
        if not user:
            await message.reply("لطفا ابتدا حساب کاربری خود را متصل کنید.")
            return

        # Get recent transactions
        transactions = await tx_repo.get_user_recent_transactions(user.id, limit=10)
        if not transactions:
            await message.reply("تراکنشی یافت نشد.")
            return

        response = "آخرین تراکنش‌های شما:\n\n"
        for tx in transactions:
            response += f"💰 مبلغ: {tx.amount:,} تومان\n"
            response += f"📝 توضیحات: {tx.description}\n"
            response += f"⏰ تاریخ: {tx.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"

        await message.reply(response)
