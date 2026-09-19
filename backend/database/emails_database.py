import sqlite3
import os
import uuid
from datetime import datetime

DB_PATH = 'database.db'

def get_db_connection():
    """Obtenir une connexion à la base de données"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Créer toutes les tables nécessaires"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # ============================================
    # TABLE CHAT CONVERSATIONS
    # ============================================
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_conversations (
            id TEXT PRIMARY KEY,
            title TEXT,
            agent_id TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    
    # ============================================
    # TABLE CHAT MESSAGES
    # ============================================
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT,
            content TEXT,
            sender TEXT,
            timestamp TEXT,
            is_user INTEGER,
            FOREIGN KEY (conversation_id) REFERENCES chat_conversations(id)
        )
    ''')
    
    # ============================================
    # TABLE EMAILS (inchangée)
    # ============================================
    c.execute('''
        CREATE TABLE IF NOT EXISTS emails (
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
    
    # ============================================
    # DONNÉES DE TEST POUR EMAILS (si vide)
    # ============================================
    c.execute('SELECT COUNT(*) FROM emails')
    count = c.fetchone()[0]
    
    if count == 0:
        test_emails = [
            {
                'id': str(uuid.uuid4()),
                'sender': 'client1@email.com',
                'subject': 'Problème de connexion',
                'body': 'Bonjour, je n\'arrive pas à me connecter à mon compte depuis 3 jours. Pouvez-vous m\'aider ?',
                'received_at': datetime.now().isoformat(),
                'category': 'Technique',
                'urgency': 'Haute',
                'action': 'Réponse IA',
                'is_processed': 1,
                'response': 'Bonjour, nous avons bien reçu votre demande. Pouvez-vous vérifier vos spams ? Si le problème persiste, nous allons réinitialiser votre compte manuellement.'
            },
            {
                'id': str(uuid.uuid4()),
                'sender': 'client2@email.com',
                'subject': 'Question sur ma facture',
                'body': 'Bonjour, je souhaiterais connaître le détail de ma facture du mois dernier.',
                'received_at': datetime.now().isoformat(),
                'category': 'Question',
                'urgency': 'Normale',
                'action': 'Réponse IA',
                'is_processed': 1,
                'response': 'Bonjour, nous vous remercions pour votre message. Vous trouverez ci-joint le détail de votre facture.'
            },
            {
                'id': str(uuid.uuid4()),
                'sender': 'client3@email.com',
                'subject': 'Réclamation service client',
                'body': 'Je suis très mécontent du service que j\'ai reçu. Je demande une explication.',
                'received_at': datetime.now().isoformat(),
                'category': 'Réclamation',
                'urgency': 'Haute',
                'action': 'Humain',
                'is_processed': 1,
                'response': None
            },
            {
                'id': str(uuid.uuid4()),
                'sender': 'client4@email.com',
                'subject': 'Demande de devis',
                'body': 'Bonjour, je souhaiterais obtenir un devis pour vos services.',
                'received_at': datetime.now().isoformat(),
                'category': 'Demande',
                'urgency': 'Basse',
                'action': 'En attente',
                'is_processed': 0,
                'response': None
            }
        ]
        
        for email in test_emails:
            c.execute('''
                INSERT INTO emails (id, sender, subject, body, received_at, category, urgency, action, is_processed, response)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                email['id'],
                email['sender'],
                email['subject'],
                email['body'],
                email['received_at'],
                email['category'],
                email['urgency'],
                email['action'],
                email['is_processed'],
                email['response']
            ))
    
    conn.commit()
    conn.close()
    print("✅ Base de données initialisée avec succès")