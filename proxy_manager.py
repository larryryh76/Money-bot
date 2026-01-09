import threading
import requests
import random
from bs4 import BeautifulSoup

class ProxyManager:
    """
    Manages fetching and providing proxies in a non-blocking way.
    It fetches proxies in a background thread at startup and uses a threading.Event
    to signal when the proxy list is ready for use.
    """
    def __init__(self):
        self.proxies = []
        self.ready = threading.Event()

    def _fetch_proxies_thread(self):
        """
        The actual proxy fetching logic that runs in a separate thread.
        This function scrapes a website for free proxies.
        Once proxies are fetched, it sets the 'ready' event.
        """
        try:
            response = requests.get("https://free-proxy-list.net/")
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table", attrs={"class": "table table-striped table-bordered"})
            for row in table.find_all("tr")[1:]:
                tds = row.find_all("td")
                ip = tds[0].text.strip()
                port = tds[1].text.strip()
                # We add the http protocol for Selenium compatibility
                self.proxies.append(f"http://{ip}:{port}")
        except Exception as e:
            print(f"Failed to fetch proxies: {e}")
        finally:
            # Signal that the proxy list is ready, even if it's empty.
            # This prevents the application from hanging if proxy fetching fails.
            self.ready.set()

    def start(self):
        """
        Starts the background thread to fetch proxies.
        This should be called once at application startup.
        """
        fetch_thread = threading.Thread(target=self._fetch_proxies_thread, daemon=True)
        fetch_thread.start()

    def get_proxy(self):
        """
        Returns a random proxy from the list.
        It waits for the 'ready' event to be set, ensuring that this call
        will block only if proxies are not yet available.
        """
        self.ready.wait()  # This will block until proxies are fetched
        if self.proxies:
            return random.choice(self.proxies)
        return None
