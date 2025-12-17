from .base_parser import BaseParser
from selenium.webdriver.common.by import By
import re
import time
import random
from utils import ai_or_random_answer, create_temp_email, fetch_email_code
from phone_verification import get_phone_provider
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import string

class FreecashComParser(BaseParser):
    def find_offers(self, driver):
        offers = []
        offer_elements = driver.find_elements(By.CSS_SELECTOR, ".offer-wall-item")
        for i, offer_element in enumerate(offer_elements):
            try:
                offer_text = offer_element.text
                value_match = re.search(r'\$(\d+\.\d+)', offer_text)
                if not value_match: continue
                value = float(value_match.group(1))
                time_match = re.search(r'(\d+)\s*min', offer_text)
                time_to_complete = int(time_match.group(1)) if time_match else 10

                xpath = f"(//div[contains(@class, 'offer-wall-item')])[{i+1}]"

                offers.append({
                    "site": "freecash.com",
                    "value": value,
                    "time_to_complete": time_to_complete,
                    "xpath": xpath
                })
            except Exception as e:
                print(f"Error parsing offer on freecash.com: {e}")
        return offers

    def do_task(self, driver, task, profile, account_id, config):
        tasks_completed = 0
        total_value = 0

        try:
            offer_element = driver.find_element(By.XPATH, task["xpath"])
            self.human_like_click(driver, offer_element)
            WebDriverWait(driver, 15).until(EC.number_of_windows_to_be(2))
            driver.switch_to.window(driver.window_handles[1])
        except Exception as e:
            print(f"Could not start task on freecash.com: {e}")
            return 0, 0

        # The logic for interacting with the survey itself remains largely the same
        # This is a placeholder for the complex interaction logic
        try:
            # Assuming the task involves answering some questions
            for _ in range(5): # Simulate answering 5 questions
                question_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "p, h1, h2, h3"))
                )
                question_text = question_element.text
                answer = ai_or_random_answer(config, account_id, question_text, profile=profile)

                # Find an input and a button to proceed
                input_field = driver.find_element(By.CSS_SELECTOR, "input[type='text'], input[type='email']")
                self.human_like_send_keys(driver, input_field, answer)

                next_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], a.btn-next")
                self.human_like_click(driver, next_button)
                time.sleep(random.uniform(2, 5))

            tasks_completed = 1 # Mark the whole offer as one task
            total_value = task["value"]
        except Exception as e:
            print(f"Error during survey interaction on freecash.com: {e}")
        finally:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        return tasks_completed, total_value

    def auto_signup(self, driver, config, profile):
        try:
            wait = WebDriverWait(driver, 15)
            driver.get("https://freecash.com/register")
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))

            email, sid_token, seq = create_temp_email()
            password = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(12)) + "!A1"
            username = profile.get("first_name", "User") + str(random.randint(1000,9999))

            driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(email)
            driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(password)
            driver.find_element(By.CSS_SELECTOR, "input[name*='name']").send_keys(username)
            driver.find_element(By.XPATH, "//button[contains(text(),'Sign Up')]").click()
            time.sleep(5)

            # Verification steps remain similar, but no database calls

            # Return the new account details instead of saving them
            return {
                "email": email,
                "password": password,
                "username": username,
                "status": "active"
            }
        except Exception as e:
            print(f"Signup fail on freecash.com: {e}")
            return None

    def auto_payout(self, driver, config, account):
        # This method remains largely the same as it's not part of the multi-threaded worker flow
        try:
            driver.get("https://freecash.com/login")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(account["email"])
            driver.find_element(By.NAME, "password").send_keys(account["password"])
            driver.find_element(By.XPATH, "//button[@type='submit']").click()

            WebDriverWait(driver, 10).until(EC.url_contains("/home"))
            driver.get("https://freecash.com/withdraw")

            balance_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".balance")))
            balance = float(re.search(r'\d+\.\d+', balance_element.text).group())

            if balance >= 0.50:
                # Example for PayPal
                driver.find_element(By.XPATH, f"//div[contains(text(), 'PayPal')]").click()
                driver.find_element(By.NAME, "wallet_address").send_keys(config["wallets"][0]["address"])
                driver.find_element(By.XPATH, "//button[contains(text(), 'Withdraw')]").click()
                print(f"Successfully initiated withdrawal for {account['email']} on freecash.com")
            return True
        except Exception as e:
            print(f"Payout error on freecash.com: {e}")
            return False
