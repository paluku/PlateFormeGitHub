#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic complet pour identifier les erreurs
et localiser exactement où intervenir
"""

import sys
import os
import traceback

print("=" * 70)
print("🔍 DIAGNOSTIC COMPLET DES AGENTS")
print("=" * 70)

# Couleurs pour le terminal (optionnel)
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_ok(msg):
    print(f"   {Colors.GREEN}✅{Colors.RESET} {msg}")

def print_error(msg):
    print(f"   {Colors.RED}❌{Colors.RESET} {msg}")

def print_warning(msg):
    print(f"   {Colors.YELLOW}⚠️{Colors.RESET} {msg}")

def print_info(msg):
    print(f"   {Colors.BLUE}ℹ️{Colors.RESET} {msg}")

# =============================================
# 1. INFORMATIONS DE BASE
# =============================================
print("\n📁 1. INFORMATIONS DE BASE")
print("-" * 50)
print(f"   Dossier courant: {os.getcwd()}")
print(f"   Python version: {sys.version}")
print(f"   Python path: {sys.path[:3]}...")

# =============================================
# 2. VÉRIFICATION DES FICHIERS
# =============================================
print("\n📄 2. VÉRIFICATION DES FICHIERS")
print("-" * 50)

files_to_check = {
    "agents/__init__.py": "Dossier agents",
    "agents/llm_agent.py": "Agent IA",
    "agents/file_reader.py": "Agent FileReader",
    "agents/file_creator.py": "Agent FileCreator",
    "agents/agent_manager.py": "Gestionnaire d'agents",
    "api/__init__.py": "Dossier API",
    "api/chat.py": "API Chat",
    "app.py": "Application principale",
}

missing_files = []
for file, desc in files_to_check.items():
    exists = os.path.exists(file)
    if exists:
        size = os.path.getsize(file)
        print_ok(f"{file} ({desc}) - {size} octets")
    else:
        print_error(f"{file} ({desc}) - FICHIER MANQUANT !")
        missing_files.append(file)

if missing_files:
    print(f"\n   {Colors.RED}⚠️ Fichiers manquants: {', '.join(missing_files)}{Colors.RESET}")

# =============================================
# 3. CONTENU DES FICHIERS CLÉS
# =============================================
print("\n📝 3. CONTENU DES FICHIERS CLÉS")
print("-" * 50)

# 3.1 Vérifier file_creator.py
print("\n   📄 3.1 agents/file_creator.py")
file_path = "agents/file_creator.py"
if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if "class FileCreatorAgent" in content:
            print_ok("Classe FileCreatorAgent trouvée")
            # Trouver la ligne
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "class FileCreatorAgent" in line:
                    print_info(f"   Ligne {i+1}: {line.strip()}")
                    break
        else:
            print_error("Classe FileCreatorAgent NON TROUVÉE")
            
        # Vérifier la méthode create_file
        if "def create_file" in content:
            print_ok("Méthode create_file trouvée")
        else:
            print_error("Méthode create_file NON TROUVÉE")
else:
    print_error("Fichier file_creator.py manquant !")

# 3.2 Vérifier agent_manager.py
print("\n   📄 3.2 agents/agent_manager.py")
file_path = "agents/agent_manager.py"
if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Vérifier les imports
        checks = {
            "FileCreatorAgent": "Import de FileCreatorAgent",
            "FileReaderAgent": "Import de FileReaderAgent",
            "LLMAgent": "Import de LLMAgent",
            "FileCreatorWrapper": "Classe FileCreatorWrapper",
            "FileReaderWrapper": "Classe FileReaderWrapper",
            "AgentManager": "Classe AgentManager",
        }
        
        for check, desc in checks.items():
            if check in content:
                print_ok(f"{desc} trouvé")
                # Trouver la ligne
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if check in line and "class" in line or "from" in line or "import" in line:
                        print_info(f"   Ligne {i+1}: {line.strip()[:80]}...")
                        break
            else:
                print_error(f"{desc} NON TROUVÉ")
else:
    print_error("Fichier agent_manager.py manquant !")

# =============================================
# 4. TESTS D'IMPORT
# =============================================
print("\n📦 4. TESTS D'IMPORT")
print("-" * 50)

def test_import(module_name, class_name):
    print(f"\n   → Test: {class_name} depuis {module_name}")
    try:
        exec(f"from {module_name} import {class_name}")
        print_ok(f"Import de {class_name} réussi")
        return True
    except ImportError as e:
        print_error(f"ImportError: {e}")
        # Afficher la trace complète
        traceback.print_exc()
        return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        traceback.print_exc()
        return False

# Tester les imports
imports_to_test = [
    ("agents.file_creator", "FileCreatorAgent"),
    ("agents.file_reader", "FileReaderAgent"),
    ("agents.llm_agent", "LLMAgent"),
    ("agents.agent_manager", "AgentManager"),
]

results = {}
for module, class_name in imports_to_test:
    results[f"{module}.{class_name}"] = test_import(module, class_name)

# =============================================
# 5. TEST D'INSTANCIATION
# =============================================
print("\n🏗️ 5. TEST D'INSTANCIATION")
print("-" * 50)

# 5.1 Test FileCreatorAgent
print("\n   → 5.1 FileCreatorAgent")
try:
    from agents.file_creator import FileCreatorAgent
    creator = FileCreatorAgent()
    print_ok("FileCreatorAgent instancié avec succès")
    
    # Tester create_file
    result = creator.create_file("Test de contenu", "test_debug", "txt")
    if result.get('success'):
        print_ok(f"Fichier créé: {result.get('filename')}")
    else:
        print_error(f"Erreur création: {result.get('error')}")
        
except Exception as e:
    print_error(f"Erreur: {e}")
    traceback.print_exc()

# 5.2 Test AgentManager
print("\n   → 5.2 AgentManager")
try:
    from agents.agent_manager import AgentManager
    manager = AgentManager()
    print_ok("AgentManager instancié avec succès")
    
    # Lister les agents disponibles
    agents = list(manager.agents.keys())
    print_info(f"Agents disponibles: {', '.join(agents)}")
    
    # Vérifier filecreator
    if 'filecreator' in agents:
        print_ok("Agent filecreator trouvé")
        
        # Tester l'agent filecreator
        agent = manager.get_agent('filecreator')
        if agent:
            print_ok("Agent filecreator récupéré")
        else:
            print_error("Agent filecreator est None")
    else:
        print_error("Agent filecreator NON trouvé dans la liste")
        
except Exception as e:
    print_error(f"Erreur: {e}")
    traceback.print_exc()

# =============================================
# 6. TEST COMPLET AVEC MESSAGE
# =============================================
print("\n🧪 6. TEST COMPLET AVEC MESSAGE")
print("-" * 50)

try:
    from agents.agent_manager import AgentManager
    manager = AgentManager()
    agent = manager.get_agent('filecreator')
    
    if agent:
        print_info("Envoi d'un message test...")
        message = "Crée un fichier CSV avec: Jean, 32, Paris"
        response = agent.process(message, [])
        print(f"\n   Réponse reçue:\n   {response[:200]}...")
        print_ok("Test réussi !")
    else:
        print_error("Impossible de récupérer l'agent filecreator")
        
except Exception as e:
    print_error(f"Erreur lors du test: {e}")
    traceback.print_exc()

# =============================================
# 7. DIAGNOSTIC FINAL
# =============================================
print("\n" + "=" * 70)
print("📊 7. DIAGNOSTIC FINAL")
print("=" * 70)

print("\n   ✅ RÉUSSIS:")
print("   " + "-" * 40)

# Identifier les problèmes
issues = []

if not os.path.exists("agents/file_creator.py"):
    issues.append("❌ agents/file_creator.py manquant")
elif "class FileCreatorAgent" not in open("agents/file_creator.py").read():
    issues.append("❌ class FileCreatorAgent non trouvée dans file_creator.py")
    
if not os.path.exists("agents/agent_manager.py"):
    issues.append("❌ agents/agent_manager.py manquant")
else:
    content = open("agents/agent_manager.py").read()
    if "FileCreatorWrapper" not in content:
        issues.append("❌ FileCreatorWrapper non trouvé dans agent_manager.py")
    if "filecreator" not in content:
        issues.append("❌ 'filecreator' non trouvé dans le dictionnaire agents")

# Afficher les succès
if not issues:
    print_ok("✅ Tous les tests sont passés !")
else:
    print_warning("Problèmes détectés:")
    for issue in issues:
        print_error(issue)

# =============================================
# 8. RECOMMANDATIONS
# =============================================
print("\n💡 8. RECOMMANDATIONS")
print("-" * 50)

if not os.path.exists("agents/file_creator.py"):
    print("   ➤ Créer agents/file_creator.py avec la classe FileCreatorAgent")
if "FileCreatorWrapper" not in open("agents/agent_manager.py").read() if os.path.exists("agents/agent_manager.py") else "":
    print("   ➤ Ajouter la classe FileCreatorWrapper dans agents/agent_manager.py")
if "filecreator" not in open("agents/agent_manager.py").read() if os.path.exists("agents/agent_manager.py") else "":
    print("   ➤ Ajouter 'filecreator' dans le dictionnaire self.agents")

print("\n" + "=" * 70)
print("✅ DIAGNOSTIC TERMINÉ")
print("=" * 70)