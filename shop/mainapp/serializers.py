from rest_framework import serializers

from .models import Product, Category, UserProductRelation


class ProductListSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='name', read_only=True)
    likes = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=2, decimal_places=1, read_only=True)

    class Meta:
        model = Product
        fields = ('title', 'slug', 'category', 'price', 'likes', 'rating')


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class UserProductRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProductRelation
        fields = ('product', 'like', 'in_bookmarks', 'rate')
