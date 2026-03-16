from flask import Blueprint, request, jsonify, session
from bot.instagrapi_bot import bot_instance
from services.logger import get_logger
from config import Config

# Initialize the Blueprint
bot_bp = Blueprint('bot', __name__)
logger = get_logger()

@bot_bp.route('/start', methods=['POST'])
def start_bot():
    """
    Endpoint to start the Instagram bot.
    Expects JSON input: {"target": "username_to_scrape"}
    """
    if not session.get('logged_in'):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    if bot_instance.is_running:
        return jsonify({"status": "error", "message": "Bot is already running"}), 400

    data = request.get_json()
    target_account = data.get('target')

    if not target_account:
        return jsonify({"status": "error", "message": "Target account is required"}), 400

    try:
        # Trigger the background thread in the bot instance
        bot_instance.start(target_account)
        logger.info(f"Dashboard: Bot start command issued for target: {target_account}")
        return jsonify({"status": "success", "message": f"Bot started targeting {target_account}"})
    except Exception as e:
        logger.error(f"Dashboard: Failed to start bot: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@bot_bp.route('/stop', methods=['POST'])
def stop_bot():
    """
    Endpoint to gracefully stop the Instagram bot.
    """
    if not session.get('logged_in'):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    if not bot_instance.is_running:
        return jsonify({"status": "error", "message": "Bot is not running"}), 400

    try:
        bot_instance.stop()
        logger.info("Dashboard: Bot stop command issued.")
        return jsonify({"status": "success", "message": "Stop signal sent to bot"})
    except Exception as e:
        logger.error(f"Dashboard: Failed to stop bot: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@bot_bp.route('/status', methods=['GET'])
def get_status():
    """
    Returns the current execution status of the bot.
    """
    if not session.get('logged_in'):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    return jsonify({
        "is_running": bot_instance.is_running,
        "target_account": bot_instance.target_account,
        "client_authenticated": bool(bot_instance.cl.user_id)
    })

@bot_bp.route('/logs', methods=['GET'])
def get_bot_logs():
    """
    Reads the tail of the bot.log file to display on the dashboard.
    """
    if not session.get('logged_in'):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    try:
        log_path = Config.BOT_LOG_PATH
        if not log_path.exists():
            return jsonify({"logs": ["Log file not created yet."]})

        with open(log_path, "r", encoding="utf-8") as f:
            # Read last 50 lines for a more comprehensive dashboard view
            lines = f.readlines()
            tail_logs = [line.strip() for line in lines[-50:]]
            
        return jsonify({"logs": tail_logs})
    except Exception as e:
        logger.error(f"Dashboard: Error reading log file: {str(e)}")
        return jsonify({"status": "error", "message": "Could not read logs"}), 500