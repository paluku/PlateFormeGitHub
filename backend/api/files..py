# api/files.py
from flask import Blueprint, request, jsonify, render_template, send_file
import os
from pathlib import Path
from utils.permissions import login_required, owner_required
from utils.error_handler import logger
from agents.multi_file_reader import MultiFileReaderAgent

# ============================================
# CRÉATION DU BLUEPRINT
# ============================================
files_bp = Blueprint('files', __name__, url_prefix='/uploads')

# ============================================
# INITIALISER L'AGENT MULTI-FICHIERS
# ============================================
file_reader = MultiFileReaderAgent(
    upload_folder="uploads",
    max_files=20,
    max_size_mb=50
)

# ============================================
# ROUTE : PAGE UPLOADS
# ============================================
@files_bp.route('/', methods=['GET'])
@login_required
@owner_required
def uploads_page():
    """Page de gestion des fichiers"""
    return render_template('uploads.html')

# ============================================
# ROUTE : LISTER LES FICHIERS
# ============================================
@files_bp.route('/api/files', methods=['GET'])
@login_required
@owner_required
def list_files():
    """Liste les fichiers uploadés"""
    try:
        upload_dir = 'uploads'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        files = os.listdir(upload_dir)
        files = [f for f in files if os.path.isfile(os.path.join(upload_dir, f))]
        
        return jsonify({
            'success': True,
            'files': files,
            'count': len(files)
        })
    except Exception as e:
        logger.error(f"❌ Erreur liste fichiers: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# ROUTE : UPLOADER UN FICHIER
# ============================================
@files_bp.route('/api/upload', methods=['POST'])
@login_required
@owner_required
def upload_file():
    """Upload un fichier"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Aucun fichier'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nom de fichier vide'}), 400
        
        # Vérifier l'extension
        ext = Path(file.filename).suffix.lower()
        allowed_exts = ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.csv', '.txt', 
                       '.json', '.pptx', '.ppt', '.jpg', '.jpeg', '.png', '.gif', '.zip']
        
        if ext not in allowed_exts:
            return jsonify({'success': False, 'error': f'Format non supporté: {ext}'}), 400
        
        # Sauvegarder
        upload_dir = 'uploads'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        file_path = os.path.join(upload_dir, file.filename)
        file.save(file_path)
        
        logger.info(f"✅ Fichier uploadé: {file.filename}")
        return jsonify({'success': True, 'message': f'Fichier {file.filename} uploadé'})
    except Exception as e:
        logger.error(f"❌ Erreur upload: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# ROUTE : TÉLÉCHARGER UN FICHIER
# ============================================
@files_bp.route('/api/uploads/<filename>', methods=['GET'])
@login_required
@owner_required
def download_file(filename):
    """Télécharge un fichier"""
    try:
        file_path = os.path.join('uploads', filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'Fichier non trouvé'}), 404
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        logger.error(f"❌ Erreur téléchargement: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================
# ROUTE : SUPPRIMER UN FICHIER
# ============================================
@files_bp.route('/api/files/<filename>', methods=['DELETE'])
@login_required
@owner_required
def delete_file(filename):
    """Supprime un fichier"""
    try:
        file_path = os.path.join('uploads', filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'Fichier non trouvé'}), 404
        
        os.remove(file_path)
        logger.info(f"🗑️ Fichier supprimé: {filename}")
        return jsonify({'success': True, 'message': f'Fichier {filename} supprimé'})
    except Exception as e:
        logger.error(f"❌ Erreur suppression: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================
# ROUTE : LECTURE DE FICHIER (via chat)
# ============================================
@files_bp.route('/api/read', methods=['POST'])
@login_required
@owner_required
def read_file_content():
    """Lit le contenu d'un fichier via l'agent"""
    try:
        data = request.json
        filename = data.get('filename')
        if not filename:
            return jsonify({'success': False, 'error': 'Nom de fichier requis'}), 400
        
        file_path = os.path.join('uploads', filename)
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'Fichier non trouvé'}), 404
        
        # Utiliser l'agent pour lire
        content = file_reader.read_file(file_path)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'content': content
        })
    except Exception as e:
        logger.error(f"❌ Erreur lecture: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# ROUTE : RÉSUMÉ DE FICHIER (via chat)
# ============================================
@files_bp.route('/api/summarize', methods=['POST'])
#@login_required
#@owner_required
def summarize_file():
    """Résume un fichier via l'agent (appelle le chat)"""
    try:
        data = request.json
        filename = data.get('filename')
        if not filename:
            return jsonify({'success': False, 'error': 'Nom de fichier requis'}), 400
        
        # Appeler le chat avec l'agent filereader
        import requests
        response = requests.post(
            'http://localhost:5000/api/chat/',
            json={
                'message': f"Analyse et résume le fichier {filename}. Donne les points clés.",
                'agent': 'filereader',
                'conversation_id': 1
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'success': True,
                'filename': filename,
                'summary': data.get('response', '')
            })
        else:
            return jsonify({'success': False, 'error': 'Erreur lors du résumé'}), 500
    except Exception as e:
        logger.error(f"❌ Erreur résumé: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500