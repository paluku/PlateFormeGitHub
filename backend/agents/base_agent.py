# agents/base_agent.py - VERSION 1: AGENT BASE
"""
AGENT BASE - Niveau 1: Le plus simple
Role: Répond avec des messages prédéfinis
Ordre de construction: 5ème (premier agent)
"""

class BaseAgent:
    def __init__(self, name="Agent Base", model="llama3.2"):
        self.name = name
        self.model = model
        self.system_prompt = "Tu es un agent simple."
        
    def process(self, message, history=[]):
        """Répond simplement"""
        return f"📝 Agent {self.name} a reçu: {message}"
    
    def get_info(self):
        return {
            "name": self.name,
            "type": "Base Agent",
            "model": self.model,
            "complexity": 1
        }

# Test simple
if __name__ == "__main__":
    agent = BaseAgent()
    print(agent.process("Bonjour !"))