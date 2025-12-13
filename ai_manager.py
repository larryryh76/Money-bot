import random
import json
import time
import requests
from bs4 import BeautifulSoup
from database_manager import load_accounts, get_logs, get_parameter, set_parameter, save_sites, load_sites, save_recipe

class ArchitectAI:
    def __init__(self, config):
        self.config = config

    def generate_recipe(self, site, html):
        prompt = f"""
        Analyze the following HTML from {site} and generate a JSON recipe for a GenericParser.
        The recipe should define the steps for 'auto_signup'.
        The JSON should be a dictionary with keys for each action. Each action is a list of steps.
        Each step is a dictionary with 'command', 'target' (e.g., 'id=element_id', 'css=.class'), and optional 'value'.
        Available commands: 'get', 'click', 'send_keys'.
        For 'send_keys', use placeholder values like '{{email}}', '{{password}}', '{{username}}'.

        HTML:
        {html}
        """

        try:
            resp = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                 headers={"Authorization": f"Bearer {self.config.get('api_key')}"},
                                 json={"model": self.config.get("ai_model", "deepseek/deepseek-r1:free"),
                                       "messages": [{"role": "user", "content": prompt}],
                                       "max_tokens": 1024}).json()
            recipe_str = resp['choices'][0]['message']['content'].strip()
            recipe = json.loads(recipe_str)
            save_recipe(site, recipe)
            return recipe
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"Error generating recipe for {site}: {e}")
            return None

class OperationsAI:
    def __init__(self, config):
        self.config = config
        self.learning_ai = LearningAI(config)
        self.evolution_ai = EvolutionAI(self.learning_ai)
        self.architect_ai = ArchitectAI(config)
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

        active_accounts = [acc for acc in load_accounts() if acc["status"] == "active"]
        active_sites = set([acc["site"] for acc in active_accounts])
        active_offers = [offer for offer in active_offers if offer["site"] in active_sites]

        return active_offers

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
        logs = get_logs()
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
            with open("profiles.json", "r+") as f:
                profiles = json.load(f)
                profiles.append(new_profile)
                f.seek(0)
                json.dump(profiles, f, indent=2)

            return new_profile
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"Error generating new profile: {e}")
            return json.loads(best_profile_str)

    def innovate(self):
        # Scrape a reliable blog for new survey sites
        try:
            url = "https://www.savethestudent.org/make-money/best-paid-online-survey-sites.html"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            new_sites = []
            for link in soup.select("a.btn.btn-lg"):
                href = link.get('href')
                if href:
                    try:
                        # Follow redirect to get the actual site URL
                        res = requests.get(f"https://www.savethestudent.org{href}")
                        domain = res.url.split("/")[2].replace("www.", "")
                        new_sites.append(domain)
                    except requests.exceptions.RequestException:
                        continue

            return list(set(new_sites)) # Return unique sites
        except requests.exceptions.RequestException as e:
            print(f"Error scraping for new sites: {e}")
            return []

class EvolutionAI:
    def __init__(self, learning_ai):
        self.learning_ai = learning_ai

    def improve_self(self, site_performance):
        # Adjust action_delay based on the overall success rate
        total_success = sum([site_performance[site]["success"] for site in site_performance])
        total_failure = sum([site_performance[site]["failure"] for site in site_performance])
        success_rate = total_success / (total_success + total_failure + 1)

        action_delay = get_parameter("action_delay", 1.0)
        if success_rate < 0.5:
            action_delay *= 1.1 # Slow down if failing
        else:
            action_delay *= 0.9 # Speed up if succeeding

        set_parameter("action_delay", action_delay)

    def optimize(self, site_performance, profile_performance):
        # Autonomously apply changes to system parameters

        # Disable sites with low success rates
        sites = load_sites()
        for site, performance in site_performance.items():
            if performance["success"] < 10 and performance["failure"] > 20:
                if site in sites and sites[site].get("status", "enabled") == "enabled":
                    sites[site]["status"] = "disabled"
                    print(f"EvolutionAI: Autonomously disabled site {site} due to low performance.")
        save_sites(sites)

        # Health check for parsers
        logs = get_logs()
        action_failures = {}
        for log in logs:
            if not log["success"]:
                key = (log["site"], log["action"])
                action_failures[key] = action_failures.get(key, 0) + 1

        for (site, action), failures in action_failures.items():
            if failures >= 10: # 10 consecutive failures
                if site in sites and sites[site].get("status", "enabled") == "enabled":
                    sites[site]["status"] = "maintenance_required"
                    print(f"EvolutionAI: Site {site} requires maintenance for action {action}.")
        save_sites(sites)

        # Adjust parameters based on overall performance
        total_success = sum([profile_performance[p]["success"] for p in profile_performance])
        total_failure = sum([profile_performance[p]["failure"] for p in profile_performance])
        success_rate = total_success / (total_success + total_failure + 1)

        action_delay = get_parameter("action_delay", 1.0)
        if success_rate < 0.5:
            action_delay *= 1.05 # Slow down if overall performance is poor
            print(f"EvolutionAI: Decreased action speed due to low success rate.")
        else:
            action_delay *= 0.95 # Speed up if overall performance is good
            print(f"EvolutionAI: Increased action speed due to high success rate.")
        set_parameter("action_delay", action_delay)

        # Adapt strategies
        self.learning_ai.adapt_strategies(profile_performance)
