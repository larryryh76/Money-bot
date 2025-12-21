from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time
import random
import base64
import requests
from humancursor.web_cursor import WebCursor
from visual_annotator import VisualAnnotator

class BaseParser:
    def find_offers(self, driver):
        # This method will be deprecated in favor of the new visual AI approach
        raise NotImplementedError

    def do_task(self, driver, objective, config):
        """
        Performs a task on the page using a multimodal AI to interpret the screen.
        """
        try:
            # 1. Annotate the screen
            annotator = VisualAnnotator()
            annotation_script = annotator.get_annotation_script()
            driver.execute_script(annotation_script)

            # 2. Take a screenshot
            screenshot_base64 = driver.get_screenshot_as_base64()

            # 3. Send to Multimodal AI
            headers = {
                "Authorization": f"Bearer {config['API_KEY']}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "openai/gpt-4o", # Or another powerful multimodal model
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"Based on the screenshot, which label should I click to achieve the following objective: '{objective}'? Respond with only the single character of the label."},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"}}
                        ]
                    }
                ],
                "max_tokens": 5
            }

            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()

            ai_response = response.json()['choices'][0]['message']['content'].strip()

            # 4. Execute the AI's decision
            target_label = ai_response
            print(f"AI decided to click label: {target_label}")

            target_element = driver.find_element(By.CSS_SELECTOR, f"[data-bot-target='{target_label}']")

            if target_element:
                self.human_like_click(driver, target_element)
                return True
            else:
                print(f"Could not find element with label: {target_label}")
                return False

        except Exception as e:
            print(f"An error occurred during the visual AI task: {e}")
            return False

    def human_like_click(self, driver, element):
        cursor = WebCursor(driver)
        cursor.move_to(element)
        time.sleep(random.uniform(0.1, 0.4))
        element.click()

    def human_like_send_keys(self, driver, element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))

    def auto_signup(self, driver, config, profile):
        raise NotImplementedError

    def auto_payout(self, driver, config, account):
        raise NotImplementedError
