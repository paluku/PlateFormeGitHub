import sqlite3
from pathlib import Path

# Dossier de la base de données
DB_FOLDER = Path(__file__).parent.parent
DB_PATH = DB_FOLDER / "conversations.db"

def get_connection():
    """Retourne une connexion à la base de données"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Crée les tables si elles n'existent pas"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table conversations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Table messages
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
    )
    """)
    
    conn.commit()
    conn.close()

def get_conversation(conv_id):
    """Récupère une conversation avec ses messages"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM conversations WHERE id = ?", (conv_id,))
    conv = cursor.fetchone()
    
    if conv:
        cursor.execute("""
            SELECT role, content, created_at 
            FROM messages 
            WHERE conversation_id = ? 
            ORDER BY id
        """, (conv_id,))
        messages = cursor.fetchall()
        conn.close()
        return dict(conv), [dict(m) for m in messages]
    
    conn.close()
    return None, None

def create_conversation(title="Nouvelle conversation"):
    """Crée une nouvelle conversation"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO conversations (title) VALUES (?)",
        (title,)
    )
    conv_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return conv_id

def get_all_conversations():
    """Récupère toutes les conversations"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM conversations ORDER BY created_at DESC")
    conversations = cursor.fetchall()
    conn.close()
    return [dict(conv) for conv in conversations]