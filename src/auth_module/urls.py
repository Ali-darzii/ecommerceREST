from django.urls import path
from . import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'profile', views.UserProfileView, basename='user_profile')
router.register(r'user-public-information', views.UserPublicInformationView, basename='user_public')
router.register(r'user-full-information', views.UserFullInformationView, basename='user_full')

urlpatterns = [
    path("register/otp/", views.PhoneOTPRegisterView.as_view(), name="otp"),
    path("login/", views.UserLoginView.as_view(), name="logg_in"),
    path("logout/", views.UserLogoutView.as_view(), name="logg_out"),
    path("send_mail/", views.EmailView.as_view(), name="send_mail"),
    path("send_mail/<str:code>/", views.EmailView.as_view(), name="send_mail_get"),
] + router.urls
