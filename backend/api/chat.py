from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from agents.agent_manager import AgentManager
from memory.memory import save_message, get_history, get_full_history
from agents.file_creator import FileCreatorAgent
from datetime import datetime
import os
import re
import requests
from agents.multi_file_reader import MultiFileReaderAgent

# Initialiser l'agent de lecture de fichiers
file_reader = MultiFileReaderAgent()

# Créer le blueprint
chat_bp = Blueprint('chat', __name__)

# Configuration upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'csv', 'json', 'pdf', 'docx', 'md', 'py', 'js', 'html', 'xml', 'xlsx', 'xls', 'pptx', 'ppt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# =============================================
# ENDPOINTS POUR LE CHAT
# =============================================

@chat_bp.route('/api/chat/', methods=['POST'])
def chat():
    """Endpoint principal pour le chat"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        agent_type = data.get('agent', 'base')
        conversation_id = data.get('conversation_id', 1)
        
        print(f"📨 Message reçu: {message[:50]}... (agent: {agent_type})")
        print(f"🤖 Agent: {agent_type}")
        
        if not message:
            return jsonify({'error': 'Message vide'}), 400
        
        # ============================================
        # GESTION SPÉCIALE POUR L'AGENT ASSISTANT
        # ============================================
        if agent_type == 'assistant':
            print("🤖 Traitement par assistant")
            
            # 🔍 Détecter le nom du fichier dans la question
            file_match = re.search(r'([\w\-\.]+\.[a-zA-Z0-9]+)', message)
            file_content = None
            filename = None
            
            if file_match:
                filename = file_match.group(1)
                file_path = os.path.join('uploads', filename)
                print(f"📂 Fichier détecté: {file_path}")
                
                if os.path.exists(file_path):
                    try:
                        file_content = file_reader.read_file(file_path)
                        print(f"✅ Fichier chargé: {filename} ({len(file_content)} caractères)")
                    except Exception as e:
                        print(f"❌ Erreur lecture: {e}")
                        return jsonify({
                            'response': f"❌ Impossible de lire le fichier: {str(e)}"
                        })
                else:
                    # Vérifier aussi dans le dossier courant
                    alt_path = os.path.join(os.getcwd(), filename)
                    if os.path.exists(alt_path):
                        try:
                            file_content = file_reader.read_file(alt_path)
                            print(f"✅ Fichier chargé depuis le dossier courant: {filename}")
                        except Exception as e:
                            return jsonify({
                                'response': f"❌ Impossible de lire le fichier: {str(e)}"
                            })
                    else:
                        return jsonify({
                            'response': f"❌ Fichier '{filename}' non trouvé dans uploads/. Vérifie le nom."
                        })
            
            # 📝 Préparer le prompt pour Ollama
            if file_content and filename:
                prompt = f"""
Tu es un assistant utile. Voici le contenu du fichier {filename}:

{file_content[:4000]}

Question de l'utilisateur: {message}

Instructions:
- Réponds UNIQUEMENT en te basant sur le contenu du fichier.
- Si la question demande un résumé, fais un résumé clair et structuré.
- Si la réponse n'est pas dans le fichier, dis-le clairement.
- Sois précis et concis.
"""
                print("📤 Envoi du contenu du fichier à Ollama")
            else:
                # Si aucun fichier détecté, utiliser le message tel quel
                prompt = message
                print("ℹ️ Aucun fichier détecté, prompt direct")

            # 🔗 Appel à Ollama
            try:
                ollama_response = requests.post(
                    'http://localhost:11434/api/generate',
                    json={
                        'model': 'llama3.2:latest',
                        'prompt': prompt,
                        'stream': False
                    },
                    timeout=60
                )
                
                if ollama_response.status_code == 200:
                    response_text = ollama_response.json().get('response', 'Pas de réponse')
                    print("✅ Réponse Ollama reçue")
                    
                    # Si un fichier a été lu, ajouter une note
                    if file_content and filename:
                        response_text = f"📄 **Fichier analysé: {filename}**\n\n{response_text}"
                    
                    # Sauvegarder la réponse
                    save_message('assistant', response_text, conversation_id)
                    
                    return jsonify({
                        'response': response_text,
                        'agent': agent_type,
                        'conversation_id': conversation_id
                    })
                else:
                    print(f"❌ Erreur Ollama: {ollama_response.status_code}")
                    error_msg = f"❌ Erreur Ollama: {ollama_response.status_code}"
                    save_message('assistant', error_msg, conversation_id)
                    return jsonify({
                        'response': error_msg,
                        'agent': agent_type,
                        'conversation_id': conversation_id
                    })
            except requests.exceptions.Timeout:
                print("❌ Timeout Ollama")
                error_msg = "⏳ Temps d'attente dépassé. Réessaie plus tard."
                save_message('assistant', error_msg, conversation_id)
                return jsonify({
                    'response': error_msg,
                    'agent': agent_type,
                    'conversation_id': conversation_id
                })
            except requests.exceptions.ConnectionError:
                print("❌ Ollama non accessible")
                error_msg = "❌ Ollama n'est pas accessible. Vérifie qu'il tourne avec: ollama serve"
                save_message('assistant', error_msg, conversation_id)
                return jsonify({
                    'response': error_msg,
                    'agent': agent_type,
                    'conversation_id': conversation_id
                })

        # ============================================
        # AUTRES AGENTS (base, echo, specialist, etc.)
        # ============================================
        agent_manager = AgentManager()
        save_message('user', message, conversation_id)
        history = get_full_history(conversation_id, limit=10)
        agent = agent_manager.get_agent(agent_type)
        
        if not agent:
            return jsonify({'error': f'Agent {agent_type} non trouvé'}), 404
        
        response = agent.process(message, history)
        save_message('assistant', response, conversation_id)
        
        return jsonify({
            'response': response,
            'agent': agent_type,
            'conversation_id': conversation_id
        })
    except Exception as e:
        print(f"❌ Erreur chat: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/api/chat/history/<int:conv_id>', methods=['GET'])
def get_chat_history(conv_id):
    try:
        history = get_full_history(conv_id)
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/api/chat/conversations', methods=['GET'])
def get_conversations():
    try:
        from database.database import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, COUNT(m.id) as message_count 
            FROM conversations c
            LEFT JOIN messages m ON c.id = m.conversation_id
            GROUP BY c.id
            ORDER BY c.created_at DESC
        """)
        conversations = cursor.fetchall()
        conn.close()
        return jsonify([dict(conv) for conv in conversations])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================
# ENDPOINTS POUR L'UPLOAD DE FICHIERS
# =============================================

@chat_bp.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'Format non supporté. Formats: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        filename = secure_filename(file.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        return jsonify({
            'message': f'Fichier {filename} uploadé avec succès',
            'filename': filename,
            'path': file_path
        })
    except Exception as e:
        print(f"❌ Erreur upload: {str(e)}")
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/api/files', methods=['GET'])
def list_files():
    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        files = os.listdir(UPLOAD_FOLDER)
        return jsonify({
            'files': files,
            'count': len(files)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/api/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'message': f'Fichier {filename} supprimé'})
        else:
            return jsonify({'error': 'Fichier non trouvé'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================
# ENDPOINTS POUR LES FICHIERS EXPORTÉS
# =============================================

@chat_bp.route('/api/exports', methods=['GET'])
def list_exports():
    try:
        creator = FileCreatorAgent()
        files = creator.list_files()
        return jsonify({'files': files, 'count': len(files)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/api/exports/<filename>', methods=['GET'])
def download_export(filename):
    try:
        return send_from_directory('exports', filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@chat_bp.route('/api/exports/<filename>', methods=['DELETE'])
def delete_export(filename):
    try:
        creator = FileCreatorAgent()
        result = creator.delete_file(filename)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================
# ENDPOINTS POUR LA LECTURE DE FICHIERS
# =============================================

@chat_bp.route('/api/read-file/<filename>', methods=['GET'])
def read_file_content(filename):
    try:
        safe_filename = secure_filename(filename)
        file_path = os.path.join('uploads', safe_filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Fichier non trouvé'}), 404
        
        # Détecter l'extension
        ext = os.path.splitext(file_path)[1].lower()
        content = ""
        
        # Fichiers texte
        text_extensions = {'.txt', '.csv', '.json', '.md', '.py', '.js', '.html', '.xml', '.css', '.sql', '.log'}
        
        if ext in text_extensions:
            # Essayer plusieurs encodages
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            else:
                content = f"⚠️ Impossible de lire le fichier {safe_filename} (encodage non supporté)"
        else:
            # Fichiers binaires
            content = f"📄 Fichier binaire: {safe_filename}\n"
            content += f"📊 Taille: {os.path.getsize(file_path)} bytes\n"
            content += f"📁 Extension: {ext}\n"
            content += "⚠️ Le contenu ne peut pas être affiché en texte brut"
        
        return jsonify({
            'filename': safe_filename,
            'content': content,
            'size': os.path.getsize(file_path),
            'extension': ext
        })
    except Exception as e:
        print(f"❌ Erreur lecture fichier: {str(e)}")
        return jsonify({'error': str(e)}), 500


# =============================================
# ENDPOINTS POUR LE CHAT AVEC FICHIER
# =============================================
@chat_bp.route('/api/chat-with-file', methods=['POST'])
def chat_with_file():
    """
    Analyse une question sur plusieurs fichiers simultanément.
    """

    try:
        data = request.json

        filenames = data.get('filenames', [])
        question = data.get('question')
        agent_type = data.get('agent', 'assistant')

        # Compatibilité avec l'ancien frontend :
        # si un seul filename est envoyé, on le transforme en liste.
        if not filenames:
            old_filename = data.get('filename')
            if old_filename:
                filenames = [old_filename]

        if not filenames or not question:
            return jsonify({
                'error': 'filenames et question sont requis'
            }), 400

        # Sécurité + construction des chemins
        file_paths = []

        for filename in filenames:

            safe_filename = secure_filename(filename)

            if not safe_filename:
                continue

            file_path = os.path.join(UPLOAD_FOLDER, safe_filename)

            if not os.path.exists(file_path):
                print(f"⚠️ Fichier introuvable: {safe_filename}")
                continue

            file_paths.append(file_path)

        if not file_paths:
            return jsonify({
                'error': 'Aucun des fichiers demandés n’a été trouvé'
            }), 404

        print("=" * 60)
        print("🤖 ANALYSE MULTI-FICHIERS")
        print(f"📚 Fichiers: {len(file_paths)}")
        print(f"❓ Question: {question}")
        print("=" * 60)

        # ==================================================
        # LIRE TOUS LES FICHIERS
        # ==================================================

        result = file_reader.read_files(
            file_paths,
            combine=False
        )

        if isinstance(result, dict) and 'error' in result:
            return jsonify(result), 400

        contents = result.get('results', {})
        errors = result.get('errors', [])

        if not contents:
            return jsonify({
                'error': 'Impossible de lire les fichiers',
                'errors': errors
            }), 400

        print(f"✅ {len(contents)} fichiers lus")

        # ==================================================
        # CONSTRUIRE LE CONTEXTE GLOBAL
        # ==================================================

        context_parts = []

        for filename, content in contents.items():

            context_parts.append(
                f"""
============================================================
📄 FICHIER : {filename}
============================================================

{content}
"""
            )

        combined_context = "\n".join(context_parts)

        # ==================================================
        # LIMITE DE SÉCURITÉ
        # ==================================================

        # V1 : on limite le contexte global.
        # Cette limite pourra être remplacée ensuite
        # par un système RAG/recherche par pertinence.

        max_context_length = 30000

        if len(combined_context) > max_context_length:

            combined_context = (
                combined_context[:max_context_length]
                + "\n\n⚠️ CONTEXTE TRONQUÉ : certains contenus "
                  "n'ont pas pu être transmis à Ollama."
            )

        # ==================================================
        # PROMPT MULTI-FICHIERS
        # ==================================================

        prompt = f"""
Tu es un assistant IA pour une PME.

Tu disposes de plusieurs fichiers appartenant à la même entreprise.

IMPORTANT :
- Analyse TOUS les fichiers fournis.
- Croise les informations entre les fichiers.
- Ne te limite pas au premier fichier.
- Si une information apparaît dans plusieurs fichiers, compare-les.
- Si deux fichiers contiennent des informations contradictoires,
  signale clairement la contradiction.
- Ne crée aucune information absente des fichiers.
- Si l'information nécessaire n'est pas présente, dis-le clairement.
- Cite le ou les noms des fichiers utilisés pour chaque information importante.
- Réponds en français.
- Donne une réponse synthétique mais suffisamment détaillée.
- Pour une question concernant des urgences, distingue les vrais problèmes
  des informations simplement importantes.

QUESTION DE L'UTILISATEUR :
{question}

============================================================
CONTENU DES FICHIERS
============================================================

{combined_context}

============================================================
FIN DES FICHIERS
============================================================

Construis maintenant une réponse globale à la question.
"""

        print(
            f"📤 Envoi du contexte global à Ollama "
            f"({len(combined_context)} caractères)"
        )

        # ==================================================
        # APPEL OLLAMA
        # ==================================================

        ollama_response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama3.2:latest',
                'prompt': prompt,
                'stream': False
            },
            timeout=180
        )

        if ollama_response.status_code != 200:

            print(
                f"❌ Erreur Ollama: "
                f"{ollama_response.status_code}"
            )

            return jsonify({
                'error': f'Erreur Ollama: {ollama_response.status_code}',
                'details': ollama_response.text
            }), 500

        response_text = ollama_response.json().get(
            'response',
            'Pas de réponse'
        )

        print("✅ Réponse multi-fichiers reçue")

        # ==================================================
        # RÉPONSE
        # ==================================================

        return jsonify({
            'response': response_text,
            'filenames': list(contents.keys()),
            'files_analyzed': len(contents),
            'errors': errors,
            'agent': agent_type
        })

    except requests.exceptions.Timeout:

        print("❌ Timeout Ollama")

        return jsonify({
            'error': 'Temps d\'attente dépassé. '
                     'L\'analyse de plusieurs fichiers peut être longue.'
        }), 500

    except requests.exceptions.ConnectionError:

        print("❌ Ollama non accessible")

        return jsonify({
            'error': 'Ollama n\'est pas accessible. Vérifie qu\'il tourne.'
        }), 500

    except Exception as e:

        print(f"❌ Erreur chat multi-fichiers: {str(e)}")

        import traceback
        traceback.print_exc()

        return jsonify({
            'error': str(e)
        }), 500

# =============================================
# ENDPOINTS POUR LES UPLOADS
# =============================================

@chat_bp.route('/api/uploads', methods=['GET'])
def list_uploaded_files():
    try:
        upload_folder = 'uploads'
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        files = os.listdir(upload_folder)
        files_info = []
        for f in files:
            file_path = os.path.join(upload_folder, f)
            if os.path.isfile(file_path):
                files_info.append({
                    'name': f,
                    'size': os.path.getsize(file_path),
                    'modified': os.path.getmtime(file_path)
                })
        
        return jsonify({
            'files': files_info,
            'count': len(files_info)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================
# ENDPOINT POUR L'ANALYSE DE PDF AVEC SOURCES
# =============================================

@chat_bp.route('/api/analyze-pdf', methods=['POST'])
def analyze_pdf():
    """
    Endpoint spécialisé pour l'analyse de PDF avec extraction de sources.
    """
    try:
        data = request.json
        filename = data.get('filename')
        questions = data.get('questions', [])
        
        if not filename:
            return jsonify({'error': 'filename requis'}), 400
        
        safe_filename = secure_filename(filename)
        file_path = os.path.join('uploads', safe_filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': f'Fichier {safe_filename} non trouvé'}), 404
        
        # Lire le fichier
        content = file_reader.read_file(file_path)
        
        results = {}
        for question in questions:
            prompt = f"""
Contenu du fichier {safe_filename}:
---
{content[:5000]}
---

Question: {question}

Instructions:
- Réponds UNIQUEMENT en te basant sur le contenu du fichier.
- Indique la source (page/ligne) si possible.
- Si la réponse n'est pas dans le fichier, dis-le clairement.
"""
            
            ollama_response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'llama3.2:latest',
                    'prompt': prompt,
                    'stream': False
                },
                timeout=60
            )
            
            if ollama_response.status_code == 200:
                results[question] = ollama_response.json().get('response', 'Pas de réponse')
            else:
                results[question] = f"Erreur: {ollama_response.status_code}"
        
        return jsonify({
            'filename': safe_filename,
            'results': results
        })
    except Exception as e:
        print(f"❌ Erreur analyze_pdf: {str(e)}")
        return jsonify({'error': str(e)}), 500
        
        
        
        
        
        
        # api/chat.py - Ajouter à la fin

from agents.post_analysis_agent import PostAnalysisAgent

# Initialiser l'agent
post_analysis = PostAnalysisAgent()


@chat_bp.route('/api/analyze-and-execute', methods=['POST'])
def analyze_and_execute():
    """Analyse un document et exécute les actions détectées"""
    try:
        data = request.json
        filename = data.get('filename')
        question = data.get('question')
        auto_execute = data.get('auto_execute', True)
        
        if not filename or not question:
            return jsonify({'error': 'filename et question requis'}), 400
        
        safe_filename = secure_filename(filename)
        file_path = os.path.join('uploads', safe_filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': f'Fichier {safe_filename} non trouvé'}), 404
        
        print(f"📂 Analyse de: {safe_filename}")
        
        # 1. Lire le fichier
        content = file_reader.read_file(file_path)
        
        # 2. Analyser avec Ollama
        import requests as req
        prompt = f"""
Contenu du fichier {safe_filename}:
---
{content[:6000]}
---

Question: {question}

Réponds en français en te basant sur le contenu du fichier.
"""
        
        ollama_response = req.post(
            'http://localhost:11434/api/generate',
            json={'model': 'llama3.2:latest', 'prompt': prompt, 'stream': False},
            timeout=120
        )
        
        if ollama_response.status_code != 200:
            return jsonify({'error': 'Erreur Ollama'}), 500
        
        response_text = ollama_response.json().get('response', '')
        
        # 3. Détecter les actions
        actions = post_analysis.detect_actions(content, question, response_text)
        
        # 4. Exécuter les actions si demandé
        action_results = []
        if auto_execute and actions:
            action_results = post_analysis.execute_actions(actions, safe_filename)
        
        return jsonify({
            'success': True,
            'filename': safe_filename,
            'response': response_text,
            'actions_detected': actions,
            'actions_executed': action_results,
            'auto_execute': auto_execute
        })
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
        
# api/chat.py - Ajouter à la fin

@chat_bp.route('/api/test-email', methods=['POST'])
def test_email():
    """Teste l'envoi d'email via Resend"""
    try:
        data = request.json
        to_email = data.get('email')
        
        if not to_email:
            return jsonify({'error': 'Email requis'}), 400
        
        from agents.post_analysis_agent import PostAnalysisAgent
        agent = PostAnalysisAgent()
        
        result = agent._send_email({
            'recipients': [to_email],
            'subject': '🧪 Test - Agent Post-Analyse',
            'context': 'Ceci est un email de test envoyé depuis votre application.'
        }, 'test_email.txt')
        
        return jsonify({
            'success': result.get('success', False),
            'message': result.get('message', ''),
            'error': result.get('error'),
            'simulated': result.get('simulated', False),
            'email_id': result.get('email_id'),
            'config': {
                'resend_configured': bool(agent.resend_api_key),
                'from_email': agent.email_from,
                'reply_to': agent.email_reply_to
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500 

# api/chat.py - Ajouter à la fin

@chat_bp.route('/api/test-resend', methods=['POST'])
def test_resend():
    """Teste la configuration Resend et affiche l'erreur exacte"""
    try:
        import os
        import resend
        from dotenv import load_dotenv
        load_dotenv()
        
        # Récupérer la config
        api_key = os.getenv('RESEND_API_KEY', '')
        email_from = os.getenv('EMAIL_FROM', 'onboarding@resend.dev')
        email_to = os.getenv('EMAIL_REPLY_TO', '')
        
        result = {
            'config': {
                'api_key_present': bool(api_key),
                'api_key_preview': api_key[:15] + '...' if api_key else 'ABSENTE',
                'email_from': email_from,
                'email_to': email_to
            }
        }
        
        if not api_key:
            result['success'] = False
            result['error'] = 'RESEND_API_KEY non configurée dans .env'
            return jsonify(result)
        
        if not email_to:
            result['success'] = False
            result['error'] = 'EMAIL_REPLY_TO non configurée dans .env'
            return jsonify(result)
        
        # Essayer d'envoyer
        resend.api_key = api_key
        
        try:
            email = resend.Emails.send({
                "from": f"Test <{email_from}>",
                "to": [email_to],
                "subject": "🧪 Test Resend - Diagnostic",
                "html": "<h1>Test</h1><p>Si vous recevez cet email, Resend fonctionne.</p>"
            })
            
            result['success'] = True
            result['email_id'] = email.get('id')
            result['message'] = f'✅ Email envoyé à {email_to}'
            
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            result['error_type'] = type(e).__name__
            
            # Analyser l'erreur
            error_str = str(e).lower()
            if '403' in error_str or 'forbidden' in error_str:
                result['diagnostic'] = '❌ Resend refuse : tu ne peux envoyer qu\'à ton propre email (limite gratuite)'
            elif '401' in error_str or 'unauthorized' in error_str:
                result['diagnostic'] = '❌ Clé API invalide. Vérifie RESEND_API_KEY'
            elif '422' in error_str:
                result['diagnostic'] = '❌ Paramètres invalides (from ou to)'
            elif 'testing emails' in error_str:
                result['diagnostic'] = '❌ Tu ne peux envoyer qu\'à l\'email de ton compte Resend'
            else:
                result['diagnostic'] = f'❌ Erreur: {str(e)}'
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500






        