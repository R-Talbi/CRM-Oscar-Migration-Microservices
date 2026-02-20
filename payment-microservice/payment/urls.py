from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SourceTypeViewSet, SourceViewSet, BankcardViewSet

router = DefaultRouter()
router.register(r'source-types', SourceTypeViewSet, basename='sourcetype')
router.register(r'sources', SourceViewSet, basename='source')
router.register(r'bankcards', BankcardViewSet, basename='bankcard')

urlpatterns = [path('', include(router.urls))]
