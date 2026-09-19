# agents/post_analysis_agent.py

import os
import re
import json
import csv
import shutil
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False
    print("⚠️ Resend non installé. Exécute: python -m pip install resend")


class PostAnalysisAgent:
    """Agent qui exécute des actions après l'analyse d'un document."""
    
    def __init__(self):
        # Configuration Resend
        self.resend_api_key = os.getenv('RESEND_API_KEY', '')
        self.email_from = os.getenv('EMAIL_FROM', 'onboarding@resend.dev')
        self.email_from_name = os.getenv('EMAIL_FROM_NAME', 'Agent Post-Analyse')
        self.email_reply_to = os.getenv('EMAIL_REPLY_TO', '')
        
        if RESEND_AVAILABLE and self.resend_api_key:
            resend.api_key = self.resend_api_key
            print(f"📧 Resend configuré (from: {self.email_from})")
        else:
            print("⚠️ Resend non configuré - mode simulation activé")
        
        # Créer les dossiers nécessaires
        os.makedirs('logs', exist_ok=True)
        os.makedirs('exports/classement', exist_ok=True)
        
        print("🚀 PostAnalysisAgent initialisé")
    
    # ============================================
    # DÉTECTER LES ACTIONS
    # ============================================
    def detect_actions(self, content: str, question: str, response: str) -> List[Dict]:
        """Détecte les actions à effectuer"""
        actions = []
        content_lower = content.lower()
        
        # DÉTECTION 1 : EMAILS
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, content)
        emails = list(set(emails))
        emails = [e for e in emails if e]
        
        if emails:
            actions.append({
                'type': 'send_email',
                'priority': 'high',
                'data': {
                    'recipients': emails,
                    'subject': "Réponse automatique - Document traité",
                    'context': response
                }
            })
            print(f"📧 {len(emails)} email(s) détecté(s): {emails}")
        
        # DÉTECTION 2 : DATES
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4})'
        ]
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, content, re.IGNORECASE))
        
        if dates:
            actions.append({
                'type': 'create_reminder',
                'data': {'dates': list(set(dates))[:5]}
            })
            print(f"📅 {len(set(dates))} date(s) détectée(s)")
        
        # DÉTECTION 3 : MONTANTS
        amounts = re.findall(r'(\d+[.,]?\d*\s*(?:€|EUR|euros))', content, re.IGNORECASE)
        if amounts:
            actions.append({
                'type': 'record_amount',
                'data': {'amounts': list(set(amounts))[:5]}
            })
            print(f"💰 {len(set(amounts))} montant(s) détecté(s)")
        
        # DÉTECTION 4 : URGENCE
        urgent_kw = ['urgent', 'réclamation', 'immédiatement', 'problème', 'mécontent',
                     'litige', 'plainte', 'insatisfait']
        if any(kw in content_lower for kw in urgent_kw):
            actions.append({
                'type': 'notify_manager',
                'data': {'reason': 'Document urgent détecté'}
            })
            print("🚨 Document urgent détecté")
        
        # DÉTECTION 5 : TYPE DE DOCUMENT
        doc_types = {
            'contrat': ['contrat', 'convention', 'accord'],
            'facture': ['facture', 'invoice', 'facturation'],
            'devis': ['devis', 'estimation', 'proposition'],
            'réclamation': ['réclamation', 'plainte', 'litige'],
            'commande': ['commande', 'bon de commande', 'order'],
            'livraison': ['livraison', 'expédition', 'colis']
        }
        for doc_type, keywords in doc_types.items():
            if any(kw in content_lower for kw in keywords):
                actions.append({
                    'type': 'classify_document',
                    'data': {'document_type': doc_type}
                })
                print(f"📁 Type de document: {doc_type}")
                break
        
        return actions
    
    # ============================================
    # EXÉCUTER LES ACTIONS
    # ============================================
    def execute_actions(self, actions: List[Dict], filename: str) -> List[Dict]:
        """Exécute toutes les actions détectées"""
        results = []
        
        for action in actions:
            try:
                result = self._execute_single(action, filename)
                results.append(result)
            except Exception as e:
                results.append({
                    'action': action['type'],
                    'success': False,
                    'error': str(e)
                })
                print(f"❌ Erreur action {action['type']}: {e}")
        
        return results
    
    def _execute_single(self, action: Dict, filename: str) -> Dict:
        """Exécute une seule action"""
        action_type = action['type']
        data = action.get('data', {})
        
        print(f"🚀 Exécution: {action_type}")
        
        if action_type == 'send_email':
            return self._send_email(data, filename)
        elif action_type == 'create_reminder':
            return self._create_reminder(data, filename)
        elif action_type == 'record_amount':
            return self._record_amount(data, filename)
        elif action_type == 'notify_manager':
            return self._notify_manager(data, filename)
        elif action_type == 'classify_document':
            return self._classify(data, filename)
        else:
            return {'action': action_type, 'success': False, 'error': 'Action inconnue'}
    
    # ============================================
    # ENVOI D'EMAIL VIA RESEND
    # ============================================
    def _send_email(self, data: Dict, filename: str) -> Dict:
        """Envoie un email via Resend"""
        
        print("=" * 60)
        print("🚨 _send_email DÉMARRÉE")
        print(f"📧 Data: {data}")
        print(f"📄 Filename: {filename}")
        print(f"📧 Resend disponible: {RESEND_AVAILABLE}")
        print(f"📧 API Key présente: {bool(self.resend_api_key)}")
        print(f"📧 From: {self.email_from}")
        print(f"📧 Reply-To: {self.email_reply_to}")
        print("=" * 60)
        
        recipients = data.get('recipients', [])
        
        if not recipients:
            print("❌ Aucun destinataire")
            return {'action': 'send_email', 'success': False, 'error': 'Aucun destinataire détecté'}
        
        # ⚠️ EXCLUSION DÉSACTIVÉE POUR PERMETTRE L'ENVOI À SOI-MÊME
        # recipients = [r for r in recipients if r != self.email_reply_to]
        
        if not recipients:
            print("❌ Aucun destinataire après filtrage")
            return {'action': 'send_email', 'success': False, 'error': 'Aucun destinataire'}
        
        subject = data.get('subject', f'Réponse automatique - {filename}')
        context = data.get('context', '')
        
        # Corps HTML
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px;">
                    <h1 style="margin: 0; font-size: 1.4rem;">📄 Réponse automatique</h1>
                    <p style="margin: 8px 0 0 0; opacity: 0.9;">Document traité : <strong>{filename}</strong></p>
                </div>
                <div style="padding: 25px;">
                    <p>Bonjour,</p>
                    <p>Nous avons bien reçu votre document <strong>{filename}</strong> et l'avons analysé automatiquement.</p>
                    <div style="background: #f8f9fa; border-left: 4px solid #667eea; padding: 15px; margin: 20px 0; border-radius: 5px;">
                        <strong>📋 Résumé de l'analyse :</strong>
                        <p style="margin: 10px 0 0 0; color: #555; white-space: pre-wrap;">{context[:1500]}</p>
                    </div>
                    <p>Si vous avez des questions ou besoin d'informations complémentaires, n'hésitez pas à nous contacter.</p>
                    <p style="margin-top: 30px;">Cordialement,<br><strong>L'équipe de traitement automatique</strong></p>
                </div>
                <div style="background: #f8f9fa; padding: 15px; text-align: center; color: #888; font-size: 0.85rem;">
                    📧 Cet email a été envoyé automatiquement par l'Agent Post-Analyse
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""Bonjour,

Nous avons bien reçu votre document {filename} et l'avons analysé automatiquement.

Résumé de l'analyse :
{context[:1500]}

Cordialement,
L'équipe de traitement automatique
"""
        
        # Mode simulation si Resend non configuré
        if not RESEND_AVAILABLE or not self.resend_api_key:
            print("⚠️ Resend non configuré - Simulation")
            return {
                'action': 'send_email',
                'success': True,
                'message': f'(Simulation) Email à: {", ".join(recipients)}',
                'simulated': True,
                'recipients': recipients
            }
        
        # Envoi réel
        try:
            sent_ids = []
            failed = []
            
            for recipient in recipients:
                try:
                    print(f"📤 Tentative d'envoi à: {recipient}")
                    
                    params = {
                        "from": f"{self.email_from_name} <{self.email_from}>",
                        "to": [recipient],
                        "subject": subject,
                        "html": html_body,
                        "text": text_body,
                    }
                    
                    if self.email_reply_to:
                        params["reply_to"] = self.email_reply_to
                    
                    email = resend.Emails.send(params)
                    sent_ids.append({
                        'recipient': recipient,
                        'id': email.get('id')
                    })
                    print(f"✅ Email envoyé à {recipient} (ID: {email.get('id')})")
                    
                    self._save_email_history(recipient, subject, context[:500], email.get('id'))
                    
                except Exception as e:
                    import traceback
                    print(f"❌ ERREUR RESEND pour {recipient}")
                    print(f"   Type: {type(e).__name__}")
                    print(f"   Message: {str(e)}")
                    print(traceback.format_exc())
                    
                    failed.append({'recipient': recipient, 'error': str(e)})
                    self._save_email_history(recipient, subject, context[:500], None, str(e))
            
            return {
                'action': 'send_email',
                'success': len(sent_ids) > 0,
                'message': f'✅ {len(sent_ids)} email(s) envoyé(s) sur {len(recipients)}',
                'sent': sent_ids,
                'failed': failed,
                'recipients': recipients
            }
            
        except Exception as e:
            import traceback
            print(f"❌ Erreur Resend globale: {e}")
            print(traceback.format_exc())
            return {
                'action': 'send_email',
                'success': False,
                'error': f'Erreur Resend: {str(e)}'
            }
    
    # ============================================
    # SAUVEGARDER L'HISTORIQUE
    # ============================================
    def _save_email_history(self, recipient, subject, body, email_id=None, error=None):
        """Sauvegarde l'email dans l'historique"""
        try:
            import sqlite3
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS email_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipient TEXT,
                    subject TEXT,
                    body TEXT,
                    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    success INTEGER DEFAULT 1,
                    email_id TEXT,
                    error TEXT
                )
            ''')
            
            c.execute('''
                INSERT INTO email_history (recipient, subject, body, success, email_id, error)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                recipient,
                subject,
                body,
                0 if error else 1,
                email_id or '',
                error or ''
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde historique: {e}")
    
    # ============================================
    # CRÉER UN RAPPEL
    # ============================================
    def _create_reminder(self, data: Dict, filename: str) -> Dict:
        """Crée un rappel pour les dates détectées"""
        dates = data.get('dates', [])
        try:
            with open('logs/rappels.txt', 'a', encoding='utf-8') as f:
                for d in dates:
                    f.write(f"{datetime.now().isoformat()} | {filename} | {d}\n")
            return {
                'action': 'create_reminder',
                'success': True,
                'message': f'✅ {len(dates)} rappel(s) créé(s)',
                'dates': dates
            }
        except Exception as e:
            return {'action': 'create_reminder', 'success': False, 'error': str(e)}
    
    # ============================================
    # ENREGISTRER UN MONTANT
    # ============================================
    def _record_amount(self, data: Dict, filename: str) -> Dict:
        """Enregistre les montants détectés"""
        amounts = data.get('amounts', [])
        try:
            file_exists = os.path.exists('exports/montants.csv')
            with open('exports/montants.csv', 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['Date', 'Fichier', 'Montant'])
                for amount in amounts:
                    writer.writerow([datetime.now().isoformat(), filename, amount])
            return {
                'action': 'record_amount',
                'success': True,
                'message': f'✅ {len(amounts)} montant(s) enregistré(s)',
                'amounts': amounts
            }
        except Exception as e:
            return {'action': 'record_amount', 'success': False, 'error': str(e)}
    
    # ============================================
    # NOTIFIER LE RESPONSABLE
    # ============================================
    def _notify_manager(self, data: Dict, filename: str) -> Dict:
        """Notifie le responsable"""
        try:
            with open('logs/urgences.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().isoformat()} | {filename} | {data.get('reason')}\n")
            return {
                'action': 'notify_manager',
                'success': True,
                'message': '✅ Responsable notifié'
            }
        except Exception as e:
            return {'action': 'notify_manager', 'success': False, 'error': str(e)}
    
    # ============================================
    # CLASSER UN DOCUMENT
    # ============================================
    def _classify(self, data: Dict, filename: str) -> Dict:
        """Classe le document dans un dossier"""
        doc_type = data.get('document_type', 'autre')
        try:
            dest_dir = f'exports/classement/{doc_type}'
            os.makedirs(dest_dir, exist_ok=True)
            
            src = os.path.join('uploads', filename)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(dest_dir, filename))
                return {
                    'action': 'classify_document',
                    'success': True,
                    'message': f'✅ Classé dans {doc_type}/'
                }
            return {
                'action': 'classify_document',
                'success': False,
                'error': 'Fichier source introuvable'
            }
        except Exception as e:
            return {'action': 'classify_document', 'success': False, 'error': str(e)}