import asyncio
from datetime import datetime
from database.models import Server, User, Transaction
from main import logger
from utils.sms import sms_service


async def charge_hourly_costs():
    """کسر هزینه‌های ساعتی سرورها"""
    while True:
        try:
            now = datetime.utcnow()

            # دریافت سرورهای فعال
            active_servers = await Server.filter(
                status='running'
            ).prefetch_related('user')

            for server in active_servers:
                # محاسبه ساعت‌های گذشته از آخرین شارژ
                hours_passed = (now - server.last_charge_at).total_seconds() / 3600
                if hours_passed >= 1:  # اگر حداقل یک ساعت گذشته
                    # محاسبه هزینه
                    cost = float(server.hourly_price) * int(hours_passed)
                    user = await server.user

                    if user.balance >= cost:
                        # کسر از موجودی
                        user.balance -= cost
                        await user.save()

                        # ثبت تراکنش
                        await Transaction.create(
                            user=user,
                            amount=-cost,
                            description=f"هزینه {int(hours_passed)} ساعت استفاده از سرور {server.name}"
                        )

                        # آپدیت زمان آخرین شارژ
                        server.last_charge_at = now
                        await server.save()

                    else:
                        # اگر موجودی کافی نبود
                        await notify_insufficient_balance(server, cost)

                        # خاموش کردن سرور
                        server.status = 'stopped'
                        await server.save()
                        # TODO: خاموش کردن در هتزنر

        except Exception as e:
            logger.error(f"Error in billing: {e}")

        await asyncio.sleep(60)  # بررسی هر دقیقه


async def notify_insufficient_balance(server: Server, required_amount: float):
    """اطلاع‌رسانی کمبود موجودی"""
    user = await server.user
    message = (
        f"⚠️ موجودی ناکافی\n\n"
        f"سرور: {server.name}\n"
        f"هزینه ساعتی: {server.hourly_price:,} تومان\n"
        f"موجودی مورد نیاز: {required_amount:,} تومان\n"
        f"موجودی فعلی: {user.balance:,} تومان\n\n"
        "سرور شما به دلیل کمبود موجودی خاموش شد. "
        "لطفاً نسبت به شارژ حساب خود اقدام کنید."
    )

    # ارسال پیامک
    await sms_service.send_sms(user.phone, message)

    # ارسال پیام در تلگرام
    if user.telegram_id:
        try:
            await notify_user(user.telegram_id, message)
        except Exception as e:
            logger.error(f"Failed to notify user {user.id} on Telegram: {e}")


async def check_future_balance():
    """بررسی موجودی برای روزهای آینده"""
    while True:
        try:
            now = datetime.utcnow()

            # دریافت همه سرورهای فعال
            active_servers = await Server.filter(
                status='running'
            ).prefetch_related('user')

            # گروه‌بندی سرورها بر اساس کاربر
            user_servers = {}
            for server in active_servers:
                if server.user_id not in user_servers:
                    user_servers[server.user_id] = []
                user_servers[server.user_id].append(server)

            for user_id, servers in user_servers.items():
                user = await User.get(id=user_id)
                current_balance = await user.get_balance()

                # محاسبه هزینه روزانه همه سرورها
                daily_cost = sum(float(server.hourly_price) * 24 for server in servers)

                # محاسبه موجودی برای 5 روز آینده
                five_days_cost = daily_cost * 5
                if current_balance < five_days_cost and current_balance >= (daily_cost * 2):
                    await notify_low_balance_warning(user, servers, 5, current_balance, five_days_cost)

                # محاسبه موجودی برای 2 روز آینده
                two_days_cost = daily_cost * 2
                if current_balance < two_days_cost:
                    await notify_low_balance_warning(user, servers, 2, current_balance, two_days_cost)

        except Exception as e:
            logger.error(f"Error checking future balance: {e}")

        await asyncio.sleep(3600)  # بررسی هر ساعت


async def notify_low_balance_warning(user: User, servers: list, days: int, current_balance: float,
                                     required_amount: float):
    """ارسال هشدار موجودی کم برای روزهای آینده"""

    servers_text = "\n".join([
        f"🔹 {server.name}: {float(server.hourly_price) * 24:,} تومان در روز"
        for server in servers
    ])

    message = (
        f"⚠️ هشدار موجودی کم\n\n"
        f"موجودی فعلی شما کفاف {days} روز آینده را نمی‌دهد.\n\n"
        f"💰 موجودی فعلی: {current_balance:,} تومان\n"
        f"💰 موجودی مورد نیاز: {required_amount:,} تومان\n\n"
        f"📊 هزینه روزانه سرورهای شما:\n"
        f"{servers_text}\n\n"
        f"⚠️ در صورت عدم شارژ حساب، سرورهای شما پس از اتمام موجودی خاموش خواهند شد."
    )

    # ارسال پیامک
    try:
        await sms_service.send_sms(user.phone, message)
    except Exception as e:
        logger.error(f"Failed to send SMS to user {user.id}: {e}")

    # ارسال پیام در تلگرام
    if user.telegram_id:
        try:
            await notify_user(user.telegram_id, message)
        except Exception as e:
            logger.error(f"Failed to notify user {user.id} on Telegram: {e}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(charge_hourly_costs())
    loop.create_task(check_future_balance())
    loop.run_forever()
