# Bolt's Journal - Critical Learnings

## 2025-01-31 - Initial Performance Audit
**Learning:** The application suffered from a massive startup bottleneck due to a 10-second delay between thread initializations. With 90 threads, this caused a 15-minute delay before the bot was fully operational. Additionally, synchronous proxy fetching at the top level blocked the initial execution, and the lack of connection pooling in a high-concurrency environment (90 threads) led to inefficient network resource usage.
**Action:** Implement background proxy fetching with a `threading.Event` to unblock startup, and use `requests.Session` with an `HTTPAdapter` configured for high concurrency. Use a 1.0s staggered startup and random jitter (1-10s) to avoid "thundering herd" resource exhaustion when multiple threads launch Chrome simultaneously.
