from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'service': 'customer-microservice'
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check),
    path('api/customers/', include('customer.urls')),
]