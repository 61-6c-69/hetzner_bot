import aiohttp
from typing import Tuple
from config import ZARINPAL_MERCHANT, ZARINPAL_CALLBACK_URL


class PaymentHandler:
    """کلاس مدیریت پرداخت‌ها"""

    @staticmethod
    async def create_payment(amount: int, description: str) -> Tuple[str, str]:
        """ایجاد درخواست پرداخت در زرین‌پال
        
        Args:
            amount: مبلغ به تومان
            description: توضیحات تراکنش
            
        Returns:
            tuple: (لینک پرداخت, کد پیگیری)
        """
        url = "https://api.zarinpal.com/pg/v4/payment/request.json"
        data = {
            "merchant_id": ZARINPAL_MERCHANT,
            "amount": amount * 10,  # تبدیل تومان به ریال
            "description": description,
            "callback_url": ZARINPAL_CALLBACK_URL,
            "metadata": {"mobile": "", "email": ""}
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                result = await response.json()

                if result["data"]["code"] == 100:
                    authority = result["data"]["authority"]
                    payment_url = f"https://www.zarinpal.com/pg/StartPay/{authority}"
                    return payment_url, authority
                else:
                    raise Exception(f"خطا در ایجاد تراکنش: {result['errors']['message']}")

    @staticmethod
    async def verify_payment(authority: str, amount: int) -> bool:
        """تایید پرداخت در زرین‌پال
        
        Args:
            authority: کد پیگیری تراکنش
            amount: مبلغ به تومان
            
        Returns:
            bool: وضعیت تراکنش
        """
        url = "https://api.zarinpal.com/pg/v4/payment/verify.json"
        data = {
            "merchant_id": ZARINPAL_MERCHANT,
            "amount": amount * 10,  # تبدیل تومان به ریال
            "authority": authority
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                result = await response.json()
                return result["data"]["code"] == 100

    @staticmethod
    def format_payment_message(amount: int, description: str, payment_url: str) -> str:
        """ایجاد پیام راهنمای پرداخت
        
        Args:
            amount: مبلغ به تومان
            description: توضیحات تراکنش
            payment_url: لینک پرداخت
            
        Returns:
            str: پیام راهنمای پرداخت
        """
        return (
            f"💰 مبلغ قابل پرداخت: {amount:,} تومان\n\n"
            "راهنمای پرداخت:\n"
            "1️⃣ روی دکمه «پرداخت» کلیک کنید\n"
            "2️⃣ در درگاه زرین‌پال پرداخت را انجام دهید\n"
            "3️⃣ پس از پرداخت موفق، به صورت خودکار به ربات برمی‌گردید\n"
            "4️⃣ پس از تایید تراکنش، موجودی شما افزایش می‌یابد\n\n"
            f"توضیحات: {description}\n"
            f"لینک پرداخت: {payment_url}"
        )


payment_handler = PaymentHandler()
