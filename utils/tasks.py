from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSessionLocal
from api.models.server import Server
from api.models.transaction import Transaction

async def charge_servers():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Server).where(Server.status == 'running')
        )
        servers = result.scalars().all()
        
        for server in servers:
            # محاسبه زمان گذشته از آخرین شارژ
            time_diff = datetime.now() - server.last_charge_at
            hours = time_diff.total_seconds() / 3600
            
            if hours >= 1:
                charge_amount = server.hourly_price * int(hours)
                # ایجاد تراکنش
                transaction = Transaction(
                    user_id=server.user_id,
                    amount=-charge_amount,
                    description=f"Server charge: {server.name}",
                    status='completed'
                )
                db.add(transaction)
                
                # آپدیت زمان آخرین شارژ
                server.last_charge_at = datetime.now()
                
        await db.commit() 