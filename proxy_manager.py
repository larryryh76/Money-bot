import requests
import random
import threading

class ProxyManager:
    def __init__(self, config):
        self.config = config
        self.proxies = []

    def fetch_proxies(self):
        try:
            response = requests.get("https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all")
            self.proxies = response.text.split("\r\n")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching proxies: {e}")

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
