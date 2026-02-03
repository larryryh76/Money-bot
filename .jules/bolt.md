## 2025-05-15 - Optimizing high-concurrency bot startup and network I/O

**Learning:** Synchronous network I/O at the top level and long static delays in thread creation loops are major bottlenecks in high-concurrency applications. For this bot (90 threads), the original startup would take 15+ minutes. By using background proxy fetching and a staggered-with-jitter thread launch, we can achieve nearly instant startup while still protecting system resources.

**Action:** Always move heavy initialization and network I/O out of the main execution path. Use `threading.Event` for synchronization and combine small inter-thread delays with internal random jitter to prevent 'thundering herd' issues when launching multiple browser instances.
