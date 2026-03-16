import os
from flask import Blueprint, render_template, request, redirect, session, flash, url_for

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        IG_USERNAME = os.getenv("IG_USERNAME")
        IG_PASSWORD = os.getenv("IG_PASSWORD")

        if username == IG_USERNAME and password == IG_PASSWORD:

            # ตั้ง session
            session["user"] = username
            session.permanent = True

            # เข้า dashboard ทันที
            return redirect("/dashboard")

        else:

            flash("Invalid credentials")
            return redirect(url_for("auth.login"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():

    session.clear()
    return redirect("/login")