from datetime import datetime
from repositories.server_repository import ServerRepository
from repositories.transaction_repository import TransactionRepository
from repositories.user_repository import UserRepository
from utils.notifications import send_notification, NotificationType
from utils.hetzner_api import hetzner
from database.database import AsyncSessionLocal
from sqlalchemy import select
from database.models import User


async def calculate_hourly_cost(servers) -> float:
    """محاسبه هزینه ساعتی همه سرورها"""
    return sum(server.hourly_price for server in servers)


async def check_and_handle_low_balance():
    """بررسی موجودی کاربران و خاموش کردن سرورها در صورت کمبود موجودی"""
    async with AsyncSessionLocal() as db:
        user_repo = UserRepository(db)
        server_repo = ServerRepository(db)

        # دریافت همه کاربران
        users = await user_repo.get_all_users()
        
        for user in users:
            # دریافت سرورهای فعال کاربر
            active_servers = await server_repo.get_user_active_servers(user.id)
            if not active_servers:
                continue

            # محاسبه هزینه ساعت آینده
            hourly_cost = await calculate_hourly_cost(active_servers)
            
            # اگر موجودی کمتر از هزینه ساعت آینده بود
            if user.balance < hourly_cost:
                # خاموش کردن سرورها
                for server in active_servers:
                    try:
                        # خاموش کردن سرور در هتزنر
                        await hetzner.power_off(server.hetzner_id)
                        # به‌روزرسانی وضعیت در دیتابیس
                        await server_repo.update_status(
                            server.id,
                            'stopped',
                            'Stopped due to insufficient balance'
                        )
                    except Exception as e:
                        print(f"Error stopping server {server.id}: {e}")

                # ارسال اعلان به کاربر
                await send_notification(
                    user.id,
                    NotificationType.LOW_BALANCE_SHUTDOWN,
                    hourly_cost=hourly_cost,
                    current_balance=user.balance,
                    servers_count=len(active_servers)
                )


async def charge_servers():
    """شارژ سرورهای در حال اجرا"""
    async with AsyncSessionLocal() as db:
        server_repo = ServerRepository(db)
        transaction_repo = TransactionRepository(db)
        user_repo = UserRepository(db)
        
        # دریافت سرورهای فعال
        servers = await server_repo.get_running_servers()
        
        # گروه‌بندی سرورها بر اساس کاربر
        user_servers = {}
        for server in servers:
            if server.user_id not in user_servers:
                user_servers[server.user_id] = []
            user_servers[server.user_id].append(server)

        # بررسی و شارژ برای هر کاربر
        for user_id, user_servers in user_servers.items():
            # محاسبه هزینه کل ساعتی
            hourly_cost = await calculate_hourly_cost(user_servers)
            
            # دریافت کاربر و بررسی موجودی
            user = await user_repo.get(user_id)
            if user.balance < hourly_cost:
                # اگر موجودی کافی نبود، سرورها را خاموش می‌کنیم
                for server in user_servers:
                    await hetzner.power_off(server.hetzner_id)
                    await server_repo.update_status(
                        server.id,
                        'stopped',
                        'Stopped due to insufficient balance'
                    )
                
                # ارسال اعلان
                await send_notification(
                    user_id,
                    NotificationType.LOW_BALANCE_SHUTDOWN,
                    hourly_cost=hourly_cost,
                    current_balance=user.balance,
                    servers_count=len(user_servers)
                )
                continue

            # شارژ سرورها
            for server in user_servers:
                # محاسبه زمان گذشته از آخرین شارژ
                time_diff = datetime.now() - server.last_charge_at
                hours = time_diff.total_seconds() / 3600
                
                if hours >= 1:
                    charge_amount = server.hourly_price * int(hours)
                    
                    # ایجاد تراکنش
                    await transaction_repo.create_server_charge(
                        user_id=server.user_id,
                        amount=charge_amount,
                        server_id=server.id
                    )
                    
                    # آپدیت زمان آخرین شارژ
                    await server_repo.update_last_charge(server.id, datetime.now())
