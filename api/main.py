from routers import auth, server, payment, support, admin, user
from tortoise.contrib.fastapi import register_tortoise
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from config import ALLOWED_ORIGINS, TORTOISE_ORM
from utils.auth import get_current_user
from fastapi import FastAPI, Depends
from database.models import User
from models import UserResponse

app = FastAPI(title="Hetzner Server Management API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Tortoise ORM
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/verify-otp")

# Include routers
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    server.router,
    prefix="/servers",
    tags=["Servers"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    payment.router,
    prefix="/payments",
    tags=["Payments"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    support.router,
    prefix="/support",
    tags=["Support"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    user.router,
    prefix="/user",
    tags=["User"],
    dependencies=[Depends(get_current_user)]
)


@app.get("/")
async def root():
    return {"message": "Hetzner Server Management API"}


@app.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
