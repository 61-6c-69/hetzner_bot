from sqlalchemy import select
from database.models import Transaction, User
from database.database import AsyncSessionLocal

async def handle_transactions_list(message: types.Message):
    async with AsyncSessionLocal() as db:
        # Get user
        result = await db.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.reply("لطفا ابتدا حساب کاربری خود را متصل کنید.")
            return
            
        # Get recent transactions
        result = await db.execute(
            select(Transaction)
            .where(Transaction.user_id == user.id)
            .order_by(Transaction.created_at.desc())
            .limit(10)
        )
        transactions = result.scalars().all()
        
        if not transactions:
            await message.reply("تراکنشی یافت نشد.")
            return
            
        response = "آخرین تراکنش‌های شما:\n\n"
        for tx in transactions:
            response += f"💰 مبلغ: {tx.amount:,} تومان\n"
            response += f"📝 توضیحات: {tx.description}\n"
            response += f"⏰ تاریخ: {tx.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            
        await message.reply(response) 