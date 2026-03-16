import time
import threading
from instagrapi import Client
from instagrapi.exceptions import (
    LoginRequired,
    FeedbackRequired,
    PleaseWaitFewMinutes
)

from config import Config
from services.logger import get_logger
from services.anti_ban import anti_ban_manager
from services.session_manager import session_manager

logger = get_logger()


class InstagramBot:

    def __init__(self):
        self.cl = Client()
        self.is_running = False
        self.stop_event = threading.Event()
        self.target_account = ""
        self.followed_list = self._load_followed_users()

    def _load_followed_users(self):
        if not Config.FOLLOWED_USERS_FILE.exists():
            return set()

        with open(Config.FOLLOWED_USERS_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())

    def _save_followed_user(self, user_id):
        self.followed_list.add(str(user_id))

        with open(Config.FOLLOWED_USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")

    def login(self):

        try:

            session_data = session_manager.load_session()

            if session_data:

                logger.info("Loading saved Instagram session...")

                self.cl.set_settings(session_data)

                try:
                    self.cl.get_timeline_feed()
                    logger.info("Session login successful")

                except LoginRequired:

                    logger.warning("Session expired. Logging in again...")

                    self.cl.login(
                        Config.IG_USERNAME,
                        Config.IG_PASSWORD
                    )

            else:

                logger.info("No session found. Performing fresh login...")

                self.cl.login(
                    Config.IG_USERNAME,
                    Config.IG_PASSWORD
                )

            session_manager.save_session(self.cl.get_settings())

            return True

        except Exception as e:

            logger.error(f"Login failed: {str(e)}")
            return False

    def start(self, target_account):

        if self.is_running:
            logger.warning("Bot already running")
            return

        self.target_account = target_account
        self.is_running = True
        self.stop_event.clear()

        self.thread = threading.Thread(target=self._run_loop)
        self.thread.daemon = True
        self.thread.start()

        logger.info(f"Bot started targeting: {target_account}")

    def stop(self):

        self.is_running = False
        self.stop_event.set()

        logger.info("Bot stop signal received")

    def _run_loop(self):

        try:

            if not self.cl.user_id:

                if not self.login():
                    self.is_running = False
                    return

            logger.info(f"Getting target id: {self.target_account}")

            target_id = self.cl.user_id_from_username(
                self.target_account
            )

            logger.info("Fetching followers...")

            followers = self.cl.user_followers(
                target_id,
                amount=200
            )

            for user_id, user_info in followers.items():

                if self.stop_event.is_set():
                    logger.info("Bot stopped")
                    break

                if str(user_id) in self.followed_list:
                    continue

                if not anti_ban_manager.can_follow():

                    logger.warning("Daily limit reached. Sleeping 1 hour")

                    self.stop_event.wait(3600)
                    continue

                try:

                    logger.info(f"Following {user_info.username}")

                    self.cl.user_follow(user_id)

                    self._save_followed_user(user_id)

                    anti_ban_manager.increment_follow()

                    anti_ban_manager.sleep_random(
                        action_name=f"follow {user_info.username}"
                    )

                except FeedbackRequired:

                    logger.error("Instagram action blocked")

                    self.stop()
                    break

                except PleaseWaitFewMinutes:

                    logger.warning("Rate limit. Sleeping 15 minutes")

                    self.stop_event.wait(900)

                except Exception as e:

                    logger.error(f"Follow error: {str(e)}")

                    time.sleep(10)

            logger.info("Task completed")

        except Exception as e:

            logger.error(f"Bot crashed: {str(e)}")

        finally:

            self.is_running = False


bot_instance = InstagramBot()