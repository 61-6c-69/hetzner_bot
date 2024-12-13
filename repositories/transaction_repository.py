from database.models import Transaction, TransactionType, TransactionStatus
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import select
from datetime import datetime


class TransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_transactions(self, user_id: int) -> List[Transaction]:
        """Get all transactions for a user"""
        result = await self.db.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_user_recent_transactions(self, user_id: int, limit: int) -> List[Transaction]:
        """Get all transactions for a user"""
        result = await self.db.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create_deposit(
        self,
        user_id: int,
        amount: float,
        payment_id: str,
        description: Optional[str] = None
    ) -> Transaction:
        """Create a new deposit transaction"""
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            type=TransactionType.DEPOSIT,
            status=TransactionStatus.PENDING,
            payment_id=payment_id,
            description=description or 'شارژ حساب کاربری',
            created_at=datetime.utcnow()
        )
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction

    async def update_status(
        self,
        payment_id: str,
        status: TransactionStatus,
        approved_by: Optional[int] = None
    ) -> Optional[Transaction]:
        """Update transaction status by payment ID"""
        result = await self.db.execute(
            select(Transaction)
            .where(Transaction.payment_id == payment_id)
        )
        transaction = result.scalar_one_or_none()
        
        if transaction:
            transaction.status = status
            if approved_by and status == TransactionStatus.COMPLETED:
                transaction.approved_by = approved_by
                transaction.approved_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(transaction)
        
        return transaction

    async def get_by_payment_id(self, payment_id: str) -> Optional[Transaction]:
        """Get transaction by payment ID"""
        result = await self.db.execute(
            select(Transaction)
            .where(Transaction.payment_id == payment_id)
        )
        return result.scalar_one_or_none()

    async def create_server_charge(
        self,
        user_id: int,
        amount: float,
        server_id: int
    ) -> Transaction:
        """Create a server charge transaction"""
        transaction = Transaction(
            user_id=user_id,
            amount=-amount,  # منفی چون هزینه است
            type=TransactionType.SERVER_CHARGE,
            status=TransactionStatus.COMPLETED,
            description=f'هزینه سرور {server_id}',
            created_at=datetime.utcnow()
        )
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction