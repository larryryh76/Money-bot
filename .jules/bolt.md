## 2024-05-20 - Blocking I/O at Application Startup

**Learning:** The application's main thread was blocked at startup by a synchronous network call (`fetch_proxies`) to scrape a website. This is a significant performance anti-pattern, as it delays the entire application initialization until the network request completes. Any failure or slowness in the external service directly translates to application startup delays.

**Action:** Move synchronous I/O operations at startup to a background thread. Use a signaling mechanism, like `threading.Event`, to notify other threads when the required resource (e.g., a proxy list) is available. This allows the main application to initialize concurrently while fetching resources.
