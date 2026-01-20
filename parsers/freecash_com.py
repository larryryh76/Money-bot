from parsers.base_parser import BaseParser
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import random
import time

class FreecashComParser(BaseParser):
    def __init__(self, driver, api_key="", wallet="", config=None):
        super().__init__(driver, api_key, wallet, config)
        self.site = "freecash.com"

    def signup(self, email, password):
        try:
            self.driver.get(f"https://{self.site}{self.config['signup']}")
            self.wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(email)
            self.driver.find_element(By.NAME, "password").send_keys(password)
            self.driver.find_element(By.NAME, "passwordConfirmation").send_keys(password)
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            # You might need to add email verification logic here
            return True
        except Exception as e:
            print(f"Error signing up on {self.site}: {e}")
            return False

    def do_tasks(self):
        return super().do_tasks()

    def withdraw(self):
        try:
            self.driver.get(f"https://{self.site}{self.config['withdraw']}")
            time.sleep(random.uniform(5, 10))

            balance_str = self.driver.find_element(By.CSS_SELECTOR, ".balance, [class*='balance']").text.replace("$", "").strip()
            balance = float(balance_str) if balance_str.replace(".", "").isdigit() else 0

            if balance >= self.config['min']:
                self.human_move_and_click(self.driver.find_element(By.XPATH, "//button[contains(text(),'Crypto') or contains(text(),'BTC') or contains(text(),'Cash Out')]"))
                time.sleep(3)
                self.human_type(self.driver.find_element(By.CSS_SELECTOR, "input[placeholder*='address']"), self.wallet)
                self.human_move_and_click(self.driver.find_element(By.XPATH, "//button[contains(text(),'Withdraw') or contains(text(),'Confirm')]"))
                print(f"Payout ${balance} from {self.site} to {self.wallet}")
                return True
            else:
                print(f"${balance} < ${self.config['min']} on {self.site}")
                return False
        except Exception as e:
            print(f"Error withdrawing from {self.site}: {e}")
            return False
