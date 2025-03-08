from rest_framework import serializers
from drf_yasg import openapi

general_error_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'detail': openapi.Schema(type=openapi.TYPE_STRING),
        'error_code': openapi.Schema(type=openapi.TYPE_INTEGER),
    }
)


class OTPSuccessful(serializers.Serializer):
    detail = serializers.CharField(default="Sent.")


class OTPCheckSuccessful(serializers.Serializer):
    access_token = serializers.CharField(default="User created. ")
    refresh_token = serializers.CharField(default="User created.")
    user_id = serializers.IntegerField()


class OTPCheckNotActiveSuccessful(serializers.Serializer):
    data = serializers.CharField(default="User is not active.")
    user_id = serializers.IntegerField()
