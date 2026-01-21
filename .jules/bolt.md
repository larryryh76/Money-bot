## 2024-05-20 - Initial Performance Analysis

**Learning:** The application's startup is severely bottlenecked by two issues:
1.  **Synchronous I/O:** The `fetch_proxies()` function performs a blocking network request at startup, halting all execution until the proxy list is scraped.
2.  **Startup Delay:** A `time.sleep(10)` call within the thread creation loop introduces a massive, unnecessary delay, scaling linearly with the number of threads.

**Action:** I will refactor the proxy fetching to run in a non-blocking background thread and drastically reduce the sleep timer in the startup loop. This will ensure the application starts almost instantaneously, regardless of network conditions or thread count.