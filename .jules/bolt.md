# Bolt's Journal ⚡

## 2024-05-20 - Initial Analysis: Synchronous I/O and Startup Delays
**Learning:** The application's startup is severely hampered by two anti-patterns:
1.  A synchronous network call (`fetch_proxies`) blocks the main thread at the very beginning of the script.
2.  A long, static `time.sleep(10)` inside the thread creation loop causes a cumulative delay of 15 minutes for 90 threads.
**Action:** Prioritize moving blocking I/O to background threads and remove or drastically reduce static sleep intervals in startup loops. Use threading events to manage dependencies between threads, like workers needing a proxy list.
