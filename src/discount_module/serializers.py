from rest_framework import serializers
from .models import ProductDiscount


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDiscount
        fields = "__all__"
