import json
import os
from pathlib import Path
from config import Config
from services.logger import get_logger

logger = get_logger()

class SessionManager:
    """
    Handles the persistence of Instagram login sessions to avoid 
    frequent logins and reduce the risk of account flagging.
    """

    def __init__(self, session_path=Config.SESSION_SETTINGS_PATH):
        self.session_path = Path(session_path)
        # Ensure the directory for the session file exists
        self.session_path.parent.mkdir(parents=True, exist_ok=True)

    def save_session(self, session_data):
        """
        Saves the instagrapi session settings to a JSON file.
        
        Args:
            session_data (dict): The dictionary containing session cookies/settings.
        """
        try:
            with open(self.session_path, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=4)
            logger.info(f"Session saved successfully to {self.session_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save session: {str(e)}")
            return False

    def load_session(self):
        """
        Loads the saved session settings from the JSON file.
        
        Returns:
            dict: The session settings if found, else None.
        """
        if not self.session_path.exists():
            logger.info("No existing session file found. A fresh login will be required.")
            return None

        try:
            with open(self.session_path, "r", encoding="utf-8") as f:
                session_data = json.load(f)
            
            if not session_data:
                logger.warning("Session file is empty.")
                return None
                
            logger.info("Existing session loaded from file.")
            return session_data
        except json.JSONDecodeError:
            logger.error("Session file is corrupted. Deleting and requesting fresh login.")
            self.clear_session()
            return None
        except Exception as e:
            logger.error(f"Error loading session: {str(e)}")
            return None

    def clear_session(self):
        """
        Deletes the session file. Useful for manual logouts or 
        when a session becomes invalid (checkpoint reached).
        """
        try:
            if self.session_path.exists():
                os.remove(self.session_path)
                logger.info("Session file cleared.")
            return True
        except Exception as e:
            logger.error(f"Failed to clear session file: {str(e)}")
            return False

    def session_exists(self):
        """
        Checks if a session file currently exists on disk.
        """
        return self.session_path.exists()

# Singleton instance to be used across the application
session_manager = SessionManager()