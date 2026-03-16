import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Configuration class for the Instagram Automation Bot.
    Handles environment variables, file paths, and bot behavior limits.
    """
    
    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-12345")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # Instagram Credentials
    IG_USERNAME = os.getenv("IG_USERNAME")
    IG_PASSWORD = os.getenv("IG_PASSWORD")
    IG_2FA_SEED = os.getenv("IG_2FA_SEED", None)

    # Base Directory
    BASE_DIR = Path(__file__).resolve().parent

    # Path Settings
    LOGS_DIR = BASE_DIR / "logs"
    DATA_DIR = BASE_DIR / "data"
    SESSIONS_DIR = DATA_DIR / "sessions"
    
    # Ensure directories exist
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    # File Paths
    BOT_LOG_PATH = LOGS_DIR / "bot.log"
    ERROR_LOG_PATH = LOGS_DIR / "error.log"
    FOLLOWED_USERS_FILE = DATA_DIR / "followed_users.txt"
    SESSION_SETTINGS_PATH = SESSIONS_DIR / "ig_session.json"

    # Bot Behavior Limits (Anti-Ban Measures)
    # These settings help mimic human behavior to avoid Instagram detection
    FOLLOW_LIMIT_PER_DAY = 150
    FOLLOW_LIMIT_PER_HOUR = 20
    
    # Delay Settings (in seconds)
    MIN_DELAY = 30    # Minimum wait between actions
    MAX_DELAY = 120   # Maximum wait between actions
    
    # Anti-Ban Protection
    ENABLE_RANDOM_SLEEP = True
    MAX_RETRIES = 3   # For failed requests
    
    # Dashboard Settings
    STATS_UPDATE_INTERVAL = 5  # Seconds for JS polling if applicable

    @staticmethod
    def validate():
        """Basic validation to ensure critical variables are present."""
        if not Config.IG_USERNAME or not Config.IG_PASSWORD:
            print("[!] WARNING: IG_USERNAME or IG_PASSWORD not found in environment variables.")
            return False
        return True

# Initialize validation check on import
Config.validate()