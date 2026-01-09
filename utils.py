import requests
import time
import random

def create_temp_email():
    resp = requests.get("https://api.guerrillamail.com/ajax.php?f=get_email_address")
    data = resp.json()
    return data['email_addr'], data['sid_token'], data['seq']

def fetch_email_code(sid_token, seq):
    time.sleep(5)
    resp = requests.get(f"https://api.guerrillamail.com/ajax.php?f=check_email&seq={seq}&sid_token={sid_token}")
    if resp.json()['list']:
        mail_id = resp.json()['list'][0]['mail_id']
        fetch_resp = requests.get(f"https://api.guerrillamail.com/ajax.php?f=fetch_email&email_id={mail_id}&sid_token={sid_token}")
        body = fetch_resp.json()['email']['body']
        code = ''.join(c for c in body if c.isdigit())[-6:]
        return code
    return str(random.randint(100000, 999999))

def ai_or_random_answer(question, context="", options=None, api_key=""):
    if api_key:
        try:
            if options:
                prompt = f"Context: {context}\n\nQuestion: {question}\n\nOptions: {', '.join(options)}\n\nSelect the best option."
            else:
                prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer in 1-5 words as a random adult."

            resp = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                 headers={"Authorization": f"Bearer {api_key}"},
                                 json={"model": "deepseek/deepseek-r1:free",
                                       "messages": [{"role": "user", "content": prompt}],
                                       "max_tokens": 15}).json()
            return resp['choices'][0]['message']['content'].strip()
        except requests.exceptions.RequestException as e:
            print(f"Error calling OpenRouter API: {e}")

    if options:
        return random.choice(options)
    return random.choice(["Yes", "No", "Sometimes", "Once a week", "Agree"])
