from flask import Blueprint, jsonify, request
from database.database import get_conversation, create_conversation

conversation_bp = Blueprint('conversations', __name__, url_prefix='/api/conversations')

@conversation_bp.route('/', methods=['GET'])
def get_conversations():
    """Récupère toutes les conversations"""
    from database.database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM conversations ORDER BY created_at DESC")
    conversations = cursor.fetchall()
    conn.close()
    return jsonify([dict(conv) for conv in conversations])

@conversation_bp.route('/', methods=['POST'])
def new_conversation():
    """Crée une nouvelle conversation"""
    data = request.json or {}
    title = data.get('title', 'Nouvelle conversation')
    conv_id = create_conversation(title)
    return jsonify({'id': conv_id, 'title': title})

@conversation_bp.route('/<int:conv_id>', methods=['GET'])
def get_conversation_by_id(conv_id):
    """Récupère une conversation spécifique"""
    conv, messages = get_conversation(conv_id)
    if not conv:
        return jsonify({'error': 'Conversation non trouvée'}), 404
    return jsonify({'conversation': conv, 'messages': messages})