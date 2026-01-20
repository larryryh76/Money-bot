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

def is_attention_check(question, options, context, api_key):
    """
    Uses an AI model to determine if a question is an attention check and returns the correct answer.
    """
    if not api_key or not options:
        return None

    prompt = (
        "You are an expert at identifying attention check questions in online surveys. "
        "Analyze the following question, its options, and the surrounding HTML context. "
        "If it is a clear attention check (e.g., 'select the color blue', 'what is 2+2?', 'select the third option'), "
        "return ONLY the text of the correct option from the list provided. "
        "If it is not an attention check, return the exact phrase 'Not an attention check'.\n\n"
        f"Question: {question}\n\n"
        f"Options: {', '.join(options)}\n\n"
        f"Context (HTML snippet): {context[:2000]}"
    )

    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "deepseek/deepseek-r1:free",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 50,
                "temperature": 0.1
            },
        ).json()

        answer = resp['choices'][0]['message']['content'].strip().strip('"')

        if "Not an attention check" not in answer and answer in options:
            print(f"Attention check detected! Question: '{question}'. Correct answer: '{answer}'")
            return answer
        else:
            return None

    except (requests.exceptions.RequestException, KeyError) as e:
        print(f"Error calling OpenRouter API for attention check: {e}")
        return None

def ai_or_random_answer(question, context="", options=None, api_key=""):
    # First, check for attention checks
    attention_answer = is_attention_check(question, options, context, api_key)
    if attention_answer:
        return attention_answer

    # If not an attention check, proceed as normal
    if api_key:
        try:
            if options:
                prompt = f"Context: {context}\n\nQuestion: {question}\n\nOptions: {', '.join(options)}\n\nSelect the best option based on a consistent persona."
            else:
                prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer in 1-5 words as a random adult."

            resp = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                 headers={"Authorization": f"Bearer {api_key}"},
                                 json={"model": "deepseek/deepseek-r1:free",
                                       "messages": [{"role": "user", "content": prompt}],
                                       "max_tokens": 15}).json()
            return resp['choices'][0]['message']['content'].strip()
        except (requests.exceptions.RequestException, KeyError) as e:
            print(f"Error calling OpenRouter API: {e}")

    if options:
        return random.choice(options)
    return random.choice(["Yes", "No", "Sometimes", "Once a week", "Agree"])
