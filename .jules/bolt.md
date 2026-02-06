## 2025-05-14 - Network & Startup Optimizations
**Learning:** High thread counts (90) demand efficient resource management. Synchronous network I/O at startup and repeated TCP/TLS handshakes are major bottlenecks. Background proxy refreshing and connection pooling significantly improve responsiveness.
**Action:** Always use requests.Session with an appropriately sized pool for multi-threaded scrapers. Decouple long-running I/O from the main thread.
