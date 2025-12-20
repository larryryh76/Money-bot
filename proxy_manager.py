import requests
import random
import threading
import os
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup

class ProxyProvider(ABC):
    """Abstract base class for all proxy providers."""
    def __init__(self, api_key=None):
        self.api_key = api_key

    @abstractmethod
    def fetch_proxies(self):
        """Fetch a list of proxies from the provider."""
        pass

class ProxyScrapeProvider(ProxyProvider):
    def fetch_proxies(self):
        try:
            url = f"https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
            if self.api_key:
                url += f"&api_key={self.api_key}"
            response = requests.get(url)
            response.raise_for_status()
            return response.text.split("\r\n")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from ProxyScrape: {e}")
            return []

class WebshareProvider(ProxyProvider):
    def fetch_proxies(self):
        if not self.api_key:
            return []
        try:
            url = f"https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=100"
            headers = {"Authorization": f"Token {self.api_key}"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return [f"{p['username']}:{p['password']}@{p['proxy_address']}:{p['ports']['http']}" for p in data.get('results', [])]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from Webshare: {e}")
            return []

class FreeProxyListProvider(ProxyProvider):
    def fetch_proxies(self):
        proxies = []
        try:
            url = "https://free-proxy-list.net/"
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find("table", class_="table-striped")
            for row in table.find_all("tr")[1:]:
                cells = row.find_all("td")
                if len(cells) > 1 and cells[6].text == 'yes': # Only get https proxies
                    proxies.append(f"http://{cells[0].text}:{cells[1].text}")
            return proxies
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from FreeProxyList: {e}")
            return []

class ProxyManager:
    def __init__(self, config):
        self.config = config
        self.proxies = []
        self.providers = self._load_providers()

    def _load_providers(self):
        provider_classes = {
            "ProxyScrape": ProxyScrapeProvider,
            "Webshare": WebshareProvider,
            "FreeProxyList": FreeProxyListProvider
        }
        loaded_providers = []
        for provider_config in self.config.get("proxy_providers", []):
            name = provider_config["name"]
            api_key_env = provider_config.get("api_key_env")
            api_key = os.getenv(api_key_env) if api_key_env else None

            if name in provider_classes:
                loaded_providers.append(provider_classes[name](api_key=api_key))
        return loaded_providers

    def fetch_proxies(self):
        for provider in self.providers:
            print(f"Fetching proxies from {provider.__class__.__name__}...")
            fetched_proxies = provider.fetch_proxies()
            if fetched_proxies:
                self.proxies.extend(fetched_proxies)
                print(f"Successfully fetched {len(fetched_proxies)} proxies.")
            else:
                print(f"Failed to fetch proxies from {provider.__class__.__name__}. Trying next provider.")

        if not self.proxies:
            print("Failed to fetch proxies from any provider.")

    def test_proxies(self):
        # The rest of the class remains the same
        tested_proxies = []
        threads = []

        def test_proxy(proxy):
            try:
                # Format proxy for requests library
                proxy_url = f"http://{proxy}" if '@' in proxy else proxy
                proxies_dict = {"http": proxy_url, "https": proxy_url}
                response = requests.get("https://www.google.com", proxies=proxies_dict, timeout=5)
                if response.status_code == 200:
                    tested_proxies.append(proxy)
            except:
                pass

        # To avoid overwhelming the system, test a random sample of 100 proxies if more than 100 are fetched
        proxies_to_test = random.sample(self.proxies, min(len(self.proxies), 100))
        for proxy in proxies_to_test:
            thread = threading.Thread(target=test_proxy, args=(proxy,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.proxies = tested_proxies
        print(f"Found {len(self.proxies)} working proxies.")

    def get_proxy(self):
        if self.proxies:
            return random.choice(self.proxies)
        return None
