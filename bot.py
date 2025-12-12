import time, random, requests, threading, os, re, string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from ai_manager import OperationsAI, EvolutionAI
from proxy_manager import ProxyManager
from captcha_solver import solve_captcha
from phone_verification import get_phone_provider
from dotenv import load_dotenv
from database_manager import init_db, load_sites, save_sites, write_log_db, get_persona_answer, save_persona_answer, load_accounts
from worker import Worker
from utils import get_parser

import json

load_dotenv()
init_db()

# Load config
with open("config.json") as f:
    config = json.load(f)

config["API_KEY"] = os.getenv("API_KEY")
config["ENCRYPTION_PASSWORD"] = os.getenv("ENCRYPTION_PASSWORD")
config["TWOCAPTCHA_API_KEY"] = os.getenv("TWOCAPTCHA_API_KEY")

THREADS = config.get("threads", 90)
THREAD_DELAY = config.get("thread_delay", 10)
CASHOUT_CHECK_INTERVAL = config.get("cashout_check_interval", 3600)
CHROMEDRIVER_PATH = config.get("chromedriver_path", "/usr/bin/chromedriver")

# Load sites
SITE_PATHS = load_sites()

proxy_manager = ProxyManager(config)
proxy_manager.fetch_proxies()
proxy_manager.test_proxies()

def get_proxy():
    return proxy_manager.get_proxy()



def load_profiles():
    try:
        with open("profiles.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def write_log(log_entry):
    write_log_db(log_entry)

def auto_signup(site, config, profile):
    """Handles the account creation process for a given site."""
    parser = get_parser(site)
    if not parser:
        print(f"No parser found for {site}")
        return False

    driver = None
    try:
        proxy = get_proxy()
        ua = UserAgent()
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument(f'--user-agent={ua.random}')
        if proxy: options.add_argument(f'--proxy-server={proxy}')
        service = Service(config.get("chromedriver_path", "/usr/bin/chromedriver"))
        driver = webdriver.Chrome(service=service, options=options)

        return parser.auto_signup(driver, config, profile)
    except (requests.exceptions.RequestException, webdriver.WebDriverException) as e:
        print(f"A network-related error occurred during signup for {site}: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during signup for {site}: {e}")
        return False
    finally:
        if driver:
            driver.quit()

class Bot:
    def __init__(self, config):
        self.config = config
        self.operations_ai = OperationsAI(config)
        self.evolution_ai = self.operations_ai.evolution_ai
        self.profiles = load_profiles()
        self.task_queue = []
        self.workers = []
        self.last_cashout_check = {}
        self.running = True

    def save_state(self):
        with open("bot_state.json", "w") as f:
            json.dump({"task_queue": self.task_queue}, f)

    def load_state(self):
        try:
            with open("bot_state.json", "r") as f:
                state = json.load(f)
                self.task_queue = state.get("task_queue", [])
        except FileNotFoundError:
            pass

    def start(self):
        self.load_state()

        # Perform initial analysis and optimization
        site_performance, profile_performance = self.operations_ai.learning_ai.analyze_logs()
        self.evolution_ai.optimize(site_performance, profile_performance)
        self.evolution_ai.improve_self(site_performance)
        self.integrate_new_sites()

        # Start worker threads
        for i in range(self.config.get("threads", 1)):
            worker = Worker(self.config, self.operations_ai, self.evolution_ai, proxy_manager)
            self.workers.append(worker)
            worker.start()
            time.sleep(self.config.get("thread_delay", 1))

        # Main loop to manage the task queue and account creation
        while self.running:
            if not self.task_queue:
                self.populate_task_queue()

            self.manage_account_creation()

            # Distribute tasks to workers
            for worker in self.workers:
                if not worker.task_queue:
                    if self.task_queue:
                        worker.task_queue.append(self.task_queue.pop(0))

            time.sleep(60) # Check for new tasks and accounts every 60 seconds

    def shutdown(self):
        print("Shutting down bot...")
        self.running = False
        for worker in self.workers:
            worker.stop()
        for worker in self.workers:
            worker.join()
        self.save_state()

    def populate_task_queue(self):
        all_offers = []

        proxy = get_proxy()
        ua = UserAgent()
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument(f'--user-agent={ua.random}')
        if proxy: options.add_argument(f'--proxy-server={proxy}')
        service = Service(self.config.get("chromedriver_path", "/usr/bin/chromedriver"))
        driver = webdriver.Chrome(service=service, options=options)

        for site, site_data in load_sites().items():
            if site_data.get("status", "enabled") != "enabled":
                continue
            try:
                driver.get(f"https://{site}{site_data['tasks']}")
                parser = get_parser(site)
                if parser:
                    all_offers.extend(parser.find_offers(driver))
            except (requests.exceptions.RequestException, webdriver.WebDriverException) as e:
                print(f"A network-related error occurred while populating task queue for {site}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while populating task queue for {site}: {e}")

        driver.quit()
        self.task_queue = self.operations_ai.manage_tasks(self.profiles, all_offers)

    def integrate_new_sites(self):
        new_sites = self.operations_ai.learning_ai.innovate()
        if new_sites:
            current_sites = load_sites()
            for site in new_sites:
                if site not in current_sites:
                    print(f"Integrating new site: {site}")
                    # Add with default paths, can be refined by evolution AI later
                    current_sites[site] = {
                        "signup": "/register", "login": "/login", "tasks": "/offers",
                        "withdraw": "/cashout", "min": 1.00, "status": "enabled"
                    }
            save_sites(current_sites)

    def manage_account_creation(self):
        """Checks if new accounts are needed and creates them."""
        min_accounts = self.config.get("min_accounts_per_site", 5)
        accounts = load_accounts()

        site_counts = {}
        for acc in accounts:
            site_counts[acc["site"]] = site_counts.get(acc["site"], 0) + 1

        for site, site_data in load_sites().items():
            if site_data.get("status", "enabled") != "enabled":
                continue
            if site_counts.get(site, 0) < min_accounts:
                if not self.profiles:
                    print("No profiles available to create new accounts.")
                    return
                print(f"Site {site} has fewer than {min_accounts} accounts. Creating a new one.")
                # Run signup in a new thread to avoid blocking the main loop
                profile = random.choice(self.profiles)
                signup_thread = threading.Thread(target=auto_signup, args=(site, self.config, profile))
                signup_thread.start()

if __name__ == "__main__":
    with open("config.json") as f:
        config = json.load(f)
    bot = Bot(config)
    try:
        bot.start()
    except KeyboardInterrupt:
        print("Caught keyboard interrupt. Shutting down.")
    finally:
        bot.shutdown()
