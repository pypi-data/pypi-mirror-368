class Amounts:
    def __init__(self, api):
        self.__api = api

    def available_minutes(self) -> int:
        response = self.__api.request("GET", "/user/amounts").json()
        return response['minutes']['available']

    def used_minutes(self) -> int:
        response = self.__api.request("GET", "/user/amounts").json()
        return response['minutes']['used']

    def balance(self) -> float:
        response = self.__api.request("GET", "/user/amounts").json()
        return response['amount']


class Rate:
    def __init__(self, title: str, minutes: int, period: str):
        self.title = title
        self.minutes = minutes
        self.period = period


class Settings:
    def __init__(self, api):
        self.__api = api

    def threads(self) -> int:
        response = self.__api.request("GET", "/user/settings").json()
        return response['settings']['threads']

    def auto_payments_status(self) -> bool:
        response = self.__api.request("GET", "/user/settings").json()
        return response['settings']['auto-payment-over-rate-limits']

    def auto_payments_on(self) -> bool:
        self.__api.request("PATCH", "/user/settings/auto-payments-over-rate-limits/on").json()
        return self.auto_payments_status() is True

    def auto_payments_off(self):
        self.__api.request("PATCH", "/user/settings/auto-payments-over-rate-limits/off").json()
        return self.auto_payments_status() is False


class User:

    def __init__(self, api):
        self.__rate = None
        self.__api = api

    def rate(self, update: bool = False) -> Rate:
        if self.__rate is None or update:
            response = self.__api.request("GET", "/user/settings").json()
            self.__rate = Rate(
                title=response['rate']['title'],
                minutes=response['rate']['minutes'],
                period=response['rate']['period']
            )
        return self.__rate

    def settings(self) -> Settings:
        return Settings(self.__api)

    def amounts(self) -> Amounts:
        return Amounts(self.__api)
