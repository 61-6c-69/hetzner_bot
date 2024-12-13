from typing import TypeVar, Generic, Type, Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database.models import Base
from utils.cache import cache_service
from datetime import timedelta

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
        self.cache_ttl = timedelta(minutes=30)

    def _get_cache_key(self, key: str) -> str:
        """Generate cache key for the model"""
        return f"{self.model.__name__}:{key}"

    async def _get_from_cache(self, cache_key: str) -> Optional[ModelType]:
        """Get item from cache"""
        return await cache_service.get(cache_key)

    async def _set_cache(self, cache_key: str, value: ModelType) -> None:
        """Set item in cache"""
        await cache_service.set(cache_key, value, int(self.cache_ttl.total_seconds()))

    async def _clear_cache(self, cache_key: str) -> None:
        """Clear item from cache"""
        await cache_service.delete(cache_key)

    async def get(self, id: int) -> Optional[ModelType]:
        """Get item by ID with caching"""
        cache_key = self._get_cache_key(str(id))
        
        # Try to get from cache first
        cached_item = await self._get_from_cache(cache_key)
        if cached_item:
            return cached_item

        # If not in cache, get from database
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        item = result.scalar_one_or_none()

        # Cache the result if found
        if item:
            await self._set_cache(cache_key, item)

        return item

    async def get_all(
        self,
        page: int = 1,
        per_page: int = 10,
        cache_key: Optional[str] = None
    ) -> Tuple[List[ModelType], int]:
        """Get all items with pagination and optional caching"""
        if cache_key:
            full_cache_key = self._get_cache_key(f"all:{cache_key}:{page}:{per_page}")
            cached_result = await self._get_from_cache(full_cache_key)
            if cached_result:
                return cached_result

        # Get total count
        count_query = select(func.count()).select_from(self.model)
        total = await self.db.scalar(count_query)

        # Get paginated items
        query = select(self.model).offset((page - 1) * per_page).limit(per_page)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        # Cache the result if cache_key provided
        if cache_key:
            full_cache_key = self._get_cache_key(f"all:{cache_key}:{page}:{per_page}")
            await self._set_cache(full_cache_key, (items, total))

        return items, total

    async def create(self, **kwargs) -> ModelType:
        """Create a new item"""
        item = self.model(**kwargs)
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)

        # Cache the new item
        cache_key = self._get_cache_key(str(item.id))
        await self._set_cache(cache_key, item)

        return item

    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Update an item"""
        item = await self.get(id)
        if item:
            for key, value in kwargs.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            await self.db.commit()
            await self.db.refresh(item)

            # Update cache
            cache_key = self._get_cache_key(str(id))
            await self._set_cache(cache_key, item)

        return item

    async def delete(self, id: int) -> bool:
        """Delete an item"""
        item = await self.get(id)
        if item:
            await self.db.delete(item)
            await self.db.commit()

            # Clear cache
            cache_key = self._get_cache_key(str(id))
            await self._clear_cache(cache_key)

            return True
        return False

    async def exists(self, id: int) -> bool:
        """Check if item exists"""
        cache_key = self._get_cache_key(str(id))
        
        # Check cache first
        if await self._get_from_cache(cache_key):
            return True

        # If not in cache, check database
        result = await self.db.execute(
            select(func.count())
            .select_from(self.model)
            .where(self.model.id == id)
        )
        return result.scalar_one() > 0
