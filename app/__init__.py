import os

from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv

from app.models import bcrypt, get_user_by_id
from app.students import students_bp
from app.courses  import courses_bp
from app.colleges import colleges_bp
from app.user     import user_bp

load_dotenv(override=True)


def create_app():
    app = Flask(__name__, template_folder="templates")

    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
    app.config["DEBUG"]      = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # init extensions
    bcrypt.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "user.login"       # redirect here if not logged in
    login_manager.login_message = "Please log in to access this page."

    @login_manager.user_loader
    def load_user(user_id):
        return get_user_by_id(int(user_id))

    # register blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(colleges_bp)

    return app
