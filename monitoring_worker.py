from database.models import Server, ServerStats
from utils.server_monitor import ServerMonitor
from datetime import datetime, timedelta
from database.database import get_db
from sqlalchemy import select
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def monitor_servers():
    """مانیتورینگ مداوم سرورها"""
    while True:
        try:
            async with get_db() as db:
                monitor = ServerMonitor(db)
                
                # دریافت همه سرورهای فعال
                result = await db.execute(
                    select(Server).where(Server.status == 'running')
                )
                active_servers = result.scalars().all()

                for server in active_servers:
                    try:
                        # جمع‌آوری متریک‌ها
                        metrics = await monitor.collect_metrics(server.id)
                        if not metrics:
                            continue
                            
                        # تحلیل متریک‌ها و شناسایی مشکلات
                        issues = await monitor.analyze_metrics(server.id, metrics)
                        
                        # ارسال اعلان برای مشکلات
                        await monitor.notify_issues(server.id, issues)
                        
                        # تهیه خلاصه عملکرد روزانه (یکبار در روز)
                        if datetime.utcnow().hour == 0:  # در ابتدای هر روز
                            summary = await monitor.get_performance_summary(
                                server.id,
                                period=timedelta(days=1)
                            )
                            logger.info(f"خلاصه عملکرد روزانه سرور {server.id}: {summary}")

                    except Exception as e:
                        logger.error(f"خطا در مانیتورینگ سرور {server.id}: {str(e)}")

        except Exception as e:
            logger.error(f"خطا در چرخه مانیتورینگ: {str(e)}")

        finally:
            # انتظار 5 دقیقه تا چرخه بعدی
            await asyncio.sleep(300)


async def cleanup_old_metrics():
    """پاک کردن متریک‌های قدیمی"""
    while True:
        try:
            async with get_db() as db:
                # حذف متریک‌های قدیمی‌تر از 30 روز
                thirty_days_ago = datetime.utcnow() - timedelta(days=30)
                await db.execute(
                    select(ServerStats)
                    .where(ServerStats.timestamp < thirty_days_ago)
                ).delete()
                await db.commit()
                
        except Exception as e:
            logger.error(f"خطا در پاک‌سازی متریک‌های قدیمی: {str(e)}")
            
        finally:
            # اجرای پاک‌سازی هر 24 ساعت
            await asyncio.sleep(24 * 60 * 60)


async def main():
    """تابع اصلی برای اجرای همه وظایف مانیتورینگ"""
    logger.info("شروع سرویس مانیتورینگ...")
    
    # اجرای همزمان مانیتورینگ و پاک‌سازی
    await asyncio.gather(
        monitor_servers(),
        cleanup_old_metrics()
    )

if __name__ == "__main__":
    asyncio.run(main())
