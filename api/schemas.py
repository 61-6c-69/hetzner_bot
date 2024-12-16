from typing import Dict, Optional, List, Any, Generic, TypeVar
from pydantic import BaseModel, EmailStr, constr, Field
from datetime import datetime
from enum import Enum

from api.models import UserResponse

T = TypeVar('T')


class ServerActionType(str, Enum):
    START = "start"
    STOP = "stop"
    RESTART = "restart"


class NotificationCreate(BaseModel):
    message: str


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


class NotificationSettingsBase(BaseModel):
    server_notifications: bool
    payment_notifications: bool
    ticket_notifications: bool
    low_balance_threshold: int


class NotificationSettingsUpdate(NotificationSettingsBase):
    pass


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


class TicketStatus(str, Enum):
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    CLOSED = 'closed'
    WAITING_FOR_USER = 'waiting_for_user'
    WAITING_FOR_ADMIN = 'waiting_for_admin'


class TicketPriority(str, Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    URGENT = 'urgent'


class TicketCreate(BaseModel):
    subject: str = Field(..., min_length=3, max_length=200)
    message: str = Field(..., min_length=10)
    priority: TicketPriority = Field(default=TicketPriority.MEDIUM)


class TicketUpdate(BaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None


class TicketReply(BaseModel):
    message: str = Field(..., min_length=1)
    is_admin: bool = False


class TicketMessage(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    message: str
    file_path: Optional[str]
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TicketResponse(BaseModel):
    id: int
    user_id: int
    subject: str
    message: str
    file_path: Optional[str]
    status: TicketStatus
    priority: TicketPriority
    created_at: datetime
    updated_at: datetime
    messages: List[TicketMessage] = []
    user: Optional['UserResponse'] = None

    class Config:
        from_attributes = True


class TicketMessageResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    message: str
    file_path: Optional[str]
    is_admin: bool
    created_at: datetime
    user: Optional['UserResponse'] = None

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


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=10, ge=1, le=100)
    search: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: str = Field(default='asc', regex='^(asc|desc)$')


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int


class PaginatedUsers(PaginatedResponse[User]):
    pass


class PaginatedServers(PaginatedResponse[Server]):
    pass


class PaginatedTransactions(PaginatedResponse[Transaction]):
    pass


class PaginatedTickets(PaginatedResponse[TicketResponse]):
    pass


class PaginatedTicketMessages(PaginatedResponse[TicketMessageResponse]):
    pass
