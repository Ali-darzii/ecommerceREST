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
            User.objects.get(phone_no=phone_no, is_active=True)
            raise serializers.ValidationError("Phone number already taken.")
        except User.DoesNotExist:
            return phone_no

    def validate(self, attrs):
        if self.context['request'].method == "PUT":
            if attrs.get("token") is None:
                raise serializers.ValidationError(ErrorResponses.MISSING_PARAMS)
        attrs = super(OTPRequestSerializer, self).validate(attrs)
        return attrs


class SetPasswordSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ("password", "confirm_password", "phone_no")

    def validate_phone_no(self, phone_no):
        try:
            User.objects.get(phone_no=phone_no, is_active=True)
            raise serializers.ValidationError("Phone number already taken.")
        except User.DoesNotExist:
            return phone_no

    def password_validate(self, password):
        if len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8.")
        if not re.findall("[0,9]", password):
            raise serializers.ValidationError("Password must contain at least one number.")
        return password

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Passwords don't match.")
        attrs = super(SetPasswordSerializer, self).validate(attrs)
        return attrs
