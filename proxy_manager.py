import requests
import random
from bs4 import BeautifulSoup

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.good_proxies = []

    def fetch_proxies(self):
        try:
            response = requests.get("https://free-proxy-list.net/")
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table", attrs={"class": "table table-striped table-bordered"})
            for row in table.find_all("tr")[1:]:
                tds = row.find_all("td")
                ip = tds[0].text.strip()
                port = tds[1].text.strip()
                self.proxies.append(f"http://{ip}:{port}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching proxies: {e}")

    def test_proxies(self):
        self.good_proxies = []
        for proxy in self.proxies:
            try:
                response = requests.get("https://www.google.com", proxies={"http": proxy, "https": proxy}, timeout=5)
                if response.status_code == 200:
                    self.good_proxies.append(proxy)
            except requests.exceptions.RequestException:
                pass

    def get_proxy(self):
        if self.good_proxies:
            return random.choice(self.good_proxies)
        return None
