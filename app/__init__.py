# this is where the flask app gets created
# using create_app() so its easier to manage

import os

from flask import Flask
from dotenv import load_dotenv

from app.controllers.students import students_bp
from app.controllers.courses import courses_bp
from app.controllers.colleges import colleges_bp

# load .env so we get the secret key and debug settings
load_dotenv(override=True)


def create_app():
    app = Flask(__name__, template_folder="templates")

    # secret key is needed by flask for sessions
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
    app.config["DEBUG"] = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # register all the blueprints (students, courses, colleges)
    app.register_blueprint(students_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(colleges_bp)

    return app
