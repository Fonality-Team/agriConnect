import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.product import Product, Category
from app.models.product_image import ProductImage
from app.models.price_and_delivery import PriceHistory

def clear_all_data():
    """Clear all data from the database"""
    print("Clearing all data from database...")

    # Delete in reverse dependency order
    PriceHistory.query.delete()
    ProductImage.query.delete()
    Product.query.delete()
    Category.query.delete()

    # Only delete test users (keep admin if needed)
    test_emails = ['john@farm.com', 'mary@farm.com', 'peter@farm.com',
                   'grace@farm.com', 'samuel@farm.com', 'esther@farm.com',
                   'joseph@farm.com', 'rebecca@farm.com', 'david@farm.com',
                   'sarah@farm.com']

    for email in test_emails:
        user = User.query.filter_by(email=email).first()
        if user:
            db.session.delete(user)

    db.session.commit()
    print("All test data cleared successfully!")

def main():
    """Main function to run the clearing script"""
    app = create_app()

    with app.app_context():
        confirm = input("Are you sure you want to clear all data? This cannot be undone. (yes/no): ")
        if confirm.lower() == 'yes':
            clear_all_data()
        else:
            print("Operation cancelled.")

if __name__ == '__main__':
    main()
