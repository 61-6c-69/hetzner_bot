from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from database.models import User, Ticket
from config import ADMIN_IDS, UPLOAD_DIR
from utils.auth import get_current_user
from api.models import TicketResponse
from models import TicketMessage
from typing import List
from bot import bot
import logging
import os

router = APIRouter()


@router.get("/tickets", response_model=List[TicketResponse])
async def list_tickets(user: User = Depends(get_current_user)):
    """دریافت لیست تیکت‌ها"""
    tickets = await Ticket.filter(user=user).order_by('-created_at')
    return tickets


@router.post("/tickets", response_model=TicketResponse)
async def create_ticket(
    message: str,
    subject: str,
    priority: str = "medium",
    file: UploadFile = File(None),
    user: User = Depends(get_current_user)
):
    """ایجاد تیکت جدید"""
    # بررسی اولویت
    if priority not in ['low', 'medium', 'high']:
        raise HTTPException(status_code=400, detail="Invalid priority")

    # ذخیره فایل اگر ارسال شده باشد
    file_path = None
    if file:
        # ایجاد دایرکتوری برای فایل‌های کاربر
        file_dir = os.path.join(UPLOAD_DIR, str(user.id))
        os.makedirs(file_dir, exist_ok=True)

        # ذخیره فایل با نام امن
        safe_filename = os.path.basename(file.filename)
        file_path = os.path.join(file_dir, safe_filename)
        
        try:
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
        except Exception as e:
            logging.error(f"Failed to save file: {e}")
            raise HTTPException(status_code=500, detail="Failed to save file")

    # ایجاد تیکت جدید
    try:
        ticket = await Ticket.create(
            user=user,
            user_id=user.id,
            subject=subject,
            message=message,
            file_path=file_path,
            status='open',
            priority=priority
        )
    except Exception as e:
        # اگر ذخیره تیکت با خطا مواجه شد، فایل را پاک کنیم
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        logging.error(f"Failed to create ticket: {e}")
        raise HTTPException(status_code=500, detail="Failed to create ticket")

    # ارسال نوتیفیکیشن به ادمین‌ها
    notification = (
        "🎫 <b>تیکت جدید</b>\n\n"
        f"👤 کاربر: {user.first_name}"
        f"{f' {user.last_name}' if user.last_name else ''}\n"
        f"📱 موبایل: {user.phone}\n"
        f"📋 موضوع: {subject}\n"
        f"🔥 اولویت: {priority}\n"
        f"💭 پیام: {message}\n"
        f"📎 فایل: {'دارد' if file else 'ندارد'}"
    )

    # ارسال پیام به ادمین‌ها
    for admin_id in ADMIN_IDS:
        try:
            # ارسال پیام متنی
            await bot.send_message(
                admin_id,
                notification,
                parse_mode='HTML'
            )
            
            # اگر فایل وجود دارد، آن را هم ارسال کن
            if file_path:
                with open(file_path, 'rb') as f:
                    await bot.send_document(
                        admin_id,
                        f,
                        caption=f"فایل پیوست تیکت #{ticket.id}"
                    )
        except Exception as e:
            logging.error(f"Failed to notify admin {admin_id}: {e}")

    return ticket


@router.post("/tickets/{ticket_id}/reply")
async def reply_ticket(
    ticket_id: int,
    message: str,
    file: UploadFile = File(None),
    user: User = Depends(get_current_user)
):
    """پاسخ به تیکت"""
    # بررسی وجود تیکت
    ticket = await Ticket.get_or_none(id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # بررسی دسترسی
    if user.id not in ADMIN_IDS and ticket.user_id != user.id:
        raise HTTPException(status_code=403, detail="Permission denied")

    # ذخیره فایل اگر ارسال شده باشد
    file_path = None
    if file:
        file_dir = os.path.join(UPLOAD_DIR, str(ticket.user_id))
        os.makedirs(file_dir, exist_ok=True)
        
        safe_filename = os.path.basename(file.filename)
        file_path = os.path.join(file_dir, safe_filename)
        
        try:
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
        except Exception as e:
            logging.error(f"Failed to save file: {e}")
            raise HTTPException(status_code=500, detail="Failed to save file")

    # به‌روزرسانی وضعیت تیکت
    if user.id in ADMIN_IDS:
        ticket.status = 'answered'
    else:
        ticket.status = 'open'
    await ticket.save()

    # اطلاع‌رسانی
    if user.id in ADMIN_IDS:
        # اگر ادمین پاسخ داده، به کاربر اطلاع بده
        notification = (
            "🎫 <b>پاسخ جدید برای تیکت شما</b>\n\n"
            f"📋 موضوع: {ticket.subject}\n"
            f"💭 پاسخ: {message}\n"
            f"📎 فایل: {'دارد' if file else 'ندارد'}"
        )
        try:
            # ارسال پیام متنی
            await bot.send_message(
                ticket.user.telegram_id,
                notification,
                parse_mode='HTML'
            )
            
            # ارسال فایل اگر وجود دارد
            if file_path:
                with open(file_path, 'rb') as f:
                    await bot.send_document(
                        ticket.user.telegram_id,
                        f,
                        caption="فایل پیوست پاسخ تیکت"
                    )
        except Exception as e:
            logging.error(f"Failed to notify user {ticket.user_id}: {e}")
    else:
        # اگر کاربر پاسخ داده، به ادمین‌ها اطلاع بده
        notification = (
            "🎫 <b>پاسخ جدید در تیکت</b>\n\n"
            f"👤 کاربر: {user.first_name}\n"
            f"📋 موضوع: {ticket.subject}\n"
            f"💭 پیام: {message}\n"
            f"📎 فایل: {'دارد' if file else 'ندارد'}"
        )
        for admin_id in ADMIN_IDS:
            try:
                # ارسال پیام متنی
                await bot.send_message(
                    admin_id,
                    notification,
                    parse_mode='HTML'
                )
                
                # ارسال فایل اگر وجود دارد
                if file_path:
                    with open(file_path, 'rb') as f:
                        await bot.send_document(
                            admin_id,
                            f,
                            caption=f"فایل پیوست تیکت #{ticket.id}"
                        )
            except Exception as e:
                logging.error(f"Failed to notify admin {admin_id}: {e}")

    return {"status": "success"}


@router.get("/tickets/{ticket_id}/messages")
async def get_ticket_messages(
    ticket_id: int,
    user: User = Depends(get_current_user)
):
    """دریافت پیام‌های یک تیکت"""
    # بررسی وجود تیکت
    ticket = await Ticket.get_or_none(id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # بررسی دسترسی
    if user.id not in ADMIN_IDS and ticket.user_id != user.id:
        raise HTTPException(status_code=403, detail="Permission denied")

    # دریافت پیام‌ها
    messages = await TicketMessage.filter(ticket=ticket).order_by('created_at')
    return messages
