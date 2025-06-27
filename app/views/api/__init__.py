from flask import Blueprint, jsonify
from app.models.user import User
from app.models.product import Product

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/farmer/<int:product_id>/contact')
def get_farmer_contact(product_id):
    """Get farmer contact information for a specific product"""
    try:
        product = Product.query.get(product_id)
        if not product or not product.farmer:
            return jsonify({
                'error': 'Product or farmer not found',
                'username': None,
                'phone': None,
                'whatsapp': None
            }), 404

        farmer = product.farmer
        return jsonify({
            'farmer_id': farmer.id,
            'username': farmer.username,
            'phone': farmer.phone,
            'whatsapp': farmer.whatsapp
        })
    except Exception as e:
        print(f"Error fetching farmer contact: {e}")
        return jsonify({
            'error': 'Failed to fetch contact information',
            'farmer_id': None,
            'username': None,
            'phone': None,
            'whatsapp': None
        }), 500

# TODO: Future chat system endpoints will be added here
# @api_bp.route('/chat/start', methods=['POST'])
# def start_chat():
#     """Start a new chat conversation between buyer and seller"""
#     pass
#
# @api_bp.route('/chat/messages/<int:chat_id>')
# def get_chat_messages(chat_id):
#     """Get messages for a specific chat conversation"""
#     pass
#
# @api_bp.route('/chat/send', methods=['POST'])
# def send_message():
#     """Send a message in a chat conversation"""
#     pass
