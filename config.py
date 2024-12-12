from environs import Env
import os

env = Env()
env.read_env()

# Bot Configuration
BOT_TOKEN = env.str("BOT_TOKEN")
ADMIN_IDS = [
    123456789,  # نام ادمین
    987654321,  # نام ادمین دیگر
]

# Upload Configuration
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

API_URL = env.str("API_URL")

REDIS_URL = env.str("REDIS_URL")

# API Configuration
SECRET_KEY = env.str("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# CORS Configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://your-domain.com"
]

# SMS.ir Configuration
SMS_API_KEY = env.str("SMS_API_KEY")
SMS_TEMPLATE_ID = env.str("SMS_TEMPLATE_ID")

# Zarinpal Configuration
ZARINPAL_MERCHANT = env.str("ZARINPAL_MERCHANT")
ZARINPAL_CALLBACK_URL = env.str("ZARINPAL_CALLBACK_URL")

# Hetzner Configuration
HETZNER_API_TOKEN = env.str("HETZNER_API_TOKEN")

# Database
DATABASE_URL = env.str("DATABASE_URL")

# ضریب سود (20 درصد)
PROFIT_MARGIN = 1.20

# API Key برای سرویس نرخ ارز (اگر نیاز باشد)
EXCHANGE_API_KEY = env.str("EXCHANGE_API_KEY", default=None)

# Domain Configuration
DOMAIN = env.str("DOMAIN", "your-domain.com")

# Tortoise ORM Configuration
TORTOISE_ORM = {
    "connections": {
        "default": DATABASE_URL
    },
    "apps": {
        "models": {
            "models": ["database.models", "aerich.models"],
            "default_connection": "default",
        }
    },
    "use_tz": False,
    "timezone": "UTC"
}
