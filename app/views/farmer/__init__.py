from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models.product import Product, Category
from app.models.product import ProductImage
from app.extensions import db
from app.services.upload_service import LocalFileUpload
from app.models.price_and_delivery import PriceHistory
from sqlalchemy import or_
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Length, Optional
import os
from werkzeug.utils import secure_filename
from app.models.kyc import KYC
from datetime import datetime

farmer_bp = Blueprint('farmer', __name__, template_folder='../templates/farmer')


# KYC Form
class KYCForm(FlaskForm):
    document_type = SelectField('Document Type',
                              choices=[
                                  ('national_id', 'National ID'),
                                  ('passport', 'Passport'),
                                  ('drivers_license', "Driver's License"),
                                  ('voters_card', "Voter's Card")
                              ],
                              validators=[DataRequired()])
    document_number = StringField('Document Number',
                                validators=[DataRequired(), Length(min=4, max=50)])
    document_image = FileField('Document Image',
                             validators=[
                                 DataRequired(),
                                 FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
                             ])
    submit = SubmitField('Submit KYC')


class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=500)])
    price = DecimalField('Price (FCFA)', validators=[DataRequired(), NumberRange(min=0)])
    quantity = IntegerField('Quantity Available', validators=[DataRequired(), NumberRange(min=1)])
    unit = SelectField('Unit', choices=[
        ('kg', 'Kilograms'),
        ('g', 'Grams'),
        ('pieces', 'Pieces'),
        ('bunches', 'Bunches'),
        ('bags', 'Bags'),
        ('boxes', 'Boxes'),
        ('liters', 'Liters')
    ], validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    location = StringField('Location/Farm Address', validators=[Optional(), Length(max=200)])
    harvest_date = StringField('Harvest Date', validators=[Optional()], description="Optional: When was this harvested?")
    image = FileField('Product Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Create Product')

class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')



def farmer_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        # kyc has been approve


        if not current_user.is_authenticated or current_user.role not in ['farmer', 'admin']:
            flash('Famers access required.', 'danger')
            return redirect(url_for('main.index'))
        if current_user.role == 'farmer' and not KYC.query.filter_by(user_id=current_user.id, status='verified').first():
            flash('KYC verification required before accessing farmer features.', 'warning')
            return redirect(url_for('farmer.submit_kyc'))
        return func(*args, **kwargs)
    return wrapper

@farmer_bp.route('/products/create', methods=['GET', 'POST'])
@login_required
@farmer_required
def create_product():
    form = ProductForm()
    categories = Category.query.all()
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        try:
            # Create new product
            product = Product(
                name=form.name.data,
                description=form.description.data,
                price=float(form.price.data),
                quantity=form.quantity.data,
                unit=form.unit.data,
                category_id=form.category_id.data,
                farmer_id=current_user.id,
                location=form.location.data,
                harvest_date=form.harvest_date.data
            )

            db.session.add(product)
            db.session.flush()  # Get the product ID

            # Handle image upload
            if form.image.data:
                filename = secure_filename(form.image.data.filename)
                if filename:
                    # Create unique filename
                    import uuid
                    file_ext = filename.rsplit('.', 1)[1].lower()
                    unique_filename = f"{uuid.uuid4().hex}.{file_ext}"

                    # Save file
                    upload_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'app/static/uploads'), unique_filename)
                    form.image.data.save(upload_path)

                    # Create ProductImage record
                    product_image = ProductImage(
                        product_id=product.id,
                        image_url=f"/static/uploads/{unique_filename}",
                        is_primary=True
                    )
                    db.session.add(product_image)

            db.session.commit()
            flash('Product created successfully!', 'success')
            return redirect(url_for('farmer.list_products'))

        except Exception as e:
            db.session.rollback()
            flash('Error creating product. Please try again.', 'error')
            current_app.logger.error(f"Error creating product: {str(e)}")

    return render_template('farmer/create_product.html', form=form, categories=categories)

@farmer_bp.route('/products')
@login_required
@farmer_required
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
    delete_form = DeleteForm()

    return render_template('farmer/list_products.html',
                         products=products_pagination.items,
                         pagination=products_pagination,
                         categories=categories,
                         current_search=search_query,
                         current_category=category_filter,
                         delete_form=delete_form)

@farmer_bp.route('/dashboard')
@farmer_bp.route('/',)
@login_required
@farmer_required
def dashboard():
    # Get comprehensive farmer statistics
    product_count = Product.query.filter_by(farmer_id=current_user.id).count()

    # Get recent products (last 5)
    recent_products = Product.query.filter_by(farmer_id=current_user.id)\
        .order_by(Product.created_at.desc()).limit(5).all()

    # Calculate average price
    products = Product.query.filter_by(farmer_id=current_user.id).all()
    avg_price = sum(p.price for p in products) / len(products) if products else 0

    # Get categories count
    categories_used = len(set(p.category_id for p in products if p.category_id))

    # Get price changes for this farmer's products
    farmer_product_ids = [p.id for p in products]
    price_changes = 0
    if farmer_product_ids:
        price_changes = PriceHistory.query.filter(
            PriceHistory.product_id.in_(farmer_product_ids)
        ).count()

    return render_template('farmer/dashboard.html',
                         product_count=product_count,
                         recent_products=recent_products,
                         avg_price=avg_price,
                         categories_used=categories_used,
                         price_changes=price_changes)

@farmer_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
@farmer_required
def delete_product(product_id):
    form = DeleteForm()
    if form.validate_on_submit():
        product = Product.query.filter_by(id=product_id, farmer_id=current_user.id).first_or_404()
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted.', 'success')
    else:
        flash('Invalid CSRF token.', 'danger')
    return redirect(url_for('farmer.list_products'))

@farmer_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@farmer_required
def edit_product(product_id):
    product = Product.query.filter_by(id=product_id, farmer_id=current_user.id).first_or_404()
    form = ProductForm(obj=product)
    categories = Category.query.all()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    delete_form = DeleteForm()

    if form.validate_on_submit():
        # Price tracking: if price changed, add to PriceHistory
        if product.price != form.price.data:
            price_history = PriceHistory(product_id=product.id, price=float(form.price.data))
            db.session.add(price_history)

        form.populate_obj(product)

        # Handle new image uploads
        if form.image.data:
            upload_service = LocalFileUpload()
            try:
                url = upload_service.upload_file(form.image.data, f'products/{product.id}')
                # Find primary image or create new one
                primary_image = next((img for img in product.images if img.is_primary), None)
                if primary_image:
                    # ToDo: delete old image from storage
                    primary_image.image_url = url
                else:
                    product_image = ProductImage(product_id=product.id, image_url=url, is_primary=True)
                    db.session.add(product_image)
            except Exception as e:
                flash(f'Image upload failed: {e}', 'danger')

        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('farmer.list_products'))

    # Fetch price history for monitoring
    price_history_list = PriceHistory.query.filter_by(product_id=product.id).order_by(PriceHistory.changed_at.desc()).all()
    return render_template('farmer/edit_product.html', form=form, product=product, categories=categories, price_history=price_history_list, delete_form=delete_form)

@farmer_bp.route('/products/delete_image/<int:image_id>', methods=['POST'])
@login_required
@farmer_required
def delete_product_image(image_id):
    form = DeleteForm()
    if form.validate_on_submit():
        image = ProductImage.query.get_or_404(image_id)
        product = Product.query.filter_by(id=image.product_id, farmer_id=current_user.id).first()
        if not product:
            flash('Not authorized.', 'danger')
            return redirect(url_for('farmer.list_products'))
        # ToDo: delete image file from storage
        db.session.delete(image)
        db.session.commit()
        flash('Image deleted.', 'success')
        return redirect(url_for('farmer.edit_product', product_id=product.id))
    else:
        flash('Invalid CSRF token.', 'danger')
        return redirect(request.referrer or url_for('farmer.list_products'))


@farmer_bp.route('/kyc/submit', methods=['GET', 'POST'])
@login_required
def submit_kyc():
    form = KYCForm()

    # Check if user already has KYC record
    existing_kyc = KYC.query.filter_by(user_id=current_user.id).first()
    if existing_kyc and existing_kyc.status in ['pending', 'verified']:
        flash('You have already submitted KYC information.', 'info')
        return redirect(url_for('farmer.view_kyc'))

    if form.validate_on_submit():
        try:
            # Handle document upload
            upload_service = LocalFileUpload()
            document_url = None
            if form.document_image.data:
                filename = secure_filename(form.document_image.data.filename)
                if filename:
                    import uuid
                    file_ext = filename.rsplit('.', 1)[1].lower()
                    unique_filename = f"kyc_{uuid.uuid4().hex}.{file_ext}"
                    document_url = upload_service.upload_file(form.document_image.data, f'kyc/{current_user.id}/{unique_filename}')

            # Create new KYC record
            kyc = KYC(
                user_id=current_user.id,
                document_type=form.document_type.data,
                document_number=form.document_number.data,
                document_image_url=document_url,
                status='pending',
                submitted_at=datetime.now()
            )

            db.session.add(kyc)
            db.session.commit()
            flash('KYC information submitted successfully!', 'success')
            return redirect(url_for('farmer.view_kyc'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting KYC information: {str(e)}', 'error')
            current_app.logger.error(f"Error submitting KYC: {str(e)}")

    return render_template('farmer/submit_kyc.html', form=form)

@farmer_bp.route('/kyc')
@login_required
def view_kyc():
    kyc = KYC.query.filter_by(user_id=current_user.id).first()
    if kyc is None:
        flash('No KYC information found. Please submit your KYC first.', 'warning')
        return redirect(url_for('farmer.submit_kyc'))
    if kyc.status == 'pending':
        flash('Your KYC is still pending verification.', 'info')
    elif kyc.status == 'rejected':
        flash('Your KYC was rejected. Please resubmit with correct information.', 'warning')
        return redirect(url_for('farmer.submit_kyc'))
    elif kyc.status == 'verified':
        flash('Your KYC has been verified successfully!', 'success')
        return redirect(url_for('farmer.dashboard'))
    return render_template('farmer/view_kyc.html', kyc=kyc)
