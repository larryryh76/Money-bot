hiimport time, random, requests, threading, os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent

# Env vars
API_KEY = os.getenv('OPENROUTER_KEY', '')  # Optional
WALLET = os.getenv('WALLET', '')

# Free proxy list
PROXIES = [
    'http://103.153.154.170:80', 'http://190.103.177.131:4145', 'http://103.153.155.131:80', 'http://190.103.177.131:80',
    'http://103.153.154.170:4145', 'http://190.103.177.131:4145', 'http://103.153.155.131:4145', 'http://190.103.177.131:80'
]

# Sites with paths (2025 verified)
SITE_PATHS = {
    "freecash.com": {"signup": "/register", "tasks": "/offers", "withdraw": "/cashout", "min": 0.50},
    "lootably.com": {"signup": "/authentication/signup", "tasks": "/offers", "withdraw": "/withdraw", "min": 5.00},
    "surveytime.io": {"signup": "/", "tasks": "/paid-surveys", "withdraw": "/rewards", "min": 1.00},
    "prizerebel.com": {"signup": "/", "tasks": "/offers", "withdraw": "/redeem", "min": 5.00},
    "cointiply.com": {"signup": "/", "tasks": "/offers", "withdraw": "/withdraw", "min": 3.00}
}

def get_proxy():
    return random.choice(PROXIES)

def ai_or_random_answer(question):
    if API_KEY:
        try:
            resp = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                 headers={"Authorization": f"Bearer {API_KEY}"},
                                 json={"model": "deepseek/deepseek-r1:free",
                                       "messages": [{"role": "user", "content": f"1-5 words: {question} Random adult."}],
                                       "max_tokens": 15}).json()
            return resp['choices'][0]['message']['content'].strip()
        except: pass
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
    driver.get(f"https://{site}{paths['tasks']}")
    time.sleep(10)
    for _ in range(5):
        try:
            btn = driver.find_element(By.XPATH, "//button[contains(text(),'Start') or contains(text(),'Next') or contains(text(),'Play')] | //a[contains(@href,'offer')]")
            btn.click()
            time.sleep(random.uniform(10, 25))
            tasks += 1
        except:
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

def run():
    while True:
        try:
            proxy = get_proxy()
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

print("Starting 90 accounts...")
for i in range(90):
    threading.Thread(target=run, daemon=True).start()
    time.sleep(10)

while True:
    time.sleep(3600)
