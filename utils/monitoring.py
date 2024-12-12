import asyncio
import logging
from datetime import datetime, timedelta
from database.models import Server, ServerStats, User
from utils.hetzner_api import hetzner
from utils.notifications import send_notification, NotificationType
from config import LOW_BALANCE_THRESHOLD

logger = logging.getLogger(__name__)

async def check_servers_status():
    """بررسی وضعیت سرورها"""
    while True:
        try:
            # دریافت همه سرورهای فعال
            servers = await Server.filter(status='running').prefetch_related('user')
            
            for server in servers:
                try:
                    # دریافت آمار از Hetzner API
                    stats = await hetzner.get_server_metrics(server.hetzner_id)
                    
                    # ذخیره در دیتابیس
                    await ServerStats.create(
                        server=server,
                        cpu_usage=stats['cpu'],
                        memory_usage=stats['memory'],
                        disk_usage=stats['disk'],
                        network_in=stats['network_in'],
                        network_out=stats['network_out']
                    )
                    
                    # بررسی هشدارها
                    await check_resource_usage(server, stats)
                    await check_user_balance(server.user)
                    
                except Exception as e:
                    logger.error(f"Error checking server {server.id}: {e}")
            
            # پاک کردن آمار قدیمی (بیشتر از 30 روز)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            await ServerStats.filter(timestamp__lt=thirty_days_ago).delete()
            
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
        
        await asyncio.sleep(300)  # هر 5 دقیقه

async def check_resource_usage(server: Server, stats: dict):
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

async def check_user_balance(user: User):
    """بررسی موجودی کاربر"""
    if user.balance < LOW_BALANCE_THRESHOLD:
        await send_notification(
            user,
            NotificationType.LOW_BALANCE,
            amount=LOW_BALANCE_THRESHOLD
        )