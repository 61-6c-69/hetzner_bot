from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from utils.cache import cache_service
import logging
import json

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self):
        self.cache = cache_service
        self.default_ttl = 300  # 5 دقیقه پیش‌فرض

    async def get_or_set(
        self,
        key: str,
        fetch_func: callable,
        ttl: Optional[int] = None,
        force_refresh: bool = False
    ) -> Any:
        """دریافت داده از کش یا فراخوانی تابع در صورت نبود در کش"""
        if not force_refresh:
            cached_data = await self.cache.get(key)
            if cached_data is not None:
                return cached_data

        try:
            # دریافت داده جدید
            fresh_data = await fetch_func()
            
            # ذخیره در کش
            await self.cache.set(
                key,
                fresh_data,
                ttl=ttl or self.default_ttl
            )
            
            return fresh_data
            
        except Exception as e:
            logger.error(f"خطا در دریافت/ذخیره داده برای کلید {key}: {str(e)}")
            # برگ��داندن داده کش شده قدیمی در صورت خطا
            return await self.cache.get(key)

    async def invalidate_pattern(self, pattern: str) -> None:
        """حذف همه کلیدهای منطبق با الگو"""
        try:
            keys = await self.cache.scan_keys(f"*{pattern}*")
            for key in keys:
                await self.cache.delete(key)
        except Exception as e:
            logger.error(f"خطا در حذف کش با الگوی {pattern}: {str(e)}")

    async def get_with_version(
        self,
        key: str,
        version_key: str,
        fetch_func: callable,
        ttl: Optional[int] = None
    ) -> Any:
        """دریافت داده با کنترل نسخه"""
        cached_version = await self.cache.get(version_key)
        cached_data = await self.cache.get(key)
        
        current_version = await fetch_func.get_version()
        
        if cached_data and cached_version == current_version:
            return cached_data
            
        # دریافت و ذخیره داده جدید
        fresh_data = await fetch_func()
        await self.cache.set(key, fresh_data, ttl=ttl or self.default_ttl)
        await self.cache.set(version_key, current_version)
        
        return fresh_data

    async def batch_get_or_set(
        self,
        keys: list[str],
        fetch_func: callable,
        ttl: Optional[int] = None
    ) -> Dict[str, Any]:
        """دریافت یا ذخیره دسته‌ای داده‌ها"""
        result = {}
        missing_keys = []
        
        # بررسی کش برای همه کلیدها
        for key in keys:
            cached = await self.cache.get(key)
            if cached is not None:
                result[key] = cached
            else:
                missing_keys.append(key)
                
        if missing_keys:
            # دریافت داده‌های جدید برای کلیدهای ناموجود
            fresh_data = await fetch_func(missing_keys)
            
            # ذخیره در کش
            for key, data in fresh_data.items():
                await self.cache.set(key, data, ttl=ttl or self.default_ttl)
                result[key] = data
                
        return result

cache_manager = CacheManager() 