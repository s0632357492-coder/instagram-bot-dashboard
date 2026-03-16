from flask import Blueprint, request, jsonify, session
from bot.instagrapi_bot import bot_instance
from services.logger import get_logger
from config import Config

bot_bp = Blueprint("bot", __name__)

logger = get_logger()


# -----------------------------
# START BOT
# -----------------------------
@bot_bp.route("/start", methods=["POST"])
def start_bot():

    if "user" not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    if bot_instance.is_running:
        return jsonify({"status": "error", "message": "Bot is already running"}), 400

    data = request.get_json()
    target_account = data.get("target")

    if not target_account:
        return jsonify({"status": "error", "message": "Target account is required"}), 400

    try:

        bot_instance.start(target_account)

        logger.info(f"Dashboard: Bot start command issued for target: {target_account}")

        return jsonify({
            "status": "success",
            "message": f"Bot started targeting {target_account}"
        })

    except Exception as e:

        logger.error(f"Dashboard: Failed to start bot: {str(e)}")

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# -----------------------------
# STOP BOT
# -----------------------------
@bot_bp.route("/stop", methods=["POST"])
def stop_bot():

    if "user" not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    if not bot_instance.is_running:
        return jsonify({"status": "error", "message": "Bot is not running"}), 400

    try:

        bot_instance.stop()

        logger.info("Dashboard: Bot stop command issued.")

        return jsonify({
            "status": "success",
            "message": "Stop signal sent to bot"
        })

    except Exception as e:

        logger.error(f"Dashboard: Failed to stop bot: {str(e)}")

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# -----------------------------
# STATUS
# -----------------------------
@bot_bp.route("/status", methods=["GET"])
def get_status():

    if "user" not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    return jsonify({
        "is_running": bot_instance.is_running,
        "target_account": bot_instance.target_account,
        "client_authenticated": bool(bot_instance.cl.user_id)
    })


# -----------------------------
# LOGS
# -----------------------------
@bot_bp.route("/logs", methods=["GET"])
def get_bot_logs():

    if "user" not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    try:

        log_path = Config.BOT_LOG_PATH

        if not log_path.exists():
            return jsonify({"logs": ["Log file not created yet."]})

        with open(log_path, "r", encoding="utf-8") as f:

            lines = f.readlines()

            tail_logs = [line.strip() for line in lines[-50:]]

        return jsonify({"logs": tail_logs})

    except Exception as e:

        logger.error(f"Dashboard: Error reading log file: {str(e)}")

        return jsonify({
            "status": "error",
            "message": "Could not read logs"
        }), 500