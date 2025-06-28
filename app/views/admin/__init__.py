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
from app.models.kyc import KYC

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
    # Get price history with better ordering for charts
    price_history = PriceHistory.query.join(Product).order_by(
        PriceHistory.changed_at.desc()
    ).limit(100).all()  # Limit to last 100 changes for performance

    # Calculate statistics
    stats = {
        'total_changes': PriceHistory.query.count(),
        'unique_products': len(set(p.product_id for p in price_history if p.product_id)),
        'average_price': 0,
        'highest_price': 0,
        'lowest_price': 0
    }

    if price_history:
        prices = [p.price for p in price_history]
        stats['average_price'] = sum(prices) / len(prices)
        stats['highest_price'] = max(prices)
        stats['lowest_price'] = min(prices)

    # Get recent price trends (last 30 days) for better chart visualization
    recent_cutoff = datetime.now() - timedelta(days=30)
    recent_price_history = PriceHistory.query.filter(
        PriceHistory.changed_at >= recent_cutoff
    ).join(Product).order_by(PriceHistory.changed_at.asc()).all()

    return render_template('admin/price_tracking.html',
                         price_history=recent_price_history if recent_price_history else price_history,
                         stats=stats)

@admin_bp.route('/products')
@login_required
@admin_required
def list_products():
    search_query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    products_query = Product.query
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
    return render_template('admin/products.html',
                         products=products_pagination.items,
                         pagination=products_pagination,
                         categories=categories,
                         current_search=search_query,
                         current_category=category_filter,
                         total_products=products_pagination.total)

@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    from flask_wtf.csrf import validate_csrf

    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully.', 'success')
    return redirect(url_for('admin.list_products'))

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    # Enhanced dashboard with analytics
    total_users = User.query.count()
    total_farmers = User.query.filter_by(role='farmer').count()
    total_products = Product.query.count()
    total_categories = Category.query.count()

    # Recent activity
    recent_products = Product.query.order_by(Product.created_at.desc()).limit(10).all()
    recent_users = User.query.order_by(User.id.desc()).limit(10).all()

    # Price changes this week
    week_ago = datetime.now() - timedelta(days=7)
    recent_price_changes = PriceHistory.query.filter(
        PriceHistory.changed_at >= week_ago
    ).count()

    # Products by category with proper handling
    try:
        category_stats = db.session.query(
            Category.name,
            func.count(Product.id).label('product_count')
        ).outerjoin(Product).group_by(Category.name).all()
    except Exception:
        category_stats = []

    return render_template('admin/analytics.html',
                         total_users=total_users,
                         total_farmers=total_farmers,
                         total_products=total_products,
                         total_categories=total_categories,
                         recent_products=recent_products,
                         recent_users=recent_users,
                         recent_price_changes=recent_price_changes,
                         category_stats=category_stats)

@admin_bp.route('/kyc')
@login_required
@admin_required
def kyc_list():
    kycs = KYC.query.order_by(KYC.submitted_at.desc()).all()
    return render_template('admin/kyc_list.html', kycs=kycs)

@admin_bp.route('/kyc/<int:kyc_id>')
@login_required
@admin_required
def kyc_detail(kyc_id):
    kyc = KYC.query.get_or_404(kyc_id)
    return render_template('admin/kyc_detail.html', kyc=kyc)

@admin_bp.route('/kyc/<int:kyc_id>/approve', methods=['POST'])
@login_required
@admin_required
def kyc_approve(kyc_id):
    kyc = KYC.query.get_or_404(kyc_id)
    kyc.status = 'verified'
    db.session.commit()
    flash('KYC approved.', 'success')
    return redirect(url_for('admin.kyc_detail', kyc_id=kyc_id))

@admin_bp.route('/kyc/<int:kyc_id>/reject', methods=['POST'])
@login_required
@admin_required
def kyc_reject(kyc_id):
    kyc = KYC.query.get_or_404(kyc_id)
    kyc.status = 'rejected'
    db.session.commit()
    flash('KYC rejected.', 'warning')
    return redirect(url_for('admin.kyc_detail', kyc_id=kyc_id))
