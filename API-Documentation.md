# API Dokumentation

# Kong Gateway
# Base URL: http://localhost:80

# Offers Service

# GET /api/offers/
Alle Angebote abrufen
```json
{
"Response": {
    "id": 1,
    "name": "Summer Sale",
    "description": "20% off"
  }
}
```

# GET /api/offers/ranges/
Alle Ranges abrufen

# POST /api/offers/ranges/
Neue Range erstellen
```json
{
"Request": {
  "name": "Winter Range",
  "slug": "winter-2026"
}
}
```
Response : 201 Created


# Basket Service

# GET /api/basket/
Alle Baskets abrufen

# POST /api/basket/
Neuen Basket erstellen
```json
{
"Request": {
  "customer_id": 1,
  "customer_email": "user@example.com"
}
  }
```
Response: 201 Created


# POST /api/basket/{id}/add_product/
Produkt zum Basket hinzufügen

```json
{
"Request": {
  "product_id": 1,
  "product_title": "T-Shirt",
  "price_excl_tax": "25.00",
  "price_incl_tax": "29.75",
  "quantity": 2
}
}
```

# Orders Service

# GET /api/orders/
Alle Orders abrufen

# POST /api/orders/
Neue Order erstellen

```json
{
"Request": {
  "number": "ORD-12345",
  "customer_id": 1,
  "basket_id": 1,
  "total_incl_tax": "119.00",
  "total_excl_tax": "100.00"
}
}

```

# Payment Service

# GET /api/payment/sources/
Payment Sources abrufen

# GET /api/payment/bankcards/
Bankcards abrufen
