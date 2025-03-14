from rest_framework.views import APIView

from product_module.models import Product, ProductCategory, ProductBrand, Comment
from product_module.serializers import ProductCategorySerializer, ProductBrandSerializer, \
    CommentSerializer, ProductDetailSerializer, ProductListSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework import mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count
from product_module.tasks import product_visited, comment_created
from utils.filters import ProductFilter
from rest_framework.response import Response

from utils.permission import IsOwner
from utils.utils import get_client_ip
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ValidationError
from utils.Responses import ErrorResponses
from rest_framework import status


class ProductViewSet(ReadOnlyModelViewSet):
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'visit_count']

    def get_queryset(self):
        return Product.active_objects.annotate(visit_count=Count("productvisit"))

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        product_visited.apply_async(args=(instance.id, get_client_ip(request), request.user.id))
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductListSerializer


class ProductCategoryViewSet(ReadOnlyModelViewSet):
    serializer_class = ProductCategorySerializer
    queryset = ProductCategory.active_objects.all()


class ProductBrandViewSet(ReadOnlyModelViewSet):
    serializer_class = ProductBrandSerializer
    queryset = ProductBrand.active_objects.all()


class ProductGalleryViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    serializer_class = ProductBrandSerializer
    queryset = ProductBrand.active_objects.all()


class CommentViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, ReadOnlyModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    lookup_url_kwarg = "product_id"

    def get_permissions(self):
        if self.action == "create" or self.action == "destroy":
            self.permission_classes = [IsOwner, IsAuthenticated]

    # def perform_create(self, serializer):
    #     if serializer.validated_data.get("user") != self.request.user:
    #         raise ValidationError("You can't create another user's comment.")
    #     serializer.save()

    # def perform_destroy(self, instance):
    #     if instance.user != self.request.user:
    #         raise ValidationError("You can't  remove another user's comment")
    #     instance.delete()


class LikeOrDisLikeComment(APIView):
    permission_classes = [IsAuthenticated]

    def get_comment(self):
        try:
            return Comment.objects.get(pk=self.kwargs.get("comment_id"))
        except Comment.DoesNotExist:
            return Response(data=ErrorResponses.OBJECT_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, comment_id):
        """ add Like or remove Like a comment  """
        comment = self.get_comment()
        serializer = CommentSerializer(instance=comment)
        if request.user in comment.likes.user.all():
            comment.likes.user.remove(request.user)
            comment.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        comment.likes.user.add(request.user)
        comment.dislikes.user.remove(request.user)
        comment.diss_like = comment.dislikes.user.count()
        comment.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request, comment_id):
        """ add Dislike or remove Dislike a comment """
        comment = self.get_comment()
        serializer = CommentSerializer(instance=comment)
        if request.user in comment.dislikes.user.all():
            comment.dislikes.user.remove(request.user)
            comment.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        comment.dislikes.user.add(request.user)
        comment.likes.user.remove(request.user)
        comment.like = comment.likes.user.count()
        comment.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def like_comment(request, deside, comment_id):
    """ Like or Dislike a comment """
    try:
        comment = Comment.objects.get(pk=comment_id)
    except Comment.DoesNotExist:
        return Response(data=ErrorResponses.OBJECT_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
    serializer = CommentSerializer(comment)
    if deside == "like":
        if request.user in comment.likes.user.all():
            # remove his like
            comment.likes.user.remove(request.user)
            comment.like = comment.like - 1
            comment.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        # submit his like
        comment.likes.user.add(request.user)
        comment.dislikes.user.remove(request.user)
        comment.like += 1
        comment.diss_like = comment.dislikes.user.count()
        comment.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    if deside == "dislike":
        if request.user in comment.dislikes.user.all():
            # remove his dislike
            comment.dislikes.user.remove(request.user)
            comment.diss_like -= 1
            comment.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        # submit his dislike
        comment.dislikes.user.add(request.user)
        comment.likes.user.remove(request.user)
        comment.diss_like += 1
        comment.like = comment.likes.user.count()
        comment.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    return Response(data=ErrorResponses.BAD_FORMAT, status=status.HTTP_404_NOT_FOUND)
