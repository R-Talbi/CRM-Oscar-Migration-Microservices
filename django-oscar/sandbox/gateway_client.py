#Gateway Client - Kommunikation mit Microservices über Kong!
#Strangler Pattern: Monolith ruft Microservices über Kong auf!

import requests

KONG_URL = "http://localhost"

def get_basket(basket_id):
    """Basket über Kong abrufen"""
    response = requests.get(f"{KONG_URL}/api/basket/{basket_id}/")
    if response.status_code == 200:
        return response.json()
    return None

def get_baskets_for_customer(customer_id):
    """Alle Baskets eines Kunden über Kong"""
    response = requests.get(f"{KONG_URL}/api/basket/")
    if response.status_code == 200:
        data = response.json()
        return [b for b in data['results'] 
                if b['customer_id'] == customer_id]
    return []

def get_offers():
    """Offers über Kong abrufen"""
    response = requests.get(f"{KONG_URL}/api/offers/")
    if response.status_code == 200:
        return response.json()
    return None

def get_order(order_id):
    """Order über Kong abrufen"""
    response = requests.get(f"{KONG_URL}/api/orders/{order_id}/")
    if response.status_code == 200:
        return response.json()
    return None