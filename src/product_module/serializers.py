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


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ("is_active","brand","category","inventory")

    available = serializers.SerializerMethodField()
    final_price = serializers.IntegerField(source="calculate_final_price")
    discount = serializers.SerializerMethodField()

    def get_available(self, obj):
        return True if obj.inventory else False

    def get_discount(self, obj):
       return obj.get_discount()

class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ("is_active",)

    available = serializers.SerializerMethodField()
    final_price = serializers.IntegerField(source="calculate_final_price")
    discount = serializers.SerializerMethodField()
    category = ProductCategorySerializer(many=True)
    product_gallery = ProductGallerySerializer(many=True)
    product_comment = CommentSerializer(many=True)
    brand = ProductBrandSerializer()

    def get_discount(self, obj):
       return obj.get_discount()

    def get_available(self, obj):
        return True if obj.inventory else False