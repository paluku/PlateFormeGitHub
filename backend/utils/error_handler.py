# utils/error_handler.py

import sys
import traceback
import logging
from datetime import datetime
from functools import wraps
from flask import jsonify, request
import os




# ============================================
# CONFIGURATION DU LOGGER
# ============================================
logger = logging.getLogger('email_agent')
logger.setLevel(logging.DEBUG)

if logger.hasHandlers():
    logger.handlers.clear()

formatter = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Fichier
import os
os.makedirs('logs', exist_ok=True)
file_handler = logging.FileHandler('logs/email_agent.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# ============================================
# DÉCORATEUR POUR LES ERREURS
# ============================================
def log_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logger.info(f"📥 REQUÊTE: {request.method} {request.path}")
            if request.is_json:
                logger.debug(f"📦 JSON: {request.get_json(silent=True)}")
            
            result = func(*args, **kwargs)
            logger.info(f"✅ SUCCÈS")
            return result
            
        except Exception as e:
            error_msg = f"""
╔══════════════════════════════════════════════════════════════════
║ ❌ ERREUR DÉTECTÉE
╠══════════════════════════════════════════════════════════════════
║ 📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
║ 🔍 Type: {type(e).__name__}
║ 📝 Message: {str(e)}
╠══════════════════════════════════════════════════════════════════
"""
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            return jsonify({
                'error': {
                    'type': type(e).__name__,
                    'message': str(e)
                }
            }), 500
    return wrapper


# ============================================
# FONCTIONS DE LOG
# ============================================
def log_startup(module_name):
    logger.info(f"🚀 {module_name} - DÉMARRAGE")

def log_db_operation(operation, table, details=None):
    msg = f"🗄️ DB: {operation} - {table}"
    if details:
        msg += f" | {details}"
    logger.debug(msg)

def log_ollama_request(prompt_preview, model):
    logger.info(f"🤖 OLLAMA - Modèle: {model}")
    logger.debug(f"📝 Prompt: {prompt_preview[:200]}...")

def log_email_analysis(email_id, result):
    logger.info(f"📧 EMAIL ANALYSÉ - ID: {email_id}")
    logger.info(f"📊 {result.get('category')} | {result.get('urgency')} | {result.get('action')}")

def log_error_summary():
    try:
        with open('logs/email_agent.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            errors = [l for l in lines if '❌' in l]
            if errors:
                logger.info(f"📊 {len(errors)} erreur(s) récente(s)")
    except:
        pass


# ============================================
# VÉRIFICATION DE SANTÉ
# ============================================
def check_app_health():
    logger.info("🏥 VÉRIFICATION DE SANTÉ")
    checks = {
        "Base de données": check_database(),
        "Ollama": check_ollama(),
        "Resend": check_resend(),
    }
    
    all_ok = True
    for name, status in checks.items():
        if status['ok']:
            logger.info(f"✅ {name}: OK")
        else:
            logger.error(f"❌ {name}: {status['error']}")
            all_ok = False
    
    return all_ok

def check_database():
    try:
        import sqlite3
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in c.fetchall()]
        conn.close()
        return {'ok': True, 'tables': tables}
    except Exception as e:
        return {'ok': False, 'error': str(e)}

def check_ollama():
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        if response.status_code == 200:
            return {'ok': True}
        return {'ok': False, 'error': f"Status: {response.status_code}"}
    except Exception as e:
        return {'ok': False, 'error': str(e)}

def check_resend():
    try:
        api_key = os.getenv('RESEND_API_KEY', '')
        if not api_key:
            return {'ok': False, 'error': 'RESEND_API_KEY non configurée'}
        return {'ok': True}
    except Exception as e:
        return {'ok': False, 'error': str(e)}
        
        
        
# utils/error_handler.py


# ============================================
# CONFIGURATION DU LOGGER
# ============================================
logger = logging.getLogger('computer_agent')
logger.setLevel(logging.DEBUG)

if logger.hasHandlers():
    logger.handlers.clear()

formatter = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Fichier
os.makedirs('logs', exist_ok=True)
file_handler = logging.FileHandler('logs/computer_agent.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# ============================================
# DÉCORATEUR POUR CAPTURER LES ERREURS
# ============================================
def log_errors(func):
    """Décorateur pour capturer et logger les erreurs des routes Flask"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logger.info(f"📥 REQUÊTE: {request.method} {request.path}")
            if request.is_json:
                logger.debug(f"📦 JSON: {request.get_json(silent=True)}")
            
            result = func(*args, **kwargs)
            
            if isinstance(result, tuple):
                status_code = result[1] if len(result) > 1 else 200
                logger.info(f"✅ SUCCÈS: {status_code}")
            else:
                logger.info(f"✅ SUCCÈS: 200")
            
            return result
            
        except Exception as e:
            error_msg = f"""
╔══════════════════════════════════════════════════════════════════
║ ❌ ERREUR DÉTECTÉE
╠══════════════════════════════════════════════════════════════════
║ 📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
║ 📂 Fichier: {sys.exc_info()[2].tb_frame.f_code.co_filename}
║ 📍 Ligne: {sys.exc_info()[2].tb_lineno}
║ 🎯 Fonction: {sys.exc_info()[2].tb_frame.f_code.co_name}
║ 🔍 Type: {type(e).__name__}
║ 📝 Message: {str(e)}
╠══════════════════════════════════════════════════════════════════
║ 📋 TRACE COMPLÈTE:
"""
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            logger.info("╚══════════════════════════════════════════════════════════════════")
            
            return jsonify({
                'error': {
                    'type': type(e).__name__,
                    'message': str(e),
                    'file': sys.exc_info()[2].tb_frame.f_code.co_filename,
                    'line': sys.exc_info()[2].tb_lineno,
                    'function': sys.exc_info()[2].tb_frame.f_code.co_name
                }
            }), 500
    
    return wrapper


# ============================================
# FONCTIONS DE LOG SPÉCIFIQUES
# ============================================
def log_computer_action(action, details=None):
    """Log une action du ComputerAgent"""
    msg = f"🖥️ ACTION: {action}"
    if details:
        msg += f" | {details}"
    logger.info(msg)


def log_computer_error(action, error):
    """Log une erreur du ComputerAgent"""
    logger.error(f"❌ ERREUR {action}: {error}")
    logger.error(traceback.format_exc())


# ============================================
# EXPORTS
# ============================================
__all__ = [
    'logger',
    'log_errors',
    'log_computer_action',
    'log_computer_error'
]