from django.urls import path
from . import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'profile', views.UserProfileViewSet, basename='projects')

urlpatterns = [
    path("register/otp/", views.PhoneOTPRegisterView.as_view(), name="otp"),
    path("login/", views.UserLoginView.as_view(), name="logg_in"),
    path("logout/", views.UserLogoutView.as_view(), name="logg_out"),
    path("send_mail/", views.EmailView.as_view(), name="send_mail"),
    path("send_mail/<str:code>/", views.EmailView.as_view(), name="send_mail_get"),
    path("user-information/", views.UserInformation, name="user_information"),

] + router.urls
