from django.urls import path
from . import views

urlpatterns = [
    path("auth/", views.PhoneAuthentication.as_view())
]
