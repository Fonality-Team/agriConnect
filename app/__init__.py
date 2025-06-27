from flask import Flask, render_template
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

    # Register views
    register_views(app)

    # 404 error handler
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app
