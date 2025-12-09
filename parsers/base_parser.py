from selenium.webdriver.common.action_chains import ActionChains
import time
import random

class BaseParser:
    def find_offers(self, driver):
        raise NotImplementedError

    def do_task(self, driver, offer):
        raise NotImplementedError

    def human_like_click(self, driver, element):
        actions = ActionChains(driver)
        actions.move_to_element(element)
        actions.pause(random.uniform(0.1, 0.5))
        actions.click()
        actions.perform()

    def human_like_send_keys(self, driver, element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))

    def auto_signup(self, driver, config, profile):
        raise NotImplementedError

    def auto_payout(self, driver, config, account):
        raise NotImplementedError
