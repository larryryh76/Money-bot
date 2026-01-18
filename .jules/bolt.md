## 2024-05-20 - Initial Performance Bottlenecks

**Learning:** Two major performance anti-patterns were identified in the initial analysis of `bot.py`. First, a blocking network I/O call (`fetch_proxies`) is executed on the main thread at startup, delaying the entire application. Second, a long, static `time.sleep(10)` inside the thread creation loop creates an artificially massive startup delay, scaling linearly with the number of threads.

**Action:** I will refactor the proxy fetching to be asynchronous using a background thread and a `threading.Event` to signal completion. I will also drastically reduce the sleep duration in the startup loop to a minimal, non-blocking value to prevent overwhelming services while still allowing for rapid startup.
