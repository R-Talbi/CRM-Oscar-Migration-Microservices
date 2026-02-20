from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RangeViewSet, BenefitViewSet, ConditionViewSet, ConditionalOfferViewSet

router = DefaultRouter()
router.register(r"ranges", RangeViewSet, basename="range")
router.register(r"benefits", BenefitViewSet, basename="benefit")
router.register(r"conditions", ConditionViewSet, basename="condition")
router.register(r"", ConditionalOfferViewSet, basename="offer")

urlpatterns = [path("", include(router.urls))]
