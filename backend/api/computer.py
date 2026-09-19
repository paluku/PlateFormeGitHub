# api/computer.py

from flask import Blueprint, request, jsonify, send_from_directory
import os
import subprocess
import time
import sys

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Importer le logger
from utils.error_handler import (
    logger, 
    log_errors, 
    log_computer_action, 
    log_computer_error
)

# Essayer d'importer pyautogui
try:
    import pyautogui
    pyautogui.FAILSAFE = True
    PYAUTOGUI_OK = True
    logger.info("✅ pyautogui chargé")
except ImportError:
    PYAUTOGUI_OK = False
    logger.warning("⚠️ pyautogui non installé")


# Créer le blueprint
computer_bp = Blueprint('computer', __name__, url_prefix='/api/computer')

# Dossier pour les captures
SCREENSHOT_FOLDER = 'screenshots'
os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)


# ============================================
# 1. INFO ÉCRAN
# ============================================
@computer_bp.route('/screen', methods=['GET'])
@log_errors
def screen_info():
    """Retourne la taille de l'écran"""
    log_computer_action("screen_info")
    
    if not PYAUTOGUI_OK:
        logger.error("pyautogui non disponible")
        return jsonify({'error': 'pyautogui non installé'}), 500
    
    w, h = pyautogui.size()
    logger.info(f"📺 Écran détecté: {w}x{h}")
    
    return jsonify({
        'width': w,
        'height': h,
        'pyautogui': True
    })


# ============================================
# 2. OUVRIR NOTEPAD
# ============================================
@computer_bp.route('/open-notepad', methods=['POST'])
@log_errors
def open_notepad():
    """Ouvre Notepad"""
    log_computer_action("open_notepad")
    
    import platform
    os_type = platform.system().lower()
    logger.debug(f"💻 OS détecté: {os_type}")
    
    if 'win' in os_type:
        subprocess.Popen(['notepad.exe'])
        app_name = 'Notepad'
    elif 'darwin' in os_type or 'mac' in os_type:
        subprocess.Popen(['open', '-a', 'TextEdit'])
        app_name = 'TextEdit'
    else:
        subprocess.Popen(['gedit'])
        app_name = 'gedit'
    
    logger.info(f"🚀 {app_name} lancé")
    time.sleep(2)
    
    return jsonify({
        'success': True,
        'app': app_name,
        'message': f'✅ {app_name} ouvert'
    })


# ============================================
# 3. ÉCRIRE DU TEXTE
# ============================================
@computer_bp.route('/write-text', methods=['POST'])
@log_errors
def write_text():
    """Écrit du texte"""
    log_computer_action("write_text")
    
    if not PYAUTOGUI_OK:
        logger.error("pyautogui non disponible")
        return jsonify({'error': 'pyautogui non installé'}), 500
    
    data = request.json
    text = data.get('text', '')
    
    if not text:
        logger.warning("⚠️ Texte vide")
        return jsonify({'success': False, 'error': 'Texte vide'}), 400
    
    logger.debug(f"✍️ Écriture: {text[:50]}...")
    pyautogui.write(text, interval=0.05)
    
    logger.info(f"✅ {len(text)} caractères écrits")
    
    return jsonify({
        'success': True,
        'text': text,
        'message': f'✅ {len(text)} caractères écrits'
    })


# ============================================
# 4. APPUYER SUR ENTRÉE
# ============================================
@computer_bp.route('/press-enter', methods=['POST'])
@log_errors
def press_enter():
    """Appuie sur Entrée"""
    log_computer_action("press_enter")
    
    if not PYAUTOGUI_OK:
        logger.error("pyautogui non disponible")
        return jsonify({'error': 'pyautogui non installé'}), 500
    
    pyautogui.press('enter')
    logger.info("✅ Entrée pressée")
    
    return jsonify({
        'success': True,
        'message': '✅ Entrée pressée'
    })


# ============================================
# 5. CAPTURE D'ÉCRAN
# ============================================
@computer_bp.route('/screenshot', methods=['POST'])
@log_errors
def screenshot():
    """Fait une capture d'écran"""
    log_computer_action("screenshot")
    
    if not PYAUTOGUI_OK:
        logger.error("pyautogui non disponible")
        return jsonify({'error': 'pyautogui non installé'}), 500
    
    from datetime import datetime
    
    filename = f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    filepath = os.path.join(SCREENSHOT_FOLDER, filename)
    
    logger.debug(f"📸 Capture en cours...")
    img = pyautogui.screenshot()
    img.save(filepath)
    
    logger.info(f"✅ Capture sauvegardée: {filename}")
    
    return jsonify({
        'success': True,
        'filename': filename,
        'url': f'/api/computer/screenshots/{filename}',
        'message': f'✅ Capture: {filename}'
    })


# ============================================
# 6. SERVIR LES CAPTURES
# ============================================
@computer_bp.route('/screenshots/<filename>', methods=['GET'])
@log_errors
def serve_screenshot(filename):
    """Sert les captures d'écran"""
    logger.debug(f"📁 Envoi de: {filename}")
    return send_from_directory(SCREENSHOT_FOLDER, filename)