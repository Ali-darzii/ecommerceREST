from django.urls import path
from . import views
from custom_jwt import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path("auth/otp/", views.OTPRegisterAuthentication.as_view(), name='otp'),
    path("auth/set-password/", views.set_password, name='set_password'),
    path('auth/logout/', views.UserLogoutView.as_view(), name='logg_out'),
]
