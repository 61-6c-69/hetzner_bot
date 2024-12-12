from repositories.transaction_repository import TransactionRepository
from repositories.server_repository import ServerRepository
from repositories.user_repository import UserRepository
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from utils.auth import get_current_user
from utils.hetzner_api import hetzner
from database.database import get_db
from api import schemas
from typing import List

router = APIRouter()


@router.get("/", response_model=List[schemas.Server])
async def list_servers(
        current_user: schemas.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """دریافت لیست سرورهای کاربر"""
    repo = ServerRepository(db)
    return await repo.get_user_servers(current_user.id)


@router.post("/", response_model=schemas.Server)
async def create_server(
        server: schemas.ServerCreate,
        current_user: schemas.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """ایجاد سرور جدید"""
    server_repo = ServerRepository(db)
    user_repo = UserRepository(db)
    transaction_repo = TransactionRepository(db)

    # Calculate price
    price = await hetzner.calculate_price(server.type)

    # Check balance
    balance = await user_repo.get_balance(current_user.id)
    if balance < price:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # Create server in Hetzner
    server_data = await hetzner.create_server(
        type=server.type,
        location=server.location,
        os=server.os
    )

    # Create transaction
    await transaction_repo.create(
        user_id=current_user.id,
        amount=-price,
        description=f"خرید سرور {server.type}",
        status="completed"
    )

    # Create server in database
    return await server_repo.create(
        user_id=current_user.id,
        hetzner_id=server_data['id'],
        name=server.name,
        type=server.type,
        location=server.location,
        os=server.os,
        ip=server_data['public_net']['ipv4']['ip'],
        status=server_data['status']
    )


@router.get("/{server_id}", response_model=schemas.Server)
async def get_server(
        server_id: int,
        current_user: schemas.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """دریافت اطلاعات یک سرور"""
    repo = ServerRepository(db)
    server = await repo.get_server(server_id)
    
    if not server or server.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Server not found")
        
    return server


@router.post("/{server_id}/action")
async def server_action(
        server_id: int,
        action: schemas.ServerAction,
        current_user: schemas.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """اجرای عملیات روی سرور (روشن/خاموش/ریستارت)"""
    repo = ServerRepository(db)
    server = await repo.get_server(server_id)
    
    if not server or server.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Server not found")
        
    success = await repo.perform_action(server_id, action.action)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to perform action")
        
    return {"message": f"Server {action.action} successful"}


@router.post("/{server_id}/ip")
async def change_server_ip(
        server_id: int,
        current_user: schemas.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """تغییر IP سرور"""
    repo = ServerRepository(db)
    server = await repo.get_server(server_id)
    
    if not server or server.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Server not found")
        
    success = await repo.change_ip(server_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to change IP")
        
    return {"message": "IP changed successfully"}


@router.get("/{server_id}/stats")
async def get_server_stats(
        server_id: int,
        current_user: schemas.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """دریافت آمار و مانیتورینگ سرور"""
    repo = ServerRepository(db)
    server = await repo.get_server(server_id)
    
    if not server or server.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Server not found")
        
    stats = await repo.get_server_stats(server_id)
    if not stats:
        raise HTTPException(status_code=400, detail="Failed to get server stats")
        
    return stats


@router.delete("/{server_id}")
async def delete_server(
        server_id: int,
        current_user: schemas.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """حذف سرور"""
    repo = ServerRepository(db)
    server = await repo.get_server(server_id)
    
    if not server or server.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Server not found")
        
    success = await repo.delete(server_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete server")
        
    return {"message": "Server deleted successfully"}
