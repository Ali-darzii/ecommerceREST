from rest_framework import serializers
from product_module.models import Product, ProductGallery, Comment, ProductCategory, ProductBrand, Like


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBrand
        fields = '__all__'


class ProductGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGallery
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

    like_count = serializers.IntegerField(read_only=True)
    dislike_count = serializers.IntegerField(read_only=True)


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ("is_active", "brand", "category", "inventory")

    final_price = serializers.IntegerField()
    discount = serializers.IntegerField()
    available = serializers.BooleanField()


class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ("is_active", "inventory")

    category = ProductCategorySerializer(many=True)
    product_gallery = ProductGallerySerializer(many=True)
    brand = ProductBrandSerializer()
    final_price = serializers.IntegerField()
    discount = serializers.IntegerField()
    available = serializers.BooleanField()
