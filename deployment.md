# Deploying the AI Survey Bot on Render

This guide will walk you through deploying the AI Survey Bot on [Render](https://render.com/), a cloud platform that offers a free tier for web services.

## 1. Prerequisites

- A GitHub account with a forked or cloned version of this repository.
- A Render account.

## 2. Setting up on Render

1.  **Create a New Web Service:** From your Render dashboard, click on "New" and then "Web Service".

2.  **Connect Your Repository:** Connect your GitHub account and select the repository for the AI Survey Bot.

3.  **Configure the Service:**
    -   **Name:** Give your service a name (e.g., `ai-survey-bot`).
    -   **Region:** Choose a region closest to you.
    -   **Branch:** Select the branch you want to deploy (e.g., `main`).
    -   **Runtime:** Select `Docker`. Render will automatically detect the `Dockerfile` in the repository.
    -   **Build Command:** This should be automatically set to `docker build -t <your-image-name> .`
    -   **Start Command:** Set this to `python bot.py`.

4.  **Add Environment Variables:**
    -   Go to the "Environment" tab in your service's settings.
    -   You will need to create "Secret Files" for your configuration, as Render's free tier does not support persistent disks.
    -   **`config.json`:**
        -   Click "Add Secret File".
        -   For the "Filename", enter `config.json`.
        -   In the "Contents", paste the following, replacing the placeholder with your OpenRouter API key:
            ```json
            {
              "api_key": "REPLACE_WITH_YOUR_API_KEY",
              "wallet": "YOUR_WALLET_ADDRESS",
              "threads": 5,
              "thread_delay": 60,
              "cashout_check_interval": 3600
            }
            ```
    -   **`sites.json`:**
        -   Click "Add Secret File".
        -   For the "Filename", enter `sites.json`.
        -   In the "Contents", paste the content of the `sites.json` file from the repository.

5.  **Deploy:** Click "Create Web Service". Render will start building and deploying your bot.

## 3. Responsible Usage on Free Resources

Running a bot on a free tier requires careful resource management to avoid being suspended. Here are some key considerations:

-   **Thread Count:** The `threads` setting in `config.json` is set to a low number by default (`5`). This is to avoid overwhelming the free tier's limited CPU and memory. Increasing this value may lead to performance issues or suspension.

-   **Thread Delay:** The `thread_delay` setting in `config.json` adds a delay (in seconds) between starting each thread. This prevents a sudden spike in resource usage when the bot starts, which could trigger alerts on the platform.

-   **Cashout Check Interval:** The `cashout_check_interval` setting in `config.json` controls how often the bot checks the account balance for a potential payout. A higher value (e.g., `3600` for one hour) is recommended to avoid making excessive requests to the survey sites.

-   **Fair Use:** Be mindful of the terms of service for both Render and the survey websites you are targeting. Automated bots can be against their terms, and excessive use may lead to your accounts being banned. This bot is provided for educational purposes only.
