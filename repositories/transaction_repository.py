from database.models import Transaction, TransactionType, TransactionStatus, User
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func
from fastapi import HTTPException
from decimal import Decimal

from repositories.base import BaseRepository


class TransactionManager:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_user_with_lock(self, user_id: int) -> Optional[User]:
        """Get user with row-level lock for atomic operations"""
        result = await self.db.execute(
            select(User)
            .where(User.id == user_id)
            .with_for_update()  # This applies a row-level lock
        )
        return result.scalar_one_or_none()

    async def _calculate_balance(self, user_id: int) -> Decimal:
        """Calculate user balance with precision"""
        result = await self.db.execute(
            select(func.sum(Transaction.amount))
            .where(
                Transaction.user_id == user_id,
                Transaction.status == TransactionStatus.COMPLETED
            )
        )
        balance = result.scalar()
        return Decimal(str(balance if balance is not None else '0'))

    async def create_deposit(
        self,
        user_id: int,
        amount: float,
        payment_id: str,
        description: Optional[str] = None
    ) -> Tuple[Transaction, Decimal]:
        """Create a deposit transaction atomically"""
        # Get user with lock
        user = await self._get_user_with_lock(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create transaction
        transaction = Transaction(
            user_id=user_id,
            amount=Decimal(str(amount)),
            type=TransactionType.DEPOSIT,
            status=TransactionStatus.PENDING,
            payment_id=payment_id,
            description=description or 'شارژ حساب کاربری',
            created_at=datetime.utcnow()
        )
        self.db.add(transaction)
        
        # Calculate new balance
        new_balance = await self._calculate_balance(user_id)
        
        await self.db.commit()
        await self.db.refresh(transaction)
        
        return transaction, new_balance

    async def create_server_charge(
        self,
        user_id: int,
        amount: float,
        server_id: int
    ) -> Tuple[Transaction, Decimal]:
        """Create a server charge transaction atomically with balance check"""
        # Get user with lock
        user = await self._get_user_with_lock(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Calculate current balance
        current_balance = await self._calculate_balance(user_id)
        charge_amount = Decimal(str(amount))

        # Check if user has sufficient balance
        if current_balance < charge_amount:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient balance. Required: {charge_amount}, Available: {current_balance}"
            )

        # Create transaction
        transaction = Transaction(
            user_id=user_id,
            amount=-charge_amount,  # Negative for charges
            type=TransactionType.SERVER_CHARGE,
            status=TransactionStatus.COMPLETED,
            description=f'هزینه سرور {server_id}',
            created_at=datetime.utcnow()
        )
        self.db.add(transaction)
        
        # Calculate new balance
        new_balance = current_balance - charge_amount
        
        await self.db.commit()
        await self.db.refresh(transaction)
        
        return transaction, new_balance

    async def complete_transaction(
        self,
        payment_id: str,
        approved_by: Optional[int] = None
    ) -> Tuple[Transaction, Decimal]:
        """Complete a pending transaction atomically"""
        # Get transaction with user lock
        result = await self.db.execute(
            select(Transaction)
            .where(Transaction.payment_id == payment_id)
            .options(selectinload(Transaction.user))
        )
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
            
        if transaction.status != TransactionStatus.PENDING:
            raise HTTPException(status_code=400, detail="Transaction is not pending")

        # Get user with lock
        user = await self._get_user_with_lock(transaction.user_id)
        
        # Update transaction
        transaction.status = TransactionStatus.COMPLETED
        if approved_by:
            transaction.approved_by = approved_by
            transaction.approved_at = datetime.utcnow()
        
        # Calculate new balance
        new_balance = await self._calculate_balance(transaction.user_id)
        
        await self.db.commit()
        await self.db.refresh(transaction)
        
        return transaction, new_balance


class TransactionRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
        self.cache_ttl = timedelta(minutes=30)
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