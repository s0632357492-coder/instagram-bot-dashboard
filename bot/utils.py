import time
import random
from config import Config
from services.logger import get_logger

logger = get_logger()

def load_followed_users():
    """
    Reads the followed_users.txt file and returns a set of user IDs.
    Using a set ensures O(1) lookup time when checking if a user 
    has already been processed.
    """
    followed_ids = set()
    file_path = Config.FOLLOWED_USERS_FILE

    if not file_path.exists():
        logger.info(f"Followed users file not found at {file_path}. Creating a new one.")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()
        return followed_ids

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                user_id = line.strip()
                if user_id:
                    followed_ids.add(user_id)
        return followed_ids
    except Exception as e:
        logger.error(f"Error loading followed users: {str(e)}")
        return followed_ids

def save_followed_user(user_id):
    """
    Appends a single user ID to the followed_users.txt file.
    
    Args:
        user_id (str/int): The Instagram user ID to persist.
    """
    file_path = Config.FOLLOWED_USERS_FILE
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"{user_id}\n")
        return True
    except Exception as e:
        logger.error(f"Error saving user ID {user_id}: {str(e)}")
        return False

def get_random_sleep_interval():
    """
    Calculates a random float value between the configured 
    MIN_DELAY and MAX_DELAY to simulate human behavior.
    """
    return random.uniform(Config.MIN_DELAY, Config.MAX_DELAY)

def perform_smart_delay(action_description="Next action"):
    """
    Calculates a random delay and pauses execution.
    Provides detailed logging for transparency in the bot logs.
    """
    delay = get_random_sleep_interval()
    
    # Logic for occasional longer breaks (5% chance) to bypass pattern detection
    if random.random() < 0.05:
        extra_break = random.randint(300, 600)  # 5 to 10 minutes
        logger.info(f"Taking a strategic long break: {extra_break} seconds.")
        delay += extra_break

    logger.info(f"Waiting {round(delay, 2)} seconds before: {action_description}")
    time.sleep(delay)

def format_timestamp(seconds):
    """
    Converts seconds into a human-readable HH:MM:SS format 
    for the dashboard display.
    """
    return time.strftime('%H:%M:%S', time.gmtime(seconds))