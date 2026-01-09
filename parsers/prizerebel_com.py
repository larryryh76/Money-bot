from parsers.base_parser import BaseParser
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from utils import ai_or_random_answer
import random
import time

class PrizerebelComParser(BaseParser):
    def __init__(self, driver, api_key="", wallet="", config=None):
        super().__init__(driver, api_key, wallet, config)
        self.site = "prizerebel.com"

    def signup(self, email, password):
        try:
            self.driver.get(f"https://{self.site}{self.config['signup']}")
            self.wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(email)
            self.driver.find_element(By.NAME, "password").send_keys(password)
            self.driver.find_element(By.NAME, "password2").send_keys(password)
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            return True
        except Exception as e:
            print(f"Error signing up on {self.site}: {e}")
            return False

    def do_tasks(self):
        try:
            self.driver.get(f"https://{self.site}{self.config['tasks']}")
            print(f"Doing tasks on {self.site}")
            return True
        except Exception as e:
            print(f"Error doing tasks on {self.site}: {e}")
            return False

    def withdraw(self):
        try:
            self.driver.get(f"https://{self.site}{self.config['withdraw']}")
            print(f"Withdrawing from {self.site}")
            return True
        except Exception as e:
            print(f"Error withdrawing from {self.site}: {e}")
            return False
