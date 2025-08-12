# leafsdk/core/mission/condition.py
from leafsdk import logger

class BatteryCondition:
    def __init__(self, threshold_percent):
        self.threshold = threshold_percent

    def check(self, mav):
        msg = mav.receive_message(type='SYS_STATUS', blocking=False)
        if msg and msg.battery_remaining >= self.threshold:
            logger.info(f"Battery OK: {msg.battery_remaining}% ≥ {self.threshold}%")
            return True
        else:
            logger.info(f"Waiting: Battery {msg.battery_remaining if msg else '?'}% < {self.threshold}%")
            return False
