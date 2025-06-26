from flask import Flask
from app.core.config import Config
from app.extensions import initialize_extensions
from app.views import register_views
from app.models import *


def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Initialize extensions
    initialize_extensions(app)

    # Register blueprints
    register_views(app)
    return app
