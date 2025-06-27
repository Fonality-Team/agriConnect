import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.user import User
from app.models.product import Product, Category
from app.models.product_image import ProductImage
from app.models.price_and_delivery import PriceHistory

def check_database():
    """Check what data already exists in the database"""
    print("=== Database Status ===")

    # Check users
    users = User.query.all()
    print(f"\nUsers ({len(users)} total):")
    for user in users:
        print(f"  - {user.username} ({user.email}) - Role: {user.role}")

    # Check categories
    categories = Category.query.all()
    print(f"\nCategories ({len(categories)} total):")
    for cat in categories:
        print(f"  - {cat.name}")

    # Check products
    products = Product.query.all()
    print(f"\nProducts ({len(products)} total):")
    for product in products[:10]:  # Show only first 10
        print(f"  - {product.name} (FCFA {product.price})")

    if len(products) > 10:
        print(f"  ... and {len(products) - 10} more products")

    # Check product images
    images = ProductImage.query.count()
    print(f"\nProduct Images: {images}")

    # Check price history
    price_history = PriceHistory.query.count()
    print(f"Price History Records: {price_history}")

    print("\n=== End Status ===")

def main():
    """Main function to check database status"""
    app = create_app()

    with app.app_context():
        check_database()

if __name__ == '__main__':
    main()
