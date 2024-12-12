from typing import Optional, Dict
from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ServerBase(BaseModel):
    name: str
    type: str
    location: str
    os: str


class ServerCreate(ServerBase):
    pass


class Server(ServerBase):
    id: int
    user_id: int
    hetzner_id: str
    hourly_price: int
    monthly_price: int
    ip: str
    status: str
    specs: Dict
    created_at: datetime

    class Config:
        from_attributes = True
