from django.urls import path
from . import views

urlpatterns = [
    path("make-order/<str:deside>/<int:order_detail>/", views.MakeOrderAPIView, name="order"),
    path("make-order/<str:deside>/<int:proudct>/", views.MakeOrderAPIView, name="order"),

]
