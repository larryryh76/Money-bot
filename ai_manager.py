import random
import json
import time
import requests
from bs4 import BeautifulSoup
from secure_storage import load_accounts_encrypted
from file_lock import FileLock

ENCRYPTION_PASSWORD = None

class OperationsAI:
    def __init__(self, config):
        self.config = config
        global ENCRYPTION_PASSWORD
        ENCRYPTION_PASSWORD = self.config.get("encryption_password", "CHANGE_THIS_PASSWORD")
        with open("sites.json") as f:
            self.sites = json.load(f)
        self.learning_ai = LearningAI(config)
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
        wallets = self.config.get("wallets", [])

        for option in available_options:
            for wallet in wallets:
                if option.upper() == wallet["type"].upper():
                    return wallet

        return None

class LearningAI:
    def __init__(self, config):
        self.config = config

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
        best_profile_str = max(profile_performance, key=lambda p: profile_performance[p]["success"] / (profile_performance[p]["success"] + profile_performance[p]["failure"] + 1))

        prompt = f"Given the most successful demographic profile for a survey bot: {best_profile_str}, generate a new, similar but distinct profile. The new profile should be a JSON object with the same keys. Respond with only the JSON object."

        try:
            resp = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                 headers={"Authorization": f"Bearer {self.config.get('api_key')}"},
                                 json={"model": self.config.get("ai_model", "deepseek/deepseek-r1:free"),
                                       "messages": [{"role": "user", "content": prompt}],
                                       "max_tokens": 200}).json()
            new_profile_str = resp['choices'][0]['message']['content'].strip()
            new_profile = json.loads(new_profile_str)

            # Save the new profile
            with FileLock("profiles.json") as f:
                profiles = json.load(f)
                profiles.append(new_profile)
                f.seek(0)
                json.dump(profiles, f, indent=2)

            return new_profile
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"Error generating new profile: {e}")
            return json.loads(best_profile_str)

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
    with FileLock("parameters.json") as f:
        f.seek(0)
        json.dump(parameters, f, indent=2)
        f.truncate()

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
        # Use Google Search to find new survey sites
        try:
            search_results = google_search(query="best online survey sites 2024")
            new_sites = []
            for result in search_results:
                # A simple heuristic to identify potential survey sites
                if "survey" in result["title"].lower() or "paid" in result["title"].lower():
                    domain = result["link"].split("/")[2].replace("www.", "")
                    new_sites.append(domain)
            return list(set(new_sites)) # Return unique sites
        except Exception as e:
            print(f"Error using Google Search for site discovery: {e}")
            return []

    def optimize(self, site_performance, profile_performance):
        # Autonomously apply changes to system parameters

        # Disable sites with low success rates
        with FileLock("sites.json") as f:
            sites = json.load(f)
            for site, performance in site_performance.items():
                if performance["success"] < 10 and performance["failure"] > 20:
                    if site in sites and sites[site].get("status", "enabled") == "enabled":
                        sites[site]["status"] = "disabled"
                        print(f"EvolutionAI: Autonomously disabled site {site} due to low performance.")
            f.seek(0)
            json.dump(sites, f, indent=2)
            f.truncate()

        # Adjust parameters based on overall performance
        total_success = sum([profile_performance[p]["success"] for p in profile_performance])
        total_failure = sum([profile_performance[p]["failure"] for p in profile_performance])
        success_rate = total_success / (total_success + total_failure + 1)

        parameters = load_parameters()
        if success_rate < 0.5:
            parameters["action_delay"] *= 1.05 # Slow down if overall performance is poor
            print(f"EvolutionAI: Decreased action speed due to low success rate.")
        else:
            parameters["action_delay"] *= 0.95 # Speed up if overall performance is good
            print(f"EvolutionAI: Increased action speed due to high success rate.")
        save_parameters(parameters)
