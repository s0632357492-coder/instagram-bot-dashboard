import os
import threading
from flask import Flask, render_template
from config import Config
from routes.dashboard_routes import dashboard_bp
from routes.bot_routes import bot_bp
from services.logger import setup_logger

# สร้าง logger ไว้ระดับ Global เพื่อให้เรียกใช้ได้ง่าย
logger = setup_logger()

def create_app():
    """
    Initialize and configure the Flask application.
    """
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    # ความปลอดภัยของ Session
    app.secret_key = os.getenv("SECRET_KEY", "instabot_secret")

    # Load config
    app.config.from_object(Config)

    # ตรวจสอบและสร้าง Directory ที่จำเป็น
    Config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    Config.SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Initializing Instagram Bot Dashboard...")

    # Register routes
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(bot_bp)

    # -----------------------------
    # GLOBAL STATS (Injected into all templates)
    # -----------------------------
    @app.context_processor
    def inject_stats():
        # แนะนำว่าข้อมูลตรงนี้ควรดึงมาจาก Database หรือ Global Object จริงๆ
        # อันนี้เป็นค่าเริ่มต้น
        stats = {
            "username": os.getenv("IG_USERNAME", "Not logged in"),
            "followers": 0,
            "following": 0,
            "followed_today": 0,
            "total_followed": 0,
            "bot_status": "Running" if (bot_thread and bot_thread.is_alive()) else "Stopped"
        }
        return dict(stats=stats)

    # -----------------------------
    # ERROR HANDLERS
    # -----------------------------
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("index.html", error="Page not found"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("index.html", error="Internal server error"), 500

    return app


# -----------------------------
# BOT THREAD MANAGEMENT
# -----------------------------

bot_thread = None

def start_bot_background():
    """
    ฟังก์ชันสำหรับเริ่มทำงาน Bot ใน Thread แยก
    """
    global bot_thread

    # ป้องกันการรัน Bot ซ้ำซ้อน
    if bot_thread and bot_thread.is_alive():
        logger.warning("Bot is already running in background.")
        return

    def run_bot():
        try:
            # Import ภายในเพื่อเลี่ยง Circular Import
            from bot.instagrapi_bot import bot_instance
            logger.info("Starting Bot Instance...")
            bot_instance.start()
        except Exception as e:
            logger.error(f"Bot execution failed: {e}")

    bot_thread = threading.Thread(target=run_bot, name="InstaBotThread")
    bot_thread.daemon = True  # ให้ Thread ตายตาม Main Process เมื่อปิดโปรแกรม
    bot_thread.start()
    logger.info("Bot thread started.")


# -----------------------------
# START APP
# -----------------------------

app = create_app()

if __name__ == "__main__":
    # 1. ตรวจสอบ Configuration
    if not Config.validate():
        logger.error("Configuration validation failed. Check your .env file.")
        exit(1)

    # 2. ป้องกัน Flask Debug Mode รัน Bot สองรอบ
    # Flask ในโหมด Debug จะรันโค้ด 2 รอบ (Main process + Child process สำหรับ reload)
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not Config.DEBUG:
        # คุณสามารถเลือกได้ว่าจะให้ Bot เริ่มทันที หรือไปกด Start ใน Dashboard
        # start_bot_background() 
        pass

    # 3. รัน Flask Server
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=Config.DEBUG,
        threaded=True # สำคัญมากเพื่อให้ Flask รองรับการทำงานหลายอย่างพร้อมกัน
    )