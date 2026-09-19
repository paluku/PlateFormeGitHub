import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests

class SearchAgent:
    """Agent de recherche polyvalent - Cherche et structure les résultats"""
    
    def __init__(self):
        self.name = "search_assistant"
        self.description = "Assistant de recherche polyvalent - Trouve des informations, des lieux, des prix, etc."
        
        # Base de données de connaissances
        self.knowledge_base = {
            "restaurants": [
                {"name": "Chez Fatou", "city": "Dakar", "cuisine": "Sénégalaise", "price": "€€", "rating": 4.5},
                {"name": "Le Ngor", "city": "Dakar", "cuisine": "Internationale", "price": "€€€", "rating": 4.7},
                {"name": "La Terrasse", "city": "Abidjan", "cuisine": "Française", "price": "€€", "rating": 4.3},
                {"name": "Le Petit Paris", "city": "Paris", "cuisine": "Française", "price": "€€€", "rating": 4.6},
            ],
            "activities": [
                {"name": "Visite du Musée", "city": "Dakar", "type": "Culturel", "price": 10, "duration": "2h"},
                {"name": "Plage de Ngor", "city": "Dakar", "type": "Plage", "price": 0, "duration": "Toute la journée"},
                {"name": "Safari", "city": "Saly", "type": "Nature", "price": 50, "duration": "4h"},
                {"name": "Tour Eiffel", "city": "Paris", "type": "Monument", "price": 20, "duration": "2h"},
            ],
            "services": [
                {"name": "Taxi", "city": "Dakar", "price": 5, "type": "Transport"},
                {"name": "Coiffeur", "city": "Abidjan", "price": 15, "type": "Beauté"},
                {"name": "Médecin", "city": "Paris", "price": 50, "type": "Santé"},
                {"name": "Boutique", "city": "Dakar", "price": 0, "type": "Shopping"},
            ]
        }

    def process(self, message: str, history: Optional[List] = None) -> str:
        """Traite la demande de recherche"""
        message_lower = message.lower()
        
        # Détecter le type de recherche
        if any(word in message_lower for word in ["restaurant", "manger", "cuisine", "repas", "food"]):
            return self._search_restaurants(message)
        
        elif any(word in message_lower for word in ["activité", "activite", "visite", "tour", "plage", "musée", "parc", "monument"]):
            return self._search_activities(message)
        
        elif any(word in message_lower for word in ["prix", "coût", "cout", "budget", "tarif", "combien"]):
            return self._search_prices(message)
        
        elif any(word in message_lower for word in ["service", "taxi", "coiffeur", "médecin", "docteur", "boutique", "magasin"]):
            return self._search_services(message)
        
        elif any(word in message_lower for word in ["meilleur", "meilleurs", "top", "recommandé", "recommande", "classement"]):
            return self._search_best(message)
        
        else:
            return self._general_search(message)

    def _search_restaurants(self, message: str) -> str:
        """Recherche des restaurants"""
        city = self._extract_city(message)
        cuisine = self._extract_cuisine(message)
        
        results = self.knowledge_base["restaurants"]
        if city:
            results = [r for r in results if city.lower() in r["city"].lower()]
        if cuisine:
            results = [r for r in results if cuisine.lower() in r["cuisine"].lower()]
        
        # Trier par note
        results = sorted(results, key=lambda x: x.get("rating", 0), reverse=True)
        
        response = f"🍽️ **Restaurants trouvés**\n\n"
        
        if city:
            response += f"📍 Ville: **{city}**\n"
        if cuisine:
            response += f"🍳 Cuisine: **{cuisine}**\n"
        response += "\n"
        
        if results:
            for i, r in enumerate(results[:5], 1):
                response += f"{i}. **{r['name']}**\n"
                response += f"   • Cuisine: {r['cuisine']}\n"
                response += f"   • Prix: {r.get('price', 'N/A')}\n"
                response += f"   • Note: ⭐ {r.get('rating', 0)}/5\n"
                response += "\n"
        else:
            response += "❌ Aucun restaurant trouvé pour ces critères.\n"
        
        response += "---\n"
        response += "💡 Dites-moi votre budget ou la spécialité souhaitée pour affiner.\n"
        
        return response

    def _search_activities(self, message: str) -> str:
        """Recherche des activités"""
        city = self._extract_city(message)
        activity_type = self._extract_activity_type(message)
        
        results = self.knowledge_base["activities"]
        if city:
            results = [r for r in results if city.lower() in r["city"].lower()]
        if activity_type:
            results = [r for r in results if activity_type.lower() in r["type"].lower()]
        
        response = f"🎯 **Activités trouvées**\n\n"
        
        if city:
            response += f"📍 Ville: **{city}**\n"
        response += "\n"
        
        if results:
            for i, r in enumerate(results[:5], 1):
                response += f"{i}. **{r['name']}**\n"
                response += f"   • Type: {r['type']}\n"
                response += f"   • Durée: {r['duration']}\n"
                response += f"   • Prix: {r['price']}€\n"
                response += "\n"
        else:
            response += "❌ Aucune activité trouvée pour ces critères.\n"
        
        response += "---\n"
        response += "💡 Vous pouvez aussi me demander les meilleures activités à faire.\n"
        
        return response

    def _search_prices(self, message: str) -> str:
        """Recherche des prix et budgets"""
        city = self._extract_city(message)
        item = self._extract_item(message)
        
        response = f"💰 **Informations sur les prix**\n\n"
        
        if city:
            response += f"📍 Ville: **{city}**\n"
        if item:
            response += f"🔍 Recherche: **{item}**\n"
        response += "\n"
        
        # Prix moyens par ville
        price_guide = {
            "dakar": {"restaurant": "15-30€", "hotel": "80-150€", "taxi": "5-10€"},
            "paris": {"restaurant": "20-50€", "hotel": "120-250€", "taxi": "10-20€"},
            "abidjan": {"restaurant": "10-25€", "hotel": "60-120€", "taxi": "3-8€"},
            "saly": {"restaurant": "12-25€", "hotel": "50-100€", "taxi": "4-8€"},
        }
        
        if city:
            city_key = city.lower()
            if city_key in price_guide:
                prices = price_guide[city_key]
                response += f"**Prix moyens à {city} :**\n"
                for category, price in prices.items():
                    response += f"  • {category.capitalize()}: {price}\n"
            else:
                response += f"❌ Pas d'information de prix pour {city}.\n"
        else:
            response += "**Prix moyens dans les grandes villes :**\n"
            for city_name, prices in price_guide.items():
                response += f"\n📍 {city_name.capitalize()}:\n"
                for category, price in prices.items():
                    response += f"  • {category.capitalize()}: {price}\n"
        
        response += "\n---\n"
        response += "💡 Ces prix sont indicatifs. Dites-moi ce que vous cherchez exactement.\n"
        
        return response

    def _search_services(self, message: str) -> str:
        """Recherche des services"""
        city = self._extract_city(message)
        service_type = self._extract_service_type(message)
        
        results = self.knowledge_base["services"]
        if city:
            results = [r for r in results if city.lower() in r["city"].lower()]
        if service_type:
            results = [r for r in results if service_type.lower() in r["type"].lower()]
        
        response = f"🛠️ **Services disponibles**\n\n"
        
        if city:
            response += f"📍 Ville: **{city}**\n"
        response += "\n"
        
        if results:
            for i, r in enumerate(results[:5], 1):
                response += f"{i}. **{r['name']}**\n"
                response += f"   • Type: {r['type']}\n"
                response += f"   • Prix: {r['price']}€\n"
                response += "\n"
        else:
            response += "❌ Aucun service trouvé pour ces critères.\n"
        
        response += "---\n"
        response += "💡 Pour trouver un service spécifique, précisez le type.\n"
        
        return response

    def _search_best(self, message: str) -> str:
        """Recherche les meilleurs résultats"""
        city = self._extract_city(message)
        category = self._extract_category(message)
        
        response = f"🏆 **Meilleurs résultats**\n\n"
        
        if city:
            response += f"📍 Ville: **{city}**\n"
        if category:
            response += f"📂 Catégorie: **{category}**\n"
        response += "\n"
        
        # Recommandations générales
        recommendations = {
            "restaurant": ["Chez Fatou (Dakar)", "Le Ngor (Dakar)", "La Terrasse (Abidjan)"],
            "activite": ["Plage de Ngor", "Visite du Musée", "Safari à Saly"],
            "hotel": ["Radisson Dakar", "Sofitel Abidjan", "Villa Majunga"],
        }
        
        if category and category in recommendations:
            items = recommendations[category]
            response += f"**Meilleurs {category}s :**\n"
            for item in items:
                response += f"  • {item}\n"
        else:
            response += "**Recommandations générales :**\n"
            response += "  • Meilleurs restaurants: Chez Fatou, Le Ngor\n"
            response += "  • Meilleures activités: Plage de Ngor, Musée\n"
            response += "  • Meilleurs hôtels: Radisson, Sofitel\n"
        
        response += "\n---\n"
        response += "💡 Demandez-moi les meilleurs restaurants, hôtels ou activités.\n"
        
        return response

    def _general_search(self, message: str) -> str:
        """Recherche générale"""
        # Extraire les mots-clés
        keywords = self._extract_keywords(message)
        
        response = f"🔍 **Résultats de recherche**\n\n"
        
        if keywords:
            response += f"📌 Mots-clés: **{', '.join(keywords)}**\n\n"
        
        response += "**Voici ce que je peux trouver :**\n\n"
        response += "1. 🍽️ **Restaurants** - Les meilleurs endroits pour manger\n"
        response += "2. 🎯 **Activités** - Choses à faire et visiter\n"
        response += "3. 💰 **Prix** - Informations sur les budgets\n"
        response += "4. 🛠️ **Services** - Taxis, coiffeurs, médecins\n"
        response += "5. 🏆 **Meilleurs** - Top recommandations\n\n"
        
        response += "**Exemples de questions :**\n"
        response += "• 'Restaurant à Dakar'\n"
        response += "• 'Activités à Paris'\n"
        response += "• 'Prix des hôtels à Abidjan'\n"
        response += "• 'Taxi à Saly'\n"
        response += "• 'Meilleurs restaurants'\n"
        
        return response

    # ============ MÉTHODES D'EXTRACTION ============

    def _extract_city(self, message: str) -> Optional[str]:
        """Extrait une ville du message"""
        cities = ["dakar", "paris", "abidjan", "londres", "new york", "dubai", "saly", "nice", 
                  "marseille", "lyon", "bordeaux", "toulouse"]
        
        for city in cities:
            if city.lower() in message.lower():
                return city.capitalize()
        return None

    def _extract_cuisine(self, message: str) -> Optional[str]:
        """Extrait le type de cuisine"""
        cuisines = ["sénégalaise", "senegalaise", "française", "francaise", "italienne", 
                   "chinoise", "japonaise", "africaine", "internationale", "locale"]
        
        for cuisine in cuisines:
            if cuisine.lower() in message.lower():
                return cuisine.capitalize()
        return None

    def _extract_activity_type(self, message: str) -> Optional[str]:
        """Extrait le type d'activité"""
        types = ["plage", "musée", "musee", "parc", "monument", "safari", "visite", "tour", 
                 "culturel", "nature", "aventure"]
        
        for typ in types:
            if typ.lower() in message.lower():
                return typ.capitalize()
        return None

    def _extract_item(self, message: str) -> Optional[str]:
        """Extrait l'item recherché"""
        items = ["restaurant", "hotel", "taxi", "vol", "voiture", "appartement", "villa", "billet"]
        
        for item in items:
            if item.lower() in message.lower():
                return item.capitalize()
        return None

    def _extract_service_type(self, message: str) -> Optional[str]:
        """Extrait le type de service"""
        services = ["transport", "taxi", "coiffeur", "médecin", "docteur", "boutique", "magasin"]
        
        for service in services:
            if service.lower() in message.lower():
                return service.capitalize()
        return None

    def _extract_category(self, message: str) -> Optional[str]:
        """Extrait la catégorie"""
        categories = ["restaurant", "activite", "hotel", "service", "prix", "vol", "voiture"]
        
        for category in categories:
            if category.lower() in message.lower():
                return category
        return None

    def _extract_keywords(self, message: str) -> List[str]:
        """Extrait les mots-clés importants"""
        # Nettoyer le message
        words = re.findall(r'\b\w+\b', message.lower())
        
        # Ignorer les mots communs
        stop_words = ["je", "suis", "veux", "cherche", "trouve", "trouver", "pour", "avec", "sans", 
                     "dans", "sur", "par", "un", "une", "des", "le", "la", "les", "ce", "cette"]
        
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return keywords[:5]  # Limiter à 5 mots-clés