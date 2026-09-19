# api/files.py
from flask import Blueprint, request, jsonify, render_template, send_file
import os
from pathlib import Path

files_bp = Blueprint('files', __name__, url_prefix='/uploads')

# ============================================
# ROUTE : PAGE UPLOADS
# ============================================
@files_bp.route('/', methods=['GET'])
def uploads_page():
    return render_template('uploads.html')

# ============================================
# ROUTE : LISTER LES FICHIERS
# ============================================
@files_bp.route('/api/files', methods=['GET'])
def list_files():
    try:
        upload_dir = 'uploads'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        files = os.listdir(upload_dir)
        files = [f for f in files if os.path.isfile(os.path.join(upload_dir, f))]
        return jsonify({'success': True, 'files': files, 'count': len(files)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# ROUTE : UPLOADER UN FICHIER
# ============================================
@files_bp.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Aucun fichier'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nom de fichier vide'}), 400
        
        ext = Path(file.filename).suffix.lower()
        allowed_exts = ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.csv', '.txt', 
                       '.json', '.pptx', '.ppt', '.jpg', '.jpeg', '.png', '.gif', '.zip']
        
        if ext not in allowed_exts:
            return jsonify({'success': False, 'error': f'Format non supporté: {ext}'}), 400
        
        upload_dir = 'uploads'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        file_path = os.path.join(upload_dir, file.filename)
        file.save(file_path)
        
        return jsonify({'success': True, 'message': f'Fichier {file.filename} uploadé'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# ROUTE : TÉLÉCHARGER UN FICHIER (AJOUTER)
# ============================================
@files_bp.route('/api/uploads/<filename>', methods=['GET'])
def download_file(filename):
    """Télécharge un fichier"""
    try:
        safe_filename = os.path.basename(filename)
        file_path = os.path.join('uploads', safe_filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Fichier non trouvé'}), 404
        
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# ROUTE : SUPPRIMER UN FICHIER
# ============================================
@files_bp.route('/api/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        safe_filename = os.path.basename(filename)
        file_path = os.path.join('uploads', safe_filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Fichier non trouvé'}), 404
        
        os.remove(file_path)
        return jsonify({'success': True, 'message': f'Fichier {filename} supprimé'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500