import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class TravelAgent:
    """Agent spécialisé dans la recherche de voyages, locations et transports"""
    
    def __init__(self):
        self.name = "travel_assistant"
        self.description = "Assistant de recherche de voyages, locations de voitures, billets d'avion et hébergements"
        
        # Base de données simulée (à remplacer par une vraie API)
        self.mock_data = {
            "cars": [
                {"id": 1, "name": "Toyota Yaris", "price": 45, "type": "Économique", "seats": 5, "transmission": "Manuelle"},
                {"id": 2, "name": "Renault Clio", "price": 50, "type": "Économique", "seats": 5, "transmission": "Manuelle"},
                {"id": 3, "name": "Peugeot 208", "price": 55, "type": "Compacte", "seats": 5, "transmission": "Manuelle"},
                {"id": 4, "name": "Volkswagen Golf", "price": 65, "type": "Compacte", "seats": 5, "transmission": "Automatique"},
                {"id": 5, "name": "Mercedes Classe C", "price": 120, "type": "Luxe", "seats": 5, "transmission": "Automatique"},
                {"id": 6, "name": "BMW X5", "price": 150, "type": "SUV", "seats": 7, "transmission": "Automatique"},
                {"id": 7, "name": "Renault Trafic", "price": 90, "type": "Utilitaire", "seats": 9, "transmission": "Manuelle"},
                {"id": 8, "name": "Toyota Land Cruiser", "price": 130, "type": "4x4", "seats": 7, "transmission": "Automatique"},
                {"id": 9, "name": "Dacia Sandero", "price": 40, "type": "Économique", "seats": 5, "transmission": "Manuelle"},
            ],
            "flights": [
                {"id": 1, "from": "Paris", "to": "Dakar", "price": 450, "duration": "6h30", "airline": "Air France", "stops": 0},
                {"id": 2, "from": "Paris", "to": "Abidjan", "price": 520, "duration": "7h", "airline": "Air France", "stops": 0},
                {"id": 3, "from": "Paris", "to": "Londres", "price": 120, "duration": "1h15", "airline": "British Airways", "stops": 0},
                {"id": 4, "from": "Paris", "to": "New York", "price": 650, "duration": "8h", "airline": "Delta", "stops": 0},
                {"id": 5, "from": "Paris", "to": "Dubai", "price": 580, "duration": "6h", "airline": "Emirates", "stops": 0},
                {"id": 6, "from": "Dakar", "to": "Paris", "price": 480, "duration": "6h30", "airline": "Air Senegal", "stops": 0},
                {"id": 7, "from": "Dakar", "to": "Abidjan", "price": 250, "duration": "2h", "airline": "Air Senegal", "stops": 0},
                {"id": 8, "from": "Paris", "to": "Rome", "price": 150, "duration": "2h", "airline": "Alitalia", "stops": 0},
                {"id": 9, "from": "Paris", "to": "Barcelone", "price": 130, "duration": "1h45", "airline": "Vueling", "stops": 0},
            ],
            "accommodations": [
                {"id": 1, "name": "Hôtel Radisson", "city": "Dakar", "price": 120, "stars": 4, "type": "Hôtel", "rating": 4.5},
                {"id": 2, "name": "Villa Majunga", "city": "Dakar", "price": 200, "stars": 5, "type": "Villa", "rating": 4.8},
                {"id": 3, "name": "Airbnb Centre", "city": "Paris", "price": 80, "stars": 0, "type": "Airbnb", "rating": 4.2},
                {"id": 4, "name": "Hôtel Sofitel", "city": "Abidjan", "price": 150, "stars": 5, "type": "Hôtel", "rating": 4.7},
                {"id": 5, "name": "Village Vacances", "city": "Saly", "price": 100, "stars": 3, "type": "Resort", "rating": 4.3},
                {"id": 6, "name": "Appartement Vue Mer", "city": "Nice", "price": 90, "stars": 0, "type": "Appartement", "rating": 4.4},
                {"id": 7, "name": "Hôtel Pullman", "city": "Dakar", "price": 140, "stars": 4, "type": "Hôtel", "rating": 4.6},
                {"id": 8, "name": "Villa Palmeraie", "city": "Saly", "price": 150, "stars": 4, "type": "Villa", "rating": 4.5},
                {"id": 9, "name": "Auberg Inn", "city": "Abidjan", "price": 50, "stars": 2, "type": "Auberge", "rating": 3.8},
            ]
        }

    def process(self, message: str, history: Optional[List] = None) -> str:
        """Traite la demande de l'utilisateur"""
        message_lower = message.lower()
        
        # Détecter le type de demande
        if any(word in message_lower for word in ["voiture", "location", "car", "rental", "véhicule", "4x4", "louer"]):
            return self._search_cars(message)
        
        elif any(word in message_lower for word in ["avion", "vol", "billet", "plane", "flight", "aéroport", "airport", "compagnie"]):
            return self._search_flights(message)
        
        elif any(word in message_lower for word in ["hôtel", "hotel", "appartement", "villa", "logement", "hébergement", "airbnb", "vacances", "resort", "auberge"]):
            return self._search_accommodations(message)
        
        elif any(word in message_lower for word in ["voyage", "travel", "vacance", "destination", "guide", "visiter"]):
            return self._travel_guide(message)
        
        else:
            return self._general_travel_advice(message)

    def _search_cars(self, message: str) -> str:
        """Recherche des locations de voitures"""
        city = self._extract_city(message)
        dates = self._extract_dates(message)
        car_type = self._extract_car_type(message)
        
        # Filtrer les résultats
        results = self.mock_data["cars"]
        if car_type:
            results = [c for c in results if car_type.lower() in c["type"].lower()]
        
        # Limiter à 5 résultats
        results = results[:5]
        
        # Construire la réponse
        response = f"🚗 **Locations de voitures**\n\n"
        if city:
            response += f"📍 Ville: **{city}**\n"
        if dates:
            response += f"📅 Dates: **{dates}**\n"
        response += "\n"
        
        if results:
            for car in results:
                response += f"**{car['name']}**\n"
                response += f"  • Type: {car['type']} ({car['seats']} places)\n"
                response += f"  • Transmission: {car['transmission']}\n"
                response += f"  • Prix: {car['price']}€/jour\n"
                response += "\n"
        else:
            response += "❌ Aucune voiture disponible pour ces critères.\n"
            response += "\n💡 Suggestions :\n"
            response += "  • Essayez une autre ville\n"
            response += "  • Modifiez le type de véhicule\n"
            response += "  • Vérifiez vos dates\n"
        
        response += "---\n"
        response += "💡 Pour réserver, précisez vos dates exactes et la ville.\n"
        
        return response

    def _search_flights(self, message: str) -> str:
        """Recherche des billets d'avion"""
        departure, arrival = self._extract_airports(message)
        dates = self._extract_dates(message)
        max_price = self._extract_max_price(message)
        
        # Filtrer les résultats
        results = self.mock_data["flights"]
        if departure:
            results = [f for f in results if departure.lower() in f["from"].lower()]
        if arrival:
            results = [f for f in results if arrival.lower() in f["to"].lower()]
        if max_price:
            results = [f for f in results if f["price"] <= max_price]
        
        # Trier par prix
        results = sorted(results, key=lambda x: x["price"])[:5]
        
        # Construire la réponse
        response = f"✈️ **Billets d'avion**\n\n"
        if departure:
            response += f"🛫 Départ: **{departure}**\n"
        if arrival:
            response += f"🛬 Arrivée: **{arrival}**\n"
        if dates:
            response += f"📅 Dates: **{dates}**\n"
        if max_price:
            response += f"💰 Budget max: **{max_price}€**\n"
        response += "\n"
        
        if results:
            for flight in results:
                response += f"**{flight['airline']}**\n"
                response += f"  • {flight['from']} → {flight['to']}\n"
                response += f"  • Durée: {flight['duration']}\n"
                response += f"  • Escales: {flight['stops']} escale(s)\n"
                response += f"  • Prix: {flight['price']}€\n"
                response += "\n"
        else:
            response += "❌ Aucun vol disponible pour ces critères.\n"
        
        response += "---\n"
        response += "💡 Précisez les dates et les aéroports pour une recherche précise.\n"
        
        return response

    def _search_accommodations(self, message: str) -> str:
        """Recherche des hébergements"""
        city = self._extract_city(message)
        accommodation_type = self._extract_accommodation_type(message)
        dates = self._extract_dates(message)
        max_price = self._extract_max_price(message)
        
        # Filtrer les résultats
        results = self.mock_data["accommodations"]
        if city:
            results = [a for a in results if city.lower() in a["city"].lower()]
        if accommodation_type:
            results = [a for a in results if accommodation_type.lower() in a["type"].lower()]
        if max_price:
            results = [a for a in results if a["price"] <= max_price]
        
        # Trier par prix
        results = sorted(results, key=lambda x: x["price"])[:5]
        
        # Construire la réponse
        response = f"🏨 **Hébergements**\n\n"
        if city:
            response += f"📍 Ville: **{city}**\n"
        if dates:
            response += f"📅 Dates: **{dates}**\n"
        if max_price:
            response += f"💰 Budget max: **{max_price}€**\n"
        response += "\n"
        
        if results:
            for acc in results:
                response += f"**{acc['name']}**\n"
                response += f"  • Type: {acc['type']}"
                if acc.get('stars', 0) > 0:
                    response += f" (⭐ {acc['stars']}*)"
                response += "\n"
                response += f"  • Note: {acc.get('rating', 0)}/5\n"
                response += f"  • Prix: {acc['price']}€/nuit\n"
                response += "\n"
        else:
            response += "❌ Aucun hébergement disponible pour ces critères.\n"
        
        response += "---\n"
        response += "💡 Pour plus d'options, essayez avec une autre ville ou un autre budget.\n"
        
        return response

    def _travel_guide(self, message: str) -> str:
        """Guide de voyage général"""
        city = self._extract_city(message)
        
        response = f"🌍 **Guide de voyage**\n\n"
        
        if city:
            response += f"📍 Destination: **{city}**\n\n"
            response += f"**Informations pratiques pour {city} :**\n"
            response += "  • 🗓️ Meilleure période: Consultez la météo locale\n"
            response += "  • 💰 Monnaie: Vérifiez le taux de change\n"
            response += "  • 🗣️ Langue: Renseignez-vous sur la langue locale\n"
            response += "  • 📋 Visa: Vérifiez les formalités\n"
            response += "  • 🔌 Électricité: Adaptateur nécessaire\n\n"
            
            response += "**Que visiter ?**\n"
            response += "  • Demandez-moi des recommendations spécifiques\n"
            response += "  • Exemple: 'Que visiter à Dakar ?'\n\n"
            
            response += "**Comment se déplacer ?**\n"
            response += "  • Taxis, transports en commun, location de voiture\n"
            response += "  • Exemple: 'Taxi à Dakar'\n"
        else:
            response += "**🇫🇷 Destinations recommandées :**\n"
            response += "  • 🇫🇷 Paris - Capitale de la mode et de la culture\n"
            response += "  • 🇸🇳 Dakar - La perle de l'Afrique de l'Ouest\n"
            response += "  • 🇺🇸 New York - La ville qui ne dort jamais\n"
            response += "  • 🇦🇪 Dubaï - Luxe et modernité\n"
            response += "  • 🇨🇮 Abidjan - La perle des lagunes\n"
            response += "  • 🇬🇧 Londres - Ville royale et cosmopolite\n"
            response += "  • 🇮🇹 Rome - La ville éternelle\n\n"
            
            response += "**Que recherchez-vous ?**\n"
            response += "  • 🚗 Location de voiture\n"
            response += "  • ✈️ Billet d'avion\n"
            response += "  • 🏨 Hôtel ou hébergement\n"
            response += "  • 🗺️ Guide touristique\n\n"
            response += "💡 Dites-moi une destination pour avoir plus d'informations !\n"
        
        return response

    def _general_travel_advice(self, message: str) -> str:
        """Conseils de voyage généraux"""
        return """
🧳 **Conseils de voyage**

Voici ce que je peux faire pour vous :

1. **🚗 Location de voitures**
   • Trouver des véhicules à louer
   • Comparer les prix par ville
   • Obtenir des recommandations selon votre budget

2. **✈️ Billets d'avion**
   • Rechercher des vols internationaux et domestiques
   • Comparer les compagnies aériennes
   • Trouver les meilleurs prix

3. **🏨 Hébergements**
   • Hôtels, villas, appartements
   • Airbnb, Resorts, Auberges
   • Offres de dernière minute

4. **🗺️ Conseils de voyage**
   • Destinations recommandées
   • Meilleures périodes pour voyager
   • Attractions locales à visiter

📌 **Exemples de questions :**
• "Je cherche une voiture à Dakar pour 3 jours"
• "Trouve-moi un vol Paris-Dakar pour le 15 août"
• "Hôtel pas cher à Abidjan"
• "Je veux partir en vacances à Saly"
• "Que visiter à Paris ?"
• "Location de voiture pas chère"

❓ Comment puis-je vous aider aujourd'hui ?
"""

    # ============ MÉTHODES D'EXTRACTION ============

    def _extract_city(self, message: str) -> Optional[str]:
        """Extrait une ville du message"""
        cities = ["dakar", "paris", "abidjan", "londres", "new york", "dubai", "saly", "nice", 
                  "marseille", "lyon", "bordeaux", "toulouse", "montpellier", "nantes", "rome", "barcelone"]
        
        for city in cities:
            if city.lower() in message.lower():
                return city.capitalize()
        return None

    def _extract_dates(self, message: str) -> Optional[str]:
        """Extrait les dates du message"""
        # Recherche de dates au format JJ/MM ou JJ/MM/AAAA
        date_pattern = r'\d{1,2}[/-]\d{1,2}([/-]\d{4})?'
        dates = re.findall(date_pattern, message)
        
        if dates:
            return dates[0] if isinstance(dates[0], str) else dates[0][0]
        
        # Recherche de mots-clés de dates
        date_keywords = ["aujourd'hui", "demain", "après-demain", "ce week-end", "semaine prochaine", 
                        "prochain", "prochaine", "cette semaine"]
        for keyword in date_keywords:
            if keyword in message.lower():
                return keyword
        
        return None

    def _extract_car_type(self, message: str) -> Optional[str]:
        """Extrait le type de voiture recherché"""
        car_types = ["économique", "compacte", "luxe", "suv", "utilitaire", "4x4", "berline"]
        for car_type in car_types:
            if car_type in message.lower():
                return car_type
        return None

    def _extract_airports(self, message: str):
        """Extrait les aéroports de départ et d'arrivée"""
        cities = ["paris", "dakar", "abidjan", "londres", "new york", "dubai", "saly", "nice",
                  "rome", "barcelone", "milan", "berlin", "madrid"]
        
        departure = None
        arrival = None
        
        # Chercher "de X à Y" ou "X vers Y"
        for city in cities:
            if f"de {city}" in message.lower() or f"depart {city}" in message.lower():
                departure = city.capitalize()
            if f"à {city}" in message.lower() or f"vers {city}" in message.lower() or f"pour {city}" in message.lower():
                arrival = city.capitalize()
        
        return departure, arrival

    def _extract_accommodation_type(self, message: str) -> Optional[str]:
        """Extrait le type d'hébergement"""
        types = ["hôtel", "hotel", "villa", "appartement", "airbnb", "resort", "auberge", "motel"]
        for typ in types:
            if typ in message.lower():
                return typ
        return None

    def _extract_max_price(self, message: str) -> Optional[int]:
        """Extrait le prix maximum"""
        # Recherche de prix dans le message
        price_pattern = r'(\d+)\s*€'
        prices = re.findall(price_pattern, message)
        
        if prices:
            return int(prices[0])
        return None