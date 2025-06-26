import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


from app import create_app
from app.extensions import db
from app.models import *


def main():
    """Initialize the database."""
    app = create_app()
    with app.app_context():
        db.create_all()  # Create all tables
        print("Database initialized successfully.")


if __name__ == "__main__":
    sys.exit(main())
