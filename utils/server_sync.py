from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Server
from utils.hetzner_api import hetzner
from utils.notifications import send_notification, NotificationType
from utils.cache import cache_service
from utils.cache_manager import cache_manager
from utils.rate_limiter import rate_limiter, RateLimits
import logging
from fastapi import HTTPException
import asyncio

logger = logging.getLogger(__name__)

class ServerSynchronizer:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.sync_interval = timedelta(minutes=5)
        self.last_sync: Dict[int, datetime] = {}
        self.error_counts: Dict[int, int] = {}
        self.max_retry_attempts = 3
        self.metrics_ttl = 300  # 5 دقیقه برای کش متریک‌ها

    async def _get_server_from_db(self, server_id: int) -> Optional[Server]:
        """Get server from database"""
        result = await self.db.execute(
            select(Server).where(Server.id == server_id)
        )
        return result.scalar_one_or_none()

    async def _update_server_status(self, server: Server, server_info: Dict[str, Any]) -> None:
        """به‌روزرسانی وضعیت سرور در دیتابیس"""
        old_status = str(server.status)
        new_status = str(server_info['status'])
        
        server.status = new_status
        server.ip = server_info.get('public_net', {}).get('ipv4', {}).get('ip')
        server.last_sync = datetime.utcnow()
        
        # ریست شمارنده خطا در صورت موفقیت
        self.error_counts[server.id] = 0
        
        # اگر تغییر وضعیت داشتیم، به کاربر اطلاع بدهیم
        if old_status != new_status:
            await send_notification(
                user_id=server.user_id,
                notification_type=NotificationType.SERVER_STATUS_CHANGE,
                data={
                    'server_name': str(server.name),
                    'old_status': old_status,
                    'new_status': new_status
                }
            )
            
            # حذف کش‌های مرتبط با سرور
            await cache_manager.invalidate_pattern(f"server:{server.id}")
        
        await self.db.commit()

    async def _handle_sync_error(self, server: Server, error: Exception) -> None:
        """Handle synchronization errors"""
        self.error_counts[server.id] = self.error_counts.get(server.id, 0) + 1
        
        if self.error_counts[server.id] >= self.max_retry_attempts:
            # Mark server as potentially problematic
            server.status = 'error'
            server.last_sync = datetime.utcnow()
            await self.db.commit()
            
            # Notify user about persistent sync issues
            await send_notification(
                user_id=server.user_id,
                notification_type=NotificationType.SERVER_SYNC_ERROR,
                data={
                    'server_name': str(server.name),
                    'error': str(error)
                }
            )
            
            # Reset error count
            self.error_counts[server.id] = 0

    async def sync_server(self, server_id: int, force: bool = False) -> Dict[str, Any]:
        """همگام‌سازی وضعیت سرور با Hetzner"""
        # بررسی محدودیت نرخ درخواست
        if not await rate_limiter.is_allowed(
            f"server_sync:{server_id}",
            limit=RateLimits.SERVER_SYNC
        ):
            logger.warning(f"محدودیت نرخ درخواست برای همگام‌سازی سرور {server_id}")
            return {
                "id": server_id,
                "synced": False,
                "error": "محدودیت نرخ درخواست"
            }

        async def fetch_server_info():
            server = await self._get_server_from_db(server_id)
            if not server:
                raise HTTPException(status_code=404, detail="سرور یافت نشد")
            return await hetzner.get_server_info(str(server.hetzner_id))

        try:
            # دریافت اطلاعات سرور با استفاده از کش
            server_info = await cache_manager.get_or_set(
                key=f"server_info:{server_id}",
                fetch_func=fetch_server_info,
                ttl=self.sync_interval.total_seconds(),
                force_refresh=force
            )
            
            # به‌روزرسانی در دیتابیس
            server = await self._get_server_from_db(server_id)
            await self._update_server_status(server, server_info)
            
            # به‌روزرسانی زمان آخرین همگام‌سازی
            self.last_sync[server_id] = datetime.utcnow()

            return {
                "id": server_id,
                "status": server_info['status'],
                "ip": str(server.ip),
                "synced": True
            }

        except Exception as e:
            logger.error(f"خطا در همگام‌سازی سرور {server_id}: {str(e)}")
            await self._handle_sync_error(server, e)
            return {
                "id": server_id,
                "status": str(server.status),
                "ip": str(server.ip),
                "synced": False,
                "error": str(e)
            }

    async def sync_all_servers(self) -> List[Dict[str, Any]]:
        """Synchronize all servers status with Hetzner"""
        result = await self.db.execute(select(Server))
        servers = result.scalars().all()
        
        sync_tasks = []
        
        # Create tasks for parallel synchronization
        for server in servers:
            sync_tasks.append(self.sync_server(int(server.id), force=True))
        
        # Execute all sync tasks concurrently
        if sync_tasks:
            results = await asyncio.gather(*sync_tasks, return_exceptions=True)
            
            sync_results = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Error in batch sync: {str(result)}")
                    continue
                sync_results.append(result)
            
            return sync_results
        
        return []

    async def schedule_sync(self) -> None:
        """Schedule periodic synchronization"""
        while True:
            try:
                await self.sync_all_servers()
            except Exception as e:
                logger.error(f"Error in sync schedule: {str(e)}")
            finally:
                await asyncio.sleep(self.sync_interval.total_seconds())

    async def get_server_metrics(self, server_id: int) -> Dict[str, Any]:
        """دریافت متریک‌های سرور با کش"""
        # بررسی محدودیت نرخ درخواست
        if not await rate_limiter.is_allowed(
            f"server_metrics:{server_id}",
            limit=RateLimits.SERVER_METRICS
        ):
            logger.warning(f"محدودیت نرخ درخواست برای متریک‌های سرور {server_id}")
            raise HTTPException(
                status_code=429,
                detail="محدودیت نرخ درخواست برای جمع‌آوری متریک‌ها"
            )

        async def fetch_metrics():
            server = await self._get_server_from_db(server_id)
            if not server:
                raise HTTPException(status_code=404, detail="سرور یافت نشد")
            return await hetzner.get_server_metrics(str(server.hetzner_id))

        # استفاده از مدیر کش برای دریافت یا به‌روزرسانی متریک‌ها
        metrics = await cache_manager.get_or_set(
            key=f"server_metrics:{server_id}",
            fetch_func=fetch_metrics,
            ttl=self.metrics_ttl
        )

        # بررسی آستانه‌ها و ارسال اعلان‌ها
        await self._check_metrics_thresholds(server_id, metrics)
        
        return metrics

    async def _check_metrics_thresholds(self, server_id: int, metrics: Dict[str, Any]) -> None:
        """Check metrics against thresholds and send notifications"""
        thresholds = {
            'cpu': 90,  # 90% CPU usage
            'memory': 85,  # 85% memory usage
            'disk': 80,  # 80% disk usage
        }

        notifications = []

        # Check CPU usage
        if metrics['cpu'] > thresholds['cpu']:
            notifications.append({
                'type': NotificationType.HIGH_CPU_USAGE,
                'data': {
                    'server_name': str(server_id),
                    'usage': metrics['cpu']
                }
            })

        # Check memory usage
        if metrics['memory'] > thresholds['memory']:
            notifications.append({
                'type': NotificationType.HIGH_MEMORY_USAGE,
                'data': {
                    'server_name': str(server_id),
                    'usage': metrics['memory']
                }
            })

        # Check disk usage
        if metrics['disk'] > thresholds['disk']:
            notifications.append({
                'type': NotificationType.HIGH_DISK_USAGE,
                'data': {
                    'server_name': str(server_id),
                    'usage': metrics['disk']
                }
            })

        # Send notifications
        for notification in notifications:
            await send_notification(
                user_id=server_id,
                notification_type=notification['type'],
                data=notification['data']
            )

    async def monitor_servers(self) -> None:
        """Monitor all servers and collect metrics"""
        while True:
            try:
                result = await self.db.execute(
                    select(Server).where(Server.status == 'running')
                )
                active_servers = result.scalars().all()

                for server in active_servers:
                    # Check rate limit for monitoring
                    if await rate_limiter.is_allowed(
                        f"server_monitor:{server.id}",
                        limit=RateLimits.SERVER_METRICS
                    ):
                        try:
                            await self.get_server_metrics(int(server.id))
                        except Exception as e:
                            logger.error(f"Error monitoring server {server.id}: {str(e)}")
                    else:
                        logger.warning(f"Skipping monitoring for server {server.id} due to rate limit")

            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")

            finally:
                await asyncio.sleep(300)  # Monitor every 5 minutes