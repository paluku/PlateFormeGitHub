from flask import Blueprint, jsonify

agents_bp = Blueprint('agents', __name__, url_prefix='/api/agents')

@agents_bp.route('/', methods=['GET'])
def list_agents():
    """Liste tous les agents disponibles"""
    agents = [
        {'id': 'base', 'name': 'Base Agent', 'level': 1, 'description': 'Agent de base - Réponses simples'},
        {'id': 'echo', 'name': 'Echo Agent', 'level': 2, 'description': 'Écho et analyse des messages'},
        {'id': 'assistant', 'name': 'Assistant Agent', 'level': 3, 'description': 'Assistant conversationnel avec mémoire'},
        {'id': 'specialist', 'name': 'Specialist Agent', 'level': 4, 'description': 'Agent spécialisé avec compétences'},
        {'id': 'collaborative', 'name': 'Collaborative Agent', 'level': 5, 'description': 'Coordination multi-agents'},
         {'id': 'filecreator', 'name': 'FileCreator Agent', 'level': 6, 'description': 'Crée et exporte des fichiers (TXT, CSV, JSON, HTML, MD, PY, XML)'}

   ]
    return jsonify(agents)