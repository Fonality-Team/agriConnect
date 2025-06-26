from datetime import datetime
from app.extensions import db

class KYC(db.Model):
    __tablename__ = 'kyc'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    document_type = db.Column(db.String(50), nullable=False)  # e.g., ID card, passport
    document_number = db.Column(db.String(50), nullable=False)
    document_image_url = db.Column(db.String(255), nullable=True)  # Path or URL to uploaded document
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, verified, rejected
    submitted_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<KYC for user_id {self.user_id}>'
