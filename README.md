# AI Survey Bot

This is a multi-threaded bot that automates survey completion on various websites using an AI-powered question answering system.

## How to Use

### 1. Configuration

The bot is configured using two JSON files:

-   **`config.json`:** This file contains the main settings for the bot.
    -   `api_key`: Your OpenRouter API key.
    -   `wallet`: Your cryptocurrency wallet address for payouts.
    -   `threads`: The number of concurrent threads to run.
    -   `thread_delay`: The delay (in seconds) between starting each thread.
    -   `cashout_check_interval`: The interval (in seconds) at which the bot checks the account balance for a potential payout.

-   **`sites.json`:** This file contains the site-specific configurations. You can add, remove, or modify the sites in this file to customize the bot's targets.

### 2. Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/ai-survey-bot.git
    cd ai-survey-bot
    ```

2.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### 3. Running the Bot

To run the bot, simply execute the following command:

```bash
python bot.py
```

## Deployment

For instructions on how to deploy the bot on a free cloud service, see [`deployment.md`](deployment.md).

## Disclaimer

This bot is provided for educational purposes only. Automated bots can be against the terms of service of the survey websites you are targeting. Use at your own risk.

**Security Note:** The `accounts.json` file stores account credentials in plaintext. It is recommended to run this bot in a secure environment.

**Development Note:** The `LearningAI` and `EvolutionAI` classes currently have placeholder methods. These are intended to be expanded upon in future development. The `innovate` feature, which automatically discovers new survey sites, is also experimental and may not work reliably.
