import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


from app import create_app
from app.extensions import db
from app.models import *


#  create admin user
def create_admin_user():
    """Create an admin user if it doesn't exist."""
    from app.models.user import User

    admin = User.query.filter_by(role='admin').first()
    if not admin:
        email = input("Enter admin email: ")
        password = input("Enter admin password: ")
        admin = User(email=email, role='admin', username='admin', password=password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user created with email: {email}")
    else:
        print("Admin user already exists.")




def main():
    """Initialize the database."""
    app = create_app()
    with app.app_context():
        db.create_all()  # Create all tables
        print("Database initialized successfully.")


        create_admin_user()  # Create admin user if it doesn't exist


if __name__ == "__main__":
    sys.exit(main())
