# Deploying the AI Survey Bot on Render

This guide will walk you through deploying the AI Survey Bot on [Render](https://render.com/), a cloud platform that offers a free tier for hosting background workers and databases.

## 1. Key Architectural Change: PostgreSQL Database

Due to the ephemeral filesystem on Render's free tier, the bot has been refactored to use a PostgreSQL database instead of a local SQLite file. **This is a critical change.** You cannot run the bot on Render without a remote database.

## 2. Prerequisites

- A GitHub account with a forked or cloned version of this repository.
- A Render account.
- An account with a free PostgreSQL provider like [Neon](https://neon.tech/) or [ElephantSQL](https://www.elephantsql.com/).

## 3. Step 1: Set up the PostgreSQL Database

1.  **Create a Free Database:** Go to your chosen provider (e.g., Neon) and create a new, free PostgreSQL project.
2.  **Get the Connection String:** After the database is created, find the **connection string** or **DATABASE_URL**. It will look something like `postgres://user:password@host:port/dbname`. Keep this safe; you will need it for the next step.

## 4. Step 2: Deploy the Bot on Render

The bot should be deployed as a **Background Worker**, as it's a continuously running process.

1.  **Create a New Service:** From your Render dashboard, click "New +" and select "Background Worker".
2.  **Connect Your Repository:** Connect your GitHub account and select the repository for the AI Survey Bot.
3.  **Configure the Service:**
    -   **Name:** Give your service a name (e.g., `survey-bot-worker`).
    -   **Region:** Choose a region close to you.
    -   **Branch:** Select the main branch.
    -   **Build Command:** `pip install -r requirements.txt`
    -   **Start Command:** `python3 bot.py`
    -   **Instance Type:** Select "Free".

4.  **Add Environment Variables:**
    -   Before the first deploy, go to the "Environment" tab.
    -   Add the following environment variables:
        -   `DATABASE_URL`: The full connection string you got from your PostgreSQL provider.
        -   `API_KEY`: Your OpenRouter API key.
        -   `ENCRYPTION_PASSWORD`: A strong, unique password for encrypting credentials.
        -   `TWOCAPTCHA_API_KEY`: Your 2Captcha API key (optional).
        -   `PYTHON_VERSION`: `3.12` (or the version you are using).

5.  **Deploy:** Click "Create Background Worker". Render will pull your code, install dependencies, and start the bot. You can view logs in the "Logs" tab.

## 5. Step 3: Set up the Payout Scheduler Cron Job

Render has native support for cron jobs, which is perfect for the payout scheduler.

1.  **Create a New Cron Job:** From the dashboard, click "New +" and select "Cron Job".
2.  **Connect Your Repository:** Select the same GitHub repository.
3.  **Configure the Cron Job:**
    -   **Name:** Give it a name (e.g., `payout-scheduler`).
    -   **Schedule:** Set the schedule. For example, to run once a day at midnight, use `0 0 * * *`.
    -   **Command:** `python3 payout_scheduler.py`
    -   **Instance Type:** Select "Free".
4.  **Link Environment Variables:** In the "Environment" tab for the cron job, create an "Environment Group" that links to the same variables you created for the background worker. This ensures it can connect to the same database and use the same API keys.
5.  **Create:** Click "Create Cron Job".

## 6. Responsible Usage on Render's Free Tier

-   **CRITICAL: Thread Count:** Render's free tier has very limited CPU and memory. You **must** lower the `threads` setting in `config.json` to a very small number (e.g., `2` or `3`) before deploying. A high thread count will cause the service to crash.
-   **Fair Use:** Be mindful of the terms of service for Render, your database provider, and the survey websites. Automated bots can be against their terms, and excessive use may lead to your accounts being banned. This bot is provided for educational purposes only.
