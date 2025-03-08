import re

from django.contrib.auth.signals import user_login_failed
from rest_framework import serializers
from auth_module.models import User, UserProfile
from order_module.serializers import OrderSerializer
from order_module.views import payment
from utils.Responses import ErrorResponses
from utils.utils import create_user_agent, get_client_ip
from .tasks import user_login_failed_signal


class PhoneSendOTPSerializer(serializers.Serializer):
    phone_no = serializers.CharField(max_length=11, min_length=11)

    def validate_phone_no(self, phone_no):
        if not re.match(r'^09\d{9}$', phone_no):
            raise serializers.ValidationError(detail=ErrorResponses.BAD_FORMAT)
        try:
            user = User.objects.get(phone_no=phone_no)
            user_login_failed.send(sender=self.__class__, request=self.context["request"], user=user)
            raise serializers.ValidationError("Phone number already taken.")
        except User.DoesNotExist:
            return phone_no


class PhoneCheckOTPSerializer(PhoneSendOTPSerializer):
    tk = serializers.CharField(max_length=5, min_length=5)
    password = serializers.CharField(max_length=128, min_length=8)

    def validate_tk(self, tk):
        if not tk.isnumeric():
            raise serializers.ValidationError("tk is invalid")
        return tk

    def validate_password(self, password):
        if not re.fullmatch(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", password):
            raise serializers.ValidationError("Password must contain at least one number and one letter.")
        return password


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, required=False)
    phone_no = serializers.CharField(max_length=11, required=False)
    password = serializers.CharField(max_length=128)

    def validate(self, attrs):
        if self.context["request"].method == "POST":
            if attrs.get("phone_no") is None:
                raise serializers.ValidationError(detail=ErrorResponses.MISSING_PARAMS)
        elif attrs.get("email") is None:
            raise serializers.ValidationError(detail=ErrorResponses.MISSING_PARAMS)
        return super(LoginSerializer, self).validate(attrs)


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=225, required=False)

    def email_validate(self, email):
        request = self.context["request"]
        if request.user.email != email:
            serializers.ValidationError(ErrorResponses.MISSING_PARAMS)
        if request.user.email_active:
            serializers.ValidationError("Email already activate.")
        return email

    def validate(self, attrs):
        if self.context["request"].method == "POST":
            if attrs.get("email") is None:
                raise serializers.ValidationError(detail=ErrorResponses.MISSING_PARAMS)
        return super(EmailSerializer, self).validate(attrs)


class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField()

    class Meta:
        model = UserProfile
        fields = ['avatar', 'address', 'city', 'postal_code']


class UserFullInformationSerializer(serializers.ModelSerializer):
    phone_no = serializers.CharField(max_length=11, min_length=11, read_only=True)
    email = serializers.EmailField(max_length=225)
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone_no", "email", "profile"]


class UserPublicInformationSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField()

    class Meta:
        model = User
        fields = ["email", "first_name", "avatar"]
