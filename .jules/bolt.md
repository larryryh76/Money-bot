## 2024-07-16 - Blocking I/O at Startup

**Learning:** Synchronous network I/O on the main thread during application startup is a major performance anti-pattern. In this codebase, the initial `fetch_proxies()` function blocked all other operations, including thread creation, until the HTTP request completed. This led to significant and variable startup delays, depending on network conditions.

**Action:** For any future work involving initial data fetching (e.g., configurations, remote resources), I will always use a background thread or asynchronous task. I will use a signaling mechanism like `threading.Event` to coordinate between the main thread and the background task, ensuring that dependent processes wait for the resource to be ready without blocking the entire application's initialization.
