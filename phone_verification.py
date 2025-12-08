import requests
import time
import json

class BasePhoneProvider:
    def get_phone_number(self):
        raise NotImplementedError

    def get_sms_code(self, phone_number):
        raise NotImplementedError

class OnlineSimProvider(BasePhoneProvider):
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://onlinesim.ru/api"

    def get_phone_number(self):
        try:
            response = requests.get(f"{self.base_url}/getNum.php?apikey={self.api_key}&service=6115")
            data = response.json()
            if data.get("response") == "1":
                return data["number"]
            else:
                print(f"Error getting phone number from onlinesim.ru: {data.get('error_msg')}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error getting phone number from onlinesim.ru: {e}")
            return None

    def get_sms_code(self, phone_number):
        try:
            # Wait for SMS to arrive
            for _ in range(3): # Poll 3 times
                time.sleep(20)
                response = requests.get(f"{self.base_url}/getState.php?apikey={self.api_key}&number={phone_number}")
                data = response.json()
                if data and data[0].get("response") == "1":
                    return data[0]["msg"]
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error getting SMS code from onlinesim.ru: {e}")
            return None

def get_phone_provider(config):
    providers = config.get("providers", {})
    provider_name = providers.get("phone_verification")
    api_key = providers.get("onlinesim_api_key")

    if provider_name == "onlinesim.ru":
        if not api_key:
            print("onlinesim.ru API key is missing from config.")
            return None
        return OnlineSimProvider(api_key)
    else:
        print(f"Phone verification provider '{provider_name}' is not supported.")
        return None
