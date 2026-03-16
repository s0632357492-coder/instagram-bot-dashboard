import os
import threading
from flask import Flask, render_template, session, redirect, request
from config import Config
from routes.dashboard_routes import dashboard_bp
from routes.bot_routes import bot_bp
from routes.auth_routes import auth_bp
from services.logger import setup_logger

# -----------------------------
# LOGGER
# -----------------------------
logger = setup_logger()

# -----------------------------
# GLOBAL THREAD
# -----------------------------
bot_thread = None


def create_app():

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    # -----------------------------
    # SECURITY
    # -----------------------------
    app.secret_key = os.getenv("SECRET_KEY", "instabot_secret")

    # SESSION CONFIG (สำคัญสำหรับ Render HTTPS)
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_PERMANENT"] = False

    # Load config
    app.config.from_object(Config)

    # -----------------------------
    # CREATE REQUIRED DIRECTORIES
    # -----------------------------
    Config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    Config.SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Initializing Instagram Bot Dashboard...")

    # -----------------------------
    # REGISTER BLUEPRINTS
    # -----------------------------
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(bot_bp)

    # -----------------------------
    # LOGIN PROTECTION
    # -----------------------------
    @app.before_request
    def require_login():

        # endpoint บางครั้งเป็น None
        if request.endpoint is None:
            return

        allowed_routes = [
            "auth.login",
            "auth.logout",
            "static"
        ]

        if request.endpoint in allowed_routes:
            return

        if "user" not in session:
            return redirect("/login")

    # -----------------------------
    # GLOBAL STATS
    # -----------------------------
    @app.context_processor
    def inject_stats():

        is_running = bot_thread is not None and bot_thread.is_alive()

        stats = {
            "username": os.getenv("IG_USERNAME", "Not logged in"),
            "followers": 0,
            "following": 0,
            "followed_today": 0,
            "total_followed": 0,
            "bot_status": "Running" if is_running else "Stopped"
        }

        return dict(stats=stats)

    # -----------------------------
    # ERROR HANDLERS
    # -----------------------------
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("index.html", error="404 - Page Not Found"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("index.html", error="500 - Internal Server Error"), 500

    return app


# -----------------------------
# BOT CONTROL
# -----------------------------
def start_bot_background():

    global bot_thread

    if bot_thread and bot_thread.is_alive():
        logger.info("Bot already running.")
        return False

    def run_bot():

        try:
            from bot.instagrapi_bot import bot_instance

            logger.info("Bot started in background thread.")

            bot_instance.start()

        except Exception as e:

            logger.error(f"Bot thread error: {str(e)}")

    bot_thread = threading.Thread(
        target=run_bot,
        name="InstaBotThread",
        daemon=True
    )

    bot_thread.start()

    logger.info("Bot thread launched.")

    return True


# -----------------------------
# APP START
# -----------------------------
app = create_app()

if __name__ == "__main__":

    if not Config.validate():

        logger.critical("Invalid configuration. Exiting.")
        exit(1)

    app.run(

        host="0.0.0.0",

        port=int(os.environ.get("PORT", 10000)),

        debug=Config.DEBUG,

        threaded=True
    )