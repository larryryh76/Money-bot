import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from database_manager import load_accounts, save_accounts, load_sites
from ai_manager import OperationsAI
from dotenv import load_dotenv
from utils import get_parser
import os

load_dotenv()

def main():
    with open("config.json") as f:
        config = json.load(f)

    config["API_KEY"] = os.getenv("API_KEY")

    operations_ai = OperationsAI(config)
    accounts = load_accounts()
    sites = load_sites()

    for account in accounts:
        if account["status"] == "active":
            site = account["site"]
            site_data = sites.get(site)
            if not site_data:
                continue

            parser = get_parser(site)
            if not parser:
                print(f"No parser found for {site}")
                continue

            try:
                ua = UserAgent()
                options = Options()
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument(f'--user-agent={ua.random}')
                service = Service(config.get("chromedriver_path", "/usr/bin/chromedriver"))
                driver = webdriver.Chrome(service=service, options=options)

                parser.auto_payout(driver, config, account)

                driver.quit()
            except Exception as e:
                print(f"An error occurred during payout for {site}: {e}")

if __name__ == "__main__":
    main()
