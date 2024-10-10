from django.urls import path
from . import views


urlpatterns = [


    path("auth/otp/", views.OTPRegisterAuthentication.as_view(), name='otp'),
    path("auth/set-password/", views.set_password, name='set_password'),
    path('auth/logout/', views.UserLogoutView.as_view(), name='logg_out'),
]
