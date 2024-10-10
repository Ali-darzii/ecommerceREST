import random
from rest_framework.permissions import BasePermission
import requests
from django.conf import settings
from rest_framework import status


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


def send_message(phone_no, token):
    url = settings.SMS_SERVICE_DOMAIN
    sender_number = settings.SMS_SERVICE_NUMBER
    api_key = settings.SMS_SERVICE_API_KEY
    sms_text_message = get_sms_text_message(str(token))
    payload_json = {
        "Message": sms_text_message,
        "SenderNumber": sender_number,
        "MobileNumber": phone_no
    }

    for i in range(3):
        request = requests.post(url=url, json=payload_json, headers={"apiKey": api_key})
        if request.status_code == status.HTTP_200_OK:
            print(request.content)
            print(request.status_code)
            break
