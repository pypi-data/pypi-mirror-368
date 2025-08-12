import requests
from .recognitions import Recognitions
from .user import User


class Speech2Text:

    BASE_URL = "https://speech2text.ru/api"

    def __init__(self, api_key: str, base_url=BASE_URL):
        self.api_key = api_key
        self.base_url = base_url

    def recognitions(self) -> Recognitions:
        return Recognitions(self)

    def user(self) -> User:
        return User(self)

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.api_key}"
        url = path if path.startswith("http") else f"{self.base_url}{path}"
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response


