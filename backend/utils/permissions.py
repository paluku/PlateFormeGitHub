# utils/permissions.py
from functools import wraps
from flask import session, jsonify, redirect, url_for, request
import sqlite3

def get_db():
    """Connexion à la base de données"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# ============================================
# 1. VÉRIFIER QUE L'UTILISATEUR EST CONNECTÉ
# ============================================
def login_required(func):
    """Décorateur : l'utilisateur doit être connecté"""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Pour les routes API
            if request and request.path.startswith('/api/'):
                return jsonify({'error': 'Non authentifié'}), 401
            # Pour les pages HTML
            return redirect('/login')
        return func(*args, **kwargs)
    return decorated_function

# ============================================
# 2. VÉRIFIER LE RÔLE (propriétaire)
# ============================================
def owner_required(func):
    """Décorateur : l'utilisateur doit être propriétaire ou admin"""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],))
        user = c.fetchone()
        conn.close()
        
        if not user or user['role'] not in ['owner', 'admin']:
            if request and request.path.startswith('/api/'):
                return jsonify({'error': 'Accès refusé'}), 403
            return redirect('/dashboard')
        return func(*args, **kwargs)
    return decorated_function

# ============================================
# 3. VÉRIFIER LE RÔLE (agent)
# ============================================
def cleaner_required(func):
    """Décorateur : l'utilisateur doit être agent ou admin"""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],))
        user = c.fetchone()
        conn.close()
        
        if not user or user['role'] not in ['cleaner', 'admin']:
            if request and request.path.startswith('/api/'):
                return jsonify({'error': 'Accès refusé'}), 403
            return redirect('/dashboard')
        return func(*args, **kwargs)
    return decorated_function

# ============================================
# 4. VÉRIFIER LE RÔLE (admin)
# ============================================
def admin_required(func):
    """Décorateur : l'utilisateur doit être admin"""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],))
        user = c.fetchone()
        conn.close()
        
        if not user or user['role'] != 'admin':
            if request and request.path.startswith('/api/'):
                return jsonify({'error': 'Accès refusé'}), 403
            return redirect('/dashboard')
        return func(*args, **kwargs)
    return decorated_function

# ============================================
# 5. VÉRIFIER LA PROPRIÉTÉ D'UN LOGEMENT
# ============================================
def property_owner_required(func):
    """Vérifie que l'utilisateur est le propriétaire du logement"""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Non authentifié'}), 401
        
        property_id = kwargs.get('property_id')
        if not property_id and request.json:
            property_id = request.json.get('property_id')
        
        if not property_id:
            return jsonify({'error': 'ID du logement requis'}), 400
        
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT owner_id FROM properties WHERE id = ?', (property_id,))
        prop = c.fetchone()
        conn.close()
        
        if not prop:
            return jsonify({'error': 'Logement non trouvé'}), 404
        
        if prop['owner_id'] != session['user_id']:
            # Admin peut tout voir
            conn = get_db()
            c = conn.cursor()
            c.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],))
            user = c.fetchone()
            conn.close()
            if not user or user['role'] != 'admin':
                return jsonify({'error': 'Accès refusé'}), 403
        
        return func(*args, **kwargs)
    return decorated_function