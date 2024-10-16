from abc import ABC, abstractmethod


class AbstractService(ABC):
    def __init__(self):
        self.url = ""
        self.cookies = {}
        self.params = {}
        self.headers = {}

    @abstractmethod
    def get_countries(self):
        """لیست کشورهایی که سرویس در آنها ارائه می‌شود"""
        pass

    @abstractmethod
    def get_services(self):
        """لیست سرویس‌های موجود در هر کشور"""
        pass

    @abstractmethod
    def get_operating_systems(self):
        """لیست سیستم‌عامل‌های موجود برای نصب روی سرورها"""
        pass

    @abstractmethod
    def get_apps(self):
        """لیست اپلیکیشن‌های موجود برای نصب روی سرورها"""
        pass

    @abstractmethod
    def reinstall_os(self, server_id, os_id):
        """نصب مجدد سیستم‌عامل برای یک سرور خاص"""
        pass

    @abstractmethod
    def shutdown_server(self, server_id):
        """خاموش کردن سرور"""
        pass

    @abstractmethod
    def reboot_server(self, server_id):
        """ریستارت کردن سرور"""
        pass

    @abstractmethod
    def delete_server(self, server_id):
        """حذف سرور"""
        pass

    def set_url(self, url):
        self.url = url

    def set_headers(self, headers):
        self.headers = headers

    def set_params(self, params):
        self.params = params

    def set_cookies(self, cookies):
        self.cookies = cookies if cookies else {}
