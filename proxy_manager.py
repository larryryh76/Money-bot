import random
import threading
import time
import requests
from bs4 import BeautifulSoup

class ProxyManager:
    def __init__(self, proxy_file=None):
        self.proxies = []
        self.proxy_file = proxy_file
        self.ready = threading.Event()

    def load_proxies(self):
        if self.proxy_file:
            with open(self.proxy_file, 'r') as f:
                self.proxies = [line.strip() for line in f]
        else:
            self.fetch_free_proxies()

        self.ready.set()

    def fetch_free_proxies(self):
        try:
            response = requests.get("https://free-proxy-list.net/")
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table", attrs={"class": "table table-striped table-bordered"})
            for row in table.find_all("tr")[1:]:
                tds = row.find_all("td")
                ip = tds[0].text.strip()
                port = tds[1].text.strip()
                self.proxies.append(f"http://{ip}:{port}")
        except Exception as e:
            print(f"Failed to fetch free proxies: {e}")

    def start(self):
        threading.Thread(target=self.load_proxies, daemon=True).start()

    def get_proxy(self):
        self.ready.wait()
        if self.proxies:
            return random.choice(self.proxies)
        return None
