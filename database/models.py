from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum, JSON, \
    BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from database.database import Base


class UserRole(str, PyEnum):
    USER = "user"
    ADMIN = "admin"


class TransactionType(str, PyEnum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    SERVER_CHARGE = "server_charge"
    IP_CHANGE = "ip_change"


class TransactionStatus(str, PyEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(255), unique=True)
    phone = Column(String(15), unique=True)
    first_name = Column(String(50))
    last_name = Column(String(50), nullable=True)
    password_hash = Column(String(128))
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    balance = Column(Float, default=0)
    telegram_id = Column(Integer, unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    tickets = relationship("Ticket", back_populates="user")
    messages = relationship("TicketMessage", back_populates="user")
    transactions = relationship("Transaction", foreign_keys="[Transaction.user_id]", back_populates="user")
    approved_transactions = relationship("Transaction", foreign_keys="[Transaction.approved_by]",
                                         back_populates="approver")


class TicketPriority(str, PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TicketStatus(str, PyEnum):
    OPEN = "open"
    WAITING_FOR_ADMIN = "waiting_for_admin"
    WAITING_FOR_USER = "waiting_for_user"
    CLOSED = "closed"


class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(50))
    hetzner_id = Column(String(50))
    type = Column(String(50))
    hourly_price = Column(Integer)
    monthly_price = Column(Integer)
    location = Column(String(50))
    ip = Column(String(50))
    os = Column(String(50))
    status = Column(String(20))
    specs = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_charge_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="servers")
    ip_changes = relationship("IPChange", back_populates="server")
    logs = relationship("ServerLog", back_populates="server")
    stats = relationship("ServerStats", back_populates="server")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String(200))
    message = Column(Text)
    file_path = Column(String(500), nullable=True)
    status = Column(SQLEnum(TicketStatus), default=TicketStatus.OPEN)
    priority = Column(SQLEnum(TicketPriority), default=TicketPriority.MEDIUM)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="tickets")
    messages = relationship("TicketMessage", back_populates="ticket")


class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    file_path = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    ticket = relationship("Ticket", back_populates="messages")
    user = relationship("User", back_populates="messages")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    type = Column(SQLEnum(TransactionType))
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)
    payment_id = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", foreign_keys=[user_id], back_populates="transactions")
    approver = relationship("User", foreign_keys=[approved_by])


class IPChange(Base):
    __tablename__ = "ip_changes"

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("servers.id"))
    old_ip = Column(String(15))
    price = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    server = relationship("Server", back_populates="ip_changes")


class ServerLog(Base):
    __tablename__ = "server_logs"

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("servers.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    level = Column(String(20))
    message = Column(Text)

    # Relationships
    server = relationship("Server", back_populates="logs")


class ServerStats(Base):
    __tablename__ = "server_stats"

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("servers.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    disk_usage = Column(Float)
    network_in = Column(Float)
    network_out = Column(Float)

    # Relationships
    server = relationship("Server", back_populates="stats")


class TelegramSession(Base):
    __tablename__ = "telegram_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    telegram_id = Column(BigInteger)
    device_info = Column(Text, nullable=True)
    last_activity = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="telegram_sessions")


class TelegramActivity(Base):
    __tablename__ = "telegram_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    command = Column(String(50))
    executed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="telegram_activities")


class NotificationSettings(Base):
    __tablename__ = "notification_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    server_notifications = Column(Boolean, default=True)
    payment_notifications = Column(Boolean, default=True)
    ticket_notifications = Column(Boolean, default=True)
    low_balance_threshold = Column(Integer, default=50000)

    # Relationships
    user = relationship("User", back_populates="notification_settings")
