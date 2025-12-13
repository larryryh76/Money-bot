from .base_parser import BaseParser
from selenium.webdriver.common.by import By

class GenericParser(BaseParser):
    def __init__(self, recipe):
        self.recipe = recipe

    def execute_recipe(self, driver, action):
        steps = self.recipe.get(action, [])
        for step in steps:
            command = step["command"]
            target = step.get("target")
            value = step.get("value")

            element = None
            if target:
                by, locator = target.split("=", 1)
                element = driver.find_element(getattr(By, by.upper()), locator)

            if command == "click":
                self.human_like_click(driver, element)
            elif command == "send_keys":
                element.send_keys(value)
            elif command == "get":
                driver.get(value)
            # ... more commands can be added here ...

    def find_offers(self, driver):
        self.execute_recipe(driver, "find_offers")
        # For now, we'll assume the recipe handles everything and we don't need to return offers
        return []

    def do_task(self, driver, task, profile, account_id, config):
        self.execute_recipe(driver, "do_task")
        return 0, 0

    def auto_signup(self, driver, config, profile):
        self.execute_recipe(driver, "auto_signup")
        return True

    def auto_payout(self, driver, config, account):
        self.execute_recipe(driver, "auto_payout")
        return True
