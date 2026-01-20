from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
from parsers.base_parser import BaseParser
import random
import time
import importlib
from utils import create_temp_email
import json
import os

class Worker:
    def __init__(self, db_manager, persona_manager, proxy_manager, api_key, sites):
        self.db_manager = db_manager
        self.persona_manager = persona_manager
        self.proxy_manager = proxy_manager
        self.api_key = api_key
        self.sites = sites
        with open("config.json") as f:
            config = json.load(f)
        self.wallet = config.get("wallet", "")
        self.dry_run = config.get("dry_run", False)
        self.available_parsers = self.discover_parsers()

    def discover_parsers(self):
        parsers = []
        parser_dir = "parsers"
        for filename in os.listdir(parser_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                site_name = filename.replace("_", ".").replace(".py", "")
                parsers.append(site_name)
        return parsers

    def get_parser(self, site):
        try:
            module_name = f"parsers.{site.replace('.', '_')}"
            class_name = f"{site.replace('.', '_').replace('_', ' ').title().replace(' ', '')}Parser"
            module = importlib.import_module(module_name)
            parser_class = getattr(module, class_name)
            return parser_class
        except (ImportError, AttributeError):
            return None

    def run(self):
        while True:
            if not self.available_parsers:
                print("No parsers found. Exiting.")
                break

            site_name = random.choice(self.available_parsers)
            account = self.db_manager.get_account(site_name)

            if not account:
                # Create a new account if none are available
                email, sid_token, seq = create_temp_email()
                password = ''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for i in range(12))
                account_id = self.db_manager.add_account(email, password, site_name)
                self.persona_manager.create_persona(account_id)
                account = self.db_manager.get_account(site_name)

            proxy = self.proxy_manager.get_proxy()
            ua = UserAgent()
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument(f'--user-agent={ua.random}')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--disable-blink-features=AutomationControlled")
            if proxy:
                options.add_argument(f'--proxy-server={proxy}')

            service = Service('/usr/bin/chromedriver')
            driver = webdriver.Chrome(service=service, options=options)

            try:
                parser_class = self.get_parser(site_name)
                if parser_class:
                    parser = parser_class(
                        driver=driver,
                        api_key=self.api_key,
                        wallet=self.wallet,
                        config=self.sites[site_name],
                        dry_run=self.dry_run
                    )

                    if account[4] == 'new': # status
                        if parser.signup(account[1], account[2]):
                            self.db_manager.update_account_status(account[0], 'active')
                            self.db_manager.add_log(account[0], "Signup successful")
                        else:
                            self.db_manager.update_account_status(account[0], 'failed')
                            self.db_manager.add_log(account[0], "Signup failed")

                    if account[4] == 'active':
                        if parser.do_tasks():
                            parser.withdraw()
                else:
                    print(f"No parser found for {site_name}")

            finally:
                driver.quit()

            time.sleep(random.randint(180, 300))
