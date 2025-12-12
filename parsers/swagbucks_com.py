from .base_parser import BaseParser
from selenium.webdriver.common.by import By
import re
import time
import random
from utils import ai_or_random_answer, create_temp_email, fetch_email_code
from database_manager import save_accounts, load_accounts
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
                value = float(re.search(r'(\d+)\s*SB', offer_text).group(1)) / 100 # Convert SB to dollars
                time_match = re.search(r'(\d+)\s*min', offer_text)
                time_to_complete = int(time_match.group(1)) if time_match else 10

                # Generate a unique XPath for the element
                xpath = f"(//div[contains(@class, 'offer-item')])[{i+1}]"

                offers.append({
                    "id": offer_element.id,
                    "site": "swagbucks.com",
                    "value": value,
                    "time_to_complete": time_to_complete,
                    "xpath": xpath
                })
            except:
                pass
        return offers

    def do_task(self, driver, task, profile, account_id, config):
        tasks_completed = 0
        total_value = 0
        retries = 3

        try:
            offer_element = driver.find_element(By.XPATH, task["xpath"])
            self.human_like_click(driver, offer_element)
            driver.implicitly_wait(10)
        except Exception as e:
            print(f"Could not find offer element: {e}")
            return 0, 0

        for _ in range(5): # Attempt to complete 5 tasks within the offer
            try:
                # Find a question on the page
                question_element = driver.find_element(By.CSS_SELECTOR, "div.question-text")
                question_text = question_element.text

                # Find the input field associated with the question
                input_field = None
                try:
                    input_field = question_element.find_element(By.XPATH, "./following::input[@type='text']")
                except:
                    # If no text input, look for multiple choice
                    pass

                if input_field and input_field.is_displayed():
                    answer = ai_or_random_answer(config, account_id, question_text, driver.page_source, profile=profile)
                    self.human_like_send_keys(driver, input_field, answer)
                else:
                    # Handle multiple choice questions
                    options = question_element.find_elements(By.CSS_SELECTOR, "div.answer-option")
                    if options:
                        self.human_like_click(driver, random.choice(options))

                # Click the next button
                next_button = driver.find_element(By.ID, "btnNext")
                self.human_like_click(driver, next_button)

                time.sleep(random.uniform(5, 10))
                tasks_completed += 1
                total_value += task["value"] / 5 # Assuming 5 tasks per offer
                retries = 3 # Reset retries after a successful task
            except Exception as e:
                print(f"Error during task on swagbucks.com: {e}")
                retries -= 1
                if retries == 0:
                    break # Stop trying if we fail 3 times in a row

        return tasks_completed, total_value

    def auto_signup(self, driver, config, profile):
        try:
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located((By.ID, "sbxJxRegEmail")))

            email, sid_token, seq = create_temp_email()
            password = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(12)) + "!A1"

            driver.find_element(By.ID, "sbxJxRegEmail").send_keys(email)
            driver.find_element(By.ID, "sbxJxRegPswd").send_keys(password)
            driver.find_element(By.ID, "sbxJxRegPswdConfirm").send_keys(password)
            driver.find_element(By.ID, "login-now-btn").click()
            time.sleep(5)

            if "verify" in driver.page_source.lower():
                code = fetch_email_code(sid_token, seq)
                driver.find_element(By.CSS_SELECTOR, "input[name*='code']").send_keys(code)
                driver.find_element(By.XPATH, "//button[contains(text(),'Verify')]").click()

            new_account = {
                "site": "swagbucks.com",
                "email": email,
                "password": password,
                "username": email, # Swagbucks uses email as username
                "profile": profile,
                "status": "active"
            }

            accounts = load_accounts()
            accounts.append(new_account)
            save_accounts(accounts)
            return True
        except Exception as e:
            print(f"Signup fail on swagbucks.com: {e}")
            return False

    def auto_payout(self, driver, config, account):
        try:
            # Basic login
            driver.get("https://www.swagbucks.com/p/login")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "sbxJxLoginEmail"))).send_keys(account["email"])
            driver.find_element(By.ID, "sbxJxLoginPswd").send_keys(account["password"])
            driver.find_element(By.ID, "login-btn").click()

            # Navigate to withdrawal page
            WebDriverWait(driver, 10).until(EC.url_contains("swagbucks.com"))
            driver.get("https://www.swagbucks.com/rewards-store")

            # Check balance
            balance_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "sbBalance")))
            balance = float(balance_element.text.replace("SB", "").replace(",", "")) / 100

            if balance >= 5.00: # Swagbucks min payout
                # Select wallet (example for PayPal)
                driver.find_element(By.XPATH, f"//a[contains(@href, 'PayPal')]").click()
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "redeemBtn"))).click()
                print(f"Successfully initiated withdrawal for {account['email']} on swagbucks.com")
            return True
        except Exception as e:
            print(f"Payout error on swagbucks.com: {e}")
            return False
