from dotenv import load_dotenv
import os

from enums.ServiceEnum import ServiceEnum
from services.Hetzner.hetzner_service import HetznerService

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HETZNER_API_TOKEN = os.getenv("HETZNER_API_TOKEN")
ZIBAL_API_KEY = os.getenv("ZIBAL_API_KEY")
ZARINPAL_API_KEY = os.getenv("ZARINPAL_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
PROFIT_MARGIN = float(os.getenv("PROFIT_MARGIN", 1.2))
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")


SERVICES_CONFIG = {

    # Map Services Classes (For Example: Hetzner, AWS, etc.)
    'map': {
        ServiceEnum.HETZNER: HetznerService(),
        # می‌توانید سرویس‌های دیگری هم اضافه کنید
    },

    # External Service Config
    'config': {
        'hetzner': {
            'base_url': "https://api.hetzner.cloud/v1",
            'auth_token': os.getenv('HETZNER_API_TOKEN'),  # توکن API هتزنر از فایل env
            'profit_margin': 1.15  # ضریب سود برای این سرویس
        },
        # اطلاعات دیگر سرویس‌ها نیز به همین صورت اضافه می‌شوند
    }
}
