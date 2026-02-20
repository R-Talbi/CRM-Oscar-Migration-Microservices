import requests
import json
import time

KONG = "http://localhost"
RESULTS = []
TS = str(int(time.time()))

def test(name, method, url, data=None, expected_status=200):
    try:
        if method == "GET":
            r = requests.get(url, timeout=5)
        elif method == "POST":
            r = requests.post(url, json=data, timeout=5)
        success = r.status_code == expected_status
        RESULTS.append((name, success, r.status_code))
        status = "✅" if success else "❌"
        print(f"{status} {name}: {r.status_code}")
        return r
    except Exception as e:
        RESULTS.append((name, False, str(e)))
        print(f"❌ {name}: {e}")
        return None

print("\n═══════════════════════════════════════")
print("   KONG GATEWAY INTEGRATION TESTS")
print("   Strangler Pattern Validierung")
print("═══════════════════════════════════════\n")

print("--- OFFERS ---")
test("Offers Liste", "GET", f"{KONG}/api/offers/")
test("Offers Range Liste", "GET", f"{KONG}/api/offers/ranges/")
r = test("Range erstellen", "POST", f"{KONG}/api/offers/ranges/",
    {"name": f"Range {TS}", "slug": f"range-{TS}", "includes_all_products": False}, 201)

print("\n--- BASKET ---")
test("Basket Liste", "GET", f"{KONG}/api/basket/")
r = test("Basket erstellen", "POST", f"{KONG}/api/basket/",
    {"customer_id": 1, "customer_email": "test@example.com"}, 201)
if r and r.status_code == 201:
    basket_id = r.json()['id']
    test("Produkt hinzufügen", "POST",
        f"{KONG}/api/basket/{basket_id}/add_product/",
        {"product_id": 1, "product_title": "Sommer-Shirt",
         "price_excl_tax": "25.00", "price_incl_tax": "29.75", "quantity": 2})

print("\n--- CATALOGUE ---")
test("Catalogue Liste", "GET", f"{KONG}/api/catalogue/")

print("\n--- ORDERS ---")
test("Orders Liste", "GET", f"{KONG}/api/orders/")
test("Order erstellen", "POST", f"{KONG}/api/orders/",
    {"number": f"KONG-{TS}", "customer_id": 1, "basket_id": 1,
     "currency": "EUR", "total_incl_tax": "119.00",
     "total_excl_tax": "100.00", "status": "Pending"}, 201)

print("\n--- PAYMENT ---")
test("Payment Sources", "GET", f"{KONG}/api/payment/sources/")
test("Payment Bankcards", "GET", f"{KONG}/api/payment/bankcards/")

passed = sum(1 for _, s, _ in RESULTS if s)
total = len(RESULTS)
print(f"\n═══════════════════════════════════════")
print(f"   ERGEBNIS: {passed}/{total} Tests bestanden")
print(f"═══════════════════════════════════════")
if passed == total:
    print("   ✅ ALLE SERVICES ÜBER KONG ERREICHBAR!")
    print("   ✅ STRANGLER PATTERN ERFOLGREICH!")
else:
    for name, s, code in RESULTS:
        if not s:
            print(f"   ❌ {name}: {code}")
