import re

from rest_framework import serializers
from auth_module.models import User, UserProfile
from utils.Responses import ErrorResponses
from utils.utils import create_user_agent, get_client_ip
from .tasks import user_login_failed_signal


class PhoneOTPSerializer(serializers.Serializer):
    phone_no = serializers.CharField(required=True, max_length=11)
    tk = serializers.CharField(required=False)

    def validate_tk(self, tk):
        if not tk.isnumeric():
            raise serializers.ValidationError("tk is invalid")
        return tk

    def validate_phone_no(self, phone_no):
        if not re.match(r'^09\d{9}$', phone_no):
            raise serializers.ValidationError(detail=ErrorResponses.BAD_FORMAT)
        try:
            user = User.objects.get(phone_no=phone_no, is_active=True)
            user_login_failed_signal.apply_async(
                args=(create_user_agent(self.context["request"]), get_client_ip(self.context["request"]), user.id,))
            raise serializers.ValidationError("Phone number already taken.")
        except User.DoesNotExist:
            return phone_no

    def validate(self, attrs):
        if self.context['request'].method == "PUT":
            if attrs.get("tk") is None:
                raise serializers.ValidationError(ErrorResponses.MISSING_PARAMS)
        attrs = super(PhoneOTPSerializer, self).validate(attrs)
        return attrs


class SetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, max_length=128)
    confirm_password = serializers.CharField(required=True, max_length=128)

    def password_validate(self, password):
        if len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8.")
        if not re.findall("[0,9]", password):
            raise serializers.ValidationError("Password must contain at least one number.")
        return password

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError("Passwords don't match.")
        attrs = super(SetPasswordSerializer, self).validate(attrs)
        return attrs


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, required=False)
    phone_no = serializers.CharField(max_length=11, required=False)
    password = serializers.CharField(max_length=128, required=True)

    def validate(self, attrs):
        if self.context["request"].method == "POST":
            if attrs.get("phone_no") is None:
                serializers.ValidationError(ErrorResponses.MISSING_PARAMS)

        if self.context["request"].method == "PUT":
            if attrs.get("email") is None:
                serializers.ValidationError(ErrorResponses.MISSING_PARAMS)
        attrs = super(LoginSerializer, self).validate(attrs)
        return attrs


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=225)

    def email_validate(self, email):
        request = self.context["request"]
        if request.user.email != email:
            serializers.ValidationError(ErrorResponses.MISSING_PARAMS)
        if request.user.email_activate:
            serializers.ValidationError("Email already activate.")

        return email


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(source="user_profiles.avatar")

    class Meta:
        model = User
        fields = ["phone_no", "email", "email_activate", "avatar"]


class UserPartialSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["phone_no", "email", "email_activate"]


class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = ['avatar', 'address', 'city', 'postal_code', 'user']

    user = UserPartialSerializer(read_only=True)
