import requests
import random
import threading
from bs4 import BeautifulSoup

class ProxyManager:
    def __init__(self, config):
        self.config = config
        self.proxies = []
        self.providers = [
            self._fetch_from_proxyscrape,
            self._fetch_from_free_proxy_list
        ]

    def _fetch_from_proxyscrape(self):
        try:
            url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
            response = requests.get(url)
            self.proxies.extend(response.text.split("\r\n"))
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error fetching proxies from proxyscrape: {e}")
            return False

    def _fetch_from_free_proxy_list(self):
        try:
            url = "https://free-proxy-list.net/"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find("table", class_="table-striped")
            for row in table.find_all("tr")[1:]:
                cells = row.find_all("td")
                if len(cells) > 1:
                    ip = cells[0].text
                    port = cells[1].text
                    self.proxies.append(f"http://{ip}:{port}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error fetching proxies from free-proxy-list.net: {e}")
            return False

    def fetch_proxies(self):
        for fetch_func in self.providers:
            if fetch_func():
                print(f"Successfully fetched proxies.")
                return
        print("Failed to fetch proxies from any provider.")

    def test_proxies(self):
        tested_proxies = []
        threads = []

        def test_proxy(proxy):
            try:
                response = requests.get("https://www.google.com", proxies={"http": proxy, "https": proxy}, timeout=5)
                if response.status_code == 200:
                    tested_proxies.append(proxy)
            except:
                pass

        for proxy in self.proxies:
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
