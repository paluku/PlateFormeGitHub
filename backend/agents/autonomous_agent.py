# agents/autonomous_agent.py

import os
import json
import re
import time
import base64
import requests
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    PYAUTOGUI_OK = True
except ImportError:
    PYAUTOGUI_OK = False

try:
    import pygetwindow as gw
    PYGETWINDOW_OK = True
except ImportError:
    PYGETWINDOW_OK = False
    print("⚠️ pygetwindow non installé. Exécute: python -m pip install pygetwindow")


class AutonomousAgent:
    """
    Agent autonome : reçoit un objectif et exécute tout seul les actions.
    """
    
    def __init__(self, ollama_url='http://localhost:11434'):
        self.ollama_url = ollama_url
        self.model = 'llama3.2:latest'
        self.vision_model = 'llava:latest'
        self.max_steps = 15
        self.execution_log = []
        
        print(f"🤖 AutonomousAgent initialisé")
        print(f"🧠 Modèle texte: {self.model}")
        print(f"👁️ Modèle vision: {self.vision_model}")
        print(f"🪟 pygetwindow: {'✅' if PYGETWINDOW_OK else '❌'}")
        print(f"🖱️ pyautogui: {'✅' if PYAUTOGUI_OK else '❌'}")
    
    # ============================================
    # 1. GÉNÉRER UN PLAN
    # ============================================
    def generate_plan(self, objective: str) -> Dict:
        """Demande à Ollama de générer un plan d'actions."""
        try:
            objective_lower = objective.lower()
            
            content_keywords = [
                'lettre', 'poème', 'poeme', 'texte', 'message', 'email',
                'écris', 'ecris', 'rédige', 'redige', 'génère', 'genere',
                'note', 'rapport', 'article', 'récit', 'recit'
            ]
            
            web_keywords = ['google', 'cherche', 'recherche', 'navigue', 'va sur', 'site', 'url', 'http']
            
            price_keywords = ['compare', 'comparaison', 'prix', 'price', 'combien', 'coûte', 'coute']
            
            is_web = any(kw in objective_lower for kw in web_keywords)
            is_price = any(kw in objective_lower for kw in price_keywords)
            needs_content = any(kw in objective_lower for kw in content_keywords)
            
            if is_price:
                print("📊 Comparaison de prix détectée")
                return self._generate_price_plan(objective)
            
            if needs_content and not is_web:
                print("📝 Génération du CONTENU détectée")
                return self._generate_plan_with_content(objective)
            
            return self._generate_simple_plan(objective)
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ============================================
    # PLAN DE COMPARAISON DE PRIX
    # ============================================
    def _generate_price_plan(self, objective: str) -> Dict:
        """Génère un plan pour comparer les prix"""
        try:
            product = self._extract_product(objective)
            
            if not product:
                return {'success': False, 'error': 'Produit non identifié'}
            
            print(f"🛒 Produit détecté: {product}")
            
            plan = [
                {"action": "compare_prices", "product": product}
            ]
            
            return {
                'success': True,
                'objective': objective,
                'plan': plan,
                'steps': len(plan),
                'source': 'price_compare'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _extract_product(self, objective: str) -> str:
        """Extrait le nom du produit de l'objectif"""
        patterns = [
            r'(?:prix|compare|comparaison)\s+(?:de|du|d\'|la|le|des)?\s*["\']?([^"\']+?)["\']?\s*(?:sur|$|\.)',
            r'(?:combien|coûte|coute)\s+(?:le|la|les|un|une)?\s*["\']?([^"\']+?)["\']?\s*(?:\?|$)',
            r'(?:prix)\s+["\']?([^"\']+?)["\']?\s*(?:sur|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, objective, re.IGNORECASE)
            if match:
                product = match.group(1).strip()
                product = product.replace(' sur Google', '').replace(' sur internet', '')
                product = product.replace('  ', ' ').strip()
                if product and len(product) > 2:
                    return product
        
        words = objective.split()
        for i, word in enumerate(words):
            if word.lower() in ['prix', 'compare', 'combien']:
                if i + 1 < len(words):
                    return ' '.join(words[i+1:]).strip('"?')
        
        return None
    
    # ============================================
    # PLAN AVEC CONTENU PERSONNALISÉ
    # ============================================
    def _generate_plan_with_content(self, objective: str) -> Dict:
        """Génère un plan avec du contenu personnalisé."""
        try:
            print(f"📝 ÉTAPE 1 : Génération du contenu...")
            
            content_prompt = f"""Génère le contenu demandé dans l'objectif suivant :

"{objective}"

INSTRUCTIONS :
- Écris le contenu complet (pas juste un résumé)
- Sois professionnel et complet
- Ne mets PAS de JSON, juste le texte brut
- N'ajoute pas de commentaires, juste le contenu

Réponds UNIQUEMENT avec le texte à écrire."""

            content_response = requests.post(
                f'{self.ollama_url}/api/generate',
                json={
                    'model': self.model,
                    'prompt': content_prompt,
                    'stream': False,
                    'options': {'temperature': 0.7, 'num_predict': 2000}
                },
                timeout=120
            )
            
            if content_response.status_code != 200:
                return {'success': False, 'error': 'Erreur génération contenu'}
            
            generated_content = content_response.json().get('response', '').strip()
            print(f"📄 Contenu généré ({len(generated_content)} caractères)")
            
            app = 'notepad'
            
            plan = [
                {"action": "open_app", "app": app},
                {"action": "wait", "seconds": 2},
                {"action": "write_text", "text": generated_content}
            ]
            
            if 'entrée' in objective.lower() or 'enter' in objective.lower():
                plan.append({"action": "press_key", "key": "enter"})
            
            if 'capture' in objective.lower() or 'screenshot' in objective.lower():
                plan.append({"action": "screenshot"})
            
            return {
                'success': True,
                'objective': objective,
                'plan': plan,
                'steps': len(plan),
                'content_preview': generated_content[:200],
                'source': 'ollama+content'
            }
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return self._generate_simple_plan(objective)
    
    # ============================================
    # PLAN SIMPLE
    # ============================================
    def _generate_simple_plan(self, objective: str) -> Dict:
        """Génère un plan simple avec Ollama"""
        try:
            prompt = f"""Tu es un générateur de plan JSON.

OBJECTIF : {objective}

Tu dois produire un tableau JSON d'actions.

ACTIONS DISPONIBLES :
- open_app : ouvrir une application (app = "notepad", "chrome", "calculator")
- navigate_to : ouvrir une URL (url = "https://...")
- search_google : rechercher sur Google (query = "mots clés")
- compare_prices : comparer les prix d'un produit (product = "nom du produit")
- write_text : écrire du texte (text = "...")
- press_key : appuyer sur une touche (key = "enter", "tab", "esc")
- wait : attendre (seconds = 2)
- screenshot : faire une capture d'écran

EXEMPLES :

Objectif: "Compare le prix de l'iPhone 15"
[{{"action":"compare_prices","product":"iPhone 15"}}]

Objectif: "Cherche "prix iPhone 15" sur Google"
[{{"action":"open_app","app":"chrome"}},{{"action":"wait","seconds":2}},{{"action":"search_google","query":"prix iPhone 15"}},{{"action":"wait","seconds":5}},{{"action":"screenshot"}}]

Objectif: "Ouvre Notepad"
[{{"action":"open_app","app":"notepad"}},{{"action":"wait","seconds":2}}]

Objectif: "Va sur youtube.com"
[{{"action":"open_app","app":"chrome"}},{{"action":"wait","seconds":2}},{{"action":"navigate_to","url":"https://youtube.com"}},{{"action":"wait","seconds":5}}]

Maintenant, génère le plan pour :
{objective}

Réponds UNIQUEMENT avec le tableau JSON."""

            response = requests.post(
                f'{self.ollama_url}/api/generate',
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {'temperature': 0.1}
                },
                timeout=60
            )
            
            if response.status_code != 200:
                return {'success': False, 'error': 'Erreur Ollama'}
            
            response_text = response.json().get('response', '')
            plan = self._parse_plan(response_text)
            
            if not plan:
                plan = self._fallback_plan(objective)
            
            if not plan:
                return {'success': False, 'error': 'Impossible de parser le plan'}
            
            return {
                'success': True,
                'objective': objective,
                'plan': plan,
                'steps': len(plan),
                'source': 'ollama'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ============================================
    # PARSER LE PLAN
    # ============================================
    def _parse_plan(self, response_text: str) -> List[Dict]:
        """Parse la réponse d'Ollama"""
        if not response_text:
            return []
        
        text = response_text.strip()
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        text = text.strip()
        
        try:
            plan = json.loads(text)
            if isinstance(plan, list) and len(plan) > 0:
                return self._validate_plan(plan)
        except json.JSONDecodeError:
            pass
        
        json_match = re.search(r'\[[\s\S]*?\]', text)
        if json_match:
            try:
                plan = json.loads(json_match.group())
                if isinstance(plan, list) and len(plan) > 0:
                    return self._validate_plan(plan)
            except json.JSONDecodeError:
                pass
        
        objects = re.findall(r'\{[^{}]+\}', text)
        if objects:
            plan = []
            for obj_str in objects:
                try:
                    obj = json.loads(obj_str)
                    if isinstance(obj, dict) and 'action' in obj:
                        plan.append(obj)
                except json.JSONDecodeError:
                    continue
            if plan:
                return self._validate_plan(plan)
        
        return self._manual_parse(text)
    
    def _validate_plan(self, plan: List) -> List[Dict]:
        """Valide et nettoie un plan"""
        valid_actions = [
            'open_app', 'write_text', 'press_key', 'wait', 'screenshot',
            'navigate_to', 'search_google',
            'compare_prices', 'analyze_screen',
            'move_mouse', 'click'
        ]
        
        valid_plan = []
        for action in plan:
            if not isinstance(action, dict):
                continue
            if 'action' not in action:
                continue
            if action['action'] not in valid_actions:
                continue
            valid_plan.append(action)
        
        return valid_plan
    
    def _manual_parse(self, text: str) -> List[Dict]:
        """Parse manuel"""
        plan = []
        text_lower = text.lower()
        
        if 'compare' in text_lower or 'prix' in text_lower:
            product = self._extract_product(text)
            if product:
                plan.append({"action": "compare_prices", "product": product})
                return plan
        
        if 'google' in text_lower and 'cherche' in text_lower:
            match = re.search(r'cherche\s+"?([^"]+)"?', text, re.IGNORECASE)
            query = match.group(1) if match else 'test'
            plan.append({"action": "open_app", "app": "chrome"})
            plan.append({"action": "wait", "seconds": 2})
            plan.append({"action": "search_google", "query": query.strip()})
            return plan
        
        if 'notepad' in text_lower:
            plan.append({"action": "open_app", "app": "notepad"})
            plan.append({"action": "wait", "seconds": 2})
        elif 'calculator' in text_lower or 'calculatrice' in text_lower:
            plan.append({"action": "open_app", "app": "calculator"})
            plan.append({"action": "wait", "seconds": 2})
        
        if 'capture' in text_lower or 'screenshot' in text_lower:
            plan.append({"action": "screenshot"})
        
        return plan
    
    # ============================================
    # FALLBACK
    # ============================================
    def _fallback_plan(self, objective: str) -> List[Dict]:
        """Plan de secours"""
        print(f"🆘 Plan de secours pour: {objective}")
        
        plan = []
        objective_lower = objective.lower()
        
        price_keywords = ['compare', 'comparaison', 'prix', 'price', 'combien', 'coûte', 'coute']
        if any(kw in objective_lower for kw in price_keywords):
            product = self._extract_product(objective)
            if product:
                plan.append({"action": "compare_prices", "product": product})
                return plan
        
        if 'google' in objective_lower or 'cherche' in objective_lower or 'recherche' in objective_lower:
            match = re.search(r'(?:cherche|recherche)\s+"?([^"]+?)"?(?:\s+sur|\s*$)', objective, re.IGNORECASE)
            if not match:
                match = re.search(r'(?:cherche|recherche)\s+(.+)', objective, re.IGNORECASE)
            
            query = match.group(1).strip() if match else 'test'
            query = query.replace(' sur Google', '').replace(' sur google', '')
            
            plan.append({"action": "open_app", "app": "chrome"})
            plan.append({"action": "wait", "seconds": 2})
            plan.append({"action": "search_google", "query": query})
            plan.append({"action": "wait", "seconds": 5})
            
            if 'capture' in objective_lower:
                plan.append({"action": "screenshot"})
            
            return plan
        
        if '.com' in objective_lower or '.fr' in objective_lower or 'http' in objective_lower:
            url_match = re.search(r'(https?://[^\s]+|www\.[^\s]+|[\w-]+\.(?:com|fr|org|net))', objective)
            if url_match:
                plan.append({"action": "open_app", "app": "chrome"})
                plan.append({"action": "wait", "seconds": 2})
                plan.append({"action": "navigate_to", "url": url_match.group(1)})
                plan.append({"action": "wait", "seconds": 5})
                return plan
        
        if 'notepad' in objective_lower:
            plan.append({"action": "open_app", "app": "notepad"})
            plan.append({"action": "wait", "seconds": 2})
        elif 'calculatrice' in objective_lower or 'calculator' in objective_lower:
            plan.append({"action": "open_app", "app": "calculator"})
            plan.append({"action": "wait", "seconds": 2})
        
        if 'capture' in objective_lower:
            plan.append({"action": "screenshot"})
        
        return plan
    
    # ============================================
    # 2. EXÉCUTER UN PLAN
    # ============================================
    def execute_plan(self, plan: List[Dict], objective: str = '') -> Dict:
        """Exécute un plan étape par étape."""
        results = []
        success_count = 0
        error_count = 0
        
        print(f"\n{'='*60}")
        print(f"🚀 EXÉCUTION DU PLAN ({len(plan)} étapes)")
        print(f"🎯 Objectif: {objective}")
        print(f"{'='*60}\n")
        
        for i, action in enumerate(plan, 1):
            action_type = action.get('action', 'unknown')
            print(f"\n📌 Étape {i}/{len(plan)}: {action_type}")
            
            try:
                result = self._execute_action(action)
                result['step'] = i
                result['action_type'] = action_type
                results.append(result)
                
                if result.get('success'):
                    success_count += 1
                    print(f"   ✅ Réussi")
                else:
                    error_count += 1
                    print(f"   ❌ Échec: {result.get('error', 'Erreur inconnue')}")
                    
                    if action_type not in ['screenshot']:
                        print(f"   ⚠️ Arrêt du plan")
                        break
                        
            except Exception as e:
                error_count += 1
                results.append({
                    'step': i,
                    'action_type': action_type,
                    'success': False,
                    'error': str(e)
                })
                print(f"   ❌ Exception: {e}")
                break
        
        print(f"\n{'='*60}")
        print(f"📊 RÉSULTAT: {success_count}/{len(plan)} actions réussies")
        print(f"{'='*60}\n")
        
        return {
            'success': error_count == 0,
            'objective': objective,
            'total_steps': len(plan),
            'success_count': success_count,
            'error_count': error_count,
            'results': results
        }
    
    # ============================================
    # 3. EXÉCUTER UNE ACTION
    # ============================================
    def _execute_action(self, action: Dict) -> Dict:
        """Exécute une action"""
        action_type = action.get('action')
        
        if action_type == 'open_app':
            return self._do_open_app(action.get('app'))
        elif action_type == 'write_text':
            return self._do_write_text(action.get('text', ''))
        elif action_type == 'press_key':
            return self._do_press_key(action.get('key', 'enter'))
        elif action_type == 'wait':
            return self._do_wait(action.get('seconds', 1))
        elif action_type == 'screenshot':
            return self._do_screenshot()
        elif action_type == 'navigate_to':
            return self._do_navigate_to(action.get('url', ''))
        elif action_type == 'search_google':
            return self._do_search_google(action.get('query', ''))
        elif action_type == 'compare_prices':
            return self._do_compare_prices(action.get('product', ''))
        elif action_type == 'analyze_screen':
            return self._do_analyze_screen(action.get('question'))
        elif action_type == 'move_mouse':
            return self._do_move_mouse(action.get('x', 0), action.get('y', 0))
        elif action_type == 'click':
            return self._do_click(action.get('x'), action.get('y'),
                                 action.get('button', 'left'))
        else:
            return {'success': False, 'error': f'Action inconnue: {action_type}'}
    
    # ============================================
    # FORCER LE FOCUS
    # ============================================
    def _force_focus(self, app_name: str, max_attempts: int = 5) -> bool:
        """Force le focus sur une fenêtre"""
        if not PYGETWINDOW_OK:
            return False
        
        window_titles = {
            'notepad': ['Bloc-notes', 'Notepad', 'Sans titre', 'Untitled'],
            'calculator': ['Calculatrice', 'Calculator'],
            'explorer': ['Explorateur', 'File Explorer', 'Ce PC'],
            'cmd': ['Invite de commandes', 'Command Prompt', 'cmd.exe'],
            'chrome': ['Chrome', 'Google Chrome', 'Nouvel onglet', 'New Tab'],
            'firefox': ['Firefox', 'Mozilla Firefox'],
            'paint': ['Paint', 'mspaint']
        }
        
        titles = window_titles.get(app_name, [])
        
        if not titles:
            return False
        
        for attempt in range(max_attempts):
            for title in titles:
                try:
                    windows = gw.getWindowsWithTitle(title)
                    if windows:
                        window = windows[0]
                        if window.isMinimized:
                            window.restore()
                            time.sleep(0.3)
                        try:
                            window.activate()
                        except:
                            pyautogui.hotkey('alt', 'tab')
                            time.sleep(0.3)
                        time.sleep(0.5)
                        print(f"   🎯 Focus sur: {window.title}")
                        return True
                except:
                    continue
            time.sleep(0.8)
        
        return False
    
    # ============================================
    # ACTIONS DE BASE
    # ============================================
    def _do_open_app(self, app_name: str) -> Dict:
        """Ouvre une application"""
        if not app_name:
            return {'success': False, 'error': 'Nom requis'}
        
        try:
            import subprocess
            import platform
            
            app_name_lower = app_name.lower().strip()
            os_type = platform.system().lower()
            
            apps = {
                'notepad': {'windows': 'notepad.exe', 'mac': 'open -a TextEdit', 'linux': 'gedit'},
                'calculator': {'windows': 'calc.exe', 'mac': 'open -a Calculator', 'linux': 'gnome-calculator'},
                'explorer': {'windows': 'explorer.exe', 'mac': 'open .', 'linux': 'nautilus'},
                'chrome': {'windows': 'chrome.exe', 'mac': 'open -a "Google Chrome"', 'linux': 'google-chrome'},
                'firefox': {'windows': 'firefox.exe', 'mac': 'open -a Firefox', 'linux': 'firefox'},
                'cmd': {'windows': 'cmd.exe', 'mac': 'open -a Terminal', 'linux': 'xterm'},
                'paint': {'windows': 'mspaint.exe', 'mac': None, 'linux': None}
            }
            
            if app_name_lower not in apps:
                return {'success': False, 'error': f'App non autorisée: {app_name}'}
            
            if 'win' in os_type:
                cmd = apps[app_name_lower]['windows']
            elif 'darwin' in os_type or 'mac' in os_type:
                cmd = apps[app_name_lower]['mac']
            else:
                cmd = apps[app_name_lower]['linux']
            
            if not cmd:
                return {'success': False, 'error': 'App non supportée'}
            
            subprocess.Popen(cmd, shell=True)
            print(f"   🚀 {app_name} lancé")
            
            time.sleep(2)
            self._force_focus(app_name_lower)
            
            return {'success': True, 'app': app_name}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _do_navigate_to(self, url: str) -> Dict:
        """Ouvre une URL"""
        if not url:
            return {'success': False, 'error': 'URL requise'}
        
        try:
            import subprocess
            import platform
            
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            os_type = platform.system().lower()
            print(f"   🌐 Navigation vers: {url}")
            
            if 'win' in os_type:
                subprocess.Popen(f'start chrome "{url}"', shell=True)
            elif 'darwin' in os_type or 'mac' in os_type:
                subprocess.Popen(f'open -a "Google Chrome" "{url}"', shell=True)
            else:
                subprocess.Popen(f'google-chrome "{url}"', shell=True)
            
            time.sleep(5)
            self._force_focus('chrome')
            
            return {'success': True, 'url': url}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _do_search_google(self, query: str) -> Dict:
        """Recherche Google"""
        if not query:
            return {'success': False, 'error': 'Requête requise'}
        
        try:
            import urllib.parse
            
            encoded_query = urllib.parse.quote(query)
            url = f'https://www.google.com/search?q={encoded_query}'
            
            print(f"   🔍 Recherche Google: {query}")
            
            result = self._do_navigate_to(url)
            if result.get('success'):
                time.sleep(3)
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ============================================
    # 📊 COMPARAISON DE PRIX
    # ============================================
    def _do_compare_prices(self, product: str) -> Dict:
        """Compare les prix d'un produit"""
        if not product:
            return {'success': False, 'error': 'Produit requis'}
        
        try:
            import urllib.parse
            
            print(f"   📊 Comparaison de prix pour: {product}")
            
            encoded = urllib.parse.quote(product)
            url = f'https://www.google.com/search?tbm=shop&q={encoded}'
            
            print(f"   🌐 Ouverture de Google Shopping...")
            nav_result = self._do_navigate_to(url)
            
            if not nav_result.get('success'):
                return nav_result
            
            time.sleep(6)
            
            print(f"   📸 Capture et analyse des résultats...")
            
            question = f"""Analyse cette capture d'écran de résultats Google Shopping pour "{product}".

Extrais les informations suivantes :
1. Les noms des magasins visibles (Amazon, Fnac, Cdiscount, etc.)
2. Les prix associés à chaque magasin
3. Le prix le plus bas trouvé
4. Le prix le plus élevé trouvé

Réponds de manière structurée :
- Magasin 1 : prix
- Magasin 2 : prix
- ...

Prix le plus bas : X€
Prix le plus élevé : Y€"""
            
            analysis_result = self._do_analyze_screen(question)
            
            if not analysis_result.get('success'):
                return analysis_result
            
            analysis = analysis_result.get('analysis', '')
            
            print(f"   📝 Écriture du rapport dans Notepad...")
            
            date_str = datetime.now().strftime('%d/%m/%Y %H:%M')
            
            result_text = f"""RAPPORT DE COMPARAISON DE PRIX
=====================================
Produit : {product}
Date : {date_str}

RÉSULTATS DE LA RECHERCHE :
-------------------------------------
{analysis}

=====================================
Source : Google Shopping
"""
            
            self._do_open_app('notepad')
            time.sleep(2)
            write_result = self._do_write_text(result_text)
            
            return {
                'success': True,
                'product': product,
                'analysis': analysis[:500],
                'written_to_notepad': write_result.get('success', False),
                'screenshot': analysis_result.get('filename')
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ============================================
    # 👁️ ANALYSE D'ÉCRAN
    # ============================================
    def _do_analyze_screen(self, question: str = None) -> Dict:
        """Fait une capture + analyse avec VisionAgent"""
        if not PYAUTOGUI_OK:
            return {'success': False, 'error': 'pyautogui non installé'}
        
        try:
            os.makedirs('screenshots', exist_ok=True)
            filename = f'analyze_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            filepath = os.path.join('screenshots', filename)
            
            img = pyautogui.screenshot()
            img.save(filepath)
            print(f"   📸 Capture: {filename}")
            
            if not question:
                question = """Analyse cette capture d'écran. Extrais TOUTES les informations visibles.
Si tu vois des prix (ex: 999€, 1200€), liste-les avec les produits correspondants.
Sois précis et structuré."""
            
            print(f"   👁️ Analyse avec {self.vision_model}...")
            
            with open(filepath, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            response = requests.post(
                f'{self.ollama_url}/api/generate',
                json={
                    'model': self.vision_model,
                    'prompt': question,
                    'images': [image_data],
                    'stream': False
                },
                timeout=180
            )
            
            if response.status_code != 200:
                return {'success': False, 'error': f'Erreur Ollama: {response.status_code}'}
            
            analysis = response.json().get('response', '')
            print(f"   ✅ Analyse: {analysis[:200]}...")
            
            return {
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'analysis': analysis,
                'question': question
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ============================================
    # AUTRES ACTIONS
    # ============================================
    def _do_write_text(self, text: str) -> Dict:
        """Écrit du texte"""
        if not PYAUTOGUI_OK:
            return {'success': False, 'error': 'pyautogui non installé'}
        
        if not text:
            return {'success': False, 'error': 'Texte vide'}
        
        try:
            clean_text = text.replace('\\n', '\n')
            lines = clean_text.split('\n')
            
            for i, line in enumerate(lines):
                if line:
                    pyautogui.write(line, interval=0.02)
                if i < len(lines) - 1:
                    pyautogui.press('enter')
                    time.sleep(0.05)
            
            print(f"   ✍️ Texte écrit: {clean_text[:50]}...")
            return {'success': True, 'text': clean_text[:100], 'length': len(clean_text)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _do_press_key(self, key: str) -> Dict:
        """Appuie sur une touche"""
        if not PYAUTOGUI_OK:
            return {'success': False, 'error': 'pyautogui non installé'}
        
        try:
            pyautogui.press(key)
            print(f"   ⌨️ Touche pressée: {key}")
            return {'success': True, 'key': key}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _do_wait(self, seconds: float) -> Dict:
        """Attend X secondes"""
        try:
            time.sleep(float(seconds))
            print(f"   ⏱️ Attente de {seconds}s")
            return {'success': True, 'waited': seconds}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _do_screenshot(self) -> Dict:
        """Capture d'écran"""
        if not PYAUTOGUI_OK:
            return {'success': False, 'error': 'pyautogui non installé'}
        
        try:
            os.makedirs('screenshots', exist_ok=True)
            filename = f'auto_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            filepath = os.path.join('screenshots', filename)
            
            img = pyautogui.screenshot()
            img.save(filepath)
            
            print(f"   📸 Capture: {filename}")
            return {'success': True, 'filename': filename, 'filepath': filepath}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _do_move_mouse(self, x: int, y: int) -> Dict:
        """Déplace la souris"""
        if not PYAUTOGUI_OK:
            return {'success': False, 'error': 'pyautogui non installé'}
        
        try:
            pyautogui.moveTo(int(x), int(y), duration=0.5)
            return {'success': True, 'position': {'x': x, 'y': y}}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _do_click(self, x, y, button: str = 'left') -> Dict:
        """Clique"""
        if not PYAUTOGUI_OK:
            return {'success': False, 'error': 'pyautogui non installé'}
        
        try:
            if x is not None and y is not None:
                pyautogui.click(int(x), int(y), button=button)
            else:
                pyautogui.click(button=button)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ============================================
    # 4. MÉTHODE PRINCIPALE
    # ============================================
    
    def run_objective(self, objective: str) -> Dict:
        """Méthode principale"""
        print("=" * 60)
        print("NOUVEL OBJECTIF: " + objective)
        print("=" * 60)
        
        plan_result = self.generate_plan(objective)
        
        if not plan_result.get('success'):
            return {
                'success': False,
                'objective': objective,
                'error': plan_result.get('error'),
                'stage': 'planification'
            }
        
        plan = plan_result['plan']
        print("Plan genere (" + str(len(plan)) + " etapes):")
        for i, action in enumerate(plan, 1):
            print("   " + str(i) + ". " + str(action)[:100])
        
        execution_result = self.execute_plan(plan, objective)
        
        return {
            'success': execution_result['success'],
            'objective': objective,
            'plan': plan,
            'execution': execution_result,
            'message': "OK: " + str(execution_result['success_count']) + "/" + str(execution_result['total_steps']) + " actions reussies"
        }