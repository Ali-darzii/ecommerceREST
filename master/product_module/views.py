from product_module.models import Product, ProductCategory, ProductBrand, Comment
from product_module.serializers import ProductSerializer, ProductCategorySerializer, ProductBrandSerializer, \
    CommentSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count
from product_module.tasks import product_visited
from utils.filters import ProductFilter
from rest_framework.response import Response
from utils.utils import get_client_ip
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ValidationError


class ProductViewSet(ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'visit_count']

    def get_queryset(self):
        return Product.objects.filter(is_active=True).annotate(visit_count=Count("productvisit"))

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        product_visited.apply_async(args=(instance.id, get_client_ip(request), request.user.id))
        serializer = self.get_serializer(instance)
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


class CommentViewSet(CreateModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def perform_create(self, serializer):
        if serializer.instance.user != self.request.user:
            raise ValidationError("You can't create another user's comment.")
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise ValidationError("You can't update another user's comment.")
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise ValidationError("You can't  remove another user's comment")
        instance.delete()


@api_view(['POST'])
def like_comment(request, product_id):
    pass


@api_view(['POST'])
def dislike_comment(request, product_id):
    pass
