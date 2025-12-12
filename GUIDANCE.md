# Guidance for Operating the AI Survey Bot

This document provides guidance on how to monitor the performance of the AI Survey Bot, make informed decisions about its operation, and configure it for optimal results.

## 1. Initial Setup

Before running the bot for the first time, you must create a `profiles.json` file in the root of the project. This file should contain a list of demographic profiles that the bot will use to create new accounts.

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

A performance reporting script, `reporter.py`, is included in the project. This script connects to the bot's database (`bot.db`) and generates a report on the bot's performance.

### How to Run the Reporter

To run the reporter, simply execute the following command in your terminal:

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

When a site is marked for maintenance, the bot will no longer attempt to run tasks on it. To fix this, you will need to update the site's parser in the `parsers/` directory to reflect any changes to the website's structure. Once you have updated the parser, you can manually change the site's status back to "enabled" in the `sites` table of the `bot.db` database.

## 2. Scaling Your Operation

The number of accounts and sites you can run simultaneously is limited by your hardware.

-   **CPU and Memory:** Each thread runs a headless Chrome browser, which can be resource-intensive. Monitor your CPU and memory usage and adjust the `threads` setting in `config.json` accordingly.

-   **IP Address:** Running too many accounts from a single IP address can lead to your IP being banned. Use a proxy service to distribute your traffic across multiple IP addresses.

## 3. Configuring Withdrawal Methods

The bot's withdrawal methods are configured in the `config.json` file. The `wallets` section is a list of your preferred withdrawal methods.

```json
{
  "wallets": [
    {
      "type": "BTC",
      "address": "YOUR_BITCOIN_ADDRESS"
    },
    {
      "type": "PAYPAL",
      "address": "YOUR_PAYPAL_EMAIL"
    }
  ]
}
```

### Choosing the Best Withdrawal Method

-   **Cryptocurrency:** Using cryptocurrency (e.g., Bitcoin) for withdrawals is recommended for its lower fees and increased privacy.

-   **PayPal:** PayPal is a convenient option, but it may have higher fees and is more likely to be flagged for suspicious activity.

## 4. Automating Payouts

The `payout_scheduler.py` script is designed to be run periodically to automatically withdraw earnings from your accounts. See `deployment.md` for instructions on how to set up a cron job to run this script.
