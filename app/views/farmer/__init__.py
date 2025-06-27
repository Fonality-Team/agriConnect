from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models.product import Product, Category
from app.models.product_image import ProductImage
from app.extensions import db
from app.services.upload_service import LocalFileUpload
from app.models.price_and_delivery import PriceHistory
from sqlalchemy import or_

farmer_bp = Blueprint('farmer', __name__, template_folder='../templates/farmer')

@farmer_bp.route('/products/create', methods=['GET', 'POST'])
@login_required
def create_product():
    categories = Category.query.all()
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        category_id = request.form.get('category_id')
        images = request.files.getlist('images')

        if not name or not price or not category_id:
            flash('Name, price, and category are required.', 'danger')
            return render_template('farmer/create_product.html', categories=categories)

        product = Product(
            name=name,
            description=description,
            price=float(price),
            category_id=int(category_id),
            farmer_id=current_user.id
        )
        db.session.add(product)
        db.session.flush()  # Get product.id before commit

        # Price tracking: record initial price
        price_history = PriceHistory(product_id=product.id, price=float(price))
        db.session.add(price_history)

        # Handle multiple image uploads
        upload_service = LocalFileUpload()
        for image in images:
            if image and image.filename:
                try:
                    url = upload_service.upload_file(image, f'products/{product.id}')
                    product_image = ProductImage(product_id=product.id, image_url=url)
                    db.session.add(product_image)
                except Exception as e:
                    flash(f'Image upload failed: {e}', 'danger')

        db.session.commit()
        flash('Product created successfully!', 'success')
        return redirect(url_for('farmer.list_products'))

    return render_template('farmer/create_product.html', categories=categories)

@farmer_bp.route('/products')
@login_required
def list_products():
    # Add search and filter for farmer's own products
    search_query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    products_query = Product.query.filter_by(farmer_id=current_user.id)

    if search_query:
        products_query = products_query.filter(
            Product.name.ilike(f"%{search_query}%")
        )

    if category_filter:
        products_query = products_query.join(Category).filter(Category.name == category_filter)

    products_pagination = products_query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    categories = Category.query.all()

    return render_template('farmer/list_products.html',
                         products=products_pagination.items,
                         pagination=products_pagination,
                         categories=categories,
                         current_search=search_query,
                         current_category=category_filter)

@farmer_bp.route('/dashboard')
@login_required
def dashboard():
    product_count = Product.query.filter_by(farmer_id=current_user.id).count()
    return render_template('farmer/dashboard.html', product_count=product_count)

@farmer_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    from flask_wtf.csrf import validate_csrf
    csrf_token = request.form.get('csrf_token')
    try:
        validate_csrf(csrf_token)
    except Exception:
        flash('Invalid CSRF token.', 'danger')
        return redirect(url_for('farmer.list_products'))
    product = Product.query.filter_by(id=product_id, farmer_id=current_user.id).first_or_404()
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.', 'success')
    return redirect(url_for('farmer.list_products'))

@farmer_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.filter_by(id=product_id, farmer_id=current_user.id).first_or_404()
    categories = Category.query.all()
    if request.method == 'POST':
        from flask_wtf.csrf import validate_csrf
        csrf_token = request.form.get('csrf_token')
        try:
            validate_csrf(csrf_token)
        except Exception:
            flash('Invalid CSRF token.', 'danger')
            return redirect(url_for('farmer.list_products'))

        new_name = request.form.get('name')
        new_description = request.form.get('description')
        new_price = float(request.form.get('price'))
        new_category_id = int(request.form.get('category_id'))

        # Price tracking: if price changed, add to PriceHistory
        if product.price != new_price:
            price_history = PriceHistory(product_id=product.id, price=new_price)
            db.session.add(price_history)

        product.name = new_name
        product.description = new_description
        product.price = new_price
        product.category_id = new_category_id
        db.session.commit()

        # Handle new image uploads
        images = request.files.getlist('images')
        upload_service = LocalFileUpload()
        for image in images:
            if image and image.filename:
                try:
                    url = upload_service.upload_file(image, f'products/{product.id}')
                    product_image = ProductImage(product_id=product.id, image_url=url)
                    db.session.add(product_image)
                except Exception as e:
                    flash(f'Image upload failed: {e}', 'danger')
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('farmer.list_products'))

    # Fetch price history for monitoring
    price_history_list = PriceHistory.query.filter_by(product_id=product.id).order_by(PriceHistory.changed_at.desc()).all()
    return render_template('farmer/edit_product.html', product=product, categories=categories, price_history=price_history_list)

@farmer_bp.route('/products/delete_image/<int:image_id>', methods=['POST'])
@login_required
def delete_product_image(image_id):
    from flask_wtf.csrf import validate_csrf
    csrf_token = request.form.get('csrf_token')
    try:
        validate_csrf(csrf_token)
    except Exception:
        flash('Invalid CSRF token.', 'danger')
        return redirect(request.referrer or url_for('farmer.list_products'))
    image = ProductImage.query.get_or_404(image_id)
    product = Product.query.filter_by(id=image.product_id, farmer_id=current_user.id).first()
    if not product:
        flash('Not authorized.', 'danger')
        return redirect(url_for('farmer.list_products'))
    db.session.delete(image)
    db.session.commit()
    flash('Image deleted.', 'success')
    return redirect(url_for('farmer.edit_product', product_id=product.id))
