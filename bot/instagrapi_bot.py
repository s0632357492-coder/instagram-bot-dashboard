import time
import random
import threading
from instagrapi import Client
from instagrapi.exceptions import (
    LoginRequired,
    ChallengeRequired,
    FeedbackRequired,
    PleaseWaitFewMinutes,
    RecaptchaChallengeForm
)
from config import Config
from services.logger import get_logger
from services.anti_ban import anti_ban_manager
from services.session_manager import session_manager

logger = get_logger()

class InstagramBot:
    """
    Core Instagram Bot class using instagrapi.
    Handles authentication, targeted following, and thread safety.
    """

    def __init__(self):
        self.cl = Client()
        self.is_running = False
        self.stop_event = threading.Event()
        self.target_account = ""
        self.followed_list = self._load_followed_users()

    def _load_followed_users(self):
        """Loads IDs of users already followed from the data file."""
        if not Config.FOLLOWED_USERS_FILE.exists():
            return set()
        with open(Config.FOLLOWED_USERS_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())

    def _save_followed_user(self, user_id):
        """Appends a newly followed user ID to the data file."""
        self.followed_list.add(str(user_id))
        with open(Config.FOLLOWED_USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")

    def login(self):
        """
        Handles login using saved sessions or fresh credentials.
        """
        try:
            session_data = session_manager.load_session()
            if session_data:
                logger.info("Attempting login via saved session...")
                self.cl.set_settings(session_data)
                try:
                    self.cl.login(Config.IG_USERNAME, Config.IG_PASSWORD)
                    logger.info("Login successful via session.")
                except LoginRequired:
                    logger.warning("Session expired. Attempting fresh login.")
                    self.cl.login(Config.IG_USERNAME, Config.IG_PASSWORD)
            else:
                logger.info("Attempting fresh login...")
                self.cl.login(Config.IG_USERNAME, Config.IG_PASSWORD)
            
            # Save session for next time
            session_manager.save_session(self.cl.get_settings())
            return True
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def start(self, target_account):
        """
        Starts the automation loop in a non-blocking manner.
        """
        if self.is_running:
            logger.warning("Bot is already running.")
            return

        self.target_account = target_account
        self.is_running = True
        self.stop_event.clear()
        
        # Start thread
        self.thread = threading.Thread(target=self._run_loop)
        self.thread.daemon = True
        self.thread.start()
        logger.info(f"Bot started targeting: {target_account}")

    def stop(self):
        """Signals the bot to stop at the next available interval."""
        self.is_running = False
        self.stop_event.set()
        logger.info("Stop signal sent to bot.")

    def _run_loop(self):
        """
        The main automation logic: fetches followers of a target and follows them.
        """
        try:
            if not self.cl.user_id:
                if not self.login():
                    self.is_running = False
                    return

            logger.info(f"Fetching user ID for target: {self.target_account}")
            target_id = self.cl.user_id_from_username(self.target_account)
            
            logger.info("Fetching target's followers (this may take a moment)...")
            followers = self.cl.user_followers(target_id, amount=200) 
            
            for user_id, user_info in followers.items():
                if self.stop_event.is_set():
                    logger.info("Bot stopped by user.")
                    break

                if str(user_id) in self.followed_list:
                    logger.debug(f"Skipping {user_info.username} (already followed).")
                    continue

                # Check Anti-Ban Limits
                if not anti_ban_manager.can_follow():
                    logger.warning("Safety limits reached. Sleeping for 1 hour...")
                    self.stop_event.wait(3600)
                    continue

                # Perform Follow
                try:
                    logger.info(f"Attempting to follow: {user_info.username}")
                    self.cl.user_follow(user_id)
                    
                    self._save_followed_user(user_id)
                    anti_ban_manager.increment_follow()
                    
                    # Randomized delay
                    anti_ban_manager.sleep_random(action_name=f"follow of {user_info.username}")

                except FeedbackRequired as e:
                    logger.error("Instagram Action Blocked. Stopping bot immediately.")
                    self.stop()
                    break
                except PleaseWaitFewMinutes:
                    logger.warning("Rate limit hit (PleaseWaitFewMinutes). Sleeping 15 mins.")
                    self.stop_event.wait(900)
                except Exception as e:
                    logger.error(f"Error following {user_info.username}: {str(e)}")
                    time.sleep(10)

            logger.info("Bot completed the task or reached the end of the list.")

        except Exception as e:
            logger.error(f"Bot Loop Crashed: {str(e)}")
        finally:
            self.is_running = False

# Global instance for thread-safe access from Flask routes
bot_instance = InstagramBot()