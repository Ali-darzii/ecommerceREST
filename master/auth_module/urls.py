from django.urls import path
from . import views

urlpatterns = [
    path("auth/otp/", views.OTPRegisterView.as_view(), name="otp"),
    path("auth/login/", views.UserLoginView.as_view(), name="logg_in"),
    path("auth/login/<int:pk>", views.UserLoginView.as_view(), name="logg_in_post"),
    path("auth/logout/", views.UserLogoutView.as_view(), name="logg_out"),
]
