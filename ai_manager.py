import random
import json
import time
import requests
from bs4 import BeautifulSoup

class OperationsAI:
    def __init__(self):
        with open("sites.json") as f:
            self.sites = json.load(f)
        self.learning_ai = LearningAI()
        self.cooldown_sites = {}

    def manage_tasks(self):
        site_performance = self.learning_ai.analyze_logs()

        # Sort sites by success rate
        sorted_sites = sorted(site_performance.keys(), key=lambda site: site_performance[site]["success"] / (site_performance[site]["success"] + site_performance[site]["failure"] + 1), reverse=True)

        # Add any sites that are not in the logs to the end of the list
        for site in self.sites.keys():
            if site not in sorted_sites:
                sorted_sites.append(site)

        # Exclude sites that are in cooldown
        active_sites = [site for site in sorted_sites if site not in self.cooldown_sites or time.time() - self.cooldown_sites[site] > 3600]

        return active_sites

    def allocate_resources(self):
        pass

    def set_priorities(self):
        pass

class LearningAI:
    def __init__(self):
        pass

    def analyze_logs(self):
        try:
            with open("logs.json", "r") as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

        site_performance = {}
        for log in logs:
            site = log["site"]
            if site not in site_performance:
                site_performance[site] = {"success": 0, "failure": 0}

            if log["success"]:
                site_performance[site]["success"] += 1
            else:
                site_performance[site]["failure"] += 1

        return site_performance

    def adapt_strategies(self, site_performance):
        # For now, we'll just return the site performance.
        # In the future, this could be used to adjust strategies.
        return site_performance

def load_parameters():
    try:
        with open("parameters.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"action_delay": 1.0}

def save_parameters(parameters):
    with open("parameters.json", "w") as f:
        json.dump(parameters, f, indent=2)

class EvolutionAI:
    def __init__(self):
        self.parameters = load_parameters()

    def improve_self(self):
        # Randomly adjust the action delay
        self.parameters["action_delay"] = round(random.uniform(0.5, 2.0), 2)
        save_parameters(self.parameters)

    def innovate(self):
        # Scrape for new survey sites
        try:
            response = requests.get("https://www.sidehustlenation.com/best-online-survey-websites/")
            soup = BeautifulSoup(response.text, "html.parser")
            new_sites = []
            for h3 in soup.find_all("h3"):
                a = h3.find("a")
                if a and a.has_attr("href") and "go" in a["href"]:
                    # Extract the domain name from the href
                    domain = a["href"].split("/")[2].replace("www.", "")
                    new_sites.append(domain)
            return new_sites
        except requests.exceptions.RequestException as e:
            print(f"Error scraping for new sites: {e}")
            return []

    def optimize(self):
        pass
