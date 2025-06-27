from flask import Blueprint, render_template, request, flash
from app.models.product import Product
from app.models.product import Category
from sqlalchemy import or_, desc, asc
from sqlalchemy.exc import SQLAlchemyError
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    try:
        # Get query parameters
        search_query = request.args.get('q', '').strip()
        category_name = request.args.get('category', '')
        sort_by = request.args.get('sort', 'name')
        order = request.args.get('order', 'asc')
        page = request.args.get('page', 1, type=int)
        per_page = 12

        # Build base query
        products_query = Product.query

        # Apply search filter
        if search_query:
            products_query = products_query.filter(
                Product.name.contains(search_query) |
                Product.description.contains(search_query)
            )

        # Apply category filter
        if category_name and category_name.lower() != "all":
            products_query = products_query.join(Category).filter(Category.name.ilike(category_name))

        # Apply sorting
        if sort_by == 'price':
            if order == 'desc':
                products_query = products_query.order_by(desc(Product.price))
            else:
                products_query = products_query.order_by(asc(Product.price))
        elif sort_by == 'created_at':
            products_query = products_query.order_by(desc(Product.created_at))
        else:  # name
            if order == 'desc':
                products_query = products_query.order_by(desc(Product.name))
            else:
                products_query = products_query.order_by(asc(Product.name))

        # Paginate results
        products_pagination = products_query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        categories = Category.query.all()

        content = {
            'categories': categories,
            'products': products_pagination.items,
            'pagination': products_pagination,
            'current_search': search_query,
            'current_category': category_name,
            'current_sort': sort_by,
            'current_order': order,
            'total_products': products_pagination.total
        }
        return render_template('main/index.html', **content)

    except SQLAlchemyError as e:
        flash('An error occurred while loading products. Please try again.', 'error')
        categories = Category.query.all()
        return render_template('main/index.html',
                             categories=categories,
                             products=[],
                             pagination=None,
                             total_products=0,
                             current_search='',
                             current_category='',
                             current_sort='name',
                             current_order='asc')



@main_bp.route('/about')
def about():
    """Render the About page."""
    return render_template('main/contact.html')
