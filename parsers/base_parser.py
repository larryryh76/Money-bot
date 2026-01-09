from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import time
import random

class BaseParser:
    def __init__(self, driver, api_key="", wallet="", config=None):
        self.driver = driver
        self.api_key = api_key
        self.wallet = wallet
        self.config = config
        self.wait = WebDriverWait(self.driver, 15)

    def human_type(self, element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))

    def human_move_and_click(self, element):
        action = ActionChains(self.driver)
        action.move_to_element(element)
        action.click()
        action.perform()
        time.sleep(random.uniform(0.5, 1.5))

    def signup(self, email, password):
        raise NotImplementedError

    def do_tasks(self):
        raise NotImplementedError

    def withdraw(self, wallet_address):
        raise NotImplementedError
