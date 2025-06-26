from app import create_app
from app.extensions import db
from app.models import all

def init_db():
    """Initialize the database."""
    app = create_app()
    with app.app_context():
        db.create_all()  # Create all tables
        print("Database initialized successfully.")
