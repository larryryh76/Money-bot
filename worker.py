import time
import random
import threading
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
from database_manager import update_account_status, write_log_db
from utils import get_parser

class Worker(threading.Thread):
    def __init__(self, config, operations_ai, evolution_ai, proxy_manager):
        super().__init__()
        self.config = config
        self.operations_ai = operations_ai
        self.evolution_ai = evolution_ai
        self.proxy_manager = proxy_manager
        self.task_queue = []
        self.running = True
        self.accounts = []

    def stop(self):
        self.running = False

    def set_accounts(self, accounts):
        self.accounts = accounts

    def run(self):
        while self.running:
            try:
                if not self.task_queue:
                    time.sleep(1)
                    continue

                task = self.task_queue.pop(0)
                site = task["site"]

                account = next((acc for acc in self.accounts if acc["site"] == site and acc["status"] == "active"), None)

                if not account:
                    continue

                proxy = self.proxy_manager.get_proxy()
                ua = UserAgent()
                options = Options()
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument(f"--window-size={random.randint(1024, 1920)},{random.randint(768, 1080)}")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                options.add_argument(f'--user-agent={ua.random}')
                if proxy: options.add_argument(f'--proxy-server={proxy}')

                service = Service(self.config.get("chromedriver_path", "/usr/bin/chromedriver"))
                driver = webdriver.Chrome(service=service, options=options)

                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

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
                account["status"] = new_status

            except (requests.exceptions.RequestException, webdriver.WebDriverException) as e:
                print(f"A network-related error occurred in a worker thread: {e}")
                if 'account' in locals() and account:
                    update_account_status(account["id"], "error")
            except Exception as e:
                print(f"An unexpected error occurred in a worker thread: {e}")
                if 'account' in locals() and account:
                    update_account_status(account["id"], "error")
            finally:
                if 'driver' in locals() and driver:
                    driver.quit()
