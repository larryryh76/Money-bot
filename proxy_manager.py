import threading
import time
import requests
from bs4 import BeautifulSoup
import random

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.proxies_ready = threading.Event()
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._fetch_proxies_periodically, daemon=True)

    def start(self):
        self.thread.start()

    def _fetch_proxies(self):
        """
        Fetches a list of free proxies and updates the internal list.
        This is a blocking I/O operation and should be run in a background thread.
        """
        fetched_proxies = []
        try:
            # Optimization: Fetch proxies in a background thread to avoid blocking startup.
            response = requests.get("https://free-proxy-list.net/")
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table", attrs={"class": "table table-striped table-bordered"})
            for row in table.find_all("tr")[1:]:
                tds = row.find_all("td")
                ip = tds[0].text.strip()
                port = tds[1].text.strip()
                fetched_proxies.append(f"http://{ip}:{port}")
        except Exception as e:
            print(f"Failed to fetch proxies: {e}")

        with self.lock:
            self.proxies = fetched_proxies

        # Signal that the first batch of proxies is ready.
        if not self.proxies_ready.is_set() and self.proxies:
            self.proxies_ready.set()

    def _fetch_proxies_periodically(self):
        """
        Periodically fetches proxies to keep the list fresh.
        The initial fetch happens immediately, and then it refreshes every hour.
        """
        while True:
            print("Fetching proxies...")
            self._fetch_proxies()
            print(f"Found {len(self.proxies)} proxies.")
            time.sleep(3600) # Refresh every hour

    def get_proxy(self):
        """
        Returns a random proxy from the list.
        Waits for the initial proxy list to be fetched.
        """
        self.proxies_ready.wait() # Wait until proxies are available
        with self.lock:
            if self.proxies:
                return random.choice(self.proxies)
        return None
