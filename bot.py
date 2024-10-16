from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
import os
from database.db_utils import get_or_create_user, get_user_servers, get_user_balance, add_server
from services.services import FactoryService

# ایجاد FactoryService
factory_service = FactoryService()


# استارت ربات
def start(update: Update, context: CallbackContext):
    telegram_id = update.message.chat.id
    username = update.message.chat.username

    # گرفتن یا ایجاد کاربر در دیتابیس
    user = get_or_create_user(telegram_id, username)

    text = f"به ربات مدیریت سرور خوش آمدید، {user.username}!"
    buttons = [
        [InlineKeyboardButton("لیست سرورها", callback_data='list_servers')],
        [InlineKeyboardButton("پروفایل مالی", callback_data='profile')],
        [InlineKeyboardButton("خرید سرور جدید", callback_data='buy_server')],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    update.message.reply_text(text, reply_markup=reply_markup)


# نمایش لیست کشورها برای خرید سرور
def show_countries(update: Update, context: CallbackContext):
    service_name = "hetzner"  # مثال برای Hetzner
    countries = factory_service.get_countries(service_name)

    buttons = []
    for country in countries:
        buttons.append([InlineKeyboardButton(country, callback_data=f"select_country_{country}")])

    reply_markup = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text("لطفا کشور مورد نظر خود را انتخاب کنید:", reply_markup=reply_markup)


# نمایش گزینه‌ها برای انتخاب سیستم‌عامل یا اپلیکیشن
def select_os_or_app(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data
    country = callback_data.split('_')[-1]

    buttons = [
        [InlineKeyboardButton("سیستم‌عامل", callback_data=f"os_{country}")],
        [InlineKeyboardButton("اپلیکیشن", callback_data=f"app_{country}")],
    ]

    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(f"آیا می‌خواهید سیستم‌عامل یا اپلیکیشن انتخاب کنید؟ کشور انتخاب شده: {country}",
                            reply_markup=reply_markup)


# نمایش منابع بر اساس انتخاب سیستم‌عامل یا اپلیکیشن
def show_resources(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data
    choice_type, country = callback_data.split('_')

    if choice_type == 'os':
        resources = factory_service.get_operating_systems("hetzner")  # لیست سیستم‌عامل‌ها
    else:
        resources = factory_service.get_apps("hetzner")  # لیست اپلیکیشن‌ها

    buttons = []
    for resource in resources:
        buttons.append([InlineKeyboardButton(resource['name'],
                                             callback_data=f"select_resource_{resource['id']}_{country}_{choice_type}")])

    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(f"منابع موجود برای {choice_type} در {country}:", reply_markup=reply_markup)


# نمایش گزینه‌های انتخاب RAM، CPU و هارد همراه با هزینه از طریق FactoryService
def select_hardware(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data
    _, resource_id, country, choice_type = callback_data.split('_')

    # گرفتن منابع سخت‌افزاری از طریق FactoryService
    hardware_options = factory_service.get_services("hetzner", resource_id, country, choice_type)

    buttons = []
    for option in hardware_options:
        ram = option['ram']
        cpu = option['cpu']
        disk = option['disk']

        # دریافت هزینه ساعتی بر اساس منابع سخت‌افزاری انتخاب شده
        hourly_cost = factory_service.get_hourly_cost("hetzner", ram, cpu, disk)

        # دکمه‌ها با نمایش هزینه در کنار مشخصات منابع
        buttons.append([
            InlineKeyboardButton(f"RAM: {ram}, CPU: {cpu}, Disk: {disk} | هزینه ساعتی: {hourly_cost} تومان",
                                 callback_data=f"confirm_hardware_{resource_id}_{country}_{choice_type}_{ram}_{cpu}_{disk}")
        ])

    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text("لطفا منابع سخت‌افزاری مورد نظر را انتخاب کنید:", reply_markup=reply_markup)


# نمایش هزینه انتخاب شده بر اساس سخت‌افزار انتخابی
def show_selected_hardware_cost(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data
    _, resource_id, country, choice_type, ram, cpu, disk = callback_data.split('_')

    # گرفتن هزینه ساعتی بر اساس سخت‌افزار انتخابی از FactoryService
    hourly_cost = factory_service.get_hourly_cost("hetzner", ram, cpu, disk)

    # محاسبه هزینه یک روز (24 ساعت)
    daily_cost = hourly_cost * 24

    # نمایش هزینه به کاربر قبل از تایید پرداخت
    text = (
        f"شما منابع زیر را انتخاب کرده‌اید:\n"
        f"RAM: {ram}\n"
        f"CPU: {cpu}\n"
        f"Disk: {disk}\n"
        f"\nهزینه ساعتی: {hourly_cost} تومان\n"
        f"هزینه یک روز: {daily_cost} تومان\n"
        "\nاگر تایید می‌کنید، روی دکمه پرداخت کلیک کنید."
    )

    buttons = [[InlineKeyboardButton("تایید و ادامه به پرداخت",
                                     callback_data=f"confirm_purchase_{resource_id}_{country}_{choice_type}_{ram}_{cpu}_{disk}")]]
    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text, reply_markup=reply_markup)


# بررسی موجودی کاربر و نمایش امکان خرید
def confirm_purchase(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data
    _, resource_id, country, choice_type, ram, cpu, disk = callback_data.split('_')

    telegram_id = query.message.chat.id
    user = get_or_create_user(telegram_id, query.message.chat.username)

    # گرفتن هزینه ساعتی بر اساس سخت‌افزار انتخابی از FactoryService
    hourly_cost = factory_service.get_hourly_cost("hetzner", ram, cpu, disk)

    # محاسبه هزینه یک روز (24 ساعت)
    daily_cost = hourly_cost * 24

    # گرفتن موجودی کاربر
    balance = get_user_balance(user.id)

    if balance >= daily_cost:
        buttons = [[InlineKeyboardButton("خرید سرور",
                                         callback_data=f"purchase_{resource_id}_{country}_{choice_type}_{ram}_{cpu}_{disk}")]]
        reply_markup = InlineKeyboardMarkup(buttons)
        query.edit_message_text(f"موجودی کافی دارید. برای خرید روی دکمه زیر کلیک کنید.", reply_markup=reply_markup)
    else:
        query.edit_message_text(f"موجودی شما کافی نیست. هزینه یک روز: {daily_cost} تومان.")


# نصب مجدد سیستم‌عامل یا اپلیکیشن
def reinstall_os_or_app(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data
    server_id = callback_data.split('_')[2]  # استخراج شناسه سرور

    buttons = [
        [InlineKeyboardButton("سیستم‌عامل", callback_data=f"reinstall_os_{server_id}")],
        [InlineKeyboardButton("اپلیکیشن", callback_data=f"reinstall_app_{server_id}")],
    ]

    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(f"برای سرور {server_id}، نصب مجدد سیستم‌عامل یا اپلیکیشن را انتخاب کنید:",
                            reply_markup=reply_markup)


# عملیات نصب مجدد سیستم‌عامل یا اپلیکیشن
def reinstall_action(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data
    action_type, server_id = callback_data.split('_')[1], callback_data.split('_')[2]

    if action_type == 'os':
        result = factory_service.reinstall_os("hetzner", server_id, 456)  # فرض شناسه سیستم‌عامل
    else:
        result = factory_service.install_app("hetzner", server_id, 789)  # فرض شناسه اپلیکیشن

    if result:
        query.edit_message_text(
            f"{'سیستم‌عامل' if action_type == 'os' else 'اپلیکیشن'} با موفقیت برای سرور {server_id} نصب شد.")
    else:
        query.edit_message_text(
            f"خطا در نصب مجدد {'سیستم‌عامل' if action_type == 'os' else 'اپلیکیشن'} برای سرور {server_id}.")


# نمایش لیست سرورهای کاربر
def list_servers(update: Update, context: CallbackContext):
    query = update.callback_query
    telegram_id = query.message.chat.id
    user = get_or_create_user(telegram_id, query.message.chat.username)

    # گرفتن سرورهای کاربر از دیتابیس
    servers = get_user_servers(user.id)

    if servers:
        text = "لیست سرورهای شما:\n"
        buttons = []
        for server in servers:
            text += f"سرور {server.id}: {server.server_type} در {server.country}, سیستم‌عامل: {server.os}\n"
            # دکمه‌های مرتبط با عملیات برای هر سرور
            buttons.append([
                InlineKeyboardButton(f"نصب مجدد سیستم‌عامل - سرور {server.id}",
                                     callback_data=f"reinstall_os_{server.id}"),
                InlineKeyboardButton(f"خاموش کردن - سرور {server.id}", callback_data=f"shutdown_{server.id}"),
                InlineKeyboardButton(f"ریستارت - سرور {server.id}", callback_data=f"reboot_{server.id}"),
                InlineKeyboardButton(f"حذف - سرور {server.id}", callback_data=f"delete_{server.id}")
            ])
        reply_markup = InlineKeyboardMarkup(buttons)
    else:
        text = "شما هیچ سروری ندارید."
        reply_markup = None

    query.edit_message_text(text, reply_markup=reply_markup)


# نصب مجدد سیستم‌عامل
def reinstall_os(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data
    server_id = int(callback_data.split('_')[2])  # استخراج شناسه سرور از داده callback

    service_name = "hetzner"
    os_id = 456  # شناسه سیستم‌عامل که کاربر انتخاب کرده است (باید از جایی گرفته شود)

    result = factory_service.reinstall_os(service_name, server_id, os_id)
    if result:
        query.edit_message_text(f"سیستم‌عامل سرور {server_id} با موفقیت نصب مجدد شد.")
    else:
        query.edit_message_text(f"خطا در نصب مجدد سیستم‌عامل برای سرور {server_id}.")


# خاموش کردن سرور
def shutdown_server(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data
    server_id = int(callback_data.split('_')[1])

    service_name = "hetzner"
    result = factory_service.shutdown_server(service_name, server_id)
    if result:
        query.edit_message_text(f"سرور {server_id} با موفقیت خاموش شد.")
    else:
        query.edit_message_text(f"خطا در خاموش کردن سرور {server_id}.")


# ریستارت سرور
def reboot_server(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data
    server_id = int(callback_data.split('_')[1])

    service_name = "hetzner"
    result = factory_service.reboot_server(service_name, server_id)
    if result:
        query.edit_message_text(f"سرور {server_id} با موفقیت ریستارت شد.")
    else:
        query.edit_message_text(f"خطا در ریستارت سرور {server_id}.")


# حذف سرور
def delete_server(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data
    server_id = int(callback_data.split('_')[1])

    service_name = "hetzner"
    result = factory_service.delete_server(service_name, server_id)
    if result:
        query.edit_message_text(f"سرور {server_id} با موفقیت حذف شد.")
    else:
        query.edit_message_text(f"خطا در حذف سرور {server_id}.")


# مشاهده پروفایل مالی
def view_profile(update: Update, context: CallbackContext):
    query = update.callback_query
    telegram_id = query.message.chat.id
    user = get_or_create_user(telegram_id, query.message.chat.username)

    balance = get_user_balance(user.id)
    text = f"پروفایل مالی شما:\nموجودی: {balance} تومان"
    query.edit_message_text(text)


def main():
    updater = Updater(token=os.getenv('TELEGRAM_TOKEN'), use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(list_servers, pattern='list_servers'))
    dispatcher.add_handler(CallbackQueryHandler(shutdown_server, pattern='shutdown_.*'))
    dispatcher.add_handler(CallbackQueryHandler(reboot_server, pattern='reboot_.*'))
    dispatcher.add_handler(CallbackQueryHandler(delete_server, pattern='delete_.*'))
    dispatcher.add_handler(CallbackQueryHandler(view_profile, pattern='profile'))

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(show_countries, pattern='buy_server'))
    dispatcher.add_handler(CallbackQueryHandler(select_os_or_app, pattern='select_country_.*'))
    dispatcher.add_handler(CallbackQueryHandler(show_resources, pattern='os_.*|app_.*'))
    dispatcher.add_handler(CallbackQueryHandler(confirm_purchase, pattern='select_resource_.*'))
    dispatcher.add_handler(CallbackQueryHandler(purchase_server, pattern='purchase_.*'))
    dispatcher.add_handler(CallbackQueryHandler(reinstall_os_or_app, pattern='reinstall_os_.*'))
    dispatcher.add_handler(CallbackQueryHandler(reinstall_action, pattern='reinstall_os_.*|reinstall_app_.*'))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
