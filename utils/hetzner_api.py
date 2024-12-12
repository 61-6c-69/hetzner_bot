import aiohttp
import logging
from config import HETZNER_API_TOKEN, PROFIT_MARGIN


class HetznerAPI:
    def __init__(self):
        self.base_url = "https://api.hetzner.cloud/v1"
        self.headers = {
            "Authorization": f"Bearer {HETZNER_API_TOKEN}",
            "Content-Type": "application/json"
        }

    async def _make_request(self, method: str, endpoint: str, **kwargs):
        """ارسال درخواست به API هتزنر"""
        url = f"{self.base_url}/{endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=self.headers, **kwargs) as response:
                if response.status >= 400:
                    error_data = await response.json()
                    logging.error(f"Hetzner API error: {error_data}")
                    raise Exception(f"Hetzner API error: {error_data.get('error', {}).get('message')}")
                return await response.json()

    async def create_server(self, type: str, location: str, os: str):
        """ایجاد سرور جدید"""
        data = {
            "server_type": type,
            "location": location,
            "image": os
        }
        return await self._make_request("POST", "servers", json=data)

    async def power_on(self, server_id: str):
        """روشن کردن سرور"""
        return await self._make_request("POST", f"servers/{server_id}/actions/poweron")

    async def power_off(self, server_id: str):
        """خاموش کردن سرور"""
        return await self._make_request("POST", f"servers/{server_id}/actions/poweroff")

    async def get_server_metrics(self, server_id: str) -> dict:
        """دریافت آمار سرور"""
        response = await self._make_request("GET", f"servers/{server_id}/metrics")

        metrics = response['metrics']
        return {
            'cpu': metrics['cpu']['usage'],
            'memory': metrics['memory']['used'] / metrics['memory']['total'] * 100,
            'disk': metrics['disk']['used'] / metrics['disk']['total'] * 100,
            'network_in': metrics['network']['in'],
            'network_out': metrics['network']['out']
        }

    async def get_prices(self) -> list:
        """دریافت لیست قیمت‌ها"""
        response = await self._make_request("GET", "pricing")
        return response['pricing']['server_types']

    async def calculate_price(self, server_type: str) -> float:
        """محاسبه قیمت سرور با احتساب سود"""
        prices = await self.get_prices()
        server_price = next(
            (p['prices']['hourly']['gross'] for p in prices if p['id'] == server_type),
            None
        )
        if not server_price:
            raise Exception(f"Server type {server_type} not found")

        # تبدیل یورو به تومان و اعمال ضریب سود
        eur_to_irr = 50000  # نرخ تبدیل یورو به تومان
        return float(server_price) * eur_to_irr * PROFIT_MARGIN

    async def get_server_type(self, type_id: str) -> dict:
        """دریافت اطلاعات نوع سرور"""
        response = await self._make_request("GET", f"server_types/{type_id}")
        return response['server_type']

    async def get_server_info(self, server_id: str) -> dict:
        """دریافت اطلاعات سرور"""
        response = await self._make_request("GET", f"servers/{server_id}")
        return response['server']

    async def change_ip(self, server_id: str) -> dict:
        """تغییر IP سرور"""
        return await self._make_request("POST", f"servers/{server_id}/actions/change_ip")

    async def get_ip_change_price(self) -> float:
        """دریافت هزینه تغییر IP"""
        response = await self._make_request("GET", "pricing")
        return float(response['pricing']['floating_ip']['monthly']['gross'])


hetzner = HetznerAPI()
