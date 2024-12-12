from database.models import Ticket, Base, TicketMessage
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.base import BaseRepository
from core.settings import CACHE_TTL_DEFAULT
from typing import List, Optional, TypeVar
from datetime import timedelta, datetime
from sqlalchemy import select, func

ModelType = TypeVar("ModelType", bound=Base)


class TicketRepository(BaseRepository[Ticket]):
    def __init__(self, db: AsyncSession):
        super().__init__(Ticket, db)
        self.cache_ttl = timedelta(seconds=CACHE_TTL_DEFAULT)

    async def get_user_tickets(self, user_id: int, limit: Optional[int] = None) -> List[Ticket]:
        """Get user's tickets"""
        cache_key = self._get_cache_key(f"user:{user_id}:tickets:{limit}")

        cached_tickets = await self._get_from_cache(cache_key)
        if cached_tickets:
            return cached_tickets

        query = select(Ticket).where(Ticket.user_id == user_id)
        if limit:
            query = query.limit(limit)

        result = await self.db.execute(query)
        tickets = list(result.scalars().all())

        await self._set_cache(cache_key, tickets)
        return tickets

    async def get_user_ticket(self, user_id: int, ticket_id: int) -> Optional[Ticket]:
        """Get a specific user's ticket"""
        result = await self.db.execute(
            select(Ticket)
            .where(Ticket.user_id == user_id)
            .where(Ticket.id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def create(
            self,
            user_id: int,
            subject: str,
            message: str,
            file_path: Optional[str] = None,
            priority: str = 'normal'
    ) -> Ticket:
        """Create a new ticket"""
        ticket = Ticket(
            user_id=user_id,
            subject=subject,
            message=message,
            file_path=file_path,
            status='open',
            created_at=datetime.utcnow()
        )
        self.db.add(ticket)
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    async def update_status(
            self,
            ticket_id: int,
            status: str,
            response: Optional[str] = None
    ) -> Optional[Ticket]:
        """Update ticket status and optionally add response"""
        ticket = await self.get(ticket_id)
        if ticket:
            setattr(ticket, 'status', status)
            if response:
                setattr(ticket, 'response', response)
            await self.db.commit()
            await self.db.refresh(ticket)

            # Update cache
            cache_key = self._get_cache_key(str(ticket_id))
            await self._set_cache(cache_key, ticket)

            # Clear user tickets cache
            user_tickets_key = self._get_cache_key(f"user:{ticket.user_id}:tickets")
            await self.redis.delete(user_tickets_key)
        return ticket

    async def get_open_tickets(self, limit: int = 100) -> List[Ticket]:
        """Get open tickets"""
        cache_key = self._get_cache_key(f"open_tickets:{limit}")

        cached_tickets = await self._get_from_cache(cache_key)
        if cached_tickets:
            return cached_tickets

        result = await self.db.execute(
            select(Ticket)
            .where(Ticket.status == 'open')
            .limit(limit)
        )
        tickets = list(result.scalars().all())

        await self._set_cache(cache_key, tickets)
        return tickets

    async def get_user_tickets_by_status(
            self,
            user_id: int,
            status: str,
            limit: int = 100
    ) -> List[Ticket]:
        """Get user's tickets by status"""
        cache_key = self._get_cache_key(f"user:{user_id}:tickets:{status}:{limit}")

        cached_tickets = await self._get_from_cache(cache_key)
        if cached_tickets:
            return cached_tickets

        result = await self.db.execute(
            select(Ticket)
            .where(Ticket.user_id == user_id)
            .where(Ticket.status == status)
            .limit(limit)
        )
        tickets = list(result.scalars().all())

        await self._set_cache(cache_key, tickets)
        return tickets

    async def get_tickets_stats(self, user_id: int) -> dict:
        """Get ticket statistics for a user"""
        result = await self.db.execute(
            select(
                Ticket.status,
                func.count(Ticket.id).label('count')
            )
            .where(Ticket.user_id == user_id)
            .group_by(Ticket.status)
        )

        stats = {}
        for row in result:
            stats[row.status] = row.count
        return stats

    async def add_reply(
            self,
            ticket_id: int,
            user_id: int,
            message: str,
            file_path: Optional[str] = None
    ) -> TicketMessage:
        """Add a reply to a ticket"""
        message = TicketMessage(
            ticket_id=ticket_id,
            user_id=user_id,
            message=message,
            file_path=file_path,
            created_at=datetime.utcnow()
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_ticket_messages(self, ticket_id: int) -> List[TicketMessage]:
        """Get all messages for a ticket"""
        result = await self.db.execute(
            select(TicketMessage)
            .where(TicketMessage.ticket_id == ticket_id)
            .order_by(TicketMessage.created_at)
        )
        return list(result.scalars().all())
