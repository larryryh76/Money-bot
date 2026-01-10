import requests, random, threading, time
from bs4 import BeautifulSoup

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.proxies_ready = threading.Event()
        self.lock = threading.Lock()
        self.fetch_thread = threading.Thread(target=self._fetch_proxies_periodically, daemon=True)

    def start(self):
        self.fetch_thread.start()

    def _fetch_proxies(self):
        try:
            response = requests.get("https://free-proxy-list.net/")
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table", attrs={"class": "table table-striped table-bordered"})
            new_proxies = []
            for row in table.find_all("tr")[1:]:
                tds = row.find_all("td")
                ip = tds[0].text.strip()
                port = tds[1].text.strip()
                new_proxies.append(f"http://{ip}:{port}")
            with self.lock:
                self.proxies = new_proxies
            print(f"Successfully fetched {len(new_proxies)} proxies.")
        except Exception as e:
            print(f"Failed to fetch proxies: {e}")
        finally:
            # Ensure the event is set even if fetching fails, to prevent deadlocks.
            if not self.proxies_ready.is_set():
                self.proxies_ready.set()

    def _fetch_proxies_periodically(self):
        while True:
            self._fetch_proxies()
            time.sleep(3600)

    def get_proxy(self):
        self.proxies_ready.wait()
        with self.lock:
            if self.proxies:
                return random.choice(self.proxies)
        return None
