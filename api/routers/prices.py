from utils.price_cache import get_cached_prices
from fastapi import APIRouter

router = APIRouter()


@router.get("/prices")
async def get_prices():
    """دریافت لیست قیمت‌ها"""
    return await get_cached_prices()
