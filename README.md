# پنل مدیریت سرورهای Hetzner

پنل مدیریت سرورهای Hetzner با قابلیت اتصال به تلگرام و سیستم اعلان‌رسانی هوشمند

## امکانات

### وب‌سایت
- ثبت‌نام و احراز هویت با شماره موبایل
- خرید سرور با انتخاب نوع، لوکیشن و سیستم‌عامل
- مدیریت سرورها (روشن/خاموش کردن، تغییر IP)
- مشاهده آمار و مانیتورینگ سرور
- سیستم تیکتینگ و پشتیبانی
- مدیریت موجودی و تراکنش‌ها
- درگاه پرداخت زرین‌پال
- اتصال به تلگرام و دریافت نوتیفیکیشن

### ربات تلگرام
- اتصال به حساب کاربری از طریق پنل
- مشاهده وضعیت سرورها با دستور /status
- مشاهده موجودی با دستور /balance
- دریافت نوتیفیکیشن‌های سیستم

## تکنولوژی‌ها
- Backend: FastAPI
- Frontend: Next.js + Tailwind CSS
- Database: PostgreSQL
- Cache: Redis
- Bot: aiogram
- SMS: SMS.ir
- Payment: Zarinpal

## پیش‌نیازها
- Docker و Docker Compose
- Node.js نسخه 18 یا بالاتر
- Python 3.9 یا بالاتر
- PostgreSQL
- Redis

## نصب و راه‌اندازی

### 1. کلون کردن پروژه
git clone https://github.com/your-username/hetzner-panel.git
cd hetzner-panel

### 2. تنظیم متغیرهای محیطی

فایل .env را در پوشه اصلی پروژه ایجاد کنید:

    # Database
    POSTGRES_DB=hetzner_panel
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=your_password

    # Redis
    REDIS_HOST=redis
    REDIS_PORT=6379

    # API
    JWT_SECRET=your_jwt_secret
    HETZNER_API_TOKEN=your_hetzner_token

    # SMS
    SMS_API_KEY=your_sms_api_key

    # Payment
    ZARINPAL_MERCHANT=your_merchant_id

    # Telegram Bot
    TELEGRAM_BOT_TOKEN=your_bot_token

فایل .env.local را در پوشه frontend ایجاد کنید:

    NEXT_PUBLIC_API_URL=http://localhost:8000
    NEXT_PUBLIC_SOCKET_URL=ws://localhost:8000/ws

### 3. نصب پکیج‌های مورد نیاز

در پوشه frontend:
    cd frontend
    npm install

### 4. اجرای migration ها
    docker-compose run api python -m aerich upgrade

### 5. اجرای پروژه با Docker
    docker-compose up -d

پروژه روی پورت‌های زیر در دسترس خواهد بود:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## ساختار پروژه

    .
    ├── api/                    # بک‌اند FastAPI
    │   ├── routers/           # API endpoints
    │   └── utils/             # توابع کمکی
    ├── frontend/              # فرانت‌اند Next.js
    │   ├── components/        # کامپوننت‌های React
    │   ├── pages/            # صفحات
    │   └── contexts/         # Context های React
    ├── bot/                   # ربات تلگرام
    │   ├── handlers/         # هندلرهای دستورات
    │   └── middlewares/      # میدلورهای ربات
    ├── database/             # مدل‌های دیتابیس
    │   └── models.py
    └── docker-compose.yml

## توسعه

### اجرای تست‌ها
    # API tests
    docker-compose run api pytest

    # Frontend tests
    cd frontend
    npm test

### اضافه کردن migration جدید
    docker-compose run api python -m aerich migrate
