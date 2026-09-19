from database.database import get_connection

def save_message(role, content, conversation_id=1):
    """Sauvegarde un message dans la base de données"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Vérifier si la conversation existe
        cursor.execute("SELECT id FROM conversations WHERE id = ?", (conversation_id,))
        if not cursor.fetchone():
            # Créer une conversation par défaut
            cursor.execute(
                "INSERT INTO conversations (title) VALUES (?)",
                ("Conversation par défaut",)
            )
            conversation_id = cursor.lastrowid
        
        cursor.execute(
            """
            INSERT INTO messages (conversation_id, role, content)
            VALUES (?, ?, ?)
            """,
            (conversation_id, role, content)
        )
        
        conn.commit()
        conn.close()
        return conversation_id
    except Exception as e:
        print(f"❌ Erreur save_message: {str(e)}")
        raise

def get_history(conversation_id=1, limit=50):
    """Récupère l'historique des messages"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (conversation_id, limit)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in reversed(rows):
            messages.append({
                "role": row[0],
                "content": row[1]
            })
        
        return messages
    except Exception as e:
        print(f"❌ Erreur get_history: {str(e)}")
        return []

def get_full_history(conversation_id=1, limit=50):
    """Récupère l'historique complet avec plus d'informations"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT role, content, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (conversation_id, limit)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in reversed(rows):
            messages.append({
                "role": row[0],
                "content": row[1],
                "timestamp": row[2]
            })
        
        return messages
    except Exception as e:
        print(f"❌ Erreur get_full_history: {str(e)}")
        return []

def clear_history(conversation_id=1):
    """Efface l'historique d'une conversation"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM messages WHERE conversation_id = ?",
            (conversation_id,)
        )
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Erreur clear_history: {str(e)}")