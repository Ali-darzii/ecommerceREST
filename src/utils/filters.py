import django_filters
from product_module.models import Product, ProductCategory



class ProductFilter(django_filters.FilterSet):
    price_gt = django_filters.NumberFilter(field_name="price", lookup_expr='gt')
    price_lt = django_filters.NumberFilter(field_name="price", lookup_expr='lt')

    category = django_filters.ModelMultipleChoiceFilter(
        field_name="category__title",
        queryset=ProductCategory.objects.filter(is_active=True),
        to_field_name="title",
        conjoined=True
    )

    brand = django_filters.CharFilter(field_name="brand__title", lookup_expr='iexac')

    class Meta:
        model = Product
        fields = ["price_gt", "price_lt", "category", "brand"]



