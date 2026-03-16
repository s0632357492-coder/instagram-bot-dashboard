import os
from flask import Blueprint, render_template, request, redirect, session, flash

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        IG_USERNAME = os.getenv("IG_USERNAME")
        IG_PASSWORD = os.getenv("IG_PASSWORD")

        if username == IG_USERNAME and password == IG_PASSWORD:

            session["user"] = username
            return redirect("/")

        else:

            flash("Invalid credentials")
            return redirect("/login")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():

    session.clear()
    return redirect("/login")