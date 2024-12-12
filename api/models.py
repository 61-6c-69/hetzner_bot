from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class UserResponse(BaseModel):
    id: int
    phone: str
    telegram_id: int
    first_name: str
    last_name: Optional[str]
    username: Optional[str]
    joined_date: datetime


class ServerCreate(BaseModel):
    name: str
    type: str  # نوع سرور در هتزنر (مثل cx11, cx21, etc.)
    location: str  # موقعیت سرور (مثل fsn1, nbg1, etc.)
    os: str  # سیستم عامل (مثل ubuntu-20.04, debian-11, etc.)


class ServerResponse(BaseModel):
    id: int
    name: str
    ip: str
    status: str
    os: str
    created_at: datetime


class TransactionResponse(BaseModel):
    id: int
    amount: float
    description: str
    status: str
    created_at: datetime


class PhoneVerification(BaseModel):
    phone: str


class OTPVerification(BaseModel):
    phone: str
    code: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class TicketResponse(BaseModel):
    id: int
    user_id: int
    subject: str
    message: str
    file_path: Optional[str]
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime


class ServerStatsResponse(BaseModel):
    cpu: List[dict]
    memory: List[dict]
    disk: List[dict]
    network: List[dict]


class LogResponse(BaseModel):
    id: int
    timestamp: datetime
    level: str
    message: str


class Transaction(BaseModel):
    id: int
    user_id: int
    amount: float
    type: str
    status: str
    payment_id: Optional[str]
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DepositCreate(BaseModel):
    amount: float
    description: Optional[str] = None
