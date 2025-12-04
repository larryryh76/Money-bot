import time, random, requests, threading, os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from ai_manager import OperationsAI, EvolutionAI
from proxy_manager import ProxyManager

import json

# Load config
with open("config.json") as f:
    config = json.load(f)

API_KEY = config.get("api_key", "")
WALLET = config.get("wallet", "")
THREADS = config.get("threads", 90)
THREAD_DELAY = config.get("thread_delay", 10)
CASHOUT_CHECK_INTERVAL = config.get("cashout_check_interval", 3600)
CHROMEDRIVER_PATH = config.get("chromedriver_path", "/usr/bin/chromedriver")

# Load sites
with open("sites.json") as f:
    SITE_PATHS = json.load(f)

proxy_manager = ProxyManager()
proxy_manager.fetch_proxies()
proxy_manager.test_proxies()

def get_proxy():
    return proxy_manager.get_proxy()

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

def load_accounts():
    try:
        with open("accounts.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_accounts(accounts):
    with open("accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

def write_log(log_entry):
    try:
        with open("logs.json", "r+") as f:
            logs = json.load(f)
            logs.append(log_entry)
            f.seek(0)
            json.dump(logs, f, indent=2)
    except (FileNotFoundError, json.JSONDecodeError):
        with open("logs.json", "w") as f:
            json.dump([log_entry], f, indent=2)

class Bot:
    def __init__(self):
        self.last_cashout_check = {}
        self.operations_ai = OperationsAI()
        self.evolution_ai = EvolutionAI()
        self.task_queue = self.operations_ai.manage_tasks()

    def auto_signup(self, driver, site):
        accounts = load_accounts()

        # Try to find an existing account for the site
        for account in accounts:
            if account["site"] == site:
                try:
                    paths = SITE_PATHS[site]
                    if "login" in paths:
                        driver.get(f"https://{site}{paths['login']}")
                        wait = WebDriverWait(driver, 15)
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
                        driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(account["email"])
                        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(account["password"])
                        driver.find_element(By.XPATH, "//button[contains(text(),'Login')]").click()
                        time.sleep(5)
                        return True
                except Exception as e:
                    print(f"Login fail {site}: {e}")
                    return False

        # Create a new account if none exists
        try:
            paths = SITE_PATHS[site]
            driver.get(f"https://{site}{paths['signup']}")
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
            email, sid_token, seq = create_temp_email()
            password = "TempPass123!"
            username = f"User{random.randint(1000,9999)}"

            driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(email)
            driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(password)
            driver.find_element(By.CSS_SELECTOR, "input[name*='name']").send_keys(username)
            driver.find_element(By.XPATH, "//button[contains(text(),'Sign Up')]").click()
            time.sleep(5)
            if "verify" in driver.page_source.lower():
                code = fetch_email_code(sid_token, seq)
                driver.find_element(By.CSS_SELECTOR, "input[name*='code']").send_keys(code)
                driver.find_element(By.XPATH, "//button[contains(text(),'Verify')]").click()
            
            accounts.append({"site": site, "email": email, "password": password, "username": username})
            save_accounts(accounts)
            print(f"Account created on {site}: {email}")
            return True
        except Exception as e:
            print(f"Signup fail {site}: {e}")
            return False

    def do_tasks(self, driver, site):
        paths = SITE_PATHS[site]
        tasks = 0
        retries = 3
        driver.get(f"https://{site}{paths['tasks']}")
        time.sleep(10)
        for _ in range(5):
            success = False
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
                        success = True
                    except:
                        try:
                            # Multiple choice
                            option_elements = question_element.find_elements(By.XPATH, "./following::input[@type='radio'] | ./following::input[@type='checkbox']")
                            option_labels = [opt.find_element(By.XPATH, "./following-sibling::label").text for opt in option_elements]
                            answer = ai_or_random_answer(question_text, context, options=option_labels)
                            for opt in option_elements:
                                if opt.find_element(By.XPATH, "./following-sibling::label").text == answer:
                                    opt.click()
                                    success = True
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
                                        success = True
                                        break
                            except:
                                pass
                    time.sleep(self.evolution_ai.parameters["action_delay"])

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

            write_log({"site": site, "timestamp": time.time(), "success": success})

        return tasks
        
    def auto_payout(self, driver, site):
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

    def run(self):
        consecutive_failures = {}
        while True:
            try:
                if not self.task_queue:
                    self.task_queue = self.operations_ai.manage_tasks()

                if not self.task_queue:
                    time.sleep(60)
                    continue

                site = self.task_queue.pop(0)

                proxy = get_proxy()
                ua = UserAgent()
                options = Options()
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument(f"--window-size={random.randint(1024, 1920)},{random.randint(768, 1080)}")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                options.add_argument(f'--user-agent={ua.random}')
                if proxy: options.add_argument(f'--proxy-server={proxy}')
                service = Service(CHROMEDRIVER_PATH)
                driver = webdriver.Chrome(service=service, options=options)

                print(f"→ Working on {site}")

                if self.auto_signup(driver, site):
                    tasks = self.do_tasks(driver, site)
                    print(f"Completed {tasks} tasks on {site}")

                    if site not in self.last_cashout_check or time.time() - self.last_cashout_check[site] > CASHOUT_CHECK_INTERVAL:
                        self.auto_payout(driver, site)
                        self.last_cashout_check[site] = time.time()

                    consecutive_failures[site] = 0
                else:
                    if site not in consecutive_failures:
                        consecutive_failures[site] = 0
                    consecutive_failures[site] += 1
                    if consecutive_failures[site] >= 3:
                        self.operations_ai.cooldown_sites[site] = time.time()

                driver.quit()
            except Exception as e:
                print("Error:", e)

            time.sleep(random.randint(1800, 3600))

    def integrate_new_sites(self):
        new_sites = self.evolution_ai.innovate()
        for site in new_sites:
            if site not in SITE_PATHS:
                print(f"Attempting to integrate new site: {site}")
                try:
                    # Attempt to sign up and do a task
                    proxy = get_proxy()
                    ua = UserAgent()
                    options = Options()
                    options.add_argument('--headless')
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    options.add_argument('--disable-gpu')
                    options.add_argument(f'--user-agent={ua.random}')
                    if proxy: options.add_argument(f'--proxy-server={proxy}')
                    service = Service(CHROMEDRIVER_PATH)
                    driver = webdriver.Chrome(service=service, options=options)

                    if self.auto_signup(driver, site):
                        if self.do_tasks(driver, site) > 0:
                            print(f"Successfully integrated new site: {site}")
                            SITE_PATHS[site] = {"signup": "/register", "tasks": "/offers", "withdraw": "/cashout", "min": 0.50} # Default paths
                            with open("sites.json", "w") as f:
                                json.dump(SITE_PATHS, f, indent=2)
                    driver.quit()
                except Exception as e:
                    print(f"Failed to integrate new site {site}: {e}")

    def start(self):
        self.evolution_ai.improve_self()
        self.integrate_new_sites()
        print(f"Starting {THREADS} accounts...")
        for i in range(THREADS):
            threading.Thread(target=self.run, daemon=True).start()
            time.sleep(THREAD_DELAY)

        while True:
            time.sleep(3600)

if __name__ == "__main__":
    bot = Bot()
    bot.start()
