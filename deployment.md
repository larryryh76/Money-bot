# Deploying the AI Survey Bot on Railway

This guide will walk you through deploying the AI Survey Bot on [Railway](https://railway.app/), a cloud platform that offers a free tier with a persistent filesystem, which is essential for the bot's learning and evolution features.

## 1. Prerequisites

- A GitHub account with a forked or cloned version of this repository.
- A Railway account.

## 2. Setting up on Railway

1.  **Create a New Project:** From your Railway dashboard, click on "New Project" and select "Deploy from GitHub repo".

2.  **Connect Your Repository:** Connect your GitHub account and select the repository for the AI Survey Bot.

3.  **Configure the Service:**
    -   Railway will automatically detect the `Dockerfile` in the repository and build it.
    -   **Add a Volume:** To ensure the database persists, you need to mount a volume.
        -   Go to your service's "Settings" tab.
        -   Under "Volumes", click "Add Volume".
        -   Set the "Mount Path" to `/app`. This will ensure that the entire working directory, including the `bot.db` database, is persistent.

4.  **Add Environment Variables:**
    -   Go to the "Variables" tab in your service's settings.
    -   Add the following environment variables:
        -   `API_KEY`: Your OpenRouter API key.
        -   `ENCRYPTION_PASSWORD`: A strong, unique password for encrypting credentials.
        -   `TWOCAPTCHA_API_KEY`: Your 2Captcha API key (optional).

5.  **Deploy:** Railway will automatically deploy your service when you push changes to your repository. You can also trigger a manual deploy from the dashboard.

## 4. Setting up the Payout Scheduler

The `payout_scheduler.py` script is designed to be run periodically to automatically withdraw earnings from your accounts.

### Running on Railway

Railway does not have a built-in cron job feature on its free tier. You can, however, use a free cron job service like [Cron-job.org](https://cron-job.org/) to trigger the payout scheduler.

1.  **Create a new cron job:** Go to Cron-job.org and create a new cron job.
2.  **Set the URL:** The URL should be the URL of your Railway service, with the path `/run-payout-scheduler`.
3.  **Set the schedule:** A good schedule would be once a day.

### Running Locally

If you are running the bot locally, you can set up a cron job to run the `payout_scheduler.py` script.

```bash
0 0 * * * python3 /path/to/your/project/payout_scheduler.py
```

This will run the script once a day at midnight.

## 3. Responsible Usage on Free Resources

Running a bot on a free tier requires careful resource management to avoid exceeding your usage limits. Here are some key considerations:

-   **Thread Count:** The `threads` setting in `config.json` is set to a low number by default. This is to avoid overwhelming the free tier's limited CPU and memory. Increasing this value may lead to performance issues.

-   **Thread Delay:** The `thread_delay` setting in `config.json` adds a delay between starting each thread. This prevents a sudden spike in resource usage.

-   **Fair Use:** Be mindful of the terms of service for both Railway and the survey websites you are targeting. Automated bots can be against their terms, and excessive use may lead to your accounts being banned. This bot is provided for educational purposes only.
