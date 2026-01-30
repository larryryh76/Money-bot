## 2025-05-15 - [Startup and Network Optimization]
**Learning:** A long, static sleep (e.g., `time.sleep(10)`) in the thread creation loop was identified as a major performance anti-pattern, causing excessive startup delays. Using a global `requests.Session()` without adjusting the pool size (`pool_connections`, `pool_maxsize`) can create a bottleneck in highly threaded applications.
**Action:** Always reduce startup delays in threaded loops and ensure connection pool sizes match the concurrency level when using shared sessions.
