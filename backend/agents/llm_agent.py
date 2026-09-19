import requests
from dotenv import load_dotenv
import os

load_dotenv()

class LLMAgent:
    def __init__(self, model=None, base_url=None):
        self.model = model or os.getenv('OLLAMA_MODEL', 'llama3.2:latest')
        self.base_url = base_url or os.getenv('OLLAMA_URL', 'http://localhost:11434')
        
        print(f"🤖 LLM Agent - Modèle: {self.model}")
        print(f"🔗 URL: {self.base_url}")
        
        self.system_prompts = {
            'assistant': "Tu es un assistant IA utile et amical. Réponds en français.",
            'specialist': "Tu es un expert technique en programmation et IA. Réponds en français.",
            'collaborative': "Tu es un facilitateur d'équipe multi-expert. Structure ta réponse en 3 parties: Technique, Créatif, Stratégique."
        }
    
    def process(self, message, agent_type='assistant', history=None):
        try:
            print(f"📨 Message: {message[:50]}...")
            print(f"🤖 Type: {agent_type}")
            
            system_prompt = self.system_prompts.get(agent_type, self.system_prompts['assistant'])
            
            context = ""
            if history:
                for msg in history[-5:]:
                    role = "Utilisateur" if msg.get('role') == 'user' else "Assistant"
                    context += f"{role}: {msg.get('content', '')}\n"
            
            full_prompt = f"""{system_prompt}

Historique:
{context}

Utilisateur: {message}

Assistant:"""
            
            print(f"📤 Envoi à Ollama...")
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=60
            )
            
            print(f"📥 Réponse: {response.status_code}")
            
            if response.status_code == 200:
                return response.json().get('response', 'Erreur: réponse vide')
            else:
                return f"⚠️ Erreur LLM ({response.status_code})"
                
        except Exception as e:
            print(f"❌ Erreur LLM: {str(e)}")
            return f"⚠️ Erreur: {str(e)}"