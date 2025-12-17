# Guidance for Operating the AI Survey Bot

This document provides guidance on how to monitor the performance of the AI Survey Bot, make informed decisions about its operation, and configure it for optimal results.

## 1. Initial Setup

Before running the bot for the first time, you must:

1.  **Set up the PostgreSQL Database:** The bot requires a remote PostgreSQL database to function, especially when deployed on a platform like Render. See `deployment.md` for instructions on setting up a free database.
2.  **Set Environment Variables:** Ensure that the `DATABASE_URL` environment variable is set correctly to your database connection string.
3.  **Create a `profiles.json` file:** This file should contain a list of demographic profiles that the bot will use to create new accounts.

Here is an example of a `profiles.json` file with a single profile:

```json
[
  {
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-01",
    "gender": "Male",
    "street_address": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "zip_code": "12345",
    "country": "USA"
  }
]
```

## 2. Monitoring Performance

A performance reporting script, `reporter.py`, is included in the project. This script connects to the bot's PostgreSQL database and generates a report on the bot's performance.

### How to Run the Reporter

To run the reporter, simply execute the following command in your terminal, ensuring your environment variables (especially `DATABASE_URL`) are loaded:

```bash
python3 reporter.py
```

### Interpreting the Report

The report is divided into three sections:

-   **Account Statuses:** This section shows the number of accounts for each site and their current status (e.g., `active`, `flagged`). A large number of `flagged` accounts on a particular site may indicate that the site has strong anti-bot measures.
-   **Site Performance:** This section provides a breakdown of the success rate and total earnings for each site. A low success rate may indicate that the site's tasks are difficult for the bot to complete, or that the site is not profitable.
-   **Total Earnings:** This section shows the total earnings across all sites.

### The "maintenance_required" Status

If you see a site with the status "maintenance_required", it means that the bot's `EvolutionAI` has detected that a core function (like finding or completing tasks) is consistently failing for that site. This is a self-healing mechanism to prevent the bot from wasting resources on a broken parser.

When a site is marked for maintenance, the bot will no longer attempt to run tasks on it. To fix this, you may need to update the site's parser in the `parsers/` directory. Once you believe the issue is resolved, you can manually change the site's status back to "enabled" in the `sites` table of the database using a PostgreSQL client.

## 3. Scaling Your Operation

-   **Resource Limits:** When deploying on a free service like Render, be aware of strict CPU and memory limits. You **must** lower the `threads` setting in `config.json` to a small number (e.g., 2-5) to avoid crashing your service.
-   **IP Address:** Running too many accounts from a single IP address can lead to your IP being banned. Use a proxy service to distribute your traffic across multiple IP addresses.

## 4. Configuring Withdrawal Methods

The bot's withdrawal methods are configured in the `config.json` file.

```json
{
  "wallets": [
    { "type": "BTC", "address": "YOUR_BITCOIN_ADDRESS" },
    { "type": "PAYPAL", "address": "YOUR_PAYPAL_EMAIL" }
  ]
}
```

## 5. Automating Payouts

The `payout_scheduler.py` script is designed to be run periodically to automatically withdraw earnings. See `deployment.md` for instructions on how to set this up as a cron job on Render.
