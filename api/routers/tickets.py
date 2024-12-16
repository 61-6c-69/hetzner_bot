from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from repositories import TicketRepository, UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from utils.files import save_ticket_file
from utils.auth import get_current_user
from database.database import get_db
from api import schemas, models
from bot import notify_admins
from typing import List

router = APIRouter()


@router.get("/", response_model=List[schemas.TicketResponse])
async def list_tickets(
        current_user: schemas.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    repo = TicketRepository(db)
    return await repo.get_user_tickets(current_user.id)


@router.get("/{ticket_id}", response_model=models.TicketResponse)
async def get_ticket(
        ticket_id: int,
        current_user: schemas.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    repo = TicketRepository(db)
    ticket = await repo.get_user_ticket(current_user.id, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.post("/", response_model=models.TicketResponse)
async def create_ticket(
        ticket: schemas.TicketCreate,
        file: UploadFile = File(None),
        current_user: schemas.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    ticket_repo = TicketRepository(db)
    user_repo = UserRepository(db)

    # Save file if provided
    file_path = None
    if file:
        file_path = await save_ticket_file(file, current_user.id)

    # Create ticket
    new_ticket = await ticket_repo.create(
        user_id=current_user.id,
        subject=ticket.subject,
        message=ticket.message,
        file_path=file_path,
        priority=ticket.priority
    )

    # Get user info for notification
    user = await user_repo.get(current_user.id)

    # Notify admins
    notification = (
        f"🎫 تیکت جدید\n"
        f"کاربر: {user.first_name} {user.last_name or ''}\n"
        f"موضوع: {ticket.subject}\n"
        f"اولویت: {ticket.priority}\n"
        f"پیام: {ticket.message}"
    )
    await notify_admins(notification, file_path)

    return new_ticket


@router.post("/{ticket_id}/reply", response_model=schemas.TicketMessageResponse)
async def reply_to_ticket(
        ticket_id: int,
        reply: schemas.TicketReply,
        file: UploadFile = File(None),
        current_user: schemas.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    ticket_repo = TicketRepository(db)

    # Check ticket access
    ticket = await ticket_repo.get_user_ticket(current_user.id, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Save file if provided
    file_path = None
    if file:
        file_path = await save_ticket_file(file, current_user.id)

    # Add reply
    message = await ticket_repo.add_reply(
        ticket_id=ticket_id,
        user_id=current_user.id,
        message=reply.message,
        file_path=file_path
    )

    # Update ticket status
    await ticket_repo.update_status(ticket_id, 'waiting_for_admin')

    return message


@router.get("/{ticket_id}/messages", response_model=List[schemas.TicketMessageResponse])
async def get_ticket_messages(
        ticket_id: int,
        current_user: schemas.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    repo = TicketRepository(db)

    # Check ticket access
    ticket = await repo.get_user_ticket(current_user.id, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return await repo.get_ticket_messages(ticket_id)
