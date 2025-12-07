import requests
import time

def get_phone_number():
    """Gets a temporary phone number from a free service."""
    try:
        response = requests.get("https://api.temp-mail.org/request/phone/format/json")
        data = response.json()
        return data[0]['phone']
    except requests.exceptions.RequestException as e:
        print(f"Error getting phone number: {e}")
        return None

def get_sms_code(phone_number):
    """Gets the latest SMS code for a given phone number."""
    try:
        # Wait a bit for the SMS to arrive
        time.sleep(15)
        response = requests.get(f"https://api.temp-mail.org/request/sms/format/json?phone={phone_number}")
        data = response.json()
        if data:
            # Extract the 6-digit code from the message
            import re
            match = re.search(r'\d{6}', data[0]['sms'])
            if match:
                return match.group(0)
    except requests.exceptions.RequestException as e:
        print(f"Error getting SMS code: {e}")
    return None
