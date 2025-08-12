import time
from leafsdk import logger

class MissionClock:
    def __init__(self, rate_hz: float):
        self._interval = 1.0 / rate_hz
        self._last_tick_time = None

    def tick(self):
        self._last_tick_time = time.time()

    def tock(self):
        elapsed = time.time() - self._last_tick_time
        sleep_duration = max(0.0, self._interval - elapsed)
        time.sleep(sleep_duration)