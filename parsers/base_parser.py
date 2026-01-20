from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from utils import ai_or_random_answer
import time
import random

class BaseParser:
    def __init__(self, driver, api_key="", wallet="", config=None, dry_run=False):
        self.driver = driver
        self.api_key = api_key
        self.wallet = wallet
        self.config = config
        self.dry_run = dry_run
        self.wait = WebDriverWait(self.driver, 15)

    def human_type(self, element, text):
        if self.dry_run:
            print(f"[DRY RUN] Would have typed '{text}' into element: {element}")
            return
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))

    def human_move_and_click(self, element):
        if self.dry_run:
            print(f"[DRY RUN] Would have clicked element: {element}")
            return
        action = ActionChains(self.driver)
        action.move_to_element(element)
        action.click()
        action.perform()
        time.sleep(random.uniform(0.5, 1.5))

    def signup(self, email, password):
        raise NotImplementedError

    def do_tasks(self):
        tasks = 0
        retries = 3
        try:
            self.driver.get(f"https://{self.site}{self.config['tasks']}")
            time.sleep(random.uniform(5, 15))

            num_tasks = random.randint(3, 7)
            for _ in range(num_tasks):
                if random.random() < 0.1:
                    print("Abandoning survey...")
                    break
                try:
                    question_element = self.driver.find_element(By.CSS_SELECTOR, "label, span, p, h1, h2, h3")
                    question_text = question_element.text
                    if question_text:
                        context = self.driver.page_source
                        try:
                            input_field = question_element.find_element(By.XPATH, "./following::input[@type='text'] | ./following::textarea")
                            answer = ai_or_random_answer(question_text, context, api_key=self.api_key)
                            self.human_type(input_field, answer)
                        except:
                            try:
                                option_elements = question_element.find_elements(By.XPATH, "./following::input[@type='radio'] | ./following::input[@type='checkbox']")
                                option_labels = [opt.find_element(By.XPATH, "./following-sibling::label").text for opt in option_elements]
                                answer = ai_or_random_answer(question_text, context, options=option_labels, api_key=self.api_key)
                                for opt in option_elements:
                                    if opt.find_element(By.XPATH, "./following-sibling::label").text == answer:
                                        self.human_move_and_click(opt)
                                        break
                            except:
                                pass
                        time.sleep(random.uniform(1, 3))

                    btn = self.driver.find_element(By.XPATH, "//button[contains(text(),'Start') or contains(text(),'Next') or contains(text(),'Play')] | //a[contains(@href,'offer')]")
                    self.human_move_and_click(btn)
                    time.sleep(random.uniform(10, 25))

                    tasks += 1
                    retries = 3
                except Exception as e:
                    print(f"Error in do_tasks loop: {e}")
                    retries -= 1
                    if retries == 0:
                        break
            return tasks > 0
        except Exception as e:
            print(f"Error doing tasks on {self.site}: {e}")
            return False

    def withdraw(self, wallet_address):
        raise NotImplementedError
