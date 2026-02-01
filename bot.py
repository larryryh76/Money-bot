import json
import random
import threading
import time

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load config
with open("config.json") as f:
    config = json.load(f)

API_KEY = config.get("api_key", "")
WALLET = config.get("wallet", "")
THREADS = config.get("threads", 90)

# Initialize shared session for connection pooling
session = requests.Session()
adapter = HTTPAdapter(pool_connections=THREADS, pool_maxsize=THREADS)
session.mount("http://", adapter)
session.mount("https://", adapter)
DEFAULT_TIMEOUT = 30

def fetch_proxies():
    proxies = []
    try:
        response = session.get("https://free-proxy-list.net/", timeout=DEFAULT_TIMEOUT)
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", attrs={"class": "table table-striped table-bordered"})
        if table:
            for row in table.find_all("tr")[1:]:
                tds = row.find_all("td")
                if len(tds) >= 2:
                    ip = tds[0].text.strip()
                    port = tds[1].text.strip()
                    proxies.append(f"http://{ip}:{port}")
    except Exception as e:
        print(f"Failed to fetch proxies: {e}")
    return proxies

PROXIES = []
proxies_ready = threading.Event()

def update_proxies_loop():
    global PROXIES
    while True:
        try:
            new_proxies = fetch_proxies()
            if new_proxies:
                PROXIES = new_proxies
                print(f"Proxy list updated: {len(PROXIES)} proxies available.")
        finally:
            proxies_ready.set()
        time.sleep(1800)

# Load sites
with open("sites.json") as f:
    SITE_PATHS = json.load(f)

def get_proxy():
    if PROXIES:
        return random.choice(PROXIES)
    return None

def ai_or_random_answer(question, context="", options=None):
    if API_KEY:
        try:
            if options:
                prompt = f"Context: {context}\n\nQuestion: {question}\n\nOptions: {', '.join(options)}\n\nSelect the best option."
            else:
                prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer in 1-5 words as a random adult."

            resp = session.post("https://openrouter.ai/api/v1/chat/completions",
                                 headers={"Authorization": f"Bearer {API_KEY}"},
                                 json={"model": "deepseek/deepseek-r1:free",
                                       "messages": [{"role": "user", "content": prompt}],
                                       "max_tokens": 15},
                                 timeout=DEFAULT_TIMEOUT).json()
            return resp['choices'][0]['message']['content'].strip()
        except requests.exceptions.RequestException as e:
            print(f"Error calling OpenRouter API: {e}")

    if options:
        return random.choice(options)
    return random.choice(["Yes", "No", "Sometimes", "Once a week", "Agree"])

def create_temp_email():
    resp = session.get("https://api.guerrillamail.com/ajax.php?f=get_email_address", timeout=DEFAULT_TIMEOUT)
    data = resp.json()
    return data['email_addr'], data['sid_token'], data['seq']

def fetch_email_code(sid_token, seq):
    time.sleep(5)
    resp = session.get(f"https://api.guerrillamail.com/ajax.php?f=check_email&seq={seq}&sid_token={sid_token}", timeout=DEFAULT_TIMEOUT)
    if resp.json()['list']:
        mail_id = resp.json()['list'][0]['mail_id']
        fetch_resp = session.get(f"https://api.guerrillamail.com/ajax.php?f=fetch_email&email_id={mail_id}&sid_token={sid_token}", timeout=DEFAULT_TIMEOUT)
        body = fetch_resp.json()['email']['body']
        code = ''.join(c for c in body if c.isdigit())[-6:]
        return code
    return str(random.randint(100000, 999999))

def auto_signup(driver, site):
    try:
        paths = SITE_PATHS[site]
        driver.get(f"https://{site}{paths['signup']}")
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        email, sid_token, seq = create_temp_email()
        driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(email)
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys("TempPass123!")
        driver.find_element(By.CSS_SELECTOR, "input[name*='name']").send_keys(f"User{random.randint(1000,9999)}")
        driver.find_element(By.XPATH, "//button[contains(text(),'Sign Up')]").click()
        time.sleep(5)
        if "verify" in driver.page_source.lower():
            code = fetch_email_code(sid_token, seq)
            driver.find_element(By.CSS_SELECTOR, "input[name*='code']").send_keys(code)
            driver.find_element(By.XPATH, "//button[contains(text(),'Verify')]").click()
        print(f"Account created on {site}: {email}")
        return True
    except Exception as e:
        print(f"Signup fail {site}: {e}")
        return False

def do_tasks(driver, site):
    paths = SITE_PATHS[site]
    tasks = 0
    retries = 3
    driver.get(f"https://{site}{paths['tasks']}")
    time.sleep(10)
    for _ in range(5):
        try:
            question_element = driver.find_element(By.CSS_SELECTOR, "label, span, p, h1, h2, h3")
            question_text = question_element.text
            if question_text:
                context = driver.page_source

                # Check for different input types near the question
                try:
                    # Text input
                    input_field = question_element.find_element(By.XPATH, "./following::input[@type='text'] | ./following::textarea")
                    answer = ai_or_random_answer(question_text, context)
                    input_field.send_keys(answer)
                except Exception:
                    try:
                        # Multiple choice
                        option_elements = question_element.find_elements(By.XPATH, "./following::input[@type='radio'] | ./following::input[@type='checkbox']")
                        option_labels = [opt.find_element(By.XPATH, "./following-sibling::label").text for opt in option_elements]
                        answer = ai_or_random_answer(question_text, context, options=option_labels)
                        for opt in option_elements:
                            if opt.find_element(By.XPATH, "./following-sibling::label").text == answer:
                                opt.click()
                                break
                    except Exception:
                        try:
                            # Dropdown
                            select = question_element.find_element(By.XPATH, "./following::select")
                            option_elements = select.find_elements(By.TAG_NAME, "option")
                            option_labels = [opt.text for opt in option_elements]
                            answer = ai_or_random_answer(question_text, context, options=option_labels)
                            for opt in option_elements:
                                if opt.text == answer:
                                    opt.click()
                                    break
                        except Exception:
                            pass
                time.sleep(1)

            btn = driver.find_element(By.XPATH, "//button[contains(text(),'Start') or contains(text(),'Next') or contains(text(),'Play')] | //a[contains(@href,'offer')]")
            btn.click()
            time.sleep(random.uniform(10, 25))
            tasks += 1
            retries = 3 # Reset retries after a successful task
        except Exception as e:
            print(f"Error in do_tasks: {e}")
            retries -= 1
            if retries == 0:
                break
    return tasks

def auto_payout(driver, site):
    paths = SITE_PATHS[site]
    min_bal = paths['min']
    driver.get(f"https://{site}{paths['withdraw']}")
    time.sleep(10)
    try:
        balance_str = driver.find_element(By.CSS_SELECTOR, ".balance, [class*='balance']").text.replace("$", "").strip()
        balance = float(balance_str) if balance_str.replace(".", "").isdigit() else 0
        if balance >= min_bal:
            driver.find_element(By.XPATH, "//button[contains(text(),'Crypto') or contains(text(),'BTC') or contains(text(),'Cash Out')]").click()
            time.sleep(3)
            driver.find_element(By.CSS_SELECTOR, "input[placeholder*='address']").send_keys(WALLET)
            driver.find_element(By.XPATH, "//button[contains(text(),'Withdraw') or contains(text(),'Confirm')]").click()
            print(f"Payout ${balance} from {site} to {WALLET}")
            return True
        print(f"${balance} < ${min_bal} on {site}")
    except Exception as e:
        print(f"Payout error {site}: {e}")
    return False

class Bot:
    def __init__(self):
        self.ua = UserAgent()

    def run(self):
        proxies_ready.wait()
        # Initial jitter to stagger worker start times further
        time.sleep(random.uniform(1, 10))
        while True:
            try:
                proxy = get_proxy()
                options = Options()
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument(f'--user-agent={self.ua.random}')
                if proxy:
                    options.add_argument(f'--proxy-server={proxy}')
                # Use default service to allow Selenium Manager to handle driver location
                service = Service()
                driver = webdriver.Chrome(service=service, options=options)

                site = random.choice(list(SITE_PATHS.keys()))
                print(f"→ Working on {site}")

                if auto_signup(driver, site):
                    tasks = do_tasks(driver, site)
                    print(f"Completed {tasks} tasks on {site}")
                    auto_payout(driver, site)

                driver.quit()
            except Exception as e:
                print("Error:", e)
            
            time.sleep(random.randint(1800, 3600))

    def start(self):
        print("Starting background proxy manager...")
        threading.Thread(target=update_proxies_loop, daemon=True).start()

        print(f"Starting {THREADS} accounts with staggered delay...")
        for i in range(THREADS):
            threading.Thread(target=self.run, daemon=True).start()
            # Reduced from 10s to 1s for faster startup,
            # while still avoiding massive resource spikes
            time.sleep(1.0)

        while True:
            time.sleep(3600)

if __name__ == "__main__":
    bot = Bot()
    bot.start()
