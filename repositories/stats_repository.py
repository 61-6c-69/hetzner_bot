from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import ServerStats
from repositories.base import BaseRepository


class StatsRepository(BaseRepository[ServerStats]):
    def __init__(self, db: AsyncSession):
        super().__init__(ServerStats, db)

    async def create_stats(
        self,
        server_id: int,
        cpu_usage: float,
        memory_usage: float,
        disk_usage: float,
        network_in: float,
        network_out: float
    ) -> ServerStats:
        """ایجاد آمار جدید برای سرور"""
        stats = ServerStats(
            server_id=server_id,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            network_in=network_in,
            network_out=network_out,
            timestamp=datetime.utcnow()
        )
        self.db.add(stats)
        await self.db.commit()
        await self.db.refresh(stats)
        return stats

    async def get_server_stats(
        self,
        server_id: int,
        from_date: datetime,
        to_date: datetime
    ) -> list[ServerStats]:
        """دریافت آمار سرور در بازه زمانی مشخص"""
        result = await self.db.execute(
            select(ServerStats)
            .where(
                ServerStats.server_id == server_id,
                ServerStats.timestamp >= from_date,
                ServerStats.timestamp <= to_date
            )
            .order_by(ServerStats.timestamp.desc())
        )
        return result.scalars().all()

    async def delete_old_stats(self, before_date: datetime) -> None:
        """حذف آمارهای قدیمی"""
        await self.db.execute(
            select(ServerStats)
            .where(ServerStats.timestamp < before_date)
            .delete()
        )
        await self.db.commit()

    async def get_latest_stats(self, server_id: int) -> ServerStats:
        """دریافت آخرین آمار سرور"""
        result = await self.db.execute(
            select(ServerStats)
            .where(ServerStats.server_id == server_id)
            .order_by(ServerStats.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none() 