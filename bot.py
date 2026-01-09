import threading
import time
import os
import json
from database_manager import DatabaseManager
from persona_manager import PersonaManager
from proxy_manager import ProxyManager
from worker import Worker

class Bot:
    def __init__(self):
        with open("config.json") as f:
            config = json.load(f)

        self.db_manager = DatabaseManager("bot.db")
        self.persona_manager = PersonaManager(self.db_manager)
        self.proxy_manager = ProxyManager(config.get("proxy_file"))
        self.threads = config.get("threads", 10)
        self.api_key = os.environ.get("API_KEY", config.get("api_key"))

        # Load sites
        with open("sites.json") as f:
            self.sites = json.load(f)

    def start(self):
        self.proxy_manager.start()
        print(f"Starting {self.threads} worker threads...")
        for _ in range(self.threads):
            worker = Worker(
                db_manager=self.db_manager,
                persona_manager=self.persona_manager,
                proxy_manager=self.proxy_manager,
                api_key=self.api_key,
                sites=self.sites
            )
            threading.Thread(target=worker.run, daemon=True).start()
            time.sleep(0.1)

        # Keep the main thread alive
        while True:
            time.sleep(3600)

if __name__ == "__main__":
    bot = Bot()
    bot.start()
