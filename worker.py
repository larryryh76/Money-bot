import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
from database_manager import load_accounts, save_accounts, write_log_db
from utils import get_parser
import threading

class Worker(threading.Thread):
    def __init__(self, config, operations_ai, evolution_ai, proxy_manager):
        super().__init__()
        self.config = config
        self.operations_ai = operations_ai
        self.evolution_ai = evolution_ai
        self.proxy_manager = proxy_manager
        self.task_queue = []
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            try:
                if not self.task_queue:
                    # The task queue is now managed by the main Bot class
                    time.sleep(1)
                    continue

                task = self.task_queue.pop(0)
                site = task["site"]

                # Get an account for this site
                accounts = load_accounts()
                account = next((acc for acc in accounts if acc["site"] == site and acc["status"] == "active"), None)

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

                # Anti-detection measures
                options.add_experimental_option('prefs', {'webrtc.ip_handling_policy': 'disable_non_proxied_udp',
                                                           'webrtc.multiple_routes_enabled': False,
                                                           'webrtc.nonproxied_udp_enabled': False})
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument('--disable-infobars')

                service = Service(self.config.get("chromedriver_path", "/usr/bin/chromedriver"))
                driver = webdriver.Chrome(service=service, options=options)

                # Spoof navigator.webdriver
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

                parser = get_parser(site)
                if parser:
                    tasks_completed, total_value = parser.do_task(driver, task, account["profile"], account["id"])
                    print(f"Completed {tasks_completed} tasks on {site} for a total of ${total_value:.2f}")
                    log_entry = {
                        "site": site,
                        "timestamp": time.time(),
                        "success": 1,
                        "profile": account["profile"],
                        "value": total_value
                    }
                    write_log_db(log_entry)
                    account["status"] = "active"
                else:
                    print(f"No parser found for {site}")
                    account["status"] = "error"

                # Payout logic should be handled by the payout_scheduler, so we remove it from the worker.

                # Update the account status in the database
                for i, acc in enumerate(accounts):
                    if acc["email"] == account["email"] and acc["site"] == site:
                        accounts[i] = account
                        break
                save_accounts(accounts)

                driver.quit()
            except (requests.exceptions.RequestException, webdriver.WebDriverException) as e:
                print(f"A network-related error occurred in a worker thread: {e}")
            except Exception as e:
                print(f"An unexpected error occurred in a worker thread: {e}")
            finally:
                if 'driver' in locals() and driver:
                    driver.quit()
