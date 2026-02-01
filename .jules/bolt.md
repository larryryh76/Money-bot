## 2025-05-14 - Network and Startup Optimization

**Learning:** Synchronous network I/O during application startup (like fetching a proxy list) and conservative thread-spawning delays (10s per thread) are major bottlenecks. Connection pooling with `requests.Session` is essential for multi-threaded bots making frequent API calls to avoid handshake overhead.

**Action:** Always use `requests.Session` with a configured `HTTPAdapter` (pool size matching thread count) for multi-threaded applications. Implement background resource managers (like proxy fetchers) to keep the main thread non-blocking. Use staggered but efficient thread startup (1s delay) with internal jitter to balance startup speed and resource usage.
