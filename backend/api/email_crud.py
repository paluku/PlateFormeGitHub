from flask import Blueprint, request, jsonify
import sqlite3
import uuid
from datetime import datetime

email_crud_bp = Blueprint('email_crud', __name__, url_prefix='/api/email_crud')

def get_db():
    conn = sqlite3.connect('database.db')
    # Ne pas définir row_factory pour éviter les problèmes
    return conn

# ============================================
# Récupérer tous les emails
# ============================================
@email_crud_bp.route('/', methods=['GET'])
def get_emails():
    try:
        conn = get_db()
        c = conn.cursor()
        # Vérifier si la table existe
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='emails'")
        if not c.fetchone():
            # Créer la table automatiquement
            c.execute('''
                CREATE TABLE emails (
                    id TEXT PRIMARY KEY,
                    sender TEXT,
                    subject TEXT,
                    body TEXT,
                    received_at TEXT,
                    category TEXT,
                    urgency TEXT,
                    action TEXT,
                    is_processed INTEGER DEFAULT 0,
                    response TEXT
                )
            ''')
            conn.commit()
            conn.close()
            return jsonify([])
        
        c.execute('''
            SELECT id, sender, subject, body, received_at, category, urgency, action, is_processed, response
            FROM emails
            ORDER BY received_at DESC
        ''')
        rows = c.fetchall()
        conn.close()
        
        emails = []
        for row in rows:
            emails.append({
                'id': row[0],
                'from': row[1],
                'subject': row[2],
                'body': row[3],
                'received_at': row[4],
                'category': row[5] if row[5] else 'Non classé',
                'urgency': row[6] if row[6] else 'Normale',
                'action': row[7] if row[7] else 'En attente',
                'is_processed': bool(row[8]),
                'response': row[9]
            })
        return jsonify(emails)
    except Exception as e:
        # Afficher l'erreur dans les logs Flask
        print("❌ Erreur dans /api/emails/ :")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500