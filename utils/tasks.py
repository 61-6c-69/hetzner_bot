from datetime import datetime
from sqlalchemy import select
from database.database import get_db
from api.schemas import Server, Transaction


async def charge_servers():
    async with get_db() as db:
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
