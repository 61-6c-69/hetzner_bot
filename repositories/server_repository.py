from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Server
from repositories.base import BaseRepository
from typing import List, Optional, Dict, Any, Tuple
from utils.hetzner_api import hetzner
from utils.server_sync import ServerSynchronizer
from fastapi import HTTPException


class ServerRepository(BaseRepository[Server]):
    def __init__(self, db: AsyncSession):
        super().__init__(Server, db)
        self.synchronizer = ServerSynchronizer(db)

    async def create_server(
        self,
        user_id: int,
        name: str,
        server_type: str,
        location: str,
        os: str
    ) -> Tuple[Server, Dict]:
        """Create a new server with Hetzner integration"""
        try:
            # ایجاد سرور در Hetzner
            hetzner_response = await hetzner.create_server(server_type, location, os)
            
            # ایجاد سرور در دیتابیس
            server = await super().create(
                user_id=user_id,
                name=name,
                hetzner_id=hetzner_response['server']['id'],
                type=server_type,
                location=location,
                os=os,
                status='creating',
                ip=hetzner_response['server']['public_net']['ipv4']['ip'],
                created_at=datetime.utcnow()
            )
            
            return server, hetzner_response

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating server: {str(e)}"
            )

    async def get_user_servers(
        self,
        user_id: int,
        sync: bool = False
    ) -> List[Server]:
        """Get user's servers with optional sync"""
        result = await self.db.execute(
            select(Server).where(Server.user_id == user_id)
        )
        servers = result.scalars().all()
        
        if sync:
            for server in servers:
                await self.synchronizer.sync_server(server.id)
        
        return servers

    async def get_server_with_sync(
        self,
        server_id: int,
        user_id: Optional[int] = None
    ) -> Server:
        """Get server with status sync"""
        query = select(Server).where(Server.id == server_id)
        if user_id:
            query = query.where(Server.user_id == user_id)
            
        result = await self.db.execute(query)
        server = result.scalar_one_or_none()
        
        if not server:
            raise HTTPException(status_code=404, detail="Server not found")
            
        # همگام‌سازی وضعیت
        await self.synchronizer.sync_server(server.id)
        
        return server

    async def power_on(self, server_id: int, user_id: Optional[int] = None) -> Server:
        """Power on server"""
        server = await self.get_server_with_sync(server_id, user_id)
        
        try:
            await hetzner.power_on(server.hetzner_id)
            server.status = 'starting'
            await self.db.commit()
            return server
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error powering on server: {str(e)}"
            )

    async def power_off(self, server_id: int, user_id: Optional[int] = None) -> Server:
        """Power off server"""
        server = await self.get_server_with_sync(server_id, user_id)
        
        try:
            await hetzner.power_off(server.hetzner_id)
            server.status = 'stopping'
            await self.db.commit()
            return server
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error powering off server: {str(e)}"
            )

    async def get_server_metrics(self, server_id: int, user_id: Optional[int] = None) -> Dict:
        """Get server metrics"""
        server = await self.get_server_with_sync(server_id, user_id)
        
        try:
            return await hetzner.get_server_metrics(server.hetzner_id)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting server metrics: {str(e)}"
            )

    async def change_ip(self, server_id: int, user_id: Optional[int] = None) -> Server:
        """Change server IP"""
        server = await self.get_server_with_sync(server_id, user_id)
        
        try:
            response = await hetzner.change_ip(server.hetzner_id)
            # همگام‌سازی اجباری برای دریافت IP جدید
            await self.synchronizer.sync_server(server.id, force=True)
            return server
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error changing server IP: {str(e)}"
            )
