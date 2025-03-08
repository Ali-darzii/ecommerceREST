from django.urls import path
from . import views

urlpatterns = [
    path("make-order/", views.MakeOrderAPIView.as_view(), name="order"),
    path("make-order/<str:deside>/<int:order_detail_id>/", views.MakeOrderAPIView.as_view(), name="order"),
    path("make-order/<str:deside>/<int:proudct_id>/", views.MakeOrderAPIView.as_view(), name="order"),
]
