from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(80), unique=True, nullable=False)
    email: str = db.Column(db.String(120), unique=True, nullable=False)
    phone: str | None = db.Column(db.String(20), nullable=True)
    whatsapp: str | None = db.Column(db.String(20), nullable=True)
    password_hash: str = db.Column(db.String(128), nullable=False)
    role: str = db.Column(db.String(20), nullable=False, default='user')  # 'farmer' or 'user'
    created_at: datetime = db.Column(db.DateTime, default=datetime.now)
    updated_at: datetime = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    products = db.relationship('Product', backref='farmer', lazy=True)
    location = db.relationship('Location', backref='user', uselist=False, lazy=True)
    contact = db.relationship('Contact', backref='user', uselist=False, lazy=True)
    kyc = db.relationship('KYC', backref='user', uselist=False, lazy=True)

    def __init__(self, username: str, email: str, password: str, phone: str | None = None, whatsapp: str | None = None, role: str = 'user'):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.phone = phone
        self.whatsapp = whatsapp
        self.role = role

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
