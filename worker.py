import time
import random
import os
import json
import requests
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
from dotenv import load_dotenv
from database_manager import update_account_status, write_log_db, load_accounts
from task_queue_manager import pull_task
from utils import get_parser
from proxy_manager import ProxyManager
from fingerprint_manager import FingerprintManager

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
                task = pull_task()
                if not task: continue
                self.process_task(task)
            except Exception as e:
                print(f"An unexpected error occurred in the consumer loop: {e}")
                time.sleep(10)

    def stop(self):
        self.running = False

    def process_task(self, task):
        site = task["site"]
        accounts = load_accounts()
        account = next((acc for acc in accounts if acc["site"] == site and acc["status"] == "active"), None)

        if not account:
            print(f"No active account found for {site}.")
            return

        proxy = self.proxy_manager.get_proxy()
        ua = UserAgent()

        # --- OPTIMIZED CHROME OPTIONS ---
        options = Options()
        options.page_load_strategy = 'eager' # Don't wait for full page load
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--user-agent={ua.random}')
        if proxy: options.add_argument(f'--proxy-server={proxy}')

        # Resource-saving options
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-images')
        options.add_argument('--disable-css')
        options.add_argument('--disable-fonts')
        options.add_argument('--blink-settings=imagesEnabled=false')

        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.css": 2,
        }
        options.add_experimental_option("prefs", prefs)
        # ---------------------------------

        service = Service(self.config.get("chromedriver_path", "/usr/bin/chromedriver"))
        driver = None

        try:
            driver = webdriver.Chrome(service=service, options=options)

            fm = FingerprintManager()
            spoofing_script = fm.get_spoofing_script()
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': spoofing_script})

            parser = get_parser(site)
            new_status = "active"

            # For this phase, we're calling the new do_task with a high-level objective
            objective = f"Find and click the highest value offer on {site}"
            task_successful = parser.do_task(driver, objective, self.config)

            if not task_successful:
                new_status = "flagged"

            update_account_status(account["id"], new_status)

        except Exception as e:
            print(f"An unexpected error occurred processing task for {site}: {e}")
            update_account_status(account["id"], "error")
        finally:
            if driver:
                driver.quit()

if __name__ == "__main__":
    with open("config.json") as f:
        config_data = json.load(f)

    num_consumers = config_data.get("consumers_per_instance", 1)
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
        print("Shutting down consumers...")
