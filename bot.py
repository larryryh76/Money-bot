import time
import random
import threading
import os
import json
from dotenv import load_dotenv
from ai_manager import OperationsAI
from proxy_manager import ProxyManager
from database_manager import init_db, load_sites, save_sites, load_accounts, load_profiles
from worker import Worker
from utils import get_parser, auto_signup

load_dotenv()
init_db()

class Bot:
    def __init__(self, config):
        self.config = config
        self.operations_ai = OperationsAI(config)
        self.proxy_manager = ProxyManager(config)
        self.profiles = []
        self.accounts = []
        self.task_queue = []
        self.workers = []
        self.running = True

    def start(self):
        print("Starting bot...")
        self.proxy_manager.fetch_proxies()
        self.proxy_manager.test_proxies()
        self.profiles = load_profiles()
        self.accounts = load_accounts()

        # Distribute accounts to workers for thread-safe operations
        accounts_per_worker = len(self.accounts) // self.config.get("threads", 1)

        for i in range(self.config.get("threads", 1)):
            worker = Worker(self.config, self.operations_ai, self.operations_ai.evolution_ai, self.proxy_manager)

            # Assign a slice of accounts to each worker
            start_index = i * accounts_per_worker
            end_index = (i + 1) * accounts_per_worker
            worker_accounts = self.accounts[start_index:end_index]
            worker.set_accounts(worker_accounts)

            self.workers.append(worker)
            worker.start()
            time.sleep(self.config.get("thread_delay", 1))

        while self.running:
            self.manage_account_creation()
            self.populate_task_queue()
            self.distribute_tasks_to_workers()
            time.sleep(60)

    def shutdown(self):
        print("Shutting down bot...")
        self.running = False
        for worker in self.workers:
            worker.stop()
        for worker in self.workers:
            worker.join()

    def manage_account_creation(self):
        min_accounts = self.config.get("min_accounts_per_site", 5)
        site_counts = {site: 0 for site in load_sites()}
        for acc in self.accounts:
            site_counts[acc["site"]] = site_counts.get(acc["site"], 0) + 1

        for site, count in site_counts.items():
            if count < min_accounts:
                if not self.profiles:
                    print(f"No profiles available to create new accounts for {site}.")
                    continue
                print(f"Creating new account for {site}...")
                profile = random.choice(self.profiles)
                signup_thread = threading.Thread(target=auto_signup, args=(site, self.config, profile, self.proxy_manager))
                signup_thread.start()

    def populate_task_queue(self):
        # In a more advanced system, this would be a sophisticated process.
        # For now, we'll keep it simple.
        all_offers = []
        for site, data in load_sites().items():
            if data.get("status", "enabled") == "enabled":
                # This is a placeholder for actually finding tasks.
                # In the real implementation, this would involve a WebDriver.
                all_offers.append({"site": site, "value": 1.0, "time_to_complete": 10, "xpath": "//some/xpath"})
        self.task_queue = self.operations_ai.manage_tasks(self.accounts, all_offers)

    def distribute_tasks_to_workers(self):
        for i, task in enumerate(self.task_queue):
            worker_index = i % len(self.workers)
            self.workers[worker_index].task_queue.append(task)
        self.task_queue = []


if __name__ == "__main__":
    with open("config.json") as f:
        config_data = json.load(f)

    bot = Bot(config_data)
    try:
        bot.start()
    except KeyboardInterrupt:
        bot.shutdown()
