from datetime import datetime
from typing import List, TYPE_CHECKING
from app.extensions import db

if TYPE_CHECKING:
    from app.models.user import User

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # 'text' or 'location'
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    location_name = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages', lazy=True)
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages', lazy=True)
    conversation = db.relationship('Conversation', foreign_keys=[conversation_id], backref='messages', lazy=True)

    def __repr__(self):
        return f'<Message from {self.sender_id} to {self.receiver_id}>'

class Conversation(db.Model):
    __tablename__ = 'conversations'

    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    last_message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    user1 = db.relationship('User', foreign_keys=[user1_id], lazy=True)
    user2 = db.relationship('User', foreign_keys=[user2_id], lazy=True)
    product = db.relationship('Product', backref='conversations', lazy=True)
    last_message = db.relationship('Message', foreign_keys=[last_message_id], lazy=True)

    def __repr__(self):
        return f'<Conversation between {self.user1_id} and {self.user2_id}>'

    def get_other_user(self, current_user_id: int):
        """Get the other user in the conversation"""
        return self.user2 if self.user1_id == current_user_id else self.user1

    def get_messages(self) -> List['Message']:
        """Get all messages in this conversation"""
        return Message.query.filter(
            Message.conversation_id == self.id
        ).order_by(Message.created_at.asc()).all()
