from utils.notifications import send_notification, NotificationType
from repositories.server_repository import ServerRepository
from repositories.stats_repository import StatsRepository
from datetime import datetime, timedelta
from repositories import UserRepository
from utils.hetzner_api import hetzner
from database.database import get_db
import asyncio
import logging

from utils.redis import Redis

logger = logging.getLogger(__name__)


async def check_servers_status():
    """بررسی وضعیت سرورها"""
    while True:
        try:

            async for db in get_db():
                server_repo = ServerRepository(db)
                stats_repo = StatsRepository(db)
                
                # دریافت همه سرورهای فعال
                servers = await server_repo.get_all_running_servers()

                for server in servers:
                    try:
                        # دریافت آمار از Hetzner API
                        stats = await hetzner.get_server_metrics(server.hetzner_id)

                        # ذخیره در دیتابیس
                        await stats_repo.create_stats(
                            server_id=server.id,
                            cpu_usage=stats['cpu'],
                            memory_usage=stats['memory'],
                            disk_usage=stats['disk'],
                            network_in=stats['network_in'],
                            network_out=stats['network_out']
                        )

                        # بررسی هشدارها
                        await check_resource_usage(server, stats)
                        await check_user_balance(
                            server.user,
                            server_repo,
                            UserRepository(db)
                        )

                    except Exception as e:
                        logger.error(f"Error checking server {server.id}: {e}")

                # پاک کردن آمار قدیمی (بیشتر از 30 روز)
                thirty_days_ago = datetime.utcnow() - timedelta(days=30)
                await stats_repo.delete_old_stats(thirty_days_ago)

        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")

        await asyncio.sleep(300)  # هر 5 دقیقه


async def check_resource_usage(server, stats: dict):
    """بررسی مصرف منابع"""
    thresholds = {
        'cpu': 90,
        'memory': 90,
        'disk': 90
    }

    for resource, current in {
        'cpu': stats['cpu'],
        'memory': stats['memory'],
        'disk': stats['disk']
    }.items():
        if current > thresholds[resource]:
            await send_notification(
                server.user,
                NotificationType.SERVER_WARNING,
                server_name=server.name,
                resource=resource,
                usage=current
            )


async def check_user_balance(user, server_repo: ServerRepository, user_repo: UserRepository):
    """بررسی موجودی کاربر"""
    redis = Redis()
    result = await redis.get(f"monitoring_{user.id}_balance")
    if result:
        servers = await server_repo.get_user_servers(user.id)
        price = sum(server.hourly_price for server in servers) * 24
        balance = await user_repo.get_balance(user.id)
        if balance < price:
            await send_notification(
                user,
                NotificationType.LOW_BALANCE,
                amount=balance
            )
