from sqlalchemy.ext.asyncio import AsyncSession
from utils.cache import cache_service
from typing import Optional, Tuple
from fastapi import HTTPException
from database.models import User
from sqlalchemy import select
import random
import string


class VerificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.code_length = 6
        self.code_prefix = "verify:"

    def _generate_code(self) -> str:
        """Generate a random verification code"""
        return ''.join(random.choices(string.digits, k=self.code_length))

    def _get_cache_key(self, phone: str) -> str:
        """Get cache key for a phone number"""
        return f"{self.code_prefix}{phone}"

    async def create_code(self, phone: str) -> str:
        """Create and cache a new verification code"""
        # Check if user exists
        result = await self.db.execute(
            select(User).where(User.phone == phone)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Generate and cache code
        code = self._generate_code()
        cache_key = self._get_cache_key(phone)

        await cache_service.set(cache_key, {
            "code": code,
            "user_id": user.id
        })

        return code

    async def verify_code(self, phone: str, code: str) -> Tuple[bool, Optional[int]]:
        """Verify a code and return (is_valid, user_id)"""
        cache_key = self._get_cache_key(phone)

        # Check attempts
        attempts = await cache_service.get_attempts(cache_key)
        if attempts >= cache_service.max_attempts:
            await cache_service.delete(cache_key)
            raise HTTPException(
                status_code=400,
                detail="Too many failed attempts. Please request a new code."
            )

        # Get cached data
        cached_data = await cache_service.get(cache_key)
        if not cached_data:
            raise HTTPException(
                status_code=400,
                detail="Code expired or not found"
            )

        # Verify code
        if cached_data["code"] != code:
            attempts = await cache_service.increment_attempts(cache_key)
            if attempts >= cache_service.max_attempts:
                await cache_service.delete(cache_key)
            raise HTTPException(
                status_code=400,
                detail=f"Invalid code. {cache_service.max_attempts - attempts} attempts remaining"
            )

        # Code is valid
        await cache_service.delete(cache_key)
        await cache_service.clear_attempts(cache_key)
        return True, cached_data["user_id"]

    async def get_user_by_phone(self, phone: str) -> Optional[User]:
        """Get user by phone number"""
        result = await self.db.execute(
            select(User).where(User.phone == phone)
        )
        return result.scalar_one_or_none()
