import os

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [
    123456789,  # نام ادمین
    987654321,  # نام ادمین دیگر
]

# Upload Configuration
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

API_URL = os.getenv("API_URL")

REDIS_URL = os.getenv("REDIS_URL")

# API Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# CORS Configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://your-domain.com"
]

# SMS.ir Configuration
SMS_API_KEY = os.getenv("SMS_API_KEY")
SMS_TEMPLATE_ID = os.getenv("SMS_TEMPLATE_ID")

# Zarinpal Configuration
ZARINPAL_MERCHANT = os.getenv("ZARINPAL_MERCHANT")
ZARINPAL_CALLBACK_URL = os.getenv("ZARINPAL_CALLBACK_URL")

# Hetzner Configuration
HETZNER_API_TOKEN = os.getenv("HETZNER_API_TOKEN")

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# ضریب سود (20 درصد)
PROFIT_MARGIN = 1.20

# API Key برای سرویس نرخ ارز (اگر نیاز باشد)
EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY", default=None)

# Domain Configuration
DOMAIN = os.getenv("DOMAIN", "your-domain.com")

#SUPPORT_CHAT_ID
SUPPORT_CHAT_ID = os.getenv("SUPPORT_CHAT_ID")
