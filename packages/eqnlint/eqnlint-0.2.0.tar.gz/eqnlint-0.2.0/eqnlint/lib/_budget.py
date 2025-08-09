# lib/_budget.py
import time, threading

class RateLimiter:
    def __init__(self, qps=0.5):
        self._min_dt = 1.0 / max(qps, 1e-9)
        self._t = 0.0
        self._lock = threading.Lock()

    def wait(self):
        with self._lock:
            now = time.time()
            if now < self._t + self._min_dt:
                time.sleep(self._t + self._min_dt - now)
            self._t = time.time()

class Meter:
    def __init__(self): self.calls=0; self.tokens_in=0; self.tokens_out=0
    def log(self, calls=1, t_in=0, t_out=0):
        self.calls+=calls; self.tokens_in+=t_in; self.tokens_out+=t_out
    def as_dict(self): return dict(calls=self.calls,tokens_in=self.tokens_in,tokens_out=self.tokens_out)