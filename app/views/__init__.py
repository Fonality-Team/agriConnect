from app.views.main import main_bp
from app.views.auth import auth_bp
from app.views.farmer import farmer_bp as farmer_blueprint
from app.views.admin import admin_bp as admin_blueprint
from flask import Flask
from app.views.messages import message_bp as messages_blueprint


def register_views(app: Flask):
    """
    Register all views (blueprints) with the Flask application.
    """
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(farmer_blueprint, url_prefix='/farmer')
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    app.register_blueprint(messages_blueprint, url_prefix='/messages')
    # Add other blueprints here as needed
    # e.g., app.register_blueprint(another_blueprint, url_prefix='/another')

    # Register API blueprint if it exists
    try:
        from app.views.api import api_bp
        app.register_blueprint(api_bp)
    except ImportError:
        pass
