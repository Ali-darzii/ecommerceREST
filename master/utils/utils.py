import random
from rest_framework.permissions import BasePermission
from django.conf import settings


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class NotAuthenticated(BasePermission):
    """
    Allows access only to not authenticated clients.
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return False
        return True


def otp_code_generator():
    return random.randint(10000, 99999)


def get_sms_text_message(token):
    phone_text_message = settings.PHONE_TEXT_MESSAGE
    return phone_text_message.replace("NUMBER", token)


def create_user_agent(request):
    return {
        "device_name": request.user_agent.device.family,
        "is_phone": request.user_agent.is_mobile,
        "browser": request.user_agent.browser.family,
        "os": request.user_agent.os.family
    }
