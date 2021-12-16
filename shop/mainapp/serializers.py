from rest_framework import serializers

from .models import Product


class ProductListSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Product
        fields = ('title', 'slug', 'category', 'price')


