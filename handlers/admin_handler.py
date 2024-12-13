from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database.models import Transaction, User, Server, NotificationSettings, UserRole
from config import ADMIN_IDS
from utils.notifications import send_notification, NotificationType
from utils.hetzner_api import hetzner
from utils.auth import is_admin_role
import logging

logger = logging.getLogger(__name__)

async def is_admin(telegram_id: int) -> bool:
    """Check if user is admin"""
    try:
        user = await User.get(telegram_id=telegram_id)
        return user and is_admin_role(user.role)
    except Exception:
        return False

async def handle_payment_proof(update, context):
    """رسیدگی به رسید پرداخت ارسالی کاربر"""
    message = update.message
    user_id = message.from_user.id
    
    # ذخیره اطلاعات در context برای پیگیری بعدی
    context.user_data['payment_proof'] = {
        'message_id': message.message_id,
        'file_id': message.photo[-1].file_id if message.photo else None,
        'text': message.caption or message.text
    }
    
    # ارسال به ادمین‌ها
    for admin_id in ADMIN_IDS:
        keyboard = [
            [
                InlineKeyboardButton("✅ تایید", callback_data=f"approve_payment_{user_id}"),
                InlineKeyboardButton("❌ رد", callback_data=f"reject_payment_{user_id}")
            ]
        ]
        
        # ارسال عکس یا متن به ادمین
        if message.photo:
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=message.photo[-1].file_id,
                caption=f"📝 رسید پرداخت از کاربر {user_id}\n"
                        f"توضیحات: {message.caption or 'بدون توضیحات'}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"📝 رسید پرداخت از کاربر {user_id}\n"
                     f"متن پیام: {message.text}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    # پاسخ به کاربر
    await message.reply_text(
        "✅ رسید پرداخت شما دریافت شد و در حال بررسی است.\n"
        "پس از تایید پشتیبانی، موجودی شما افزایش خواهد یافت."
    )

async def approve_payment(update, context):
    """تایید پرداخت توسط ادمین"""
    query = update.callback_query
    admin_id = query.from_user.id
    
    if not await is_admin(admin_id):
        await query.answer("⛔️ شما دسترسی به این بخش ندارید!", show_alert=True)
        return
    
    await query.answer()
    user_id = int(query.data.split('_')[2])
    
    # پیدا کردن آخرین تراکنش در انتظار کاربر
    transaction = await Transaction.filter(
        user__telegram_id=user_id,
        status='pending'
    ).order_by('-created_at').first()
    
    if transaction:
        # تایید تراکنش
        transaction.status = 'completed'
        await transaction.save()
        
        # اطلاع ��ه کاربر
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ پرداخت شما به مبلغ {transaction.amount:,} تومان تایید شد.\n"
                 f"موجودی شما افزایش یافت."
        )
        
        await query.edit_message_text(
            f"✅ پرداخت کاربر {user_id} تایید شد."
        )
    else:
        await query.edit_message_text(
            f"❌ تراکنش معلقی برای کاربر {user_id} یافت نشد!"
        )

async def reject_payment(update, context):
    """رد پرداخت توسط ادمین"""
    query = update.callback_query
    admin_id = query.from_user.id
    
    if not await is_admin(admin_id):
        await query.answer("⛔️ شما دسترسی به این بخش ندارید!", show_alert=True)
        return
    
    await query.answer()
    user_id = int(query.data.split('_')[2])
    
    # پیدا کردن آخرین تراکنش در انتظار کاربر
    transaction = await Transaction.filter(
        user__telegram_id=user_id,
        status='pending'
    ).order_by('-created_at').first()
    
    if transaction:
        # رد تراکنش
        transaction.status = 'rejected'
        await transaction.save()
        
        # اطلاع به کاربر
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ متأسفانه پرداخت شما تایید نشد.\n"
                 "لطفاً با پشتیبانی تماس بگیرید."
        )
        
        await query.edit_message_text(
            f"❌ پرداخت کاربر {user_id} رد شد."
        )
    else:
        await query.edit_message_text(
            f"❌ تراکنش معلقی برای کاربر {user_id} یافت نشد!"
        )

async def admin_panel(update, context):
    """نمایش پنل مدیریت"""
    user_id = update.effective_user.id
    if not await is_admin(user_id):
        await update.message.reply_text("⛔️ شما دسترسی به این بخش را ندارید!")
        return
    
    # آمار کلی
    total_users = await User.all().count()
    total_servers = await Server.all().count()
    pending_payments = await Transaction.filter(status='pending').count()
    
    keyboard = [
        [
            InlineKeyboardButton("👥 کاربران", callback_data="admin_users"),
            InlineKeyboardButton("🖥 سرورها", callback_data="admin_servers")
        ],
        [
            InlineKeyboardButton("💰 تراکنش‌ها", callback_data="admin_transactions"),
            InlineKeyboardButton("⚙️ تنظیمات", callback_data="admin_settings")
        ]
    ]
    
    message = (
        "🎛 پنل مدیریت\n\n"
        f"👥 تعداد کاربران: {total_users}\n"
        f"🖥 تعداد سرورها: {total_servers}\n"
        f"💰 تراکنش‌های در انتظار: {pending_payments}"
    )
    
    await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_users(update, context):
    """مدیریت کاربران"""
    query = update.callback_query
    if not await is_admin(query.from_user.id):
        await query.answer("⛔️ شما دسترسی ندارید!", show_alert=True)
        return
    
    await query.answer()
    
    # دریافت یست کاربران
    users = await User.all().order_by('-created_at').limit(10)
    
    message = "👥 لیست آخرین کاربران:\n\n"
    for user in users:
        balance_toman = await user.get_balance()
        message += (
            f"🆔 {user.telegram_id}\n"
            f"👤 {user.first_name}\n"
            f"💰 موجودی: {balance_toman:,} تومان\n"
            f"📅 عضویت: {user.created_at.strftime('%Y-%m-%d')}\n"
            "──────────────\n"
        )
    
    keyboard = [
        [
            InlineKeyboardButton("🔍 جستجو", callback_data="admin_search_user"),
            InlineKeyboardButton("⛔️ کاربران مسدود", callback_data="admin_banned_users")
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
    ]
    
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_servers(update, context):
    """مدیریت سرورها"""
    query = update.callback_query
    if not await is_admin(query.from_user.id):
        await query.answer("⛔️ شما دسترسی ندارید!", show_alert=True)
        return
    
    await query.answer()
    
    # دریافت لیست سرورها
    servers = await Server.all().prefetch_related('user').order_by('-created_at').limit(10)
    
async def admin_transactions(update, context):
    """مدیریت تراکنش‌ها"""
    query = update.callback_query
    if not await is_admin(query.from_user.id):
        await query.answer("⛔️ شما دسترسی ندارید!", show_alert=True)
        return
    
    await query.answer()
    
    # دریافت لیست تراکنش‌های در انتظار
    transactions = await Transaction.filter(status='pending').prefetch_related('user').order_by('-created_at').limit(10)
    
    message = "💰 لیست تراکنش‌های در انتظار:\n\n"
    if not transactions:
        message = "هیچ تراکنش در انتظاری وجود ندارد."
    else:
        for tx in transactions:
            message += (
                f"🆔 کاربر: {tx.user.telegram_id}\n"
                f"💰 مبلغ: {tx.amount:,} تومان\n"
                f"📝 توضیحات: {tx.description}\n"
                f"📅 تاریخ: {tx.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                "──────────────\n"
            )
    
    keyboard = [
        [
            InlineKeyboardButton("🔍 جستجو", callback_data="admin_search_transaction"),
            InlineKeyboardButton("📊 گزارش", callback_data="admin_transaction_report")
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
    ]
    
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_settings(update, context):
    """تنظیمات ادمین"""
    query = update.callback_query
    if not await is_admin(query.from_user.id):
        await query.answer("⛔️ شما دسترسی ندارید!", show_alert=True)
        return
    
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("🔔 تنظیمات اعلان‌ها", callback_data="admin_notification_settings"),
            InlineKeyboardButton("💰 تنظیمات مالی", callback_data="admin_payment_settings")
        ],
        [
            InlineKeyboardButton("👥 مدیریت ادمین‌ها", callback_data="admin_manage_admins"),
            InlineKeyboardButton("⚙️ تنظیمات سرور", callback_data="admin_server_settings")
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
    ]
    
    message = (
        "⚙️ تنظیمات پنل ادمین\n\n"
        "لطفاً بخش مورد نظر را انتخاب کنید:"
    )
    
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

async def confirm_purchase(update, context):
    """تایید خرید سرور توسط ادمین"""
    query = update.callback_query
    if not await is_admin(query.from_user.id):
        await query.answer("⛔️ شما دسترسی ندارید!", show_alert=True)
        return
    
    await query.answer()
    
    try:
        # دریافت اطلاعات خرید از callback_data
        _, user_id, server_type = query.data.split('_')
        user_id = int(user_id)
        
        user = await User.get(id=user_id)
        
        # بررسی موجودی کاربر
        server_price = await hetzner.get_server_price(server_type)
        if user.balance < server_price:
            await query.edit_message_text(
                "❌ موجودی کاربر برای خرید این سرور کافی نیست.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")
                ]])
            )
            return
        
        # ایجاد سرور
        server_result = await hetzner.create_server(
            name=f"server-{user.id}-{server_type}",
            server_type=server_type,
            ssh_keys=user.ssh_keys
        )
        
        if server_result:
            # ثبت سرور در دیتابیس
            server = await Server.create(
                user=user,
                hetzner_id=server_result['id'],
                name=server_result['name'],
                ip=server_result['ip'],
                status='running',
                os=server_result['os']
            )
            
            # کسر هزینه از موجودی کاربر
            user.balance -= server_price
            await user.save()
            
            # ارسال نوتیفیکیشن به کاربر
            await send_notification(
                user,
                NotificationType.SERVER_CREATED,
                name=server.name,
                ip=server.ip
            )
            
            await query.edit_message_text(
                f"✅ سرور با موفقیت ایجاد شد\n\n"
                f"🖥 نام: {server.name}\n"
                f"🌐 IP: {server.ip}\n"
                f"💾 OS: {server.os}\n"
                f"⚡️ وضعیت: {server.status}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")
                ]])
            )
        else:
            raise Exception("خطا در ایجاد سرور")
            
    except Exception as e:
        logger.error(f"Error in confirm_purchase: {e}")
        await query.edit_message_text(
            "❌ خطا در ایجاد سرور. لطفاً دوباره تلاش کنید.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")
            ]])
        )

async def get_user_info(user_id: int):
    """دریافت اطلاعات کاربر"""
    user = await User.get(id=user_id)
    balance_toman = await get_user_balance(user.telegram_id)
    
    return (
        f"👤 نام: {user.first_name} {user.last_name or ''}\n"
        f"📱 تلفن: {user.phone}\n"
        f"📧 ایمیل: {user.email}\n"
        f"💰 موجودی: {balance_toman:,} تومان\n"
        f"📅 تاریخ عضویت: {user.created_at.strftime('%Y-%m-%d')}"
    )

async def approve_server(user_id: int, server_price: int):
    """تایید درخواست سرور"""
    user = await User.get(id=user_id)
    balance = await get_user_balance(user.telegram_id)
    
    if balance < server_price:
        return False, "موجودی کاربر کافی نیست"
        
    # Create a server charge transaction
    await Transaction.create(
        user=user,
        amount=server_price,
        type="server_charge",
        status="completed",
        description="Server creation charge"
    )
    
    return True, "سرور با موفقیت ایجاد شد"

async def promote_to_admin(user_id: int) -> bool:
    """ارتقاء کاربر به ادمین"""
    try:
        user = await User.get(id=user_id)
        if user:
            user.role = UserRole.ADMIN
            await user.save()
            return True
    except Exception:
        return False
    return False

async def demote_from_admin(user_id: int) -> bool:
    """حذف دسترسی ادمین"""
    try:
        user = await User.get(id=user_id)
        if user and user.role == UserRole.ADMIN:
            user.role = UserRole.USER
            await user.save()
            return True
    except Exception:
        return False
    return False
