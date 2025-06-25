from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import Flask

db = SQLAlchemy()
login_manager = LoginManager()


def initialize_extensions(app: Flask):
    db.init_app(app)
    # login_manager.init_app(app)
    # login_manager.login_view = 'auth.login'  # Redirect to the login page if not authenticated
    # login_manager.login_message = 'Please log in to access this page.'  # Custom message for unauthenticated users
    # login_manager.session_protection = 'strong'  # Use strong session protection
