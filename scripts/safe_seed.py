import os
import sys
import random
from datetime import datetime, timedelta

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.product import Product, Category, ProductImage

def safe_create_categories():
    """Create categories only if they don't exist"""
    categories_data = [
        {'name': 'Fruits', 'description': 'Fresh seasonal fruits', 'image': '/static/img/Fruits.jpg'},
        {'name': 'Vegetables', 'description': 'Fresh vegetables and leafy greens', 'image': '/static/img/Fruits.jpg'},
        {'name': 'Grains', 'description': 'Rice, wheat, corn and other grains', 'image': '/static/img/Vegetables.jpg'},
        {'name': 'Tubers', 'description': 'Potatoes, yams, cassava and root vegetables', 'image': '/static/img/Tuber.jpeg'},
        {'name': 'Nuts', 'description': 'Groundnuts, cashews and other nuts', 'image': '/static/img/Nuts.jpg'},
    ]

    created_count = 0
    categories = []

    for cat_data in categories_data:
        existing_cat = Category.query.filter_by(name=cat_data['name']).first()
        if not existing_cat:
            category = Category(
                name=cat_data['name'],
                description=cat_data['description'],
                image=cat_data['image']
            )
            db.session.add(category)
            categories.append(category)
            created_count += 1
        else:
            categories.append(existing_cat)

    if created_count > 0:
        db.session.commit()
        print(f"Created {created_count} new categories")
    else:
        print("All categories already exist")

    return categories

def safe_create_users():
    """Create users only if they don't exist"""
    users_data = [
        {
            'username': 'admin_user',
            'email': 'admin@agriconnect.com',
            'role': 'admin',
            'phone': '+237123456789',
            'whatsapp': '+237123456789'
        },
        {
            'username': 'farmer_john',
            'email': 'john@farm.com',
            'role': 'farmer',
            'phone': '+237987654321',
            'whatsapp': '+237987654321'
        },
        {
            'username': 'mary_farm',
            'email': 'mary@farm.com',
            'role': 'farmer',
            'phone': '+237555123456',
            'whatsapp': '+237555123456'
        },
        {
            'username': 'peter_agri',
            'email': 'peter@farm.com',
            'role': 'farmer',
            'phone': '+237444567890',
            'whatsapp': None
        },
        {
            'username': 'grace_harvest',
            'email': 'grace@farm.com',
            'role': 'farmer',
            'phone': None,
            'whatsapp': '+237333789012'
        },
        {
            'username': 'samuel_crops',
            'email': 'samuel@farm.com',
            'role': 'farmer',
            'phone': '+237222345678',
            'whatsapp': '+237222345678'
        }
    ]

    created_count = 0
    users = []

    for user_data in users_data:
        existing_user = User.query.filter(
            (User.email == user_data['email']) |
            (User.username == user_data['username'])
        ).first()

        if not existing_user:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                role=user_data['role'],
                phone=user_data.get('phone'),
                whatsapp=user_data.get('whatsapp')
            )
            password = 'admin123' if user_data['role'] == 'admin' else 'password123'
            user.set_password(password)
            db.session.add(user)
            users.append(user)
            created_count += 1
        else:
            users.append(existing_user)

    if created_count > 0:
        db.session.commit()
        print(f"Created {created_count} new users")
    else:
        print("All users already exist")

    return users

def safe_create_products(categories, farmers, max_products=50):
    """Create products only if we don't have enough"""
    existing_count = Product.query.count()

    if existing_count >= max_products:
        print(f"Already have {existing_count} products (target: {max_products})")
        return Product.query.all()

    products_to_create = max_products - existing_count
    print(f"Creating {products_to_create} new products...")

    # Sample product templates with new fields
    product_templates = [
        {
            'name': 'Sweet Bananas',
            'description': 'Fresh ripe bananas, perfect for snacking',
            'category': 'Fruits',
            'image_id': 200,
            'unit': 'bunches',
            'location': 'Douala Farm',
            'harvest_date': 'Yesterday'
        },
        {
            'name': 'Juicy Oranges',
            'description': 'Sweet citrus oranges packed with vitamin C',
            'category': 'Fruits',
            'image_id': 201,
            'unit': 'kg',
            'location': 'Yaoundé Orchard',
            'harvest_date': 'This morning'
        },
        {
            'name': 'Fresh Tomatoes',
            'description': 'Juicy red tomatoes for cooking',
            'category': 'Vegetables',
            'image_id': 202,
            'unit': 'kg',
            'location': 'Bamenda Valley',
            'harvest_date': 'Last week'
        },
        {
            'name': 'Green Peppers',
            'description': 'Fresh bell peppers',
            'category': 'Vegetables',
            'image_id': 203,
            'unit': 'pieces',
            'location': 'Limbe Gardens',
            'harvest_date': '2 days ago'
        },
        {
            'name': 'White Rice',
            'description': 'Premium quality white rice',
            'category': 'Grains',
            'image_id': 204,
            'unit': 'bags',
            'location': 'Ndop Plains',
            'harvest_date': 'Last month'
        },
        {
            'name': 'Brown Rice',
            'description': 'Healthy brown rice with fiber',
            'category': 'Grains',
            'image_id': 205,
            'unit': 'bags',
            'location': 'Ndop Plains',
            'harvest_date': 'Last month'
        },
        {
            'name': 'Black Beans',
            'description': 'Protein-rich black beans',
            'category': 'Legumes',
            'image_id': 206,
            'unit': 'kg',
            'location': 'Foumban Farm',
            'harvest_date': 'Two weeks ago'
        },
        {
            'name': 'Irish Potatoes',
            'description': 'Fresh Irish potatoes for cooking',
            'category': 'Tubers',
            'image_id': 207,
            'unit': 'kg',
            'location': 'Dschang Hills',
            'harvest_date': 'Last week'
        },
        {
            'name': 'Groundnuts',
            'description': 'Roasted groundnuts/peanuts',
            'category': 'Nuts',
            'image_id': 208,
            'unit': 'kg',
            'location': 'Maroua Fields',
            'harvest_date': 'Three weeks ago'
        },
        {
            'name': 'Fresh Tilapia',
            'description': 'Fresh water tilapia fish',
            'category': 'Fish',
            'image_id': 209,
            'unit': 'pieces',
            'location': 'Edea Fish Farm',
            'harvest_date': 'This morning'
        }
    ]

    # Create category lookup
    category_lookup = {cat.name: cat for cat in categories}

    products = []
    for i in range(products_to_create):
        template = product_templates[i % len(product_templates)]

        # Add variation to product names
        variation = f" (Batch {i//len(product_templates) + 1})" if i >= len(product_templates) else ""

        product = Product(
            name=template['name'] + variation,
            description=template['description'],
            price=round(random.uniform(500, 5000), 2),
            quantity=random.randint(5, 100),
            unit=template['unit'],
            location=template['location'],
            harvest_date=template['harvest_date'],
            category_id=category_lookup[template['category']].id,
            farmer_id=random.choice(farmers).id,
            created_at=datetime.now() - timedelta(days=random.randint(0, 30))
        )

        db.session.add(product)
        products.append(product)

    db.session.commit()

    # Add images
    for i, product in enumerate(products):
        template = product_templates[i % len(product_templates)]
        # Add sample image using Lorem Picsum with product-specific image ID
        image = ProductImage(
            product_id=product.id,
            image_url=f'https://picsum.photos/id/{template["image_id"] + (i // len(product_templates))}/800/600',
            is_primary=True
        )
        db.session.add(image)

    db.session.commit()
    print(f"Created {len(products)} products with images")

    return Product.query.all()

def main():
    """Main function with better error handling"""
    app = create_app()

    with app.app_context():
        try:
            print("Starting safe database seeding...")

            # Create categories
            categories = safe_create_categories()

            print("\nSeeding completed successfully!")

            print(f"Total categories: {Category.query.count()}")

        except Exception as e:
            print(f"Error during seeding: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    main()
