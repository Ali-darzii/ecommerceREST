from django.urls import path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()

router.register(r'products', views.ProductViewSet, basename='products')
router.register(r'products-category', views.ProductCategoryViewSet, basename='products-category')
router.register(r'products-brand', views.ProductBrandViewSet, basename='products-brand')
router.register(r'products-comment', views.CommentViewSet, basename='products-comment')

urlpatterns = [
    path("like-disslike/<int:comment_id>", views.LikeDislikeAPIView.as_view(), name="like_dislike")

] + router.urls
