from config import SUPPORT_CHAT_ID

async def handle_support_message(update, context):
    """مدیریت پیام‌های پشتیبانی"""
    message = update.message
    user_id = message.from_user.id
    
    # ارسال به گروه پشتیبانی
    await context.bot.forward_message(
        chat_id=SUPPORT_CHAT_ID,
        from_chat_id=message.chat_id,
        message_id=message.message_id
    )
    
    await message.reply_text(
        "✅ پیام شما به پشتیبانی ارسال شد.\n"
        "در اسرع وقت پاسخ داده خواهد شد."
    ) 