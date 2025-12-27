import time, random, requests, threading, os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent

import json

# Load config
with open("config.json") as f:
    config = json.load(f)

API_KEY = config.get("api_key", "")
WALLET = config.get("wallet", "")
THREADS = config.get("threads", 90)

from bs4 import BeautifulSoup

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.ready = threading.Event()
        self.lock = threading.Lock()
        self.fetch_thread = threading.Thread(target=self._fetch_proxies_thread, daemon=True)

    def start(self):
        self.fetch_thread.start()

    def _fetch_proxies_thread(self):
        try:
            print("Fetching proxies in background...")
            response = requests.get("https://free-proxy-list.net/")
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table", attrs={"class": "table table-striped table-bordered"})
            new_proxies = []
            for row in table.find_all("tr")[1:]:
                tds = row.find_all("td")
                ip = tds[0].text.strip()
                port = tds[1].text.strip()
                new_proxies.append(f"http://{ip}:{port}")
            with self.lock:
                self.proxies = new_proxies
            print(f"Successfully fetched {len(new_proxies)} proxies.")
        except Exception as e:
            print(f"Failed to fetch proxies: {e}")
        finally:
            # Signal that fetching is complete, even if it failed, to unblock waiters
            self.ready.set()

    def get_proxy(self):
        # Wait for the initial fetch to complete
        self.ready.wait()
        with self.lock:
            if self.proxies:
                return random.choice(self.proxies)
        return None

# Load sites
with open("sites.json") as f:
    SITE_PATHS = json.load(f)

def ai_or_random_answer(question, context="", options=None):
    if API_KEY:
        try:
            if options:
                prompt = f"Context: {context}\n\nQuestion: {question}\n\nOptions: {', '.join(options)}\n\nSelect the best option."
            else:
                prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer in 1-5 words as a random adult."

            resp = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                 headers={"Authorization": f"Bearer {API_KEY}"},
                                 json={"model": "deepseek/deepseek-r1:free",
                                       "messages": [{"role": "user", "content": prompt}],
                                       "max_tokens": 15}).json()
            return resp['choices'][0]['message']['content'].strip()
        except requests.exceptions.RequestException as e:
            print(f"Error calling OpenRouter API: {e}")

    if options:
        return random.choice(options)
    return random.choice(["Yes", "No", "Sometimes", "Once a week", "Agree"])

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
                except:
                    try:
                        # Multiple choice
                        option_elements = question_element.find_elements(By.XPATH, "./following::input[@type='radio'] | ./following::input[@type='checkbox']")
                        option_labels = [opt.find_element(By.XPATH, "./following-sibling::label").text for opt in option_elements]
                        answer = ai_or_random_answer(question_text, context, options=option_labels)
                        for opt in option_elements:
                            if opt.find_element(By.XPATH, "./following-sibling::label").text == answer:
                                opt.click()
                                break
                    except:
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
                        except:
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
    def __init__(self, proxy_manager):
        self.proxy_manager = proxy_manager

    def run(self):
        # Optimization: Wait for proxies before starting, but do it inside the thread
        # This allows other threads to initialize while waiting.
        self.proxy_manager.ready.wait()
        while True:
            try:
                proxy = self.proxy_manager.get_proxy()
                ua = UserAgent()
                options = Options()
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument(f'--user-agent={ua.random}')
                if proxy: options.add_argument(f'--proxy-server={proxy}')
                service = Service('/usr/bin/chromedriver')  # Explicit path in Selenium image
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
        print(f"Starting {THREADS} accounts...")
        for i in range(THREADS):
            threading.Thread(target=self.run, daemon=True).start()
            # Optimization: Reduced sleep from 10s to 0.5s.
            # A long sleep here creates an unnecessary startup delay.
            # A small delay is kept to avoid overwhelming services at startup.
            time.sleep(0.5)

        while True:
            time.sleep(3600)

if __name__ == "__main__":
    proxy_manager = ProxyManager()
    proxy_manager.start()
    bot = Bot(proxy_manager)
    bot.start()
