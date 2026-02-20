from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from .models import ConditionalOffer, Range, Benefit, Condition
from .serializers import ConditionalOfferSerializer


class RangeViewSet(viewsets.ModelViewSet):
    queryset = Range.objects.all()

    def get_serializer_class(self):
        from rest_framework import serializers

        class RangeSerializer(serializers.ModelSerializer):
            class Meta:
                model = Range
                fields = "__all__"

        return RangeSerializer

    @action(detail=True, methods=["post"])
    def add_product(self, request, pk=None):
        range_obj = self.get_object()
        product_id = request.data.get("product_id")
        if not product_id:
            return Response({"error": "product_id required"}, status=400)
        range_obj.add_product(int(product_id))
        return Response({"status": "product added"})

    @action(detail=True, methods=["post"])
    def remove_product(self, request, pk=None):
        range_obj = self.get_object()
        product_id = request.data.get("product_id")
        range_obj.remove_product(int(product_id))
        return Response({"status": "product removed"})


class BenefitViewSet(viewsets.ModelViewSet):
    queryset = Benefit.objects.all()

    def get_serializer_class(self):
        from rest_framework import serializers

        class BenefitSerializer(serializers.ModelSerializer):
            class Meta:
                model = Benefit
                fields = "__all__"

        return BenefitSerializer


class ConditionViewSet(viewsets.ModelViewSet):
    queryset = Condition.objects.all()

    def get_serializer_class(self):
        from rest_framework import serializers

        class ConditionSerializer(serializers.ModelSerializer):
            class Meta:
                model = Condition
                fields = "__all__"

        return ConditionSerializer


class ConditionalOfferViewSet(viewsets.ModelViewSet):
    queryset = ConditionalOffer.objects.all()
    serializer_class = ConditionalOfferSerializer

    @action(detail=True, methods=["post"])
    def apply(self, request, pk=None):
        offer = self.get_object()
        basket_total = request.data.get("basket_total", 0)
        basket_quantity = request.data.get("basket_quantity", 0)
        discount = offer.apply_to_basket(Decimal(str(basket_total)), int(basket_quantity))
        return Response(
            {"offer": offer.name, "discount": str(discount), "offer_status": offer.status}
        )

    @action(detail=False, methods=["get"])
    def available(self, request):
        offers = [o for o in self.get_queryset() if o.is_available()]
        serializer = self.get_serializer(offers, many=True)
        return Response(serializer.data)
