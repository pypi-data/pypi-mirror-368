import requests
from typing import Dict, Optional
from amzsc.handlers import safe_method
from amzsc.utils import Constants


RESPONSE_STATUS = {"ERROR": "error", "SUCCESS": "success"}


class ProxyRequest:
    def __init__(self, api_key: str) -> None:
        self.__api_key = api_key

    @property
    def api_key(self) -> str:
        return self.__api_key

    def request(self, url: str) -> Dict:
        params = {"access_token": self.api_key, "location": "", "provider": ""}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    @safe_method
    def get_new_proxy(self) -> Optional[str]:
        data = self.request(Constants.GET_NEW_ENDPOINT)
        if data is None:
            return None
        if data["status"] == RESPONSE_STATUS["ERROR"]:
            return None
        return data["data"]["proxy"]

    @safe_method
    def get_current_proxy(self) -> Optional[str]:
        data = self.request(Constants.GET_CURRENT_ENDPOINT)
        if data is None:
            return None
        return data["data"]["proxy"]

    @staticmethod
    def is_proxy_live(proxy: Optional[str] = None) -> bool:
        if proxy is None:
            return False

        try:
            response = requests.get(f"{Constants.PROXY_LIVE_URL}/{proxy}", timeout=10)
            response.raise_for_status()
            data = response.json()
            if data["status"] == "Live":
                return True
            return False
        except:
            return False
