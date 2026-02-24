
"""
E2E-Tests Microservices über Kong Gateway und auch kommunikation mit monolith (wichtiges Modul Catalogue)
"""

import requests
import time

# Gateway URL
GATEWAY = "http://localhost"
MONOLITH = "http://localhost:8000"       # Monolith Zugriff

results = []

test_id = str(int(time.time()))


def api_test(name, method, url, data=None, expected=200):

    """Teste einen API Endpoint"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, json=data, timeout=5)

        if isinstance(expected, list):
            ok = response.status_code in expected
        else:
            ok = (response.status_code == expected)

        results.append((name, ok))

        status = "Gut" if ok else "Error"
        print(f"{status} {name}: {response.status_code}")

        return response

    except Exception as e:
        results.append((name, False))
        print(f"Error {name}: Error - {e}")
        return None


print("\n=== E2E Tests Start ===\n")

# Test 1: Offers-Microservice

print("--- Offers-Service ---")
api_test("Get Offers", "GET", f"{GATEWAY}/api/offers/")
api_test("Get Ranges", "GET", f"{GATEWAY}/api/offers/ranges/")
api_test("Create Range", "POST", f"{GATEWAY}/api/offers/ranges/",
         {"name": f"Range-{test_id}", "slug": f"range-{test_id}"}, 201)

# Test 2: Basket-Microservice

print("\n--- Basket-Service ---")
api_test("Get Baskets", "GET", f"{GATEWAY}/api/basket/")
r = api_test("Create Basket", "POST", f"{GATEWAY}/api/basket/",
             {"customer_id": 1}, 201)

# Wenn Basket erstellt, Produkt hinzufügen

if r and r.status_code == 201:
    basket_id = r.json()['id']
    api_test("Add Product", "POST", f"{GATEWAY}/api/basket/{basket_id}/add_product/",
             {"product_id": 1, "product_title": "Test Produkt",
              "price_excl_tax": "10.00", "price_incl_tax": "12.00", "quantity": 1})

# Test 3: Erreichbarkeit der Catalogue-Monolith über Kong

print("\n--- MONOLITH Anwendung---")
api_test("Monolith Home", "GET", f"{MONOLITH}/", [200, 302])
api_test("Catalogue", "GET", f"{MONOLITH}/en-gb/catalogue/", [200, 302])
api_test("Dashboard", "GET", f"{MONOLITH}/dashboard/", [200, 302])
api_test("Admin Panel", "GET", f"{MONOLITH}/admin/", [200, 302])

# Test 4: Orders Microservice

print("\n--- Orders-Service ---")
api_test("Get Orders", "GET", f"{GATEWAY}/api/orders/")
api_test("Create Order", "POST", f"{GATEWAY}/api/orders/",
         {"number": f"ORD-{test_id}", "customer_id": 1, "basket_id": 1,
          "total_incl_tax": "50.00", "total_excl_tax": "42.00"}, 201)

# Test 5: Payment

print("\n--- Payment-Service---")
api_test("Get Sources", "GET", f"{GATEWAY}/api/payment/sources/")
api_test("Get Bankcards", "GET", f"{GATEWAY}/api/payment/bankcards/")


print("\n" + "=" * 40)
passed = sum(1 for _, ok in results if ok)
total = len(results)
print(f"Ergebnis: {passed}/{total} test bestanden")
print("=" * 40)

if passed == total:
    print("✓ Alle Tests Erfolgreich sind")
else:
    print("Error:")
    for name, ok in results:
        if not ok:
            print(f"  - {name}")