from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models import get_user_by_username, create_user, username_exists
from app.user.forms import validate_auth_form

user_bp = Blueprint("user", __name__)


@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            data = validate_auth_form(request.form)
        except ValueError as exc:
            return render_template("login.html", message=str(exc))

        user = get_user_by_username(data["username"])
        if not user or not user.check_password(data["password"]):
            return render_template("login.html", message="Invalid username or password.")

        login_user(user)
        return redirect(url_for("students.index"))

    return render_template("login.html")


@user_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        try:
            data = validate_auth_form(request.form)
        except ValueError as exc:
            return render_template("signup.html", message=str(exc))

        if username_exists(data["username"]):
            return render_template("signup.html", message="That username is already taken.")

        create_user(data["username"], data["password"])
        return redirect(url_for("user.login"))

    return render_template("signup.html")


@user_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("user.login"))
