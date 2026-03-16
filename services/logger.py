import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from config import Config

def setup_logger():
    """
    Configures and returns a production-ready logger instance.
    Handles general bot activity logs and specific error-only logs.
    """
    # Ensure log directory exists
    Config.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Create a custom logger
    logger = logging.getLogger("InstagramBot")
    logger.setLevel(logging.DEBUG)

    # Avoid adding handlers multiple times if setup_logger is called repeatedly
    if logger.hasHandlers():
        return logger

    # Create formatters
    # Format: [2023-10-27 10:00:00] [INFO] [bot_logic.py:45] - User followed successfully
    detailed_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 1. General Bot Activity Log (INFO level and above)
    bot_log_handler = RotatingFileHandler(
        Config.BOT_LOG_PATH,
        maxBytes=5*1024*1024,  # 5MB per file
        backupCount=5,         # Keep 5 historical logs
        encoding='utf-8'
    )
    bot_log_handler.setLevel(logging.INFO)
    bot_log_handler.setFormatter(detailed_formatter)

    # 2. Specific Error Log (ERROR level and above)
    error_log_handler = RotatingFileHandler(
        Config.ERROR_LOG_PATH,
        maxBytes=2*1024*1024,  # 2MB per file
        backupCount=3,
        encoding='utf-8'
    )
    error_log_handler.setLevel(logging.ERROR)
    error_log_handler.setFormatter(detailed_formatter)

    # 3. Console Output for real-time monitoring (DEBUG level)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(detailed_formatter)

    # Add handlers to the logger
    logger.addHandler(bot_log_handler)
    logger.addHandler(error_log_handler)
    logger.addHandler(console_handler)

    return logger

def get_logger():
    """
    Utility function to retrieve the existing logger or initialize a new one.
    """
    return logging.getLogger("InstagramBot")

# Convenience functions for structured logging
def log_info(message):
    get_logger().info(message)

def log_error(message, exc_info=True):
    get_logger().error(message, exc_info=exc_info)

def log_debug(message):
    get_logger().debug(message)

def log_warning(message):
    get_logger().warning(message)