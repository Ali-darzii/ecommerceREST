import re

from rest_framework import serializers
from auth_module.models import User
from utils.ErrorResponses import ErrorResponses


class OTPRequestSerializer(serializers.Serializer):
    phone_no = serializers.CharField(required=True, max_length=11)
    tk = serializers.CharField(required=False)

    def validate_tk(self, tk):
        if not tk.is_numeric():
            raise serializers.ValidationError("tk is invalid")
        return tk

    def validate_phone_no(self, phone_no):
        if not re.match(r'^09\d{9}$', phone_no):
            raise serializers.ValidationError(detail=ErrorResponses.BAD_FORMAT)
        try:
            User.objects.get(phone_no=phone_no)
            raise serializers.ValidationError("Phone number already taken.")
        except User.DoesNotExist:
            return phone_no

    def validate(self, attrs):
        if self.context['request'].method == "PUT":
            if attrs.get("token") is None:
                raise serializers.ValidationError(ErrorResponses.MISSING_PARAMS)
        attrs = super(OTPRequestSerializer, self).validate(attrs)
        return attrs


class LoginRequestSerializer(serializers.Serializer):
    phone_no = serializers.CharField(required=True, max_length=11)
    password = serializers.CharField(required=True)
