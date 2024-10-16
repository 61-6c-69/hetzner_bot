import config
from services.Hetzner.hetzner_service import HetznerService


class FactoryService:
    def __init__(self):
        self.services_map = self.load_services()

    def load_services(self):
        services_map = {}
        for service_key in config.SERVICES_CONFIG['map']:
            service_instance = config.SERVICES_CONFIG['map'][service_key]
            if service_instance:
                service_config = config.SERVICES_CONFIG['config'].get(service_key)
                service_instance.set_url(service_config['base_url'])
                service_instance.set_headers({'auth_token': service_config['auth_token']})
                service_instance.set_params(service_config.get('params', {}))
                service_instance.set_cookies(service_config.get('cookies', {}))
                services_map[service_key] = service_instance
        return services_map

    def create_service_instance(self, service_key):
        if service_key == 'hetzner':
            return HetznerService()
        # سایر سرویس‌ها را اینجا اضافه کنید
        return None

    def get_countries(self, service_key):
        service = self.services_map.get(service_key)
        if service:
            return service.get_countries()
        return []

    def get_hourly_cost(self, provider, ram, cpu, disk):
        service = self.services_map.get(provider)
        if service:
            return service.get_hourly_cost(ram, cpu, disk)
        else:
            raise ValueError(f"Service provider {provider} not found")

    def get_services(self, service_key):
        service = self.services_map.get(service_key)
        if service:
            return service.get_services()
        return []

    def get_operating_systems(self, service_key):
        service = self.services_map.get(service_key)
        if service:
            return service.get_operating_systems()
        return []

    def get_apps(self, service_key):
        service = self.services_map.get(service_key)
        if service:
            return service.get_apps()
        return []

    def reinstall_os(self, service_key, server_id, os_id):
        service = self.services_map.get(service_key)
        if service:
            return service.reinstall_os(server_id, os_id)
        return None

    def shutdown_server(self, service_key, server_id):
        service = self.services_map.get(service_key)
        if service:
            return service.shutdown_server(server_id)
        return None

    def reboot_server(self, service_key, server_id):
        service = self.services_map.get(service_key)
        if service:
            return service.reboot_server(server_id)
        return None

    def delete_server(self, service_key, server_id):
        service = self.services_map.get(service_key)
        if service:
            return service.delete_server(server_id)
        return None
