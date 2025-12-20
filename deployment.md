# Deploying the Distributed AI Bot Farm on Render

This guide details how to deploy the bot's scalable, distributed architecture on [Render](https://render.com/). The system now consists of three core components that work together: a **PostgreSQL Database**, a **Redis Instance** for task queuing, a single **Producer** service, and one or more **Consumer** services.

## 1. Architecture Overview

-   **PostgreSQL Database:** The central source of truth for accounts, profiles, logs, and site configurations.
-   **Redis Instance:** Acts as a message broker, holding a queue of tasks to be completed. This decouples task creation from task execution.
-   **Producer (`bot.py`):** A single background service that runs periodically. It scrapes survey sites for tasks, uses the AI to prioritize them, and pushes them into the Redis queue.
-   **Consumers (`worker.py`):** One or more background services that continuously pull tasks from the Redis queue, execute them, and record the results in the database. You can scale the bot's power by adding more consumer instances.

## 2. Step 1: Set Up External Services

### PostgreSQL Database
Follow the instructions from a free provider like [Neon](https://neon.tech/) to create a new database. Get the **`DATABASE_URL`** connection string.

### Redis Instance
1.  **Create a Free Redis Instance:** Go to a provider like [Upstash](https://upstash.com/) or [Render's own Redis service](https://render.com/docs/redis).
2.  **Get the Connection String:** Find the **`REDIS_URL`** connection string. It will look something like `redis://...`.

## 3. Step 2: Create an Environment Group on Render

To ensure all your services use the same credentials, create an **Environment Group** on Render.
1.  Go to the "Environment" tab in your Render dashboard.
2.  Click "New Environment Group".
3.  Add the following secret variables:
    -   `DATABASE_URL`: Your PostgreSQL connection string.
    -   `REDIS_URL`: Your Redis connection string.
    -   `API_KEY`: Your OpenRouter API key.
    -   `ENCRYPTION_PASSWORD`: A strong, unique password.
    -   `PROXYSCRAPE_API_KEY`, `WEBSHARE_API_KEY`: Your proxy API keys (optional).
    -   `PYTHON_VERSION`: `3.12`

## 4. Step 3: Deploy the Services on Render

### Producer Service
This service finds and queues tasks. You only need one.
1.  **Create a New Service:** Click "New +" -> "Background Worker".
2.  **Repository:** Connect your GitHub repository.
3.  **Configuration:**
    -   **Name:** `bot-producer`
    -   **Build Command:** `pip install -r requirements.txt`
    -   **Start Command:** `python3 bot.py`
    -   **Instance Type:** "Free"
4.  **Environment:** Under "Advanced", link the Environment Group you created.

### Consumer Service(s)
These services execute the tasks. You can run many of these to scale your operation.
1.  **Create a New Service:** Click "New +" -> "Background Worker".
2.  **Repository:** Connect the same GitHub repository.
3.  **Configuration:**
    -   **Name:** `bot-consumer`
    -   **Build Command:** `pip install -r requirements.txt`
    -   **Start Command:** `python3 worker.py`
    -   **Instance Type:** "Free"
4.  **Environment:** Link the same Environment Group.
5.  **Scaling:** Once the first consumer is deployed, you can easily scale by going to the service's "Scaling" tab and increasing the number of instances.

### Payout Scheduler (Cron Job)
This service handles withdrawals.
1.  **Create a New Service:** Click "New +" -> "Cron Job".
2.  **Repository:** Connect the same GitHub repository.
3.  **Configuration:**
    -   **Name:** `payout-scheduler`
    -   **Schedule:** `0 0 * * *` (Once a day at midnight)
    -   **Command:** `python3 payout_scheduler.py`
4.  **Environment:** Link the same Environment Group.

## 5. Responsible Usage on a Free Tier
-   **Consumer Scaling:** Render's free tier has resource limits. Start with **one** consumer instance. Monitor its resource usage before scaling up to 2 or 3.
-   **`consumers_per_instance`:** In `config.json`, the `consumers_per_instance` setting controls how many consumer threads run inside a single Render instance. Keep this low (1-3) on the free tier. The primary way to scale is by adding more Render instances (horizontal scaling).
