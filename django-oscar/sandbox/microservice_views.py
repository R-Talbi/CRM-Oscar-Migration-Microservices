import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required

KONG_URL = "http://localhost"


@csrf_exempt
def voucher_basket_view(request, voucher_code=''):

    """
    Voucher (Monolith) kommuniziert mit Basket (Microservice) über Kong
    """

    # Voucher aus Monolith DB
    from oscar.core.loading import get_model
    Voucher = get_model('voucher', 'Voucher')
    
    try:
        voucher = Voucher.objects.get(code=voucher_code)
        voucher_data = {
            'code': voucher.code,
            'name': voucher.name,
            'num_basket_additions': voucher.num_basket_additions,
        }
    except Voucher.DoesNotExist:
        voucher_data = None

    try:
        response = requests.get(f"{KONG_URL}/api/basket/", timeout=5)
        baskets = response.json().get('results', [])
    except:
        baskets = []

    return render(request, 'voucher_basket.html', {
        'voucher': voucher_data,
        'baskets': baskets,
        'kong_url': KONG_URL,
        'kommunikation': 'Voucher (Monolith) → Kong → Basket Microservice',
    })


@csrf_exempt
def checkout_basket_view(request, customer_id):
    baskets_response = requests.get(f"{KONG_URL}/api/basket/", timeout=5)
    baskets = [b for b in baskets_response.json().get('results', [])
               if b['customer_id'] == int(customer_id)]
    offers_response = requests.get(f"{KONG_URL}/api/offers/", timeout=5)
    
    context = {
        'customer_id': customer_id,
        'basket': baskets[0] if baskets else None,
        'available_offers': offers_response.json().get('count', 0),
    }
    return render(request, 'checkout_ms.html', context)
