from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, create_engine, DECIMAL
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

Base = declarative_base()


# مدل کاربر
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(String(50), unique=True, nullable=False)
    username = Column(String(150), nullable=False)
    balance = Column(DECIMAL(10, 2), default=0.00)
    servers = relationship("Server", back_populates="owner")


# مدل سرور
class Server(Base):
    __tablename__ = 'servers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_type = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    os = Column(String(50), nullable=True)
    status = Column(String(20), default="active")
    monthly_cost = Column(DECIMAL(10, 2), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="servers")


# مدل تراکنش مالی
class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(DECIMAL(10, 2), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="transactions")


# ایجاد و تنظیم دیتابیس
DATABASE_URL = "mysql://username:password@localhost:3306/your_db_name"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
