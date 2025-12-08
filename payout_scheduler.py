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

                driver.get(f"https://{site}{site_data['login']}")

                # Basic login
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(account["email"])
                driver.find_element(By.NAME, "password").send_keys(account["password"])
                driver.find_element(By.XPATH, "//button[@type='submit']").click()

                # Navigate to withdrawal page
                WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))
                driver.get(f"https://{site}{site_data['withdraw']}")

                # Check balance
                balance_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "balance")))
                balance = float(balance_element.text.replace("$", ""))

                if balance >= site_data["min"]:
                    # Select wallet
                    available_options = [opt.text for opt in driver.find_elements(By.CSS_SELECTOR, ".wallet-option")]
                    wallet = operations_ai.select_wallet(available_options)

                    if wallet:
                        driver.find_element(By.XPATH, f"//div[contains(text(), '{wallet['type']}')]").click()
                        driver.find_element(By.NAME, "wallet_address").send_keys(wallet["address"])
                        driver.find_element(By.XPATH, "//button[contains(text(), 'Withdraw')]").click()
                        print(f"Successfully initiated withdrawal for {account['email']} on {site}")

                driver.quit()
            except Exception as e:
                print(f"An error occurred during payout for {site}: {e}")

if __name__ == "__main__":
    main()
