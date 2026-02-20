from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BasketViewSet

router = DefaultRouter()
router.register(r'', BasketViewSet, basename='basket')

urlpatterns = [
    path('', include(router.urls)),
]
