import time
import random
from datetime import datetime, timedelta
from config import Config
from services.logger import get_logger

logger = get_logger()

class AntiBanService:
    """
    Service to manage anti-ban logic, including randomized delays,
    hourly/daily limit tracking, and human-like behavior simulation.
    """

    def __init__(self):
        self.follow_count_hour = 0
        self.follow_count_day = 0
        self.last_reset_hour = datetime.now()
        self.last_reset_day = datetime.now()

    def _check_and_reset_limits(self):
        """
        Resets the hourly and daily counters if the respective 
        time windows have passed.
        """
        now = datetime.now()

        # Reset hourly counter
        if now - self.last_reset_hour >= timedelta(hours=1):
            logger.info("Resetting hourly follow counter.")
            self.follow_count_hour = 0
            self.last_reset_hour = now

        # Reset daily counter
        if now - self.last_reset_day >= timedelta(days=1):
            logger.info("Resetting daily follow counter.")
            self.follow_count_day = 0
            self.last_reset_day = now

    def can_follow(self):
        """
        Validates if the bot is within the safety limits defined in config.py.
        Returns:
            bool: True if safe to proceed, False otherwise.
        """
        self._check_and_reset_limits()

        if self.follow_count_hour >= Config.FOLLOW_LIMIT_PER_HOUR:
            logger.warning(f"Hourly limit reached: {self.follow_count_hour}/{Config.FOLLOW_LIMIT_PER_HOUR}")
            return False

        if self.follow_count_day >= Config.FOLLOW_LIMIT_PER_DAY:
            logger.warning(f"Daily limit reached: {self.follow_count_day}/{Config.FOLLOW_LIMIT_PER_DAY}")
            return False

        return True

    def sleep_random(self, action_name="Action"):
        """
        Implements a random delay between actions to mimic human behavior.
        The range is pulled from Config.MIN_DELAY and Config.MAX_DELAY.
        """
        if not Config.ENABLE_RANDOM_SLEEP:
            return

        delay = random.uniform(Config.MIN_DELAY, Config.MAX_DELAY)
        # Occasionally add a "long break" (1 in 10 chance) for better safety
        if random.randint(1, 10) == 7:
            extra_break = random.uniform(60, 180)
            delay += extra_break
            logger.info(f"Taking an extra long human-like break: {round(extra_break, 2)}s")

        logger.info(f"Anti-Ban: Sleeping for {round(delay, 2)}s before next {action_name}...")
        time.sleep(delay)

    def increment_follow(self):
        """
        Updates the counters after a successful follow action.
        """
        self.follow_count_hour += 1
        self.follow_count_day += 1
        logger.debug(f"Follow stats updated: Hour({self.follow_count_hour}), Day({self.follow_count_day})")

    def get_stats(self):
        """
        Returns the current limit statistics for the dashboard.
        """
        self._check_and_reset_limits()
        return {
            "hour_count": self.follow_count_hour,
            "day_count": self.follow_count_day,
            "hour_limit": Config.FOLLOW_LIMIT_PER_HOUR,
            "day_limit": Config.FOLLOW_LIMIT_PER_DAY,
            "next_hour_reset": (self.last_reset_hour + timedelta(hours=1)).strftime("%H:%M:%S"),
        }

# Singleton instance to be used across the application
anti_ban_manager = AntiBanService()