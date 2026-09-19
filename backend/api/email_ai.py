from flask import Blueprint, request, jsonify
import sqlite3
from agents.email_agent import EmailAgent

# ============================================
# 1. CRÉATION DU BLUEPRINT (EN PREMIER)
# ============================================
email_ai_bp = Blueprint('email_ai', __name__, url_prefix='/api/email_ai')

# 2. INITIALISATION DE L'AGENT
email_agent = EmailAgent()

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# 3. ROUTES (APRÈS LA CRÉATION DU BLUEPRINT)
# ============================================

@email_ai_bp.route('/process', methods=['POST'])
def process_email():
    try:
        data = request.json
        print("📥 Requête reçue sur /process")
        print("📦 Données:", data)
        
        email_id = data.get('email_id')
        content = data.get('content', '')
        subject = data.get('subject', '')
        from_email = data.get('from', '')
        
        # Appel à l'agent (attention, il peut planter)
        result = email_agent.analyze_email(content, subject, from_email)
        print("🔍 Résultat analyse:", result)
        
        # Mise à jour DB
        conn = get_db()
        c = conn.cursor()
        c.execute('''
            UPDATE emails 
            SET category = ?, urgency = ?, action = ?, is_processed = 1
            WHERE id = ?
        ''', (result['category'], result['urgency'], result['action'], email_id))
        conn.commit()
        conn.close()
        
        return jsonify(result)
    except Exception as e:
        print("❌ Erreur dans /process :")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@email_ai_bp.route('/generate-response', methods=['POST'])
def generate_response():
    try:
        data = request.json
        email_id = data.get('email_id')
        content = data.get('content', '')
        category = data.get('category', '')
        
        response_text = email_agent.generate_response(content, category)
        
        conn = get_db()
        c = conn.cursor()
        c.execute('''
            UPDATE emails 
            SET response = ?
            WHERE id = ?
        ''', (response_text, email_id))
        conn.commit()
        conn.close()
        
        return jsonify({'response': response_text})
    except Exception as e:
        print("❌ Erreur dans /generate-response :")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500