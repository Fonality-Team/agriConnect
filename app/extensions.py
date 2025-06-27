from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from typing import Optional

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()


def initialize_extensions(app: Flask):
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    login_manager.login_view = 'auth.login'  # Redirect to the login page if not authenticated
    login_manager.login_message = 'Please log in to access this page.'  # Custom message for unauthenticated users
    login_manager.session_protection = 'strong'  # Use strong session protection
    csrf = CSRFProtect(app)  # Initialize CSRF protection

    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id: str) -> Optional[User]:
        return User.query.get(int(user_id))
