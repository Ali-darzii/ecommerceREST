from django.urls import path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()

router.register(r'products', views.ProductViewSet, basename='products')
router.register(r'products-category', views.ProductCategoryViewSet, basename='products-category')
router.register(r'products-brand', views.ProductBrandViewSet, basename='products-brand')

urlpatterns = [] + router.urls
