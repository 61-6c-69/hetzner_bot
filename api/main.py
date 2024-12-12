from fastapi import FastAPI

from database.database import engine, Base
from api.routers import users, servers, transactions, tickets

app = FastAPI()


# Initialize database
@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Include routers
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(servers.router, prefix="/servers", tags=["servers"])
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
app.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
