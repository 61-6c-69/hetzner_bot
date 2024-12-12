from utils.notifications import notify_user
from database.models import User, Ticket
from utils.auth import get_current_admin
from fastapi import APIRouter, Depends
from utils.logger import logger
from pydantic import BaseModel

router = APIRouter()


class NotificationCreate(BaseModel):
    message: str


@router.get("/tickets")
async def list_tickets(admin: User = Depends(get_current_admin)):
    """لیست همه تیکت‌ها"""
    tickets = await Ticket.all().prefetch_related('user')
    return tickets


@router.post("/tickets/{ticket_id}/reply")
async def reply_ticket(
        ticket_id: int,
        response: str,
        admin: User = Depends(get_current_admin)
):
    """پاسخ به تیکت"""
    ticket = await Ticket.get(id=ticket_id)
    ticket.response = response
    ticket.status = 'closed'
    await ticket.save()

    # اطلاع‌رسانی به کاربر
    ticket_user = await ticket.user
    if ticket_user.telegram_id:
        await notify_user(
            ticket_user.id,
            f"🎫 پاسخ جدید برای تیکت #{ticket.id}:\n\n{response}"
        )

    return ticket


@router.post("/notifications")
async def send_notification(
        data: NotificationCreate,
        admin: User = Depends(get_current_admin)
):
    """ارسال اعلان به همه کاربران"""
    # دریافت کاربران دارای تلگرام
    users = await User.filter(telegram_id__not_isnull=True)

    # ارسال پیام به هر کاربر
    success_count = 0
    for user in users:
        try:
            await notify_user(user.id, data.message)
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to send notification to user {user.id}: {e}")

    return {
        "message": f"اعلان به {success_count} کاربر از {len(users)} کاربر ارسال شد"
    }
