# Human Intervention Guide

This document outlines the 3% of tasks that require human intervention to ensure the smooth operation of the Elite Bot System.

## 1. Initial Setup

The initial setup of the bot requires human intervention to configure the `config.json` file. This includes:

-   **API Keys:** You must provide your own API keys for OpenRouter and 2Captcha.
-   **Wallet Address:** You must provide your own cryptocurrency wallet address for payouts.
-   **Encryption Password:** You must choose a secure password for encrypting the `accounts.json` file.

## 2. Monitoring

While the bot is designed to run autonomously, it is recommended to monitor its performance periodically. This includes:

-   **Log Files:** Check the `logs.json` and `error.log` files for any unusual activity or recurring errors.
-   **Account Status:** Check the `accounts.json.encrypted` file (by decrypting it with a separate script) to monitor the status of your accounts. If a large number of accounts are being flagged or banned, it may be necessary to adjust the bot's parameters or strategies.
-   **Optimization Recommendations:** The bot will print optimization recommendations to the console when it starts. These recommendations should be reviewed and acted upon as needed.

## 3. Manual Overrides

In some cases, it may be necessary to manually override the bot's autonomous operation. This includes:

-   **Major Strategy Shifts:** If you want to change the bot's overall strategy (e.g., focus on a different type of survey), you may need to modify the `ai_manager.py` file.
-   **Adding New Sites:** While the bot can automatically discover new sites, it may not always be able to correctly configure them. In these cases, you may need to manually add the site to the `sites.json` file.
-   **Emergency Stop:** If the bot is behaving unexpectedly, you can stop it by pressing `Ctrl+C` in the console.
