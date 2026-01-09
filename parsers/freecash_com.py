from parsers.base_parser import BaseParser
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from utils import ai_or_random_answer
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
