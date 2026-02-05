# Bolt's Journal ⚡

## 2025-05-14 - Initial Assessment
**Learning:** Found several performance bottlenecks:
1.  **Staggered Startup:** 10s sleep between thread creation in `Bot.start()` causes 15min delay for 90 threads.
2.  **Synchronous I/O at module level:** `fetch_proxies()` blocks initial script execution.
3.  **Redundant Object Creation:** `UserAgent()` instantiated in every worker loop iteration.
4.  **No Connection Pooling:** Missing `requests.Session()` for repeated API calls.
5.  **Lack of Proxy Rotation/Refreshing:** Proxies are fetched once at startup.

**Action:** Implement a background proxy refresher, move `UserAgent` instantiation, use `requests.Session`, and optimize thread startup.

## 2025-05-14 - Thread Startup and Network Bottlenecks
**Learning:** In a multi-threaded Selenium application, fixed long sleeps during thread creation (e.g., 10s) significantly delay system readiness. Connection pooling via `requests.Session` is critical when multiple threads share external API endpoints (OpenRouter, Guerrilla Mail) to avoid socket exhaustion and reduce latency.
**Action:** Use connection pooling with `HTTPAdapter` configured to match thread count, and replace long startup sleeps with a combination of short staggering and per-thread jitter.
