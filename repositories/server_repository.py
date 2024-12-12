from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from database.models import Server, User
from utils.hetzner_api import hetzner
from typing import List, Optional, Dict, Any
from datetime import datetime


class ServerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_servers(self, user_id: int) -> List[Server]:
        """Get all servers for a user"""
        result = await self.db.execute(
            select(Server).where(Server.user_id == user_id)
        )
        return result.scalars().all()

    async def get_server(self, server_id: int) -> Optional[Server]:
        """Get a single server by ID"""
        result = await self.db.execute(
            select(Server).where(Server.id == server_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: int, **server_data) -> Server:
        """Create a new server"""
        server = Server(user_id=user_id, **server_data)
        self.db.add(server)
        await self.db.commit()
        await self.db.refresh(server)
        return server

    async def update_status(self, server_id: int, status: str) -> bool:
        """Update server status"""
        result = await self.db.execute(
            update(Server)
            .where(Server.id == server_id)
            .values(status=status)
            .returning(Server)
        )
        await self.db.commit()
        return bool(result.scalar_one_or_none())

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
        server = await self.get_server(server_id)
        if not server:
            return None
            
        # Get stats from Hetzner
        return await hetzner.get_server_metrics(server.hetzner_id)

    async def perform_action(self, server_id: int, action: str) -> bool:
        """Perform action on server (start/stop/restart)"""
        server = await self.get_server(server_id)
        if not server:
            return False

        # Perform action via Hetzner API
        if action == "start":
            success = await hetzner.power_on(server.hetzner_id)
            if success:
                await self.update_status(server_id, "running")
        elif action == "stop":
            success = await hetzner.power_off(server.hetzner_id)
            if success:
                await self.update_status(server_id, "stopped")
        elif action == "restart":
            success = await hetzner.power_off(server.hetzner_id)
            if success:
                success = await hetzner.power_on(server.hetzner_id)
                if success:
                    await self.update_status(server_id, "running")
        else:
            return False

        return success

    async def change_ip(self, server_id: int) -> bool:
        """Change server IP address"""
        server = await self.get_server(server_id)
        if not server:
            return False

        # Request IP change from Hetzner
        result = await hetzner.change_ip(server.hetzner_id)
        if result and result.get('ip'):
            await self.update_ip(server_id, result['ip'])
            return True
        return False

    async def delete(self, server_id: int) -> bool:
        """Delete a server"""
        server = await self.get_server(server_id)
        if not server:
            return False

        # Delete from Hetzner first
        if await hetzner.delete_server(server.hetzner_id):
            await self.db.delete(server)
            await self.db.commit()
            return True
        return False
