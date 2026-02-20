from rest_framework import serializers
from .models import ConditionalOffer, Benefit, Condition, Range


class RangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Range
        fields = "__all__"


class BenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefit
        fields = "__all__"


class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condition
        fields = "__all__"


class ConditionalOfferSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)
    condition_detail = ConditionSerializer(source="condition", read_only=True)
    benefit_detail = BenefitSerializer(source="benefit", read_only=True)

    class Meta:
        model = ConditionalOffer
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "offer_type",
            "status",
            "condition",
            "condition_detail",
            "benefit",
            "benefit_detail",
            "priority",
            "start_datetime",
            "end_datetime",
            "is_available",
            "num_applications",
            "total_discount",
        ]
