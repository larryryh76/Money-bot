from .base_parser import BaseParser
from selenium.webdriver.common.by import By
import re

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
