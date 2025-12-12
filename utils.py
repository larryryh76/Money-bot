import importlib
import requests
import time
import json
import random

def get_parser(site):
    """Dynamically loads the parser for a given site."""
    try:
        module_name = f"parsers.{site.replace('.', '_')}"
        class_name = "".join([s.capitalize() for s in site.split('.')]) + "Parser"
        module = importlib.import_module(module_name)
        return getattr(module, class_name)()
    except (ImportError, AttributeError):
        return None

def ai_or_random_answer(config, account_id, question, context="", options=None, profile=None):
    # This function is now in utils.py and needs access to the config and database
    from database_manager import get_persona_answer, save_persona_answer

    # Check if we have answered this question before for this account
    previous_answer = get_persona_answer(account_id, question)
    if previous_answer:
        return previous_answer

    # If not, generate a new answer
    if config["API_KEY"]:
        try:
            profile_str = json.dumps(profile) if profile else ""
            if options:
                prompt = f"Profile: {profile_str}\n\nContext: {context}\n\nQuestion: {question}\n\nOptions: {', '.join(options)}\n\nSelect the best option based on the profile."
            else:
                prompt = f"Profile: {profile_str}\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer in 1-5 words based on the profile."

            resp = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                 headers={"Authorization": f"Bearer {config['API_KEY']}"},
                                 json={"model": config.get("ai_model", "deepseek/deepseek-r1:free"),
                                       "messages": [{"role": "user", "content": prompt}],
                                       "max_tokens": 15}).json()
            answer = resp['choices'][0]['message']['content'].strip()
            save_persona_answer(account_id, question, answer)
            return answer
        except requests.exceptions.RequestException as e:
            print(f"Error calling OpenRouter API: {e}")

    # Fallback to random answer
    answer = random.choice(options) if options else random.choice(["Yes", "No", "Sometimes", "Once a week", "Agree"])
    save_persona_answer(account_id, question, answer)
    return answer

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
