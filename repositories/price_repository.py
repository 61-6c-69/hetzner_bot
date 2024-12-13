from utils.price_cache import update_price_cache, get_cached_prices
from sqlalchemy.ext.asyncio import AsyncSession
from utils.hetzner_api import hetzner
from database.models import Server
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy import select


class PriceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_prices(self) -> List[Dict[str, Any]]:
        """Get all server prices with caching"""
        # Try to get from cache first
        cached_prices = await get_cached_prices()
        if cached_prices:
            return cached_prices

        # If not in cache, fetch from Hetzner API
        prices = await hetzner.get_prices()
        
        # Update cache
        await update_price_cache()
        
        return prices

    async def get_server_price(self, server_type: str) -> Dict[str, Any]:
        """Get price for specific server type"""
        prices = await update_price_cache()
        return next(
            (p for p in prices if p['type'] == server_type),
            None
        )

    async def calculate_server_cost(self, server_id: int) -> Dict[str, float]:
        """Calculate current server costs"""
        result = await self.db.execute(
            select(Server).where(Server.id == server_id)
        )
        server = result.scalar_one_or_none()
        if not server:
            return None

        # Get base price
        price = await self.get_server_price(server.type)
        if not price:
            return None

        return {
            'hourly': price['hourly_price'],
            'daily': price['hourly_price'] * 24,
            'monthly': price['hourly_price'] * 24 * 30,
            'current_usage': await self._calculate_current_usage(server)
        }

    async def _calculate_current_usage(self, server: Server) -> float:
        """Calculate current usage cost for a server"""
        if not server.last_charge_at:
            return 0.0

        # Get hours since last charge
        hours = (datetime.utcnow() - server.last_charge_at).total_seconds() / 3600
        
        # Get server price
        price = await self.get_server_price(server.type)
        if not price:
            return 0.0

        return hours * price['hourly_price']
