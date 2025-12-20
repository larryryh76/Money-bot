import time
import os
import json
import random
from dotenv import load_dotenv
from ai_manager import OperationsAI
from database_manager import init_db, load_sites, load_accounts, load_profiles
from task_queue_manager import push_task, get_queue_size
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
from utils import get_parser

load_dotenv()
init_db()

class Producer:
    def __init__(self, config):
        self.config = config
        self.operations_ai = OperationsAI(config)
        self.running = True

    def start(self):
        print("Starting Producer...")
        while self.running:
            if get_queue_size() < self.config.get("max_queue_size", 1000):
                self.populate_task_queue()

            # Also periodically check for site status updates and other AI maintenance
            self.run_ai_maintenance()

            print("Producer sleeping for 15 minutes...")
            time.sleep(900) # Run every 15 minutes

    def stop(self):
        self.running = False

    def populate_task_queue(self):
        print("Populating task queue...")
        all_offers = []
        ua = UserAgent()

        for site, data in load_sites().items():
            if data.get("status", "enabled") != "enabled":
                continue

            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument(f'--user-agent={ua.random}')
            service = Service(self.config.get("chromedriver_path", "/usr/bin/chromedriver"))
            driver = None
            try:
                driver = webdriver.Chrome(service=service, options=options)
                parser = get_parser(site)
                if parser:
                    driver.get(f"https://{site}{data['tasks']}")
                    offers = parser.find_offers(driver)
                    all_offers.extend(offers)
                    print(f"Found {len(offers)} offers on {site}")
            except Exception as e:
                print(f"Error scraping {site}: {e}")
            finally:
                if driver:
                    driver.quit()

        # Let the AI prioritize and filter tasks before pushing
        accounts = load_accounts()
        prioritized_tasks = self.operations_ai.manage_tasks(accounts, all_offers)

        for task in prioritized_tasks:
            push_task(task)

    def run_ai_maintenance(self):
        print("Running AI maintenance...")
        # This is where the EvolutionAI and LearningAI would run their checks
        site_performance, profile_performance = self.operations_ai.learning_ai.analyze_logs()
        self.operations_ai.evolution_ai.optimize(site_performance, profile_performance)
        self.operations_ai.evolution_ai.improve_self(site_performance)


if __name__ == "__main__":
    with open("config.json") as f:
        config_data = json.load(f)

    producer = Producer(config_data)
    try:
        producer.start()
    except KeyboardInterrupt:
        producer.stop()
