import asyncio
import logging
from utils.tasks import charge_servers, check_and_handle_low_balance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_billing_tasks():
    """اجرای وظایف مربوط به صورتحساب"""
    while True:
        try:
            # شارژ سرورها
            await charge_servers()
            logger.info("Servers charged successfully")

            # بررسی موجودی کاربران
            await check_and_handle_low_balance()
            logger.info("Low balance check completed")

        except Exception as e:
            logger.error(f"Error in billing tasks: {e}")

        # انتظار 5 دقیقه تا اجرای بعدی
        await asyncio.sleep(300)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_billing_tasks())
