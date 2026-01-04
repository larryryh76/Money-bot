# BOLT'S JOURNAL - CRITICAL LEARNINGS ONLY

## 2024-05-24 - Startup Performance Anti-Patterns

**Learning:** I discovered two critical performance anti-patterns in this codebase:
1.  **Blocking I/O at Startup:** The `fetch_proxies()` function was a synchronous network call that blocked the entire application's initialization.
2.  **Excessive Static Sleep:** A `time.sleep(10)` in the thread creation loop caused a 15-minute startup delay for 90 threads.

**Action:** I will always look for and eliminate blocking I/O in critical paths like startup. I will also replace long, static sleeps with non-blocking alternatives or much smaller delays. For this specific case, I refactored the proxy fetching to be asynchronous and reduced the sleep to 0.1 seconds.
