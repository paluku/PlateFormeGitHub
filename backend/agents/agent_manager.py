import os
from dotenv import load_dotenv
from agents.llm_agent import LLMAgent
from agents.file_creator import FileCreatorAgent
from agents.file_reader import  FileReaderAgent
from agents.email_agent import EmailAgent  
from datetime import datetime
import os

from agents.multi_file_reader import MultiFileReaderAgent

load_dotenv()
class AgentManager:
    """Gestionnaire d'agents avec Ollama"""
    
    def __init__(self):
        model = os.getenv('OLLAMA_MODEL', 'llama3.2:latest')
        print(f"🚀 AgentManager - Modèle: {model}")
        
        # Initialiser l'agent LLM
        self.llm_agent = LLMAgent(model=model)
        self.file_creator = FileCreatorAgent()
        self.email_agent = EmailAgent() 
        self.file_reader = MultiFileReaderAgent()  # ⬅️ BON INITIALISATION
     
        self.agents = {
            'base': BaseAgent(),
            'echo': EchoAgent(),
            'assistant': AssistantAgentWithLLM(self.llm_agent),
            'specialist': SpecialistAgentWithLLM(self.llm_agent),
            'collaborative': CollaborativeAgentWithLLM(self.llm_agent),
            'filecreator': FileCreatorWrapper(self.file_creator, self.llm_agent),
            'filereader': self.file_reader,  # ⬅️ AJOUTER CETTE LIGNE
            'email_agent': self.email_agent, 
           
        }
    
    def get_agent(self, agent_name):
        return self.agents.get(agent_name)

class BaseAgent:
    def process(self, message, history=None):
        return f"Message reçu: '{message}' (Agent de base)"

class EchoAgent:
    def process(self, message, history=None):
        return f"📢 Écho: {message}"

class AssistantAgentWithLLM:
    def __init__(self, llm_agent):
        self.llm_agent = llm_agent
    
    def process(self, message, history=None):
        return self.llm_agent.process(message, 'assistant', history)

class SpecialistAgentWithLLM:
    def __init__(self, llm_agent):
        self.llm_agent = llm_agent
    
    def process(self, message, history=None):
        return self.llm_agent.process(message, 'specialist', history)

class CollaborativeAgentWithLLM:
    def __init__(self, llm_agent):
        self.llm_agent = llm_agent
    
    def process(self, message, history=None):
        return self.llm_agent.process(message, 'collaborative', history)
  
  
  



class FileReaderWrapper:
    def __init__(self, file_reader, llm_agent):
        self.file_reader = file_reader
        self.llm_agent = llm_agent

    def process(self, message, history=None):
        keywords = [
            "fichier", "file", "lire", "read",
            "ouvre", "open", "contenu"
        ]

        message_lower = message.lower()

        # Vérifie si le message concerne un fichier
        if any(keyword in message_lower for keyword in keywords):
            # Recherche d'un nom de fichier avec extension
            match = re.search(r'[\w\-.]+\.[a-zA-Z0-9]+', message)

            if match:
                filename = match.group(0)

                # Chercher dans uploads et exports
                for folder in ("uploads", "exports"):
                    path = os.path.join(folder, filename)

                    if os.path.isfile(path):
                        try:
                            content = self.file_reader.read_file(path)

                            return (
                                f"📄 **{filename}**\n\n"
                                f"{content}"
                            )
                        except Exception as e:
                            return (
                                f"❌ Impossible de lire le fichier "
                                f"'{filename}': {e}"
                            )

                return (
                    f"⚠️ Fichier '{filename}' non trouvé "
                    f"dans uploads/ ou exports/"
                )

        # Si ce n'est pas une demande de lecture de fichier,
        # déléguer au LLM
        return self.llm_agent.process(
            message,
            "assistant",
            history
        )
  
  
  
  
  
  
  
  
  

# =============================================
# AGENT FILECREATOR - Crée des fichiers
# =============================================
class FileCreatorWrapper:
    """Wrapper pour l'agent FileCreator avec IA"""
    def __init__(self, file_creator, llm_agent):
        self.file_creator = file_creator
        self.llm_agent = llm_agent
    
    def process(self, message, history=None):
        # Mots-clés pour la création de fichiers
        create_keywords = ['crée', 'génère', 'create', 'generate', 'fichier', 'file', 
                          'écris', 'write', 'exporte', 'export', 'produis', 'produce']
        
        if any(keyword in message.lower() for keyword in create_keywords):
            # Essayer de détecter le format
            formats = {
                'csv': '.csv',
                'json': '.json',
                'html': '.html',
                'md': '.md',
                'py': '.py',
                'xml': '.xml',
                'txt': '.txt',
                'pdf': '.pdf'
            }
            
            detected_format = 'txt'
            for name, ext in formats.items():
                if name in message.lower():
                    detected_format = name
                    break
            
            # Extraire un nom de fichier potentiel
            import re
            name_match = re.search(r'[\w\-\.]+\.\w+', message)
            if name_match:
                filename = name_match.group()
            else:
                from datetime import datetime
                filename = f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Demander à l'IA de générer le contenu
            content_prompt = f"""Génère le contenu pour un fichier {detected_format} basé sur cette demande:

Demande: {message}

Instructions:
- Si c'est un CSV, génère des données structurées en tableau
- Si c'est un JSON, génère une structure de données
- Si c'est un HTML, génère une page web complète
- Si c'est un Python, génère un script fonctionnel
- Si c'est un Markdown, génère une documentation bien structurée
- Si c'est un PDF, génère le contenu structuré qui sera intégré dans le document PDF

Réponds uniquement avec le contenu du fichier, sans explications supplémentaires."""

            content = self.llm_agent.process(
                content_prompt,
                'assistant',
                history
            )
            
            # Créer le fichier
            result = self.file_creator.create_file(
                content,
                filename,
                detected_format
            )
            
            if result['success']:
                return f"""✅ Fichier créé avec succès !

📄 Nom: {result['filename']}
📁 Emplacement: {result['file_path']}
📊 Format: {detected_format.upper()}"""
            else:
                return f"❌ Erreur lors de la création du fichier: {result.get('error', 'Erreur inconnue')}"
        
        # Si ce n'est pas une demande de création de fichier, passer à l'agent par défaut
        return self.llm_agent.process(message, 'assistant', history)



        
        
        