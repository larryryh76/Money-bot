import sqlite3
import json
from collections import defaultdict

def main():
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()

    # Get account statuses
    c.execute("SELECT site, status, COUNT(*) FROM accounts GROUP BY site, status")
    account_statuses = c.fetchall()

    print("--- Account Statuses ---")
    for site, status, count in account_statuses:
        print(f"{site}: {count} {status}")
    print("\n")

    # Get site performance
    c.execute("SELECT site, success, value FROM logs")
    logs = c.fetchall()

    site_performance = defaultdict(lambda: {"success": 0, "failure": 0, "earnings": 0})
    for site, success, value in logs:
        if success:
            site_performance[site]["success"] += 1
            site_performance[site]["earnings"] += value
        else:
            site_performance[site]["failure"] += 1

    print("--- Site Performance ---")
    for site, data in site_performance.items():
        total_runs = data["success"] + data["failure"]
        success_rate = (data["success"] / total_runs) * 100 if total_runs > 0 else 0
        print(f"{site}:")
        print(f"  Success Rate: {success_rate:.2f}%")
        print(f"  Total Earnings: ${data['earnings']:.2f}")
    print("\n")

    # Get total earnings
    total_earnings = sum(data["earnings"] for data in site_performance.values())
    print("--- Total Earnings ---")
    print(f"Total earnings across all sites: ${total_earnings:.2f}")

    conn.close()

if __name__ == "__main__":
    main()
