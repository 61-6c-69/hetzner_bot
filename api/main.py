from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import engine, Base
from api.routers import users, servers, transactions, tickets
from api.middleware import RateLimitMiddleware
from config import ALLOWED_ORIGINS

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

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

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
