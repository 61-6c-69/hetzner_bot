from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from repositories.ticket_repository import TicketRepository
from repositories.admin_repository import AdminRepository
from sqlalchemy.ext.asyncio import AsyncSession
from utils.notifications import notify_user
from api.schemas import NotificationCreate
from utils.auth import get_current_admin
from database.database import get_db
from database.models import User
from api import schemas
from utils.auth import get_current_admin_user

router = APIRouter()


@router.get("/tickets", response_model=schemas.PaginatedTickets)
async def list_tickets(
    pagination: schemas.PaginationParams = Depends(),
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """لیست همه تیکت‌ها"""
    repo = TicketRepository(db)
    tickets, total = await repo.get_all(
        page=pagination.page,
        per_page=pagination.per_page,
        cache_key=f"admin_tickets_{pagination.search}_{pagination.sort_by}_{pagination.sort_order}"
    )
    
    total_pages = (total + pagination.per_page - 1) // pagination.per_page
    
    return {
        "items": tickets,
        "total": total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total_pages": total_pages
    }


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


@router.get("/users", response_model=schemas.PaginatedUsers)
async def get_users(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_admin: schemas.User = Depends(get_current_admin_user)
):
    """Get list of users (admin only)"""
    repo = AdminRepository(db)
    return await repo.get_users(skip=skip, limit=limit)


@router.get("/servers", response_model=schemas.PaginatedServers)
async def get_servers(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_admin: schemas.User = Depends(get_current_admin_user)
):
    """Get list of servers (admin only)"""
    repo = AdminRepository(db)
    return await repo.get_servers(skip=skip, limit=limit)


@router.get("/transactions", response_model=schemas.PaginatedTransactions)
async def get_transactions(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_admin: schemas.User = Depends(get_current_admin_user)
):
    """Get list of transactions (admin only)"""
    repo = AdminRepository(db)
    return await repo.get_transactions(skip=skip, limit=limit)


@router.post("/users/{user_id}/ban")
async def ban_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: schemas.User = Depends(get_current_admin_user)
):
    """Ban a user (admin only)"""
    repo = AdminRepository(db)
    await repo.ban_user(user_id)
    return {"message": "User banned successfully"}


@router.post("/users/{user_id}/unban")
async def unban_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: schemas.User = Depends(get_current_admin_user)
):
    """Unban a user (admin only)"""
    repo = AdminRepository(db)
    await repo.unban_user(user_id)
    return {"message": "User unbanned successfully"}


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_admin: schemas.User = Depends(get_current_admin_user)
):
    """Get system statistics (admin only)"""
    repo = AdminRepository(db)
    return {
        "users": await repo.get_user_stats(),
        "servers": await repo.get_server_stats(),
        "transactions": await repo.get_transaction_stats()
    }


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