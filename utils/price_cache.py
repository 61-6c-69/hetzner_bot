from config import REDIS_URL
from redis import Redis
import json
from utils.hetzner_api import hetzner
from repositories.price_repository import PriceRepository
from database.database import get_db

redis_client = Redis()
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
    price_repository = PriceRepository()
    prices = price_repository.get_all_prices()

    if not prices:
        prices = get_cached_prices()

    # ذخیره در Redis
    redis_client.setex(
        CACHE_KEY,
        CACHE_DURATION,
        json.dumps(prices)
    )

    return prices
