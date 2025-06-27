from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.product import Category
from app.models.user import User
from app.models.product import Product
from app.models.price_and_delivery import PriceHistory
from app.services.upload_service import LocalFileUpload
from app.extensions import db
from sqlalchemy import func
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin')

def admin_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    return wrapper

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    user_count = User.query.count()
    category_count = Category.query.count()
    product_count = Product.query.count()
    return render_template('admin/dashboard.html',
                           user_count=user_count,
                           category_count=category_count,
                           product_count=product_count)

@admin_bp.route('/categories', methods=['GET'])
@login_required
@admin_required
def list_categories():
    categories = Category.query.order_by(Category.parent_id, Category.name).all()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    categories = Category.query.filter_by(parent_id=None).all()
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        image = request.files.get('image')


        if image:
            upload_service = LocalFileUpload()
            try:
                image_url = upload_service.upload_file(image, 'categories')
            except Exception as e:
                flash(f'Image upload failed: {e}', 'danger')
                return render_template('admin/add_category.html', categories=categories)
        parent_id = request.form.get('parent_id') or None
        if not name:
            flash('Category name is required.', 'danger')
            return render_template('admin/add_category.html', categories=categories)
        if parent_id == '':
            parent_id = None
        category = Category(name=name, description=description, parent_id=parent_id, image=image_url if image else None)
        db.session.add(category)
        try:
            db.session.commit()
            flash('Category added successfully!', 'success')
            return redirect(url_for('admin.list_categories'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {e}', 'danger')
    return render_template('admin/add_category.html', categories=categories)

@admin_bp.route('/categories/delete/<int:category_id>', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    from flask_wtf.csrf import validate_csrf
    csrf_token = request.form.get('csrf_token')
    try:
        validate_csrf(csrf_token)
    except Exception:
        flash('Invalid CSRF token.', 'danger')
        return redirect(url_for('admin.list_categories'))
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted.', 'success')
    return redirect(url_for('admin.list_categories'))

@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    users = User.query.order_by(User.id).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    from flask_wtf.csrf import validate_csrf
    csrf_token = request.form.get('csrf_token')
    try:
        validate_csrf(csrf_token)
    except Exception:
        flash('Invalid CSRF token.', 'danger')
        return redirect(url_for('admin.list_users'))
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('Cannot delete admin user.', 'danger')
        return redirect(url_for('admin.list_users'))
    db.session.delete(user)
    db.session.commit()
    flash('User deleted.', 'success')
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/users/promote/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def promote_user(user_id):
    from flask_wtf.csrf import validate_csrf
    csrf_token = request.form.get('csrf_token')
    try:
        validate_csrf(csrf_token)
    except Exception:
        flash('Invalid CSRF token.', 'danger')
        return redirect(url_for('admin.list_users'))
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('User is already an admin.', 'info')
    else:
        user.role = 'admin'
        db.session.commit()
        flash('User promoted to admin.', 'success')
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/price-tracking')
@login_required
@admin_required
def price_tracking():
    price_history = PriceHistory.query.order_by(PriceHistory.changed_at.desc()).all()
    return render_template('admin/price_tracking.html', price_history=price_history)

@admin_bp.route('/products')
@login_required
@admin_required
def list_products():
    search_query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', '')
    page = request.args.get('page', 1, type=int)
    per
