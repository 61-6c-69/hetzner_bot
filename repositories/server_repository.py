from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Server
from repositories.base import BaseRepository
from typing import List, Optional, Dict, Any

from utils.hetzner_api import hetzner


class ServerRepository(BaseRepository[Server]):
    def __init__(self, db: AsyncSession):
        super().__init__(Server, db)

    async def get_running_servers(self) -> List[Server]:
        """دریافت سرورهای در حال اجرا"""
        result = await self.db.execute(
            select(Server)
            .where(Server.status == 'running')
            .order_by(Server.id)
        )
        return result.scalars().all()

    async def get_by_id(self, server_id: int) -> Optional[Server]:
        """دریافت سرور با شناسه"""
        result = await self.db.execute(
            select(Server).where(Server.id == server_id)
        )
        return result.scalar_one_or_none()

    async def get_user_servers(self, user_id: int) -> List[Server]:
        """دریافت سرورهای یک کاربر"""
        result = await self.db.execute(
            select(Server)
            .where(Server.user_id == user_id)
            .order_by(Server.created_at.desc())
        )
        return result.scalars().all()

    async def create_server(
        self,
        user_id: int,
        name: str,
        hetzner_id: str,
        server_type: str,
        status: str = 'creating',
        hourly_price: float = 0
    ) -> Server:
        """ایجاد سرور جدید"""
        server = Server(
            user_id=user_id,
            name=name,
            hetzner_id=hetzner_id,
            server_type=server_type,
            status=status,
            hourly_price=hourly_price,
            created_at=datetime.utcnow(),
            last_charge_at=datetime.utcnow()
        )
        self.db.add(server)
        await self.db.commit()
        await self.db.refresh(server)
        return server

    async def update_status(
        self,
        server_id: int,
        status: str,
        error_message: Optional[str] = None
    ) -> Optional[Server]:
        """به‌روزرسانی وضعیت سرور"""
        server = await self.get_by_id(server_id)
        if server:
            server.status = status
            if error_message:
                server.error_message = error_message
            await self.db.commit()
            await self.db.refresh(server)
        return server

    async def update_last_charge(
        self,
        server_id: int,
        charge_time: datetime
    ) -> Optional[Server]:
        """به‌روزرسانی زمان آخرین شارژ"""
        server = await self.get_by_id(server_id)
        if server:
            server.last_charge_at = charge_time
            await self.db.commit()
            await self.db.refresh(server)
        return server

    async def delete_server(self, server_id: int) -> bool:
        """حذف سرور"""
        server = await self.get_by_id(server_id)
        if server:
            await self.db.delete(server)
            await self.db.commit()
            return True
        return False

    async def update_ip(self, server_id: int, new_ip: str) -> bool:
        """Update server IP address"""
        result = await self.db.execute(
            update(Server)
            .where(Server.id == server_id)
            .values(ip=new_ip)
            .returning(Server)
        )
        await self.db.commit()
        return bool(result.scalar_one_or_none())

    async def get_server_stats(self, server_id: int) -> Dict[str, Any]:
        """Get server monitoring stats"""
        server = await self.get(server_id)
        if not server:
            return None
            
        # Get stats from Hetzner
        return await hetzner.get_server_metrics(server.hetzner_id)
