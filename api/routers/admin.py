from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from repositories.ticket_repository import TicketRepository
from repositories.admin_repository import AdminRepository
from sqlalchemy.ext.asyncio import AsyncSession
from utils.notifications import notify_user
from utils.auth import get_current_admin
from database.database import get_db
from database.models import User
from pydantic import BaseModel
from api import schemas
from typing import List

router = APIRouter()


class NotificationCreate(BaseModel):
    message: str


@router.get("/tickets")
async def list_tickets(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """لیست همه تیکت‌ها"""
    repo = AdminRepository(db)
    return await repo.get_all_tickets()


@router.post("/tickets/{ticket_id}/reply")
async def reply_ticket(
    ticket_id: int,
    response: str,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """پاسخ به تیکت"""
    repo = TicketRepository(db)
    ticket = await repo.add_reply(ticket_id, response)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    admin_repo = AdminRepository(db)

    # اطلاع‌رسانی به کاربر
    user = await admin_repo.get_ticket_user(ticket_id)
    if user and user.telegram_id:
        await notify_user(
            user.id,
            f"🎫 پاسخ جدید برای تیکت #{ticket.id}:\n\n{response}"
        )

    return ticket


@router.post("/notifications")
async def send_notification(
    data: NotificationCreate,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """ارسال اعلان به همه کاربران"""
    repo = AdminRepository(db)
    success_count = await repo.send_notification(data.message)
    total_users = await repo.get_telegram_users_count()

    return {
        "message": f"اعلان به {success_count} کاربر از {total_users} کاربر ارسال شد"
    }


@router.get("/users", response_model=List[schemas.User])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    repo = AdminRepository(db)
    return await repo.get_users(skip, limit)


@router.get("/servers", response_model=List[schemas.Server])
async def list_all_servers(
    skip: int = 0,
    limit: int = 100,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    repo = AdminRepository(db)
    return await repo.get_all_servers(skip, limit)


@router.post("/servers/{server_id}/action")
async def server_action(
    server_id: int,
    action: schemas.ServerAction,
    background_tasks: BackgroundTasks,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    repo = AdminRepository(db)
    
    server = await repo.get_server(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    # Add task to background
    background_tasks.add_task(
        repo.process_server_action,
        server_id=server_id,
        action=action.action,
        admin_id=admin.id
    )

    return {"message": f"Server {action.action} action scheduled"}