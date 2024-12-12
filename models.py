from tortoise.models import Model
from pydantic import BaseModel
from tortoise import fields
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    password_hash = fields.CharField(max_length=128)
    email = fields.CharField(max_length=255, unique=True)
    phone = fields.CharField(max_length=15, unique=True)
    role = fields.CharEnumField(UserRole, default=UserRole.USER)
    balance = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    telegram_id = fields.BigIntField(null=True)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"


class Server(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='servers')
    user_id = fields.IntField()
    hetzner_id = fields.CharField(max_length=50)
    name = fields.CharField(max_length=100)
    ip = fields.CharField(max_length=45)
    os = fields.CharField(max_length=50)
    status = fields.CharField(max_length=20)
    specs = fields.JSONField()
    hourly_price = fields.DecimalField(max_digits=10, decimal_places=2)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "servers"


class Transaction(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='transactions')
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    type = fields.CharField(max_length=20)  # deposit, withdraw, server_charge
    status = fields.CharField(max_length=20)  # pending, completed, failed
    payment_id = fields.CharField(max_length=100, null=True)
    description = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "transactions"


class Ticket(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='tickets')
    user_id = fields.IntField()
    subject = fields.CharField(max_length=200)
    message = fields.TextField()  # پیام اصلی تیکت
    file_path = fields.CharField(max_length=500, null=True)  # مسیر فایل پیوست
    status = fields.CharField(max_length=20, default='open')  # open, answered, closed
    priority = fields.CharField(max_length=20, default='medium')  # low, medium, high
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "tickets"


class TicketMessage(Model):
    id = fields.IntField(pk=True)
    ticket = fields.ForeignKeyField('models.Ticket', related_name='messages')
    user = fields.ForeignKeyField('models.User', related_name='ticket_messages')
    content = fields.TextField()  # متن پیام
    file_path = fields.CharField(max_length=500, null=True)  # مسیر فایل پیوست
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "ticket_messages"


class NotificationSettings(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='notification_settings')
    server_notifications = fields.BooleanField(default=True)
    payment_notifications = fields.BooleanField(default=True)
    ticket_notifications = fields.BooleanField(default=True)
    low_balance_threshold = fields.IntField(default=10)

    class Meta:
        table = "notification_settings"


# Pydantic models for request/response
class NotificationSettingsUpdate(BaseModel):
    server_notifications: bool
    payment_notifications: bool
    ticket_notifications: bool
    low_balance_threshold: int


class UserCreate(BaseModel):
    username: str
    email: str
    phone: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
