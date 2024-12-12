import asyncio
import logging
from datetime import datetime, timedelta
from tortoise import Tortoise
from database.models import Server, ServerStats
from utils.hetzner_api import hetzner
from config import DATABASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init():
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={'models': ['database.models']}
    )


async def collect_server_stats():
    """جمع‌آوری آمار از سرورها"""
    while True:
        try:
            # دریافت همه سرورهای فعال
            servers = await Server.filter(status='running')

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
                    if stats['cpu'] > 90:
                        await notify_high_usage(server, 'CPU', stats['cpu'])
                    if stats['memory'] > 90:
                        await notify_high_usage(server, 'Memory', stats['memory'])
                    if stats['disk'] > 90:
                        await notify_high_usage(server, 'Disk', stats['disk'])

                except Exception as e:
                    logger.error(f"Error collecting stats for server {server.id}: {e}")

            # پاک کردن آمار قدیمی (بیشتر از 30 روز)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            await ServerStats.filter(timestamp__lt=thirty_days_ago).delete()

        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")

        await asyncio.sleep(30)  # هر 30 ثانیه


async def notify_high_usage(server, resource, value):
    """ارسال نوتیفیکیشن برای مصرف بالا"""
    from bot import notify_admins

    user = await server.user
    message = (
        f"⚠️ <b>هشدار مصرف بالا</b>\n\n"
        f"🖥 سرور: {server.name}\n"
        f"📊 {resource}: {value}%\n"
        f"👤 کاربر: {user.first_name}"
    )

    await notify_admins(message)

    # اگر کاربر تلگرام داشت به او هم اطلاع بده
    if user.telegram_id:
        from bot import bot
        try:
            await bot.send_message(
                user.telegram_id,
                message,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Failed to notify user {user.id}: {e}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())
    loop.run_until_complete(collect_server_stats())
