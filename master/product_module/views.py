from product_module.models import Product, ProductCategory, ProductBrand
from product_module.serializers import ProductSerializer, ProductCategorySerializer, ProductBrandSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.mixins import RetrieveModelMixin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from product_module.tasks import product_visited
from utils.filters import ProductFilter
from rest_framework.response import Response

from utils.utils import get_client_ip


class ProductViewSet(ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price']

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        product_visited.apply_async(args=(instance, get_client_ip(request), request.user.id))
        return Response(serializer.data)


class ProductCategoryViewSet(ReadOnlyModelViewSet):
    serializer_class = ProductCategorySerializer
    queryset = ProductCategory.objects.filter(is_active=True)


class ProductBrandViewSet(ReadOnlyModelViewSet):
    serializer_class = ProductBrandSerializer
    queryset = ProductBrand.objects.filter(is_active=True)


class ProductGalleryViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = ProductBrandSerializer
    queryset = ProductBrand.objects.filter(is_active=True)
