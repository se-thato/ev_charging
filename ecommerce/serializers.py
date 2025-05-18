from rest_framework import serializers
from .models import Product
from django.contrib.auth.models import User


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'old_price',
            'price',
            'category',
            'discount',
            'top_deals',
            'sales',
            'image',
        ]
