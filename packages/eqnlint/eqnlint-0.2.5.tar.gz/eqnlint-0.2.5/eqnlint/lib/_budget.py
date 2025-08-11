# eqnlint/lib/_budget.py
import time
import asyncio
import threading
from typing import Optional


class RateLimiter:
    """
    Simple QPS limiter usable from both sync and async code.

    - Call `wait()` from synchronous code.
    - Call `wait_async()` from asynchronous code.
    - Uses monotonic clocks (time.monotonic / loop.time) for reliable delays.
    - Not designed for simultaneous mixed sync+async access; pick one style
      per process/run to avoid interleaved timing jitter.
    """

    def __init__(self, qps: float = 0.5):
        self._interval = 1.0 / max(qps, 1e-9)  # seconds between calls
        self._last_ts: float = 0.0             # last permit timestamp (monotonic)
        self._lock = threading.Lock()          # for sync callers
        self._alock = asyncio.Lock()           # for async callers

    def set_rate(self, qps: float) -> None:
        """Update the rate (queries per second)."""
        self._interval = 1.0 / max(qps, 1e-9)

    def reset(self) -> None:
        """Forget last timestamp (next call proceeds immediately)."""
        self._last_ts = 0.0

    # -------- Sync API --------
    def wait(self) -> None:
        """Block until the next permit is available (synchronous)."""
        with self._lock:
            now = time.monotonic()
            delay = max(0.0, (self._last_ts + self._interval) - now)
            if delay > 0:
                time.sleep(delay)
                now = time.monotonic()
            self._last_ts = now

    # -------- Async API --------
    async def wait_async(self) -> None:
        """Await until the next permit is available (asynchronous)."""
        async with self._alock:
            loop = asyncio.get_running_loop()
            now = loop.time()
            delay = max(0.0, (self._last_ts + self._interval) - now)
            if delay > 0:
                try:
                    await asyncio.sleep(delay)
                except asyncio.CancelledError:
                    # If caller cancels during sleep, propagate cleanly.
                    raise
                finally:
                    # Even if cancelled, don't advance _last_ts here.
                    pass
                now = loop.time()
            self._last_ts = now


class Meter:
    """
    Lightweight usage meter. (Thread-safe enough for typical single-writer usage;
    add locks if you need strict multi-thread safety.)
    """
    def __init__(self):
        self.calls = 0
        self.tokens_in = 0
        self.tokens_out = 0

    def log(self, calls: int = 1, t_in: int = 0, t_out: int = 0) -> None:
        self.calls += calls
        self.tokens_in += t_in
        self.tokens_out += t_out

    def as_dict(self) -> dict:
        return {
            "calls": self.calls,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
        }