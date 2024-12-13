from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.payment import payment_handler
from database.models import Transaction, User
from utils.currency import currency_converter
import logging

async def increase_balance(update, context):
    """شروع فرایند افزایش موجودی"""
    query = update.callback_query
    await query.answer()
    
    # کیبورد انتخاب مبلغ شارژ
    amounts = [500_000, 1_000_000, 2_000_000, 5_000_000]  # مبالغ به تومان
    keyboard = []
    
    for amount in amounts:
        keyboard.append([
            InlineKeyboardButton(
                f"{amount:,} تومان",
                callback_data=f"pay_amount_{amount}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")])
    
    await query.edit_message_text(
        "💰 افزایش موجودی\n\n"
        "لطفاً مبلغ مورد نظر خود را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def process_payment(update, context):
    """پردازش درخواست پرداخت"""
    query = update.callback_query
    await query.answer()
    
    amount = int(query.data.split('_')[2])  # مبلغ به تومان
    user = await User.get(telegram_id=update.effective_user.id)
    
    # ایجاد تراکنش در دیتابیس
    transaction = await Transaction.create(
        user=user,
        amount=amount,
        description=f"افزایش موجودی به مبلغ {amount:,} تومان",
        status='pending'
    )
    
    try:
        # درخواست ایجاد تراکنش از زرین‌پال
        description = f"افزایش موجودی کاربر {user.id}"
        payment_url, authority = await payment_handler.create_payment(amount, description)
        
        # ذخیره شناسه پرداخت
        transaction.payment_id = authority
        await transaction.save()
        
        # ایجاد پیام و دکمه‌های پرداخت
        message = payment_handler.format_payment_message(amount, description, payment_url)
        keyboard = [[
            InlineKeyboardButton("💳 پرداخت", url=payment_url),
            InlineKeyboardButton("❌ انصراف", callback_data="cancel_payment")
        ]]
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logging.error(f"خطا در ایجاد تراکنش: {str(e)}")
        await transaction.delete()  # حذف تراکنش ناموفق
        await query.edit_message_text(
            "❌ متأسفانه خطایی در ایجاد تراکنش رخ داد.\n"
            "لطفاً دوباره تلاش کنید.",
            reply_markup=main_menu_keyboard()
        )

async def show_transactions(update, context):
    """نمایش تاریخچه تراکنش‌ها"""
    query = update.callback_query
    await query.answer()
    
    user = await User.get(telegram_id=update.effective_user.id)
    transactions = await Transaction.filter(user=user).order_by('-created_at').limit(10)
    
    if not transactions:
        await query.edit_message_text(
            "شما هنوز هیچ تراکنشی نداشته‌اید!",
            reply_markup=main_menu_keyboard()
        )
        return
    
    message = "📊 تاریخچه تراکنش‌های شما:\n\n"
    for tx in transactions:
        status_emoji = "✅" if tx.status == 'completed' else "⏳" if tx.status == 'pending' else "❌"
        message += (
            f"{status_emoji} {tx.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"💰 مبلغ: {tx.amount:,} تومان\n"
            f"📝 {tx.description}\n"
            "──────────────\n"
        )
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def cancel_payment(update, context):
    """انصراف از پرداخت"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "❌ پرداخت لغو شد.",
        reply_markup=main_menu_keyboard()
    ) 