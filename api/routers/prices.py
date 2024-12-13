from repositories.price_repository import PriceRepository
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from api import schemas

router = APIRouter()


@router.get("/", response_model=list[schemas.Price])
async def get_prices(
        db: AsyncSession = Depends(get_db)
):
    """Get all server prices"""
    repo = PriceRepository(db)
    return await repo.get_server_price()


@router.get("/server/{server_type}", response_model=schemas.Price)
async def get_server_price(
        server_type: str,
        db: AsyncSession = Depends(get_db)
):
    """Get price for specific server type"""
    repo = PriceRepository(db)
    price = await repo.get_server_price(server_type)
    if not price:
        raise HTTPException(status_code=404, detail="Price not found")
    return price


@router.get("/server/{server_id}/cost")
async def get_server_cost(
        server_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Get current cost for a specific server"""
    repo = PriceRepository(db)
    costs = await repo.calculate_server_cost(server_id)
    if not costs:
        raise HTTPException(status_code=404, detail="Server not found")
    return costs
