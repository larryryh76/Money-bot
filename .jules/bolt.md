## 2026-02-02 - Multi-layer Startup & Network Optimization
**Learning:** Significant performance gains can be achieved by decoupling resource-heavy startup tasks (like proxy fetching) from the main application lifecycle and using connection pooling for frequent API calls.
**Action:** Use background threads with `threading.Event` for initialization tasks and `requests.Session` with tailored `HTTPAdapter` settings for high-concurrency network I/O.
