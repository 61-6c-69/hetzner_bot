import requests
from celery import shared_task

from database.db_utils import get_user_servers, update_user_balance


# محاسبه هزینه‌ها
def get_exchange_rate():
    response = requests.get("https://api.exchangerate-api.com/v4/latest/EUR")
    data = response.json()
    return data['rates']['IRR'] + 20000


# وظیفه کسر هزینه سرور از موجودی کاربر
@shared_task
def charge_user_for_servers(user_id):
    servers = get_user_servers(user_id)
    total_cost = 0
    exchange_rate = get_exchange_rate()

    for server in servers:
        monthly_cost_euro = server.monthly_cost
        monthly_cost_rial = monthly_cost_euro * exchange_rate
        total_cost += monthly_cost_rial

    update_user_balance(user_id, -total_cost)  # کسر از موجودی
