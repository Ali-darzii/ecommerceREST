from rest_framework import serializers

from product_module.models import Product, ProductGallery, Comment, ProductCategory, ProductBrand


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


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    category = ProductCategorySerializer(many=True)
    product_gallery = ProductGallerySerializer(many=True)
    product_comment = CommentSerializer(many=True)
    brand = ProductBrandSerializer()
