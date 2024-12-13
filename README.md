# Hetzner Bot

A Telegram bot and web application for managing Hetzner servers.

## Features

### User Management
- ثبت نام و احراز هویت کاربران
- تایید شماره موبایل با OTP
- اتصال اکانت تلگرام
- سطوح دسترسی کاربران (ادمین و کاربر عادی)
- مدیریت تنظیمات اعلان‌ها

### مدیریت سرور
- ایجاد سرور جدید
- مشاهده لیست سرورها
- مدیریت وضعیت سرورها (روشن/خاموش/ریستارت)
- تغییر IP سرور
- مانیتورینگ منابع سرور (CPU, RAM, Disk)
- نمایش لاگ‌های سیستمی

### مدیریت مالی
- محاسبه موجودی از تراکنش‌ها
- شارژ حساب
- مشاهده تراکنش‌ها
- محاسبه خودکار هزینه‌ها

### پشتیبانی
- ارسال تیکت پشتیبانی
- آپلود فایل
- مشاهده وضعیت تیکت‌ها

### پنل ادمین
- مدیریت کاربران
- مشاهده آمار سیستم
- مدیریت تیکت‌ها
- تنظیمات سیستم

## دستورات ربات

```
/start - شروع کار با ربات
/help - راهنمای دستورات
/register - ثبت نام
/profile - مشاهده پروفایل
/balance - مشاهده موجودی
/servers - لیست سرورها
/create_server - ایجاد سرور جدید
/support - ارسال تیکت پشتیبانی
/settings - تنظیمات

# دستورات ادمین
/admin - پنل مدیریت
/promote <telegram_id> - ارتقاء کاربر به ادمین
/demote <telegram_id> - حذف دسترسی ادمین
```

## نصب و راه‌اندازی

1. کلون کردن مخزن:
```bash
git clone https://github.com/yourusername/hetzner_bot.git
cd hetzner_bot
```

2. نصب وابستگی‌ها:
```bash
pip install -r requirements.txt
```

3. کپی فایل تنظیمات:
```bash
cp .env.example .env
```

4. ویرایش فایل `.env` و تنظیم مقادیر مورد نیاز:
```env
BOT_TOKEN=your_telegram_bot_token
HETZNER_API_KEY=your_hetzner_api_key
DATABASE_URL=postgresql://user:pass@localhost/dbname
REDIS_URL=redis://localhost
```

5. اجرای مایگریشن‌های دیتابیس:
```bash
alembic upgrade head
```

6. اجرای برنامه:
```bash
# اجرای ربات تلگرام
python bot.py

# اجرای وب اپلیکیشن
uvicorn api.main:app --reload

# اجرای ورکر مانیتورینگ
python monitoring_worker.py

# اجرای ورکر بیلینگ
python billing_worker.py
```

## ساختار پروژه

```
hetzner_bot/
├── api/                    # FastAPI backend
│   ├── routers/           # API endpoints
│   ├── models.py          # Pydantic models
│   └── main.py           
├── bot/                   # Telegram bot
│   ├── handlers/         
│   └── main.py
├── database/              # Database models and config
├── repositories/          # Data access layer
├── utils/                 # Utility functions
├── frontend/              # Next.js frontend
├── alembic/               # Database migrations
├── tests/                 # Test files
└── workers/               # Background workers
```

## تکنولوژی‌ها

- Python 3.9+
- FastAPI
- SQLAlchemy
- python-telegram-bot
- Redis
- PostgreSQL
- Next.js
- TailwindCSS

## مشارکت

1. Fork کردن مخزن
2. ایجاد برنچ برای تغییرات
3. Commit کردن تغییرات
4. Push به برنچ
5. ایجاد Pull Request

## لایسنس

MIT
