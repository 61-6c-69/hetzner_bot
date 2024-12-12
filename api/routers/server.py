from database.models import User, Server, Transaction, ServerStats, ServerLog, IPChange
from fastapi import APIRouter, Depends, HTTPException
from utils.auth import get_current_user
from datetime import datetime, timedelta
from utils.hetzner_api import hetzner
from api.models import ServerResponse
from typing import List


router = APIRouter()


@router.get("/", response_model=List[ServerResponse])
async def list_servers(user: User = Depends(get_current_user)):
    """دریافت لیست سرورهای کاربر"""
    servers = await Server.filter(user=user)
    return servers


@router.post("/")
async def create_server(
        server_type: str,
        location: str,
        os: str,
        user: User = Depends(get_current_user)
):
    """ایجاد سرور جدید"""
    # محاسبه قیمت سرور
    price = await hetzner.calculate_price(server_type)

    # بررسی موجودی کاربر
    balance = await user.get_balance()
    if balance < price:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # ایجاد سرور در هتزنر
    server_data = await hetzner.create_server(
        type=server_type,
        location=location,
        os=os
    )

    # ثبت تراکنش
    await Transaction.create(
        user=user,
        amount=-price,
        description=f"خرید سرور {server_type}",
        status="completed"
    )

    # ذخیره سرور در دیتابیس
    server = await Server.create(
        user=user,
        hetzner_id=server_data['id'],
        name=server_data['name'],
        ip=server_data['ip'],
        status=server_data['status'],
        os=os
    )

    return server


@router.get("/{server_id}", response_model=ServerResponse)
async def get_server(server_id: int, user: User = Depends(get_current_user)):
    """دریافت جزئیات سرور"""
    server = await Server.get_or_none(id=server_id, user=user)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server


@router.post("/{server_id}/power")
async def power_action(
        server_id: int,
        action: str,  # 'on' or 'off'
        user: User = Depends(get_current_user)
):
    """روشن/خاموش کردن سرور"""
    server = await Server.get_or_none(id=server_id, user=user)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    if action == "off":
        result = await hetzner.power_off(server.hetzner_id)
    else:
        result = await hetzner.power_on(server.hetzner_id)

    if result.get('action', {}).get('status') == 'success':
        server.status = 'off' if action == 'off' else 'running'
        await server.save()
        return {"status": "success"}

    raise HTTPException(status_code=400, detail="Failed to change power state")


@router.post("/{server_id}/ip")
async def change_ip(server_id: int, user: User = Depends(get_current_user)):
    """تغییر IP سرور"""
    server = await Server.get_or_none(id=server_id, user=user)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    # بررسی تعداد دفعات تغییر IP
    ip_changes = await IPChange.filter(server=server).count()

    # محاسبه هزینه
    if ip_changes > 0:
        price_eur = await hetzner.get_ip_change_price()
        price = price_eur * 50000  # تبدیل به تومان

        # بررسی موجودی
        balance = await user.get_balance()
        if balance < price:
            raise HTTPException(status_code=400, detail="Insufficient balance")

        # ثبت تراکنش
        await Transaction.create(
            user=user,
            amount=-price,
            description=f"تغییر IP سرور {server.name}",
            status="completed"
        )

    # اعمال تغییر IP
    result = await hetzner.change_ip(server.hetzner_id)
    if result.get('action', {}).get('status') == 'success':
        # ذخیره IP قدیمی
        await IPChange.create(
            server=server,
            old_ip=server.ip,
            price=price if ip_changes > 0 else 0
        )

        # بروزرسانی IP جدید
        server.ip = result['ip']
        await server.save()

        return {"status": "success", "new_ip": server.ip}

    raise HTTPException(status_code=400, detail="Failed to change IP")


@router.get("/{server_id}/stats")
async def get_server_stats(
        server_id: int,
        range: str,
        user: User = Depends(get_current_user)
):
    """دریافت آمار سرور"""
    server = await Server.get_or_none(id=server_id, user=user)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    # تبدیل range به timestamp
    now = datetime.utcnow()
    if range == '1h':
        start_time = now - timedelta(hours=1)
    elif range == '24h':
        start_time = now - timedelta(days=1)
    elif range == '7d':
        start_time = now - timedelta(days=7)
    else:  # 30d
        start_time = now - timedelta(days=30)

    # دریافت آمار از دیتابیس
    stats = await ServerStats.filter(
        server=server,
        timestamp__gte=start_time
    ).order_by('timestamp')

    # تبدیل به فرمت مناسب برای نمودار
    return {
        'cpu': format_chart_data([s.cpu_usage for s in stats], [s.timestamp for s in stats]),
        'memory': format_chart_data([s.memory_usage for s in stats], [s.timestamp for s in stats]),
        'disk': format_chart_data([s.disk_usage for s in stats], [s.timestamp for s in stats]),
        'network': format_chart_data(
            [s.network_in + s.network_out for s in stats],
            [s.timestamp for s in stats]
        )
    }


@router.get("/{server_id}/logs")
async def get_server_logs(
        server_id: int,
        user: User = Depends(get_current_user)
):
    """دریافت لاگ‌های سرور"""
    server = await Server.get_or_none(id=server_id, user=user)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    logs = await ServerLog.filter(server=server).order_by('-timestamp').limit(100)
    return logs


def format_chart_data(values, timestamps):
    """تبدیل داده‌ها به فرمت مناسب برای Chart.js"""
    return {
        'labels': [t.strftime('%H:%M') for t in timestamps],
        'datasets': [{
            'data': values,
            'borderColor': '#3b82f6',
            'tension': 0.1
        }]
    }
