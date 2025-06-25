from app.views.main import main as main_blueprint
from flask import Flask


def register_views(app: Flask):
    """
    Register all views (blueprints) with the Flask application.
    """
    app.register_blueprint(main_blueprint, url_prefix='/')
    # Add other blueprints here as needed
    # e.g., app.register_blueprint(auth_blueprint, url_prefix='/auth')
    # e.g., app.register_blueprint(admin_blueprint, url_prefix='/admin')
