import aiohttp
import logging
from config import SMS_API_KEY, SMS_TEMPLATE_ID

logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        self.api_key = SMS_API_KEY
        self.template_id = SMS_TEMPLATE_ID
        self.base_url = "https://api.sms.ir/v1"
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def send_otp(self, phone: str, code: str) -> bool:
        """ارسال کد تایید"""
        url = f"{self.base_url}/send/verify"
        payload = {
            "mobile": phone,
            "templateId": self.template_id,
            "parameters": [
                {
                    "name": "Code",
                    "value": code
                }
            ]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        return True
                    else:
                        error_data = await response.json()
                        logger.error(f"SMS.ir API error: {error_data}")
                        return False
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False

sms_service = SMSService() 