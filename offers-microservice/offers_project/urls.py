from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'service': 'offers-microservice'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check),
    path('api/offers/', include('offers.urls')),
]