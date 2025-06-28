from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.extensions import socketio, db
from app.models.message import Message, Conversation
from app.models.user import User
from flask_socketio import emit, join_room, leave_room
from datetime import datetime

# Create a blueprint for the message module
message_bp = Blueprint('message', __name__)

@message_bp.route('/')
@login_required
def index():
    """
    Render the index page for the message module.
    """
    users = User.query.filter(User.id != current_user.id).all()

    marketplace_product = None
    product_id = request.args.get('product_id')
    if product_id:
        from app.models.product import Product
        marketplace_product = Product.query.get(product_id)

        farmer = marketplace_product.farmer if marketplace_product else None

        # start a conversation if the product is specified
        message = "Am intrested in this product"
        receiver_id = marketplace_product.farmer.id if farmer else None
        sender_id = current_user.id

        # check if the users have exisiting conversation
        conversation_query = Conversation.query.filter(
            ((Conversation.user1_id == current_user.id) & (Conversation.user2_id == receiver_id)) |
            ((Conversation.user1_id == receiver_id) & (Conversation.user2_id == current_user.id))
        )
        if marketplace_product:
            conversation_query = conversation_query.filter(Conversation.product_id == marketplace_product.id)

        conversation_id = conversation_query.first()

        if receiver_id and not conversation_id:
            conversation = Conversation(
                user1_id=min(current_user.id, receiver_id),
                user2_id=max(current_user.id, receiver_id),
                product_id=marketplace_product.id if marketplace_product else None
            )
            db.session.add(conversation)
            db.session.flush()

            # Create message
            message = Message(
                sender_id=current_user.id,
                receiver_id=receiver_id,
                content=message,
                conversation_id=conversation.id
            )
            db.session.add(message)
            conversation.last_message_id = message.id
            conversation.updated_at = datetime.now()
            db.session.commit()

    conversations = Conversation.query.filter(
    (Conversation.user1_id == current_user.id) |
    (Conversation.user2_id == current_user.id)
    ).order_by(Conversation.updated_at.desc()).all()


    return render_template('messages/index.html',
                         title='Messages',
                         conversations=conversations,
                         users=users,
                         marketplace_product=marketplace_product)

@message_bp.route('/conversation/<int:user_id>')
@login_required
def conversation(user_id):
    """
    Get or create a conversation with a specific user.
    Always returns JSON for AJAX requests to support frontend.
    """
    try:
        # Prevent self-messaging
        if user_id == current_user.id:
            return jsonify({'success': False, 'error': 'Cannot message yourself'}), 400

        # Validate other user
        other_user = User.query.get(user_id)
        if not other_user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        # Get product ID if provided
        product_id = request.args.get('product_id', type=int)
        product = None
        if product_id:
            from app.models.product import Product
            product = Product.query.get(product_id)
            if not product:
                return jsonify({'success': False, 'error': 'Product not found'}), 404

        # Find existing conversation
        conversation = None
        if product_id:
            conversation = Conversation.query.filter(
                ((Conversation.user1_id == current_user.id) & (Conversation.user2_id == user_id)) |
                ((Conversation.user1_id == user_id) & (Conversation.user2_id == current_user.id)),
                Conversation.product_id == product_id
            ).first()
        else:
            conversation = Conversation.query.filter(
                ((Conversation.user1_id == current_user.id) & (Conversation.user2_id == user_id)) |
                ((Conversation.user1_id == user_id) & (Conversation.user2_id == current_user.id))
            ).first()

        # Create new conversation if none exists
        if not conversation:
            conversation = Conversation(
                user1_id=min(current_user.id, user_id),
                user2_id=max(current_user.id, user_id),
                product_id=product_id if product_id else None
            )
            db.session.add(conversation)
            db.session.commit()

        # Get messages
        messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.created_at.asc()).all()

        # Mark messages as read
        Message.query.filter(
            Message.conversation_id == conversation.id,
            Message.receiver_id == current_user.id,
            Message.is_read == False
        ).update({'is_read': True})
        db.session.commit()

        # Prepare response
        response = {
            'success': True,
            'conversation_id': conversation.id,
            'messages': [{
                'id': msg.id,
                'content': msg.content,
                'sender_id': msg.sender_id,
                'sender_username': User.query.get(msg.sender_id).username,
                'created_at': msg.created_at.isoformat(),
                'is_own': msg.sender_id == current_user.id
            } for msg in messages],
            'product_id': product.id if product else None,
            'product_name': product.name if product else None,
            'product_price': float(product.price) if product else None  # Ensure price is included
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'success': False, 'error': f'Internal server error: {str(e)}'}), 500

@message_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    """
    Send a new message.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data received'}), 400

        receiver_id = data.get('receiver_id')
        content = data.get('content')
        conversation_id = data.get('conversation_id')

        if not receiver_id or not content:
            return jsonify({'success': False, 'error': 'Missing required fields: receiver_id and content'}), 400

        receiver = User.query.get(receiver_id)
        if not receiver:
            return jsonify({'success': False, 'error': 'Recipient not found'}), 404

        # Find or create conversation
        conversation = None
        if conversation_id:
            conversation = Conversation.query.get(conversation_id)
            if conversation and (conversation.user1_id != current_user.id and conversation.user2_id != current_user.id):
                return jsonify({'success': False, 'error': 'Unauthorized access to conversation'}), 403

        if not conversation:
            conversation = Conversation.query.filter(
                ((Conversation.user1_id == current_user.id) & (Conversation.user2_id == receiver_id)) |
                ((Conversation.user1_id == receiver_id) & (Conversation.user2_id == current_user.id))
            ).first()
            if not conversation:
                conversation = Conversation(
                    user1_id=min(current_user.id, receiver_id),
                    user2_id=max(current_user.id, receiver_id)
                )
                db.session.add(conversation)
                db.session.flush()

        # Create message
        message = Message(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            content=content.strip(),
            conversation_id=conversation.id
        )
        db.session.add(message)
        conversation.last_message_id = message.id
        conversation.updated_at = datetime.now()
        db.session.commit()

        # Emit Socket.IO event
        socketio.emit('new_message', {
            'message_id': message.id,
            'content': message.content,
            'sender_id': current_user.id,
            'sender_username': current_user.username,
            'receiver_id': receiver_id,
            'created_at': message.created_at.isoformat(),
            'conversation_id': conversation.id
        }, room=f'user_{receiver_id}')

        return jsonify({
            'success': True,
            'conversation_id': conversation.id,
            'message': {
                'id': message.id,
                'content': message.content,
                'sender_id': current_user.id,
                'sender_username': current_user.username,
                'created_at': message.created_at.isoformat()
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Internal server error: {str(e)}'}), 500

@message_bp.route('/user/<int:user_id>')
@login_required
def get_user(user_id):
    """
    Get user details by ID.
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        if user.id == current_user.id:
            return jsonify({'success': False, 'error': 'Cannot fetch own user details'}), 400
        return jsonify({
            'success': True,
            'user_id': user.id,
            'username': user.username,
            'role': user.role
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Internal server error: {str(e)}'}), 500

@message_bp.route('/check_session')
@login_required
def check_session():
    """
    Check if the user is authenticated.
    """
    return jsonify({
        'success': True,
        'user_id': current_user.id,
        'username': current_user.username
    })

# Socket.IO events
@socketio.on('connect')
def on_connect():
    if current_user.is_authenticated:
        join_room(f'user_{current_user.id}')
        emit('status', {'msg': f'{current_user.username} has connected'})

@socketio.on('disconnect')
def on_disconnect():
    if current_user.is_authenticated:
        leave_room(f'user_{current_user.id}')
        emit('status', {'msg': f'{current_user.username} has disconnected'})

@socketio.on('join_conversation')
def on_join_conversation(data):
    conversation_id = data.get('conversation_id')
    if conversation_id and current_user.is_authenticated:
        join_room(f'conversation_{conversation_id}')

@socketio.on('leave_conversation')
def on_leave_conversation(data):
    conversation_id = data.get('conversation_id')
    if conversation_id and current_user.is_authenticated:
        leave_room(f'conversation_{conversation_id}')
