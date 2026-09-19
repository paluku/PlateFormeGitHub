import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

class EmailAgent:
    """Agent spécialisé dans l'analyse et le traitement des emails"""
    
    def __init__(self):
        self.model = os.getenv('OLLAMA_MODEL', 'llama3.2:latest')
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434/api/generate')
    
    def analyze_email(self, content, subject, from_email):
        """
        Analyser un email et retourner:
        - Catégorie
        - Urgence
        - Action recommandée
        """
        prompt = f"""
        Tu es un assistant spécialisé dans l'analyse d'emails clients.
        
        Analyse cet email et retourne :
        1. Catégorie (parmi : Réclamation, Question, Demande, Facturation, Technique, Autre)
        2. Urgence (parmi : Haute, Moyenne, Basse)
        3. Action recommandée (parmi : Réponse IA, Humain, Automatique)
        
        Email reçu :
        De : {from_email}
        Sujet : {subject}
        Contenu : {content}
        
        Réponds UNIQUEMENT au format JSON valide :
        {{"category": "catégorie", "urgency": "urgence", "action": "action"}}
        
        Ne mets que les valeurs exactes parmi celles proposées.
        """
        
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # Extraire le JSON de la réponse
                response_text = result.get('response', '')
                
                # Essayer de parser le JSON
                try:
                    # Chercher le JSON dans la réponse
                    import re
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        analysis = json.loads(json_match.group())
                    else:
                        analysis = json.loads(response_text)
                    
                    # Nettoyer les valeurs
                    category = analysis.get('category', 'Autre')
                    urgency = analysis.get('urgency', 'Normale')
                    action = analysis.get('action', 'Humain')
                    
                    # Valider les valeurs
                    valid_categories = ['Réclamation', 'Question', 'Demande', 'Facturation', 'Technique', 'Autre']
                    valid_urgencies = ['Haute', 'Moyenne', 'Basse']
                    valid_actions = ['Réponse IA', 'Humain', 'Automatique']
                    
                    if category not in valid_categories:
                        category = 'Autre'
                    if urgency not in valid_urgencies:
                        urgency = 'Normale'
                    if action not in valid_actions:
                        action = 'Humain'
                    
                    return {
                        'category': category,
                        'urgency': urgency,
                        'action': action
                    }
                    
                except json.JSONDecodeError:
                    # Si le JSON est invalide, utiliser des valeurs par défaut
                    return {
                        'category': 'Autre',
                        'urgency': 'Normale',
                        'action': 'Humain'
                    }
            else:
                return {
                    'category': 'Autre',
                    'urgency': 'Normale',
                    'action': 'Humain'
                }
                
        except Exception as e:
            print(f"❌ Erreur lors de l'analyse: {e}")
            return {
                'category': 'Autre',
                'urgency': 'Normale',
                'action': 'Humain'
            }
    
    def generate_response(self, content, category):
        """
        Générer une réponse automatique basée sur la catégorie
        """
        templates = {
            'Réclamation': """
                Nous avons bien reçu votre réclamation et nous en sommes sincèrement désolés.
                Nous prenons votre retour très au sérieux et allons enquêter sur ce problème.
                Un de nos agents vous contactera dans les plus brefs délais pour résoudre cette situation.
                """,
            'Question': """
                Merci pour votre question. Nous vous remercions de votre intérêt.
                Nous allons examiner votre demande et vous répondrons dans les plus brefs délais.
                """,
            'Demande': """
                Nous avons bien reçu votre demande. Nous allons l'étudier et vous faire un retour 
                dans les plus brefs délais. Merci de votre confiance.
                """,
            'Facturation': """
                Nous avons bien reçu votre demande concernant la facturation.
                Nous allons vérifier votre dossier et vous tenir informé(e) dans les plus brefs délais.
                """,
            'Technique': """
                Nous avons bien reçu votre demande technique.
                Notre équipe technique va analyser le problème et vous contactera rapidement.
                """,
            'Autre': """
                Nous avons bien reçu votre message. Nous l'étudions et vous répondrons 
                dans les plus brefs délais. Merci de votre confiance.
                """
        }
        
        # Si le contenu est vide ou trop court, utiliser le template
        if len(content.strip()) < 20:
            return templates.get(category, templates['Autre']).strip()
        
        # Sinon, utiliser l'IA pour générer une réponse personnalisée
        prompt = f"""
        Tu es un assistant client. Génère une réponse professionnelle à cet email.
        
        Catégorie : {category}
        Email client : {content}
        
        Rédige une réponse :
        - Polie et professionnelle
        - Adaptée à la catégorie
        - Offrant une solution ou une orientation
        - Maximum 150 mots
        
        Réponds UNIQUEMENT avec le texte de la réponse.
        """
        
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', templates.get(category, templates['Autre'])).strip()
            else:
                return templates.get(category, templates['Autre']).strip()
                
        except Exception as e:
            print(f"❌ Erreur lors de la génération: {e}")
            return templates.get(category, templates['Autre']).strip()