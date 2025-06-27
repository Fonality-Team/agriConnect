from datetime import datetime
from app.extensions import db

class PriceHistory(db.Model):
    __tablename__ = 'price_history'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.now)

    # Relationship to product
    product = db.relationship('Product', backref='price_history', lazy=True)

    def __repr__(self):
        return f'<PriceHistory Product {self.product_id} Price {self.price} at {self.changed_at}>'

class Delivery(db.Model):
    __tablename__ = 'deliveries'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    delivery_address = db.Column(db.String(255), nullable=False)
    delivery_status = db.Column(db.String(50), nullable=False, default='pending')  # e.g., 'pending', 'shipped', 'delivered'
    order_date = db.Column(db.DateTime, default=datetime.now)
    delivery_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    product = db.relationship('Product', backref='deliveries', lazy=True)
    customer = db.relationship('User', foreign_keys=[customer_id], backref='purchases', lazy=True)
    farmer = db.relationship('User', foreign_keys=[farmer_id], backref='deliveries', lazy=True)

    def __repr__(self):
        return f'<Delivery Product {self.product_id} to Customer {self.customer_id}>'
