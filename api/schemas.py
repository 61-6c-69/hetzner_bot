from typing import Dict, Optional, List, Any
from pydantic import BaseModel, EmailStr, constr
from datetime import datetime
from enum import Enum


class ServerActionType(str, Enum):
    START = "start"
    STOP = "stop"
    RESTART = "restart"


class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    SERVER_CHARGE = "server_charge"
    IP_CHANGE = "ip_change"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class ServerAction(BaseModel):
    action: ServerActionType


class PhoneVerification(BaseModel):
    phone: constr(regex=r'^(\+98|0)?9\d{9}$')  # Validate Iranian phone numbers


class OTPVerification(BaseModel):
    phone: constr(regex=r'^(\+98|0)?9\d{9}$')
    code: constr(regex=r'^\d{6}$')  # 6-digit code


class TelegramConnect(BaseModel):
    code: str  # Telegram connection verification code


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    phone: str


class UserSettingsUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    telegram_id: Optional[int] = None
    notification_settings: Optional[NotificationSettingsUpdate] = None


class User(UserBase):
    id: int
    first_name: str
    last_name: Optional[str]
    phone: str
    role: str
    balance: float
    is_active: bool
    created_at: datetime
    telegram_id: Optional[int] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: User


class TokenData(BaseModel):
    username: Optional[str] = None


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
    ip: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TicketBase(BaseModel):
    subject: str
    message: str
    priority: str = 'medium'


class TicketCreate(TicketBase):
    pass


class TicketResponse(TicketBase):
    id: int
    user_id: int
    status: str
    file_path: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TicketMessageResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    message: str
    file_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TicketReply(BaseModel):
    message: str
    file_path: Optional[str] = None


class TicketMessage(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    message: str
    file_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionBase(BaseModel):
    amount: float
    type: TransactionType
    description: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class DepositCreate(BaseModel):
    amount: float
    description: Optional[str] = None


class Transaction(TransactionBase):
    id: int
    user_id: int
    status: TransactionStatus
    created_at: datetime
    payment_id: Optional[str] = None

    class Config:
        from_attributes = True


class TransactionResponse(Transaction):
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationSettingsBase(BaseModel):
    server_notifications: bool
    payment_notifications: bool
    ticket_notifications: bool
    low_balance_threshold: int


class NotificationSettingsUpdate(NotificationSettingsBase):
    pass


class NotificationSettings(NotificationSettingsBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class Price(BaseModel):
    id: int
    type: str
    name: str
    specs: Dict[str, Any]
    hourly_price: float
    monthly_price: float
    location: str
    available: bool

    class Config:
        from_attributes = True
