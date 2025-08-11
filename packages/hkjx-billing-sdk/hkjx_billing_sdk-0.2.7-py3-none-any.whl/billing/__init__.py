from .activities import Activities
from .http import HttpClient
from .keys import Keys


class HkJingXiuBilling:
    def __init__(self, base_url: str, admin_key: str = None):
        self.base_url = base_url
        self.http_client = HttpClient(base_url=base_url, key=admin_key)
        self.keys = Keys(self.http_client)
        self.activities = Activities(self.http_client)


__all__ = ["HkJingXiuBilling"]
