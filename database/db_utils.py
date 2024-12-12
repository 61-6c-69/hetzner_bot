from models import User, Server, Transaction


# گرفتن یا ایجاد کاربر براساس شناسه تلگرام
def get_or_create_user(telegram_id, username):
    session = get_()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id, username=username)
        session.add(user)
        session.commit()
    return user


# اضافه کردن سرور جدید
def add_server(user_id, server_type, country, os, monthly_cost):
    session = SessionLocal()
    server = Server(owner_id=user_id, server_type=server_type, country=country, os=os, monthly_cost=monthly_cost)
    session.add(server)
    session.commit()
    return server


# به‌روزرسانی موجودی کاربر
def update_user_balance(user_id, amount):
    session = SessionLocal()
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        user.balance += amount
        session.commit()


# اضافه کردن تراکنش مالی
def add_transaction(user_id, amount):
    session = SessionLocal()
    transaction = Transaction(user_id=user_id, amount=amount)
    session.add(transaction)
    session.commit()


# گرفتن سرورهای کاربر
def get_user_servers(user_id):
    session = SessionLocal()
    servers = session.query(Server).filter_by(owner_id=user_id).all()
    return servers


# گرفتن موجودی کاربر
def get_user_balance(user_id):
    session = SessionLocal()
    user = session.query(User).filter_by(id=user_id).first()
    return user.balance if user else 0.0
