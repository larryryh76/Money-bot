import psycopg2
import os
from collections import defaultdict
from dotenv import load_dotenv

def main():
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        print("Error: DATABASE_URL environment variable not set.")
        return

    conn = psycopg2.connect(DATABASE_URL)
    c = conn.cursor()

    # Get account statuses
    c.execute("SELECT site, status, COUNT(*) FROM accounts GROUP BY site, status")
    account_statuses = c.fetchall()

    print("--- Account Statuses ---")
    site_statuses = defaultdict(list)
    for site, status, count in account_statuses:
        site_statuses[site].append(f"{count} {status}")

    for site, statuses in site_statuses.items():
        print(f"{site}: {', '.join(statuses)}")
    print("\n")

    # Get site performance
    c.execute("SELECT site, success, value FROM logs")
    logs = c.fetchall()

    site_performance = defaultdict(lambda: {"success": 0, "failure": 0, "earnings": 0})
    for site, success, value in logs:
        if success:
            site_performance[site]["success"] += 1
            site_performance[site]["earnings"] += value if value else 0
        else:
            site_performance[site]["failure"] += 1

    print("--- Site Performance ---")
    if not site_performance:
        print("No site performance data available.")
    else:
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

    c.close()
    conn.close()

if __name__ == "__main__":
    main()
