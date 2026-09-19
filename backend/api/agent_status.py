from flask import Blueprint, jsonify
import time

agent_status_bp = Blueprint('agent_status', __name__, url_prefix='/api/status')

@agent_status_bp.route('/', methods=['GET'])
def get_status():
    """Statut de tous les agents"""
    return jsonify({
        'status': 'online',
        'timestamp': time.time(),
        'agents': [
            {'id': 'base', 'status': 'ready'},
            {'id': 'echo', 'status': 'ready'},
            {'id': 'assistant', 'status': 'ready'},
            {'id': 'specialist', 'status': 'ready'},
            {'id': 'collaborative', 'status': 'ready'},
            {'id': 'filecreator', 'status': 'ready', 'type': 'tool'},
            {'id': 'email_agent', 'status': 'ready'}
        ]
    })