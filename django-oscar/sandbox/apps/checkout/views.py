import requests
from django.contrib import messages
from oscar.apps.checkout import views as core_views

KONG_URL = "http://localhost"


class IndexView(core_views.IndexView):
    """
    Strangler Pattern:
    Checkout holt Basket vom Basket Microservice über Kong!
    """
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        
        # Basket über Kong holen
        try:
            customer_id = self.request.user.id
            response = requests.get(f"{KONG_URL}/api/basket/", timeout=5)
            baskets = response.json().get("results", [])
            customer_baskets = [b for b in baskets if b.get("customer_id") == customer_id]
            
            ctx["microservice_basket"] = customer_baskets[0] if customer_baskets else None
            ctx["kong_url"] = KONG_URL
            ctx["strangler_pattern"] = True
        except Exception as e:
            ctx["microservice_basket"] = None
            ctx["kong_error"] = str(e)
        
        return ctx


class PaymentDetailsView(core_views.PaymentDetailsView):
    """
    Strangler Pattern:
    Payment Details erstellt Order über Kong!
    """
    def handle_order_placement(self, order_number, user, basket, 
                                shipping_address, shipping_method,
                                shipping_charge, billing_address, 
                                order_total, **kwargs):
        # Order über Kong Microservice erstellen!
        try:
            order_data = {
                "number": order_number,
                "customer_id": user.id,
                "basket_id": basket.get("id") if isinstance(basket, dict) else basket.id,
                "currency": "EUR",
                "total_incl_tax": str(order_total.incl_tax),
                "total_excl_tax": str(order_total.excl_tax),
                "status": "Pending"
            }
            response = requests.post(
                f"{KONG_URL}/api/orders/",
                json=order_data,
                timeout=5
            )
            if response.status_code == 201:
                messages.success(
                    self.request,
                    f"Order {order_number} über Kong Gateway erstellt! "
                    f"[Orders Microservice]"
                )
        except Exception as e:
            messages.error(self.request, f"Kong Fehler: {e}")
        
        return super().handle_order_placement(
            order_number, user, basket, shipping_address,
            shipping_method, shipping_charge, billing_address,
            order_total, **kwargs
        )
