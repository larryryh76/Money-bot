from .base_parser import BaseParser
from selenium.webdriver.common.by import By
import re
import time
import random

class FreecashComParser(BaseParser):
    def find_offers(self, driver):
        offers = []
        offer_elements = driver.find_elements(By.CSS_SELECTOR, ".offer-wall-item")
        for offer_element in offer_elements:
            try:
                offer_text = offer_element.text
                value = float(re.search(r'\$(\d+\.\d+)', offer_text).group(1))
                time_match = re.search(r'(\d+)\s*min', offer_text)
                time_to_complete = int(time_match.group(1)) if time_match else 10
                offers.append({
                    "id": offer_element.id,
                    "site": "freecash.com",
                    "value": value,
                    "time_to_complete": time_to_complete,
                    "element": offer_element
                })
            except:
                pass
        return offers

    def do_task(self, driver, task, profile):
        tasks_completed = 0
        retries = 3

        task["element"].click()
        driver.implicitly_wait(10)

        for _ in range(5): # Attempt to complete 5 tasks within the offer
            try:
                # Find a question on the page
                question_element = driver.find_element(By.CSS_SELECTOR, "label, p, h1, h2, h3")
                question_text = question_element.text

                # Find the input field associated with the question
                input_field = None
                try:
                    input_field = question_element.find_element(By.XPATH, "./following::input[@type='text']")
                except:
                    # If no text input, look for multiple choice
                    pass

                if input_field and input_field.is_displayed():
                    answer = ai_or_random_answer(question_text, driver.page_source, profile=profile)
                    input_field.send_keys(answer)
                else:
                    # Handle multiple choice questions
                    options = question_element.find_elements(By.XPATH, "./following::div[@class='option']")
                    if options:
                        random.choice(options).click()

                # Click the next button
                driver.find_element(By.XPATH, "//button[contains(text(),'Next')]").click()

                time.sleep(random.uniform(5, 10))
                tasks_completed += 1
                retries = 3 # Reset retries after a successful task
            except Exception as e:
                print(f"Error during task on freecash.com: {e}")
                retries -= 1
                if retries == 0:
                    break # Stop trying if we fail 3 times in a row

        return tasks_completed
