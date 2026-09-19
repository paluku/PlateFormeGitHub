# api/autonomous.py

from flask import Blueprint, request, jsonify
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.error_handler import logger, log_errors
from agents.autonomous_agent import AutonomousAgent

autonomous_bp = Blueprint('autonomous', __name__, url_prefix='/api/autonomous')

# Initialiser l'agent
autonomous_agent = AutonomousAgent()


# ============================================
# GÉNÉRER UN PLAN (sans exécuter)
# ============================================
@autonomous_bp.route('/plan', methods=['POST'])
@log_errors
def generate_plan():
    """Génère un plan à partir d'un objectif"""
    try:
        data = request.json
        objective = data.get('objective')
        
        if not objective:
            return jsonify({'error': 'objectif requis'}), 400
        
        logger.info(f"🧠 Plan pour: {objective}")
        result = autonomous_agent.generate_plan(objective)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================
# EXÉCUTER UN OBJECTIF (plan + exécution)
# ============================================
@autonomous_bp.route('/execute', methods=['POST'])
@log_errors
def execute_objective():
    """Génère un plan ET l'exécute"""
    try:
        data = request.json
        objective = data.get('objective')
        
        if not objective:
            return jsonify({'error': 'objectif requis'}), 400
        
        logger.info(f"🚀 Exécution: {objective}")
        result = autonomous_agent.run_objective(objective)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return jsonify({'error': str(e)}), 500