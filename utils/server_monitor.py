from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Server, ServerStats
from utils.hetzner_api import hetzner
from utils.notifications import send_notification, NotificationType
from utils.cache_manager import cache_manager
from utils.rate_limiter import rate_limiter, RateLimits
import logging

logger = logging.getLogger(__name__)

class ServerMonitor:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.metrics_ttl = 300  # 5 دقیقه برای کش متریک‌ها
        self.thresholds = {
            'cpu': 90,      # 90% CPU
            'memory': 85,   # 85% RAM
            'disk': 80,     # 80% دیسک
            'network': {    # محدودیت‌های شبکه
                'in': 1000 * 1024 * 1024,    # 1 GB/s ورودی
                'out': 1000 * 1024 * 1024    # 1 GB/s خروجی
            }
        }

    async def collect_metrics(self, server_id: int) -> Dict[str, Any]:
        """جمع‌آوری متریک‌های سرور"""
        # بررسی محدودیت نرخ درخواست
        if not await rate_limiter.is_allowed(
            f"server_metrics:{server_id}",
            limit=RateLimits.SERVER_METRICS
        ):
            logger.warning(f"محدودیت نرخ درخواست برای متریک‌های سرور {server_id}")
            return None

        async def fetch_metrics():
            result = await self.db.execute(
                select(Server).where(Server.id == server_id)
            )
            server = result.scalar_one_or_none()
            if not server:
                return None
            
            metrics = await hetzner.get_server_metrics(str(server.hetzner_id))
            
            # ذخیره متریک‌ها در دیتابیس
            await self._save_metrics(server_id, metrics)
            
            return metrics

        return await cache_manager.get_or_set(
            key=f"server_metrics:{server_id}",
            fetch_func=fetch_metrics,
            ttl=self.metrics_ttl
        )

    async def _save_metrics(self, server_id: int, metrics: Dict[str, Any]) -> None:
        """ذخیره متریک‌ها در دیتابیس"""
        stats = ServerStats(
            server_id=server_id,
            cpu_usage=metrics['cpu'],
            memory_usage=metrics['memory'],
            disk_usage=metrics['disk'],
            network_in=metrics['network']['in'],
            network_out=metrics['network']['out'],
            timestamp=datetime.utcnow()
        )
        self.db.add(stats)
        await self.db.commit()

    async def analyze_metrics(self, server_id: int, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """تحلیل متریک‌ها و تشخیص مشکلات"""
        issues = []

        # بررسی CPU
        if metrics['cpu'] > self.thresholds['cpu']:
            issues.append({
                'type': 'high_cpu',
                'severity': 'critical' if metrics['cpu'] > 95 else 'warning',
                'value': metrics['cpu'],
                'threshold': self.thresholds['cpu']
            })

        # بررسی حافظه
        if metrics['memory'] > self.thresholds['memory']:
            issues.append({
                'type': 'high_memory',
                'severity': 'critical' if metrics['memory'] > 95 else 'warning',
                'value': metrics['memory'],
                'threshold': self.thresholds['memory']
            })

        # بررسی دیسک
        if metrics['disk'] > self.thresholds['disk']:
            issues.append({
                'type': 'high_disk',
                'severity': 'critical' if metrics['disk'] > 95 else 'warning',
                'value': metrics['disk'],
                'threshold': self.thresholds['disk']
            })

        # بررسی شبکه
        if metrics['network']['in'] > self.thresholds['network']['in']:
            issues.append({
                'type': 'high_network_in',
                'severity': 'warning',
                'value': metrics['network']['in'],
                'threshold': self.thresholds['network']['in']
            })

        if metrics['network']['out'] > self.thresholds['network']['out']:
            issues.append({
                'type': 'high_network_out',
                'severity': 'warning',
                'value': metrics['network']['out'],
                'threshold': self.thresholds['network']['out']
            })

        return issues

    async def get_historical_metrics(
        self,
        server_id: int,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """دریافت تاریخچه متریک‌ها"""
        end_time = end_time or datetime.utcnow()
        
        result = await self.db.execute(
            select(ServerStats)
            .where(
                ServerStats.server_id == server_id,
                ServerStats.timestamp >= start_time,
                ServerStats.timestamp <= end_time
            )
            .order_by(ServerStats.timestamp.asc())
        )
        
        stats = result.scalars().all()
        return [
            {
                'timestamp': stat.timestamp,
                'cpu': stat.cpu_usage,
                'memory': stat.memory_usage,
                'disk': stat.disk_usage,
                'network_in': stat.network_in,
                'network_out': stat.network_out
            }
            for stat in stats
        ]

    async def get_performance_summary(
        self,
        server_id: int,
        period: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """دریافت خلاصه عملکرد سرور"""
        start_time = datetime.utcnow() - period
        metrics = await self.get_historical_metrics(server_id, start_time)
        
        if not metrics:
            return None
            
        return {
            'cpu_avg': sum(m['cpu'] for m in metrics) / len(metrics),
            'memory_avg': sum(m['memory'] for m in metrics) / len(metrics),
            'disk_avg': sum(m['disk'] for m in metrics) / len(metrics),
            'network_in_total': sum(m['network_in'] for m in metrics),
            'network_out_total': sum(m['network_out'] for m in metrics),
            'peak_cpu': max(m['cpu'] for m in metrics),
            'peak_memory': max(m['memory'] for m in metrics),
            'peak_disk': max(m['disk'] for m in metrics),
            'samples_count': len(metrics),
            'period_hours': period.total_seconds() / 3600
        }

    async def notify_issues(self, server_id: int, issues: List[Dict[str, Any]]) -> None:
        """ارسال اعلان برای مشکلات شناسایی شده"""
        if not issues:
            return

        result = await self.db.execute(
            select(Server).where(Server.id == server_id)
        )
        server = result.scalar_one_or_none()
        if not server:
            return

        for issue in issues:
            notification_type = {
                'high_cpu': NotificationType.HIGH_CPU_USAGE,
                'high_memory': NotificationType.HIGH_MEMORY_USAGE,
                'high_disk': NotificationType.HIGH_DISK_USAGE,
                'high_network_in': NotificationType.HIGH_NETWORK_USAGE,
                'high_network_out': NotificationType.HIGH_NETWORK_USAGE
            }.get(issue['type'])

            if notification_type:
                await send_notification(
                    user_id=server.user_id,
                    notification_type=notification_type,
                    data={
                        'server_name': server.name,
                        'value': issue['value'],
                        'threshold': issue['threshold'],
                        'severity': issue['severity']
                    }
                )

server_monitor = ServerMonitor(None)  # باید در زمان استفاده، نمونه با دیتابیس صحیح ایجاد شود 