import logging
import requests
from services.abstract_service import AbstractService


class HetznerService(AbstractService):
    def __init__(self):
        super().__init__()

    # گرفتن هزینه ساعتی سرور بر اساس RAM، CPU و Disk از API هتزنر
    def get_hourly_cost(self, ram, cpu, disk):

        try:
            response = requests.get(self.url, headers=self.headers)
            if response.status_code == 200:
                pricing_data = response.json()

                # محاسبه هزینه‌های RAM، CPU و Disk
                ram_cost = self._get_ram_cost(pricing_data, ram)
                cpu_cost = self._get_cpu_cost(pricing_data, cpu)
                disk_cost = self._get_disk_cost(pricing_data, disk)

                # جمع هزینه‌ها
                total_hourly_cost = ram_cost + cpu_cost + disk_cost
                return total_hourly_cost
            else:
                raise Exception(f"Error fetching pricing data: {response.status_code}")
        except Exception as e:
            print(f"خطا در دریافت هزینه ساعتی از API: {e}")
            return None

    # استخراج هزینه RAM از داده‌های API
    def _get_ram_cost(self, pricing_data, ram):
        ram_pricing = pricing_data["pricing"]["server_types"]
        for ram_option in ram_pricing:
            if ram_option["name"] == ram:
                return ram_option["prices"]["hourly"]["net"]
        return 0

    # استخراج هزینه CPU از داده‌های API
    def _get_cpu_cost(self, pricing_data, cpu):
        cpu_pricing = pricing_data["pricing"]["server_types"]
        for cpu_option in cpu_pricing:
            if cpu_option["name"] == cpu:
                return cpu_option["prices"]["hourly"]["net"]
        return 0

    # استخراج هزینه Disk از داده‌های API
    def _get_disk_cost(self, pricing_data, disk):
        disk_pricing = pricing_data["pricing"]["server_types"]
        for disk_option in disk_pricing:
            if disk_option["name"] == disk:
                return disk_option["prices"]["hourly"]["net"]
        return 0

    def get_countries(self):
        """دریافت لیست کشورها از API هتزنر"""
        # فرض کنیم که لیست کشورها از یک endpoint مشخص دریافت می‌شود
        try:
            response = requests.get(f'{self.url}/locations', headers=self.headers)
            response.raise_for_status()
            countries = response.json()['locations']
            return [location['country'] for location in countries]
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching countries from Hetzner: {e}")
            return []

    def get_services(self):
        """دریافت لیست سرویس‌ها (سرورها) از API هتزنر"""
        try:
            response = requests.get(f'{self.url}/servers', headers=self.headers)
            response.raise_for_status()
            return response.json()['servers']
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching services from Hetzner: {e}")
            return []

    def get_operating_systems(self):
        """دریافت لیست سیستم‌عامل‌های موجود از API هتزنر"""
        try:
            response = requests.get(f'{self.url}/images', headers=self.headers)
            response.raise_for_status()
            return response.json()['images']
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching operating systems from Hetzner: {e}")
            return []

    def get_apps(self):
        """دریافت لیست اپلیکیشن‌های موجود برای نصب از API هتزنر"""
        # فرضی که اپ‌ها هم از API مشابه سیستم‌عامل‌ها دریافت می‌شوند
        try:
            response = requests.get(f'{self.url}/apps', headers=self.headers)
            response.raise_for_status()
            return response.json()['apps']
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching apps from Hetzner: {e}")
            return []

    def reinstall_os(self, server_id, os_id):
        """نصب مجدد سیستم‌عامل بر روی سرور مشخص"""
        try:
            data = {"os_id": os_id}
            response = requests.post(f'{self.url}/servers/{server_id}/actions/reinstall', headers=self.headers,
                                     json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error reinstalling OS on server {server_id}: {e}")
            return None

    def shutdown_server(self, server_id):
        """خاموش کردن سرور"""
        try:
            response = requests.post(f'{self.url}/servers/{server_id}/actions/shutdown', headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error shutting down server {server_id}: {e}")
            return None

    def reboot_server(self, server_id):
        """ریستارت کردن سرور"""
        try:
            response = requests.post(f'{self.url}/servers/{server_id}/actions/reboot', headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error rebooting server {server_id}: {e}")
            return None

    def delete_server(self, server_id):
        """حذف سرور"""
        try:
            response = requests.delete(f'{self.url}/servers/{server_id}', headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error deleting server {server_id}: {e}")
            return None
