import json
import re
import time
import os
import subprocess

import pyautogui


class ComputerAgent:
    """
    Agent de contrôle de l'ordinateur Windows.

    Fonctionnement :

        utilisateur
            ↓
        ComputerAgent
            ↓
        LLMAgent (Ollama)
            ↓
        action JSON
            ↓
        validation
            ↓
        exécution Windows / PyAutoGUI

    IMPORTANT :
    - Le LLM ne peut pas exécuter directement une commande système.
    - Les actions disponibles sont limitées à TOOL_HANDLERS.
    - Les applications pouvant être ouvertes sont limitées à ALLOWED_APPS.
    """

    def __init__(self, llm_agent):
        self.llm_agent = llm_agent

        # Outils disponibles pour l'IA
        self.tool_handlers = {
            "open_app": self.open_app,
            "click": self.click,
            "move_mouse": self.move_mouse,
            "type_text": self.type_text,
            "press_key": self.press_key,
            "hotkey": self.hotkey,
            "screenshot": self.screenshot,
            "wait": self.wait,
            "get_mouse_position": self.get_mouse_position,
            "get_screen_size": self.get_screen_size,
        }

        # Applications Windows autorisées.
        #
        # On commence volontairement avec quelques applications
        # simples et sûres.
        self.allowed_apps = {
            "notepad": ["notepad.exe"],
            "bloc-notes": ["notepad.exe"],
            "calculatrice": ["calc.exe"],
            "calculator": ["calc.exe"],
            "paint": ["mspaint.exe"],
            "wordpad": ["write.exe"],
        }

        # Dossier des captures
        self.screenshot_dir = os.path.join(
            os.getcwd(),
            "uploads",
            "computer"
        )

        os.makedirs(self.screenshot_dir, exist_ok=True)

    # =========================================================
    # PROMPT
    # =========================================================

    def _build_prompt(self, message, history=None):
        """
        Construit le prompt envoyé au LLMAgent.

        Le modèle doit retourner UNIQUEMENT du JSON.
        """

        tools_description = """
OUTILS DISPONIBLES :

1. open_app
Ouvre une application autorisée.

Format :
{
  "action": "open_app",
  "args": {
    "name": "notepad"
  }
}

Applications autorisées :
- notepad
- bloc-notes
- calculator
- calculatrice
- paint
- wordpad


2. click
Clique à une position de l'écran.

Format :
{
  "action": "click",
  "args": {
    "x": 500,
    "y": 300
  }
}


3. move_mouse
Déplace la souris.

Format :
{
  "action": "move_mouse",
  "args": {
    "x": 500,
    "y": 300
  }
}


4. type_text
Écrit du texte avec le clavier.

Format :
{
  "action": "type_text",
  "args": {
    "text": "Bonjour"
  }
}


5. press_key
Appuie sur une touche.

Exemple :
{
  "action": "press_key",
  "args": {
    "key": "enter"
  }
}

Touches courantes :
enter, esc, tab, space, backspace, delete,
up, down, left, right,
home, end,
pageup, pagedown,
f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12


6. hotkey
Appuie simultanément sur plusieurs touches.

Exemple :
{
  "action": "hotkey",
  "args": {
    "keys": ["ctrl", "s"]
  }
}


7. screenshot
Effectue une capture de l'écran.

Format :
{
  "action": "screenshot",
  "args": {}
}


8. wait
Attend quelques secondes.

Format :
{
  "action": "wait",
  "args": {
    "seconds": 2
  }
}


9. get_mouse_position
Retourne la position actuelle de la souris.

Format :
{
  "action": "get_mouse_position",
  "args": {}
}


10. get_screen_size
Retourne la résolution de l'écran.

Format :
{
  "action": "get_screen_size",
  "args": {}
}
"""

        history_text = ""

        if history:
            history_text = "\nHISTORIQUE RÉCENT :\n"

            for item in history[-5:]:
                if isinstance(item, dict):
                    role = item.get("role", "")
                    content = item.get("content", "")

                    if role and content:
                        history_text += (
                            f"{role}: {content}\n"
                        )
                else:
                    history_text += f"{item}\n"

        prompt = f"""
Tu es ComputerAgent, un agent spécialisé dans le contrôle
d'un ordinateur Windows.

Tu dois transformer la demande de l'utilisateur en UNE action
informatique.

{tools_description}

RÈGLES IMPORTANTES :

1. Retourne UNIQUEMENT un objet JSON valide.
2. N'écris aucune explication avant ou après le JSON.
3. Utilise uniquement les actions disponibles.
4. N'invente jamais une action.
5. N'exécute jamais de commande PowerShell.
6. N'exécute jamais de commande CMD.
7. Ne fournis jamais de code Python à exécuter.
8. Pour ouvrir une application, utilise open_app.
9. Pour écrire du texte, utilise type_text.
10. Pour appuyer sur une touche, utilise press_key.
11. Pour plusieurs touches simultanées, utilise hotkey.
12. Si une information nécessaire manque, retourne une action
    "error" avec une explication courte.
13. Une seule action doit être retournée à la fois.

{history_text}

DEMANDE UTILISATEUR :
{message}

Réponds uniquement avec le JSON correspondant à la prochaine action.
"""

        return prompt

    # =========================================================
    # PROCESS PRINCIPAL
    # =========================================================

    def process(self, message, history=None):
        """
        Point d'entrée utilisé par AgentManager.

        Compatible avec :
            agent.process(message, history)
        """

        if not message or not message.strip():
            return "Je n'ai reçu aucune commande."

        prompt = self._build_prompt(
            message=message,
            history=history
        )

        try:
            # On utilise ton LLMAgent existant.
            response = self.llm_agent.process(
                prompt,
                agent_type="assistant",
                history=None
            )

        except Exception as e:
            return f"Erreur de communication avec Ollama : {e}"

        action = self._parse_action(response)

        if not action:
            return (
                "Je n'ai pas réussi à interpréter la réponse "
                "du modèle comme une action informatique."
            )

        result = self.execute_action(action)

        return self._format_result(result)

    # =========================================================
    # PARSING JSON
    # =========================================================

    def _parse_action(self, response):
        """
        Extrait un JSON depuis la réponse d'Ollama.

        Gère également le cas où le modèle met le JSON
        dans un bloc ```json ... ```.
        """

        if not response:
            return None

        response = response.strip()

        # Cas :
        # ```json
        # {...}
        # ```
        code_match = re.search(
            r"```(?:json)?\s*(.*?)\s*```",
            response,
            re.DOTALL | re.IGNORECASE
        )

        if code_match:
            response = code_match.group(1).strip()

        # Tentative directe
        try:
            data = json.loads(response)

            if isinstance(data, dict):
                return data

        except json.JSONDecodeError:
            pass

        # Recherche du premier objet JSON
        start = response.find("{")
        end = response.rfind("}")

        if start != -1 and end != -1 and end > start:
            candidate = response[start:end + 1]

            try:
                data = json.loads(candidate)

                if isinstance(data, dict):
                    return data

            except json.JSONDecodeError:
                pass

        return None

    # =========================================================
    # VALIDATION
    # =========================================================

    def _validate_action(self, action):
        """
        Vérifie que l'action est autorisée avant exécution.
        """

        if not isinstance(action, dict):
            return False, "L'action n'est pas un objet JSON."

        action_name = action.get("action")

        if not action_name:
            return False, "L'action ne contient pas de champ 'action'."

        if action_name not in self.tool_handlers:
            return False, (
                f"Action non autorisée : {action_name}"
            )

        args = action.get("args", {})

        if args is None:
            args = {}

        if not isinstance(args, dict):
            return False, "Le champ 'args' doit être un objet JSON."

        # -----------------------------------------------------
        # Validation spécifique open_app
        # -----------------------------------------------------

        if action_name == "open_app":

            name = args.get("name")

            if not name:
                return False, "Nom de l'application manquant."

            name = str(name).lower().strip()

            if name not in self.allowed_apps:
                return False, (
                    f"Application non autorisée : {name}"
                )

        # -----------------------------------------------------
        # Validation click
        # -----------------------------------------------------

        if action_name in ["click", "move_mouse"]:

            if "x" not in args or "y" not in args:
                return False, (
                    "Les coordonnées x et y sont obligatoires."
                )

            try:
                x = int(args["x"])
                y = int(args["y"])
            except (ValueError, TypeError):
                return False, "Les coordonnées doivent être numériques."

            screen_width, screen_height = pyautogui.size()

            if x < 0 or x >= screen_width:
                return False, "Coordonnée X hors écran."

            if y < 0 or y >= screen_height:
                return False, "Coordonnée Y hors écran."

        # -----------------------------------------------------
        # Validation type_text
        # -----------------------------------------------------

        if action_name == "type_text":

            if "text" not in args:
                return False, "Texte manquant."

            text = str(args["text"])

            # Limite de sécurité
            if len(text) > 5000:
                return False, (
                    "Le texte est trop long "
                    "(maximum 5000 caractères)."
                )

        # -----------------------------------------------------
        # Validation press_key
        # -----------------------------------------------------

        if action_name == "press_key":

            key = args.get("key")

            if not key:
                return False, "Touche manquante."

            allowed_keys = {
                "enter",
                "esc",
                "tab",
                "space",
                "backspace",
                "delete",
                "up",
                "down",
                "left",
                "right",
                "home",
                "end",
                "pageup",
                "pagedown",
                "insert",
                "shift",
                "ctrl",
                "alt",
                "win",
                "capslock",
                "numlock",
                "f1",
                "f2",
                "f3",
                "f4",
                "f5",
                "f6",
                "f7",
                "f8",
                "f9",
                "f10",
                "f11",
                "f12",
            }

            if str(key).lower() not in allowed_keys:
                return False, (
                    f"Touche non autorisée : {key}"
                )

        # -----------------------------------------------------
        # Validation hotkey
        # -----------------------------------------------------

        if action_name == "hotkey":

            keys = args.get("keys")

            if not isinstance(keys, list):
                return False, (
                    "Le champ keys doit être une liste."
                )

            if not keys:
                return False, "Aucune touche indiquée."

            if len(keys) > 4:
                return False, (
                    "Un raccourci ne peut contenir "
                    "que 4 touches maximum."
                )

        # -----------------------------------------------------
        # Validation wait
        # -----------------------------------------------------

        if action_name == "wait":

            seconds = args.get("seconds", 1)

            try:
                seconds = float(seconds)
            except (ValueError, TypeError):
                return False, "Durée invalide."

            if seconds < 0 or seconds > 10:
                return False, (
                    "La durée doit être comprise entre 0 et 10 secondes."
                )

        return True, None

    # =========================================================
    # EXECUTION
    # =========================================================

    def execute_action(self, action):
        """
        Valide puis exécute une action.
        """

        valid, error = self._validate_action(action)

        if not valid:
            return {
                "success": False,
                "error": error
            }

        action_name = action["action"]
        args = action.get("args", {})

        try:
            handler = self.tool_handlers[action_name]

            result = handler(**args)

            return result

        except TypeError as e:
            return {
                "success": False,
                "error": f"Arguments invalides : {e}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # =========================================================
    # OUTILS WINDOWS
    # =========================================================

    def open_app(self, name):
        """
        Ouvre une application Windows autorisée.
        """

        name = str(name).lower().strip()

        if name not in self.allowed_apps:
            return {
                "success": False,
                "error": f"Application non autorisée : {name}"
            }

        command = self.allowed_apps[name]

        try:
            subprocess.Popen(
                command,
                shell=False
            )

            # Petite attente pour laisser Windows lancer l'application
            time.sleep(1)

            return {
                "success": True,
                "action": "open_app",
                "app": name,
                "message": f"{name} a été ouvert."
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def click(self, x, y):
        """
        Clique à l'écran.
        """

        pyautogui.click(
            int(x),
            int(y)
        )

        return {
            "success": True,
            "action": "click",
            "x": int(x),
            "y": int(y)
        }

    def move_mouse(self, x, y):
        """
        Déplace la souris.
        """

        pyautogui.moveTo(
            int(x),
            int(y),
            duration=0.2
        )

        return {
            "success": True,
            "action": "move_mouse",
            "x": int(x),
            "y": int(y)
        }

    def type_text(self, text):
        """
        Écrit du texte avec PyAutoGUI.
        """

        text = str(text)

        pyautogui.write(
            text,
            interval=0.02
        )

        return {
            "success": True,
            "action": "type_text",
            "characters": len(text)
        }

    def press_key(self, key):
        """
        Appuie sur une touche.
        """

        key = str(key).lower()

        pyautogui.press(key)

        return {
            "success": True,
            "action": "press_key",
            "key": key
        }

    def hotkey(self, keys):
        """
        Appuie simultanément sur plusieurs touches.
        """

        keys = [
            str(key).lower()
            for key in keys
        ]

        pyautogui.hotkey(*keys)

        return {
            "success": True,
            "action": "hotkey",
            "keys": keys
        }

    def screenshot(self):
        """
        Capture l'écran complet.
        """

        timestamp = time.strftime(
            "%Y%m%d_%H%M%S"
        )

        filename = f"screen_{timestamp}.png"

        path = os.path.join(
            self.screenshot_dir,
            filename
        )

        image = pyautogui.screenshot()

        image.save(path)

        return {
            "success": True,
            "action": "screenshot",
            "path": path
        }

    def wait(self, seconds=1):
        """
        Attend avant l'action suivante.
        """

        seconds = float(seconds)

        time.sleep(seconds)

        return {
            "success": True,
            "action": "wait",
            "seconds": seconds
        }

    def get_mouse_position(self):
        """
        Retourne la position actuelle de la souris.
        """

        x, y = pyautogui.position()

        return {
            "success": True,
            "action": "get_mouse_position",
            "x": x,
            "y": y
        }

    def get_screen_size(self):
        """
        Retourne la résolution de l'écran.
        """

        width, height = pyautogui.size()

        return {
            "success": True,
            "action": "get_screen_size",
            "width": width,
            "height": height
        }

    # =========================================================
    # FORMATAGE
    # =========================================================

    def _format_result(self, result):
        """
        Transforme le résultat technique en réponse lisible
        pour ton interface HTML.
        """

        if not result:
            return "Action exécutée."

        if result.get("success"):
            action = result.get("action")

            if action == "open_app":
                return result.get(
                    "message",
                    f"Application ouverte : {result.get('app')}"
                )

            if action == "click":
                return (
                    f"Clic effectué en "
                    f"({result.get('x')}, {result.get('y')})."
                )

            if action == "move_mouse":
                return (
                    f"Souris déplacée en "
                    f"({result.get('x')}, {result.get('y')})."
                )

            if action == "type_text":
                return (
                    f"Texte saisi "
                    f"({result.get('characters', 0)} caractères)."
                )

            if action == "press_key":
                return (
                    f"Touche '{result.get('key')}' pressée."
                )

            if action == "hotkey":
                keys = " + ".join(
                    result.get("keys", [])
                )

                return f"Raccourci {keys} exécuté."

            if action == "screenshot":
                return (
                    "Capture d'écran effectuée : "
                    f"{result.get('path')}"
                )

            if action == "wait":
                return (
                    f"Attente de "
                    f"{result.get('seconds')} seconde(s)."
                )

            if action == "get_mouse_position":
                return (
                    f"Position de la souris : "
                    f"({result.get('x')}, {result.get('y')})."
                )

            if action == "get_screen_size":
                return (
                    f"Résolution : "
                    f"{result.get('width')}x"
                    f"{result.get('height')}."
                )

            return "Action exécutée avec succès."

        return (
            "Action refusée ou échouée : "
            f"{result.get('error', 'erreur inconnue')}"
        )



