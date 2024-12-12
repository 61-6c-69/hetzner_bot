from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, JSON, Text, DECIMAL, BigInteger, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(128))
    email = Column(String(255), unique=True, index=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    servers = relationship("Server", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    tickets = relationship("Ticket", back_populates="user")
    telegram_sessions = relationship("TelegramSession", back_populates="user")
    telegram_activities = relationship("TelegramActivity", back_populates="user")
    notification_settings = relationship("NotificationSettings", back_populates="user")

    async def get_balance(self, db) -> float:
        """محاسبه موجودی کاربر از مجموع تراکنش‌ها"""
        from sqlalchemy import func, select
        result = await db.execute(
            select(func.sum(Transaction.amount))
            .where(
                Transaction.user_id == self.id,
                Transaction.status == 'completed'
            )
        )
        total = result.scalar()
        return float(total if total else 0)

    def is_admin(self) -> bool:
        return self.is_superuser

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

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(DECIMAL(10, 2))
    description = Column(Text)
    status = Column(String(50))
    payment_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="transactions")

class IPChange(Base):
    __tablename__ = "ip_changes"

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("servers.id"))
    old_ip = Column(String(15))
    price = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    server = relationship("Server", back_populates="ip_changes")

class OTPCode(Base):
    __tablename__ = "otp_codes"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(15))
    code = Column(String(6))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_used = Column(Boolean, default=False)

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(Text)
    message = Column(Text)
    response = Column(Text, nullable=True)
    status = Column(String(20), default='open')
    file_path = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="tickets")

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
