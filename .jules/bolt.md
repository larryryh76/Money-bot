# Bolt's Journal ⚡

This journal is for CRITICAL learnings about performance. No routine logs.

## 2024-07-22 - Startup Optimization Learnings
**Learning:** The application's startup was severely bottlenecked by two anti-patterns:
1.  **Synchronous I/O:** `fetch_proxies()` blocked the main thread, delaying initialization.
2.  **Static Sleep:** A `time.sleep(10)` in the thread creation loop caused a 15-minute startup time for 90 threads.
**Action:** Always move blocking I/O to a background thread and use a `threading.Event` to signal completion. Replace long, static sleeps in loops with minimal, non-blocking delays (e.g., `0.1s`) to prevent bottlenecks while still safeguarding against overwhelming services.
