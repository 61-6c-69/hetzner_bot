from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database.models import Ticket, User, Server, Transaction
from typing import Optional, Sequence
from sqlalchemy.orm import joinedload
from datetime import datetime
from utils.notifications import notify_user


class AdminRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_tickets(self) -> Sequence[Ticket]:
        """Get all tickets with user info"""
        result = await self.db.execute(
            select(Ticket).join(User)
        )
        return result.scalars().all()

    async def get_ticket(self, ticket_id: int) -> Optional[Ticket]:
        """Get a ticket by ID"""
        result = await self.db.execute(
            select(Ticket)
            .options(joinedload(Ticket.user))
            .where(Ticket.id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def update_ticket(
            self,
            ticket_id: int,
            status: str,
            response: Optional[str] = None
    ) -> Optional[Ticket]:
        """Update ticket status and response"""
        ticket = await self.get_ticket(ticket_id)
        if ticket:
            ticket.status = status
            if response:
                ticket.response = response
            await self.db.commit()
            await self.db.refresh(ticket)
        return ticket

    async def get_open_tickets(self, skip: int = 0, limit: int = 100) -> Sequence[Ticket]:
        """Get open tickets"""
        result = await self.db.execute(
            select(Ticket)
            .options(joinedload(Ticket.user))
            .where(Ticket.status == 'open')
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_user(self, user_id: int) -> Optional[User]:
        """Get a user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user fields"""
        user = await self.get_user(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            await self.db.commit()
            await self.db.refresh(user)
        return user

    async def get_server(self, server_id: int) -> Optional[Server]:
        """Get a server by ID"""
        result = await self.db.execute(
            select(Server)
            .options(joinedload(Server.user))
            .where(Server.id == server_id)
        )
        return result.scalar_one_or_none()

    async def process_server_action(
            self,
            server_id: int,
            action: str,
            admin_id: int
    ) -> bool:
        """Process server action"""
        server = await self.get_server(server_id)
        if not server:
            return False

        # Update server status
        server.status = action
        await self.db.commit()

        # Notify user
        if server.user and server.user.telegram_id:
            message = (
                f"🔔 اقدام مدیر بر روی سرور\n"
                f"عملیات: {action}\n"
                f"زمان: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            await notify_user(server.user.id, message)

        return True

    async def send_notification(self, message: str) -> int:
        """Send notification to all users with telegram_id
        Returns number of successful notifications"""
        result = await self.db.execute(
            select(User).where(User.telegram_id.isnot(None))
        )
        users = result.scalars().all()

        success_count = 0
        for user in users:
            try:
                if await notify_user(user.id, message):
                    success_count += 1
            except Exception:
                continue

        return success_count

    async def get_telegram_users_count(self) -> int:
        """Get count of users with telegram_id"""
        result = await self.db.execute(
            select(func.count())
            .select_from(User)
            .where(User.telegram_id.isnot(None))
        )
        return result.scalar_one()

    async def get_users(self, skip: int = 0, limit: int = 100) -> Sequence[User]:
        """Get paginated list of users"""
        result = await self.db.execute(
            select(User)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_all_servers(self, skip: int = 0, limit: int = 100) -> Sequence[Server]:
        """Get paginated list of all servers"""
        result = await self.db.execute(
            select(Server)
            .options(joinedload(Server.user))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_ticket_user(self, ticket_id: int) -> Optional[User]:
        """Get the user who created the ticket"""
        result = await self.db.execute(
            select(User)
            .join(Ticket)
            .where(Ticket.id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def get_user_stats(self) -> dict:
        """Get overall user statistics"""
        total_users = await self.db.execute(select(func.count()).select_from(User))
        active_users = await self.db.execute(
            select(func.count())
            .select_from(User)
            .where(User.is_active == True)
        )
        telegram_users = await self.db.execute(
            select(func.count())
            .select_from(User)
            .where(User.telegram_id.isnot(None))
        )

        return {
            'total_users': total_users.scalar_one(),
            'active_users': active_users.scalar_one(),
            'telegram_users': telegram_users.scalar_one()
        }

    async def get_server_stats(self) -> dict:
        """Get overall server statistics"""
        total_servers = await self.db.execute(select(func.count()).select_from(Server))
        active_servers = await self.db.execute(
            select(func.count())
            .select_from(Server)
            .where(Server.status == 'running')
        )

        return {
            'total_servers': total_servers.scalar_one(),
            'active_servers': active_servers.scalar_one()
        }

    async def get_transaction_stats(self) -> dict:
        """Get overall transaction statistics"""
        total_result = await self.db.execute(
            select(
                func.count().label('count'),
                func.sum(Transaction.amount).label('total_amount')
            )
            .select_from(Transaction)
            .where(Transaction.status == 'completed')
        )
        row = total_result.first()

        return {
            'total_transactions': row.count if row else 0,
            'total_amount': float(row.total_amount if row and row.total_amount else 0)
        }
