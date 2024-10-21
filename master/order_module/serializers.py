from rest_framework import serializers
from order_module.models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['total_price', 'total_products']

