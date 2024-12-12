from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database.database import get_db
from database import crud
from api import schemas
from utils.auth import get_current_user
from utils.hetzner_api import hetzner
from sqlalchemy import select

router = APIRouter()

@router.get("/", response_model=List[schemas.Server])
async def list_servers(
    current_user: schemas.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت لیست سرورها"""
    result = await db.execute(
        select(Server).where(Server.user_id == current_user.id)
    )
    return result.scalars().all()

@router.post("/", response_model=schemas.Server)
async def create_server(
    data: schemas.ServerCreate,
    current_user: schemas.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """ایجاد سرور جدید"""
    # دریافت قیمت ساعتی سرور از هتزنر
    server_type = await hetzner.get_server_type(data.type)
    hourly_price = server_type['prices']['hourly']
    
    # ایجاد سرور در هتزنر
    try:
        hetzner_server = await hetzner.create_server(
            type=data.type,
            location=data.location,
            os=data.os
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # ذخیره اطلاعات سرور
    server_data = schemas.ServerCreate(
        name=data.name,
        type=data.type,
        location=data.location,
        os=data.os,
        hetzner_id=hetzner_server['id'],
        hourly_price=hourly_price,
        monthly_price=hourly_price * 24 * 30,
        ip=hetzner_server['public_net']['ipv4']['ip'],
        status='running',
        specs=hetzner_server['server_type']
    )
    
    server = await crud.create_server(db, server_data, current_user.id)
    return server


@router.get("/{server_id}", response_model=schemas.Server)
async def get_server(
    server_id: int,
    current_user: schemas.User = Depends(get_current_user)
):
    """دریافت اطلاعات یک سرور"""
    server = await Server.get_or_none(id=server_id, user=current_user)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server


@router.post("/{server_id}/power")
async def power_action(
    server_id: int,
    action: str,  # 'on' or 'off'
    current_user: schemas.User = Depends(get_current_user)
):
    """روشن/خاموش کردن سرور"""
    server = await Server.get_or_none(id=server_id, user=current_user)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    try:
        if action == 'on':
            await hetzner.power_on(server.hetzner_id)
            server.status = 'running'
        elif action == 'off':
            await hetzner.power_off(server.hetzner_id)
            server.status = 'stopped'
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        await server.save()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{server_id}/ip")
async def change_ip(
    server_id: int,
    current_user: schemas.User = Depends(get_current_user)
):
    """تغییر IP سرور"""
    server = await Server.get_or_none(id=server_id, user=current_user)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # دریافت هزینه تغییر IP
    ip_change_price = await hetzner.get_ip_change_price()
    
    # بررسی موجودی کاربر
    user_balance = await current_user.get_balance()
    if user_balance < ip_change_price:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "موجودی ناکافی",
                "required": ip_change_price,
                "balance": user_balance
            }
        )
    
    try:
        result = await hetzner.change_ip(server.hetzner_id)
        server.ip = result['ip']
        await server.save()
        return {"status": "success", "new_ip": server.ip}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
