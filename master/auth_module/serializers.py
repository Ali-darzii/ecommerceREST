import re

from rest_framework import serializers
from auth_module.models import User, PhoneMessage
from utils.ErrorResponses import ErrorResponses


class RegisterRequestSerializer(serializers):
    phone_no = serializers.CharField(required=True, max_length=11)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate_phone_no(self, phone_no):
        if not re.match(r'^09\d{9}$', phone_no):
            raise serializers.ValidationError(detail=ErrorResponses.BAD_FORMAT)
        try:
            PhoneMessage.objects.get(phone_no=phone_no)
            raise serializers.ValidationError("Phone number already taken.")
        except PhoneMessage.DoesNotExist:
            return phone_no

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.findall(r"^\d+$", value):
            raise serializers.ValidationError("Password must contain number too.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Password confirm is not match")
        return attrs


class LoginRequestSerializer(serializers):
    phone_no = serializers.CharField(required=True, max_length=11)
    password = serializers.CharField(required=True)

