# agents/echo_agent.py - VERSION 2: AGENT ECHO
"""
AGENT ECHO - Niveau 2: Un peu plus avancé
Role: Analyse et répète le message avec métadonnées
Ordre de construction: 6ème
"""

from .base_agent import BaseAgent

class EchoAgent(BaseAgent):
    def __init__(self, name="Agent Echo", model="llama3.2"):
        super().__init__(name, model)
        self.system_prompt = "Tu es un agent Echo qui analyse les messages."
        
    def process(self, message, history=[]):
        """Analyse et echo le message"""
        # Analyse simple
        analysis = {
            "longueur": len(message),
            "mots": len(message.split()),
            "caracteres_speciaux": sum(1 for c in message if not c.isalnum() and not c.isspace()),
            "echo": f"ECHO: {message}"
        }
        
        return f"""📊 Analyse:
- Longueur: {analysis['longueur']} caractères
- Mots: {analysis['mots']}
- Caractères spéciaux: {analysis['caracteres_speciaux']}
- {analysis['echo']}"""