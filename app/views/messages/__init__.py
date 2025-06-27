from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.extensions import socketio, db
from app.models.message import Message, Conversation
from app.models.user import User
from flask_socketio import emit, join_room, leave_room
from datetime import datetime
from app.extensions import csrf


# Create a blueprint for the message module
message_bp = Blueprint('message', __name__)


@message_bp.route('/')
@login_required
def index():
    """
    Render the index page for the message module.
    """
    # Get all conversations for the current user
    conversations = Conversation.query.filter(
        (Conversation.user1_id == current_user.id) |
        (Conversation.user2_id == current_user.id)
    ).order_by(Conversation.updated_at.desc()).all()

    # Get all users (potential message recipients)
    users = User.query.filter(User.id != current_user.id).all()

    # Get marketplace product for context (optional - can be from conversation context)
    marketplace_product = None
    product_id = request.args.get('product_id')
    if product_id:
        from app.models.product import Product
        marketplace_product = Product.query.get(product_id)

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
    """
    other_user = User.query.get_or_404(user_id)
    product_id = request.args.get('product_id')

    # Find existing conversation for this product
    conversation = None
    if product_id:
        conversation = Conversation.query.filter(
            ((Conversation.user1_id == current_user.id) & (Conversation.user2_id == user_id)) |
            ((Conversation.user1_id == user_id) & (Conversation.user2_id == current_user.id)),
            Conversation.product_id == product_id
        ).first()
    else:
        # Find any conversation with this user
        conversation = Conversation.query.filter(
            ((Conversation.user1_id == current_user.id) & (Conversation.user2_id == user_id)) |
            ((Conversation.user1_id == user_id) & (Conversation.user2_id == current_user.id))
        ).first()

    # Create new conversation if none exists
    if not conversation:
        # For product-specific conversations, always create one
        if product_id:
            from app.models.product import Product
            product = Product.query.get(product_id)
            if product:
                conversation = Conversation(
                    user1_id=min(current_user.id, user_id),
                    user2_id=max(current_user.id, user_id),
                    product_id=product_id
                )
                db.session.add(conversation)
                db.session.commit()
        else:
            # For general conversations (not product-specific)
            conversation = Conversation(
                user1_id=min(current_user.id, user_id),
                user2_id=max(current_user.id, user_id)
            )
            db.session.add(conversation)
            db.session.commit()

    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404

    # Get messages for this conversation
    messages = conversation.get_messages()

    # Mark messages as read
    Message.query.filter(
        Message.conversation_id == conversation.id,
        Message.receiver_id == current_user.id,
        Message.is_read == False
    ).update({'is_read': True})
    db.session.commit()

    return jsonify({
        'conversation_id': conversation.id,
        'product_id': conversation.product_id,
        'product_name': conversation.product.name if conversation.product else None,
        'other_user': {
            'id': other_user.id,
            'username': other_user.username
        },
        'messages': [{
            'id': msg.id,
            'content': msg.content,
            'sender_id': msg.sender_id,
            'sender_username': msg.sender.username,
            'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M'),
            'is_own': msg.sender_id == current_user.id
        } for msg in messages]
    })


@message_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    """
    Send a new message.
    """
    try:
        data = request.get_json()
        if not data:
            print("ERROR: No JSON data received or failed to parse.")
            return jsonify({'error': 'No JSON data received or data is malformed'}), 400

        print(f"DEBUG: Received data: {data}")

        receiver_id = data.get('receiver_id')
        content = data.get('content')
        conversation_id = data.get('conversation_id')

        print(f"DEBUG: receiver_id={receiver_id}, content='{content}', conversation_id={conversation_id}")

        if not receiver_id or not content:
            print(f"ERROR: Missing fields. receiver_id: {receiver_id}, content: {content}")
            return jsonify({'error': 'Missing required fields: receiver_id and content are required.'}), 400

    except Exception as e:
        print(f"ERROR: Exception in /messages/send: {e}")
        return jsonify({'error': 'An internal error occurred.'}), 500

    receiver = User.query.get(receiver_id)
    if not receiver:
        return jsonify({'error': 'Recipient not found'}), 404

    # Find the conversation
    conversation = None
    if conversation_id:
        conversation = Conversation.query.get(conversation_id)
        # Verify user is part of this conversation
        if conversation and conversation.user1_id != current_user.id and conversation.user2_id != current_user.id:
            return jsonify({'error': 'Unauthorized access to conversation'}), 403

    # If no conversation found by ID, try to find by users
    if not conversation:
        conversation = Conversation.query.filter(
            ((Conversation.user1_id == current_user.id) & (Conversation.user2_id == receiver_id)) |
            ((Conversation.user1_id == receiver_id) & (Conversation.user2_id == current_user.id))
        ).first()

    # Create conversation if it doesn't exist
    if not conversation:
        conversation = Conversation(
            user1_id=min(current_user.id, receiver_id),
            user2_id=max(current_user.id, receiver_id)
        )
        db.session.add(conversation)
        db.session.flush()  # Get the conversation ID

    # Create the message
    message = Message(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        content=content.strip(),
        conversation_id=conversation.id
    )
    db.session.add(message)
    db.session.flush()  # Get the message ID

    # Update conversation
    conversation.last_message_id = message.id
    conversation.updated_at = datetime.now()

    db.session.commit()

    # Emit the message via Socket.IO
    socketio.emit('new_message', {
        'message_id': message.id,
        'content': message.content,
        'sender_id': current_user.id,
        'sender_username': current_user.username,
        'receiver_id': receiver_id,
        'created_at': message.created_at.strftime('%Y-%m-%d %H:%M'),
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
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M')
        }
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
