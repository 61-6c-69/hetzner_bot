from datetime import datetime
from repositories.server_repository import ServerRepository
from repositories.transaction_repository import TransactionRepository
from database.database import async_session_maker


async def charge_servers():
    """شارژ سرورهای در حال اجرا"""
    async with async_session_maker() as db:
        server_repo = ServerRepository(db)
        transaction_repo = TransactionRepository(db)
        
        # دریافت سرورهای فعال
        servers = await server_repo.get_running_servers()
        
        for server in servers:
            # محاسبه زمان گذشته از آخرین شارژ
            time_diff = datetime.now() - server.last_charge_at
            hours = time_diff.total_seconds() / 3600
            
            if hours >= 1:
                charge_amount = server.hourly_price * int(hours)
                
                # ایجاد تراکنش
                await transaction_repo.create_charge_transaction(
                    user_id=server.user_id,
                    amount=-charge_amount,
                    description=f"Server charge: {server.name}"
                )
                
                # آپدیت زمان آخرین شارژ
                await server_repo.update_last_charge(server.id, datetime.now())
