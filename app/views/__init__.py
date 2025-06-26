from app.views.main import main as main_blueprint
from app.views.auth import auth_bp as auth_blueprint
from flask import Flask


def register_views(app: Flask):
    """
    Register all views (blueprints) with the Flask application.
    """
    app.register_blueprint(main_blueprint, url_prefix='/')
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    # Add other blueprints here as needed
    # e.g., app.register_blueprint(admin_blueprint, url_prefix='/admin')
