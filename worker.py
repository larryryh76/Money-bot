import time
import random
import os
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
from dotenv import load_dotenv
from database_manager import update_account_status, write_log_db, load_accounts
from task_queue_manager import pull_task
from utils import get_parser
from proxy_manager import ProxyManager

load_dotenv()

class Consumer:
    def __init__(self, config):
        self.config = config
        self.proxy_manager = ProxyManager(config)
        self.running = True

    def start(self):
        print("Starting Consumer...")
        self.proxy_manager.fetch_proxies()
        self.proxy_manager.test_proxies()

        while self.running:
            try:
                task = pull_task() # This will block until a task is available
                if not task: continue

                self.process_task(task)

            except Exception as e:
                print(f"An unexpected error occurred in the consumer loop: {e}")
                time.sleep(10) # Avoid rapid-fire crashes

    def stop(self):
        self.running = False

    def process_task(self, task):
        site = task["site"]

        # Load accounts on-demand to get the latest status
        accounts = load_accounts()
        account = next((acc for acc in accounts if acc["site"] == site and acc["status"] == "active"), None)

        if not account:
            print(f"No active account found for {site}. Re-queuing task.")
            # We could push the task back to the queue here if desired
            return

        proxy = self.proxy_manager.get_proxy()
        ua = UserAgent()
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--user-agent={ua.random}')
        if proxy: options.add_argument(f'--proxy-server={proxy}')
        service = Service(self.config.get("chromedriver_path", "/usr/bin/chromedriver"))
        driver = None

        try:
            driver = webdriver.Chrome(service=service, options=options)
            parser = get_parser(site)
            new_status = "active"
            if parser:
                tasks_completed, total_value = parser.do_task(driver, task, account["profile"], account["id"], self.config)
                if tasks_completed > 0:
                    log_entry = {
                        "site": site, "action": "do_task", "timestamp": time.time(),
                        "success": 1, "profile": account["profile"], "value": total_value
                    }
                    write_log_db(log_entry)
                else:
                    new_status = "flagged"
            else:
                new_status = "error"

            update_account_status(account["id"], new_status)

        except (requests.exceptions.RequestException, webdriver.WebDriverException) as e:
            print(f"A network error occurred processing task for {site}: {e}")
            update_account_status(account["id"], "error")
        except Exception as e:
            print(f"An unexpected error occurred processing task for {site}: {e}")
            update_account_status(account["id"], "error")
        finally:
            if driver:
                driver.quit()

if __name__ == "__main__":
    with open("config.json") as f:
        config_data = json.load(f)

    # We can run multiple consumers in threads on one machine for vertical scaling
    num_consumers = config_data.get("consumers_per_instance", 5)
    threads = []
    for _ in range(num_consumers):
        consumer = Consumer(config_data)
        thread = threading.Thread(target=consumer.start)
        threads.append(thread)
        thread.start()

    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        for consumer in threads:
            consumer.stop()
        print("Shutting down consumers...")
