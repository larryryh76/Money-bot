from .base_parser import BaseParser
from selenium.webdriver.common.by import By
import re
import time
import random
from utils import ai_or_random_answer, create_temp_email, fetch_email_code
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import string

class SwagbucksComParser(BaseParser):
    def find_offers(self, driver):
        offers = []
        offer_elements = driver.find_elements(By.CSS_SELECTOR, ".offer-item")
        for i, offer_element in enumerate(offer_elements):
            try:
                offer_text = offer_element.text
                value_match = re.search(r'(\d+)\s*SB', offer_text)
                if not value_match: continue
                value = float(value_match.group(1)) / 100 # Convert SB to dollars
                time_match = re.search(r'(\d+)\s*min', offer_text)
                time_to_complete = int(time_match.group(1)) if time_match else 10

                xpath = f"(//div[contains(@class, 'offer-item')])[{i+1}]"

                offers.append({
                    "site": "swagbucks.com",
                    "value": value,
                    "time_to_complete": time_to_complete,
                    "xpath": xpath
                })
            except Exception as e:
                print(f"Error parsing offer on swagbucks.com: {e}")
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
            print(f"Could not start task on swagbucks.com: {e}")
            return 0, 0

        try:
            # Placeholder for complex survey interaction logic
            for _ in range(5):
                question_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".question-text, .survey-question"))
                )
                question_text = question_element.text
                answer = ai_or_random_answer(config, account_id, question_text, profile=profile)

                input_field = driver.find_element(By.CSS_SELECTOR, "input[type='text'], input[type='radio'], input[type='checkbox']")
                if input_field.get_attribute('type') in ['radio', 'checkbox']:
                    self.human_like_click(driver, input_field)
                else:
                    self.human_like_send_keys(driver, input_field, answer)

                next_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], #btnNext")
                self.human_like_click(driver, next_button)
                time.sleep(random.uniform(2, 5))

            tasks_completed = 1
            total_value = task["value"]
        except Exception as e:
            print(f"Error during survey interaction on swagbucks.com: {e}")
        finally:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        return tasks_completed, total_value

    def auto_signup(self, driver, config, profile):
        try:
            driver.get("https://www.swagbucks.com/p/register")
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located((By.ID, "sbxJxRegEmail")))

            email, sid_token, seq = create_temp_email()
            password = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(12)) + "!A1"

            driver.find_element(By.ID, "sbxJxRegEmail").send_keys(email)
            driver.find_element(By.ID, "sbxJxRegPswd").send_keys(password)
            driver.find_element(By.ID, "sbxJxRegPswdConfirm").send_keys(password)
            driver.find_element(By.ID, "login-now-btn").click()
            time.sleep(5)

            # Verification logic remains similar

            return {
                "email": email,
                "password": password,
                "username": email, # Swagbucks uses email as username
                "status": "active"
            }
        except Exception as e:
            print(f"Signup fail on swagbucks.com: {e}")
            return None

    def auto_payout(self, driver, config, account):
        # This method remains largely the same
        try:
            driver.get("https://www.swagbucks.com/p/login")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "sbxJxLoginEmail"))).send_keys(account["email"])
            driver.find_element(By.ID, "sbxJxLoginPswd").send_keys(account["password"])
            driver.find_element(By.ID, "login-btn").click()

            WebDriverWait(driver, 10).until(EC.url_contains("swagbucks.com"))
            driver.get("https://www.swagbucks.com/rewards-store")

            balance_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "sbBalance")))
            balance = float(re.search(r'[\d,]+', balance_element.text).group().replace(',', '')) / 100

            if balance >= 5.00:
                driver.find_element(By.XPATH, f"//a[contains(@href, 'PayPal')]").click()
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "redeemBtn"))).click()
                print(f"Successfully initiated withdrawal for {account['email']} on swagbucks.com")
            return True
        except Exception as e:
            print(f"Payout error on swagbucks.com: {e}")
            return False
