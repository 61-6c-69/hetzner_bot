import aiohttp
from config import ZARINPAL_MERCHANT, ZARINPAL_CALLBACK_URL
from typing import Dict, Optional


class PaymentHandler:
    def __init__(self):
        self.merchant = ZARINPAL_MERCHANT
        self.callback_url = ZARINPAL_CALLBACK_URL
        self.payment_url = "https://api.zarinpal.com/pg/v4/payment"
        self.verify_url = "https://api.zarinpal.com/pg/v4/payment/verify.json"

    async def create_payment(
        self,
        amount: float,
        description: str = "شارژ حساب کاربری"
    ) -> Dict[str, str]:
        """Create a new payment request"""
        data = {
            "merchant_id": self.merchant,
            "amount": int(amount * 10),  # Convert to Rial
            "description": description,
            "callback_url": self.callback_url
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.payment_url, json=data) as response:
                result = await response.json()

                if response.status == 200 and result.get("data", {}).get("code") == 100:
                    authority = result["data"]["authority"]
                    return {
                        "payment_id": authority,
                        "payment_url": f"https://www.zarinpal.com/pg/StartPay/{authority}"
                    }
                else:
                    raise Exception(f"Payment creation failed: {result.get('errors')}")

    async def verify_payment(
        self,
        authority: str,
        amount: float
    ) -> bool:
        """Verify a payment"""
        data = {
            "merchant_id": self.merchant,
            "authority": authority,
            "amount": int(amount * 10)  # Convert to Rial
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.verify_url, json=data) as response:
                result = await response.json()

                if response.status == 200:
                    if result.get("data", {}).get("code") == 100:
                        return True
                    elif result.get("data", {}).get("code") == 101:
                        return True  # Payment was verified before

                return False


payment_handler = PaymentHandler()
