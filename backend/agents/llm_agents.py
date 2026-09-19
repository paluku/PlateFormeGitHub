import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

class LLMAgent:
    """Agent utilisant un LLM local (Ollama, etc.)"""
    
    def __init__(self, model="mistral", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.system_prompts = {
            'assistant': "Tu es un assistant IA utile, amical et professionnel. Réponds en français.",
            'specialist': "Tu es un expert technique spécialisé en programmation, IA et technologie. Réponds en français.",
            'collaborative': "Tu es un coordinateur d'équipe qui synthétise les idées de plusieurs experts. Réponds en français."
        }
    
    def process(self, message, agent_type='assistant', history=None):
        """Traite un message avec Ollama"""
        try:
            # Construire le prompt
            system_prompt = self.system_prompts.get(agent_type, self.system_prompts['assistant'])
            
            # Construire le contexte avec l'historique
            context = ""
            if history:
                for msg in history[-5:]:
                    role = "Utilisateur" if msg.get('role') == 'user' else "Assistant"
                    context += f"{role}: {msg.get('content', '')}\n"
            
            # Prompt complet
            full_prompt = f"""{system_prompt}

Historique de la conversation:
{context}

Utilisateur: {message}

Assistant:"""
            
            # Appel à Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                return response.json().get('response', 'Erreur: réponse vide')
            else:
                return f"⚠️ Erreur LLM: {response.status_code}"
                
        except Exception as e:
            return f"⚠️ Erreur: {str(e)}"