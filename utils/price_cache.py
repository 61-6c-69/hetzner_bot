from redis import Redis
import json
from database.models import Server
from config import REDIS_URL

redis_client = Redis.from_url(REDIS_URL)
CACHE_KEY = "server_prices"
CACHE_DURATION = 60 * 60 * 24  # 24 ساعت


async def get_cached_prices():
    """دریافت قیمت‌ها از کش"""
    cached = redis_client.get(CACHE_KEY)
    if cached:
        return json.loads(cached)

    # اگر در کش نبود، از دیتابیس بخون و در کش ذخیره کن
    prices = await update_price_cache()
    return prices


async def update_price_cache():
    """به‌روزرسانی کش قیمت‌ها"""
    # دریافت آخرین قیمت‌ها از دیتابیس
    server_prices = await Server.all().distinct().values(
        'type',
        'hourly_price'
    )

    # تبدیل به دیکشنری برای دسترسی راحت‌تر
    price_map = {}
    for server in server_prices:
        price_map[server['type']] = server['hourly_price']

    prices = {
        'basic': {
            'name': 'پلن اقتصادی',
            'specs': '1 Core, 2GB RAM',
            'hourly': price_map.get('cx11', 300),  # اگر در دیتابیس نبود، مقدار پیش‌فرض
            'daily': price_map.get('cx11', 300) * 24,
            'resources': {
                'cpu': 1,
                'ram': 2,
                'disk': 20
            }
        },
        'pro': {
            'name': 'پلن حرفه‌ای',
            'specs': '2 Cores, 4GB RAM',
            'hourly': price_map.get('cx21', 600),
            'daily': price_map.get('cx21', 600) * 24,
            'resources': {
                'cpu': 2,
                'ram': 4,
                'disk': 40
            }
        },
        'enterprise': {
            'name': 'پلن سازمانی',
            'specs': '4 Cores, 8GB RAM',
            'hourly': price_map.get('cx31', 1000),
            'daily': price_map.get('cx31', 1000) * 24,
            'resources': {
                'cpu': 4,
                'ram': 8,
                'disk': 80
            }
        }
    }

    # ذخیره در Redis
    redis_client.setex(
        CACHE_KEY,
        CACHE_DURATION,
        json.dumps(prices)
    )

    return prices
