import random
import json
import time
import requests
from bs4 import BeautifulSoup
from secure_storage import load_accounts_encrypted

with open("config.json") as f:
    config = json.load(f)
ENCRYPTION_PASSWORD = config.get("encryption_password", "CHANGE_THIS_PASSWORD")

class OperationsAI:
    def __init__(self):
        with open("sites.json") as f:
            self.sites = json.load(f)
        self.learning_ai = LearningAI()
        self.cooldown_sites = {}

    def manage_tasks(self, profiles, offers):
        site_performance, profile_performance = self.learning_ai.analyze_logs()

        # Calculate a score for each offer based on its value, time, and the site's success rate
        offer_scores = {}
        for offer in offers:
            site = offer["site"]
            site_score = site_performance.get(site, {"success": 0, "failure": 0})
            site_success_rate = site_score["success"] / (site_score["success"] + site_score["failure"] + 1)

            value_per_minute = offer["value"] / offer["time_to_complete"]

            offer_scores[offer["id"]] = value_per_minute * (1 + site_success_rate)

        # Sort offers by score
        sorted_offers = sorted(offers, key=lambda offer: offer_scores[offer["id"]], reverse=True)

        # Exclude sites that are in cooldown or have no active accounts
        active_offers = [offer for offer in sorted_offers if offer["site"] not in self.cooldown_sites or time.time() - self.cooldown_sites[offer["site"]] > 3600]

        active_accounts = [acc for acc in load_accounts_encrypted(ENCRYPTION_PASSWORD) if acc["status"] == "active"]
        active_sites = set([acc["site"] for acc in active_accounts])
        active_offers = [offer for offer in active_offers if offer["site"] in active_sites]

        return active_offers

    def allocate_resources(self, accounts, threads):
        # Simple allocation for now, can be improved
        return [{"thread_id": i, "accounts": [acc for acc in accounts if i % threads == 0]} for i in range(threads)]

    def set_priorities(self, offers):
        offer_scores = {}
        for offer in offers:
            value_per_minute = offer["value"] / offer["time_to_complete"]
            offer_scores[offer["id"]] = value_per_minute

        return sorted(offers, key=lambda offer: offer_scores[offer["id"]], reverse=True)

    def select_wallet(self, available_options):
        with open("config.json") as f:
            config = json.load(f)
        wallets = config.get("wallets", [])

        prompt = f"Given the available withdrawal options: {', '.join(available_options)}, and my available wallets: {json.dumps(wallets)}. Which wallet type should I use? Respond with only the wallet type (e.g., 'BTC')."

        try:
            resp = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                 headers={"Authorization": f"Bearer {config.get('api_key')}"},
                                 json={"model": "deepseek/deepseek-r1:free",
                                       "messages": [{"role": "user", "content": prompt}],
                                       "max_tokens": 10}).json()
            selected_type = resp['choices'][0]['message']['content'].strip().upper()

            for wallet in wallets:
                if wallet["type"].upper() == selected_type:
                    return wallet
        except requests.exceptions.RequestException as e:
            print(f"Error calling OpenRouter API for wallet selection: {e}")

        return None

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
        profile_performance = {}
        for log in logs:
            site = log["site"]
            profile = json.dumps(log.get("profile")) # Use json.dumps to make the profile hashable

            if site not in site_performance:
                site_performance[site] = {"success": 0, "failure": 0}
            if profile not in profile_performance:
                profile_performance[profile] = {"success": 0, "failure": 0}

            if log["success"]:
                site_performance[site]["success"] += 1
                profile_performance[profile]["success"] += 1
            else:
                site_performance[site]["failure"] += 1
                profile_performance[profile]["failure"] += 1

        return site_performance, profile_performance

    def adapt_strategies(self, profile_performance):
        # Find the most successful profile
        best_profile = max(profile_performance, key=lambda p: profile_performance[p]["success"] / (profile_performance[p]["success"] + profile_performance[p]["failure"] + 1))

        # For now, just return the best profile. In the future, this could be used to generate new profiles.
        return json.loads(best_profile)

    def analyze_market(self):
        # This is a placeholder for a more complex market analysis
        return self.innovate()

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

    def improve_self(self, site_performance):
        # Adjust action_delay based on the overall success rate
        total_success = sum([site_performance[site]["success"] for site in site_performance])
        total_failure = sum([site_performance[site]["failure"] for site in site_performance])
        success_rate = total_success / (total_success + total_failure + 1)

        if success_rate < 0.5:
            self.parameters["action_delay"] *= 1.1 # Slow down if failing
        else:
            self.parameters["action_delay"] *= 0.9 # Speed up if succeeding

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

    def optimize(self, site_performance, profile_performance):
        # Recommend changes to system parameters
        recommendations = []

        # Recommend removing sites with low success rates
        for site, performance in site_performance.items():
            if performance["success"] < 10 and performance["failure"] > 20:
                recommendations.append(f"Remove site {site} due to low success rate.")

        # Recommend adding more profiles if the success rate is low
        total_success = sum([profile_performance[p]["success"] for p in profile_performance])
        total_failure = sum([profile_performance[p]["failure"] for p in profile_performance])
        if total_success / (total_success + total_failure + 1) < 0.5:
            recommendations.append("Add more diverse profiles to improve qualification rates.")

        return recommendations
