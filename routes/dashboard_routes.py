from flask import Blueprint, render_template, redirect, url_for, session, jsonify, request
from config import Config
from services.anti_ban import anti_ban_manager
from bot.instagrapi_bot import bot_instance
from bot.utils import load_followed_users

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    """
    Main dashboard page
    """
    if not session.get('logged_in'):
        return redirect(url_for('dashboard.login'))

    stats = {
        "status": "Running" if bot_instance.is_running else "Stopped",
        "total_followed": len(load_followed_users()),
        "target_account": bot_instance.target_account or "None",
        "username": Config.IG_USERNAME
    }

    return render_template('index.html', stats=stats)


@dashboard_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Simple login system for dashboard
    """

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # login using credentials from .env
        if username == Config.IG_USERNAME and password == Config.IG_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard.index'))

        return render_template("login.html", error="Invalid credentials")

    return render_template('login.html')


@dashboard_bp.route('/api/stats')
def get_stats():

    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    anti_ban_stats = anti_ban_manager.get_stats()

    dashboard_data = {
        "bot_status": "Running" if bot_instance.is_running else "Stopped",
        "target_account": bot_instance.target_account,
        "total_followed": len(load_followed_users()),
        "hourly_count": anti_ban_stats["hour_count"],
        "hourly_limit": anti_ban_stats["hour_limit"],
        "daily_count": anti_ban_stats["day_count"],
        "daily_limit": anti_ban_stats["day_limit"],
        "next_reset": anti_ban_stats["next_hour_reset"]
    }

    return jsonify(dashboard_data)


@dashboard_bp.route('/api/logs')
def get_logs():

    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        if not Config.BOT_LOG_PATH.exists():
            return jsonify({"logs": ["No logs found yet."]})

        with open(Config.BOT_LOG_PATH, "r") as f:
            lines = f.readlines()
            last_logs = [line.strip() for line in lines[-20:]]

        return jsonify({"logs": last_logs})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route('/logout')
def logout():

    session.clear()
    return redirect(url_for('dashboard.login'))
