import simplejson
from celery import shared_task
from django.conf import settings
import requests
from rest_framework import status

from auth_module.models import UserLogins, UserIP, UserDevice
from utils.utils import get_client_ip


@shared_task(queue="tasks")
def send_message(phone_no, token):
    url = settings.SMS_SERVICE_DOMAIN
    api_key = settings.SMS_SERVICE_API_KEY
    payload_json = {
        "OtpId": "805",
        "ReplaceToken": [str(token)],
        "MobileNumber": str(phone_no)
    }

    for i in range(3):
        request = requests.post(url=url, json=payload_json, headers={"apiKey": api_key})
        request_response = simplejson.loads(request.text)
        if request.status_code == status.HTTP_200_OK:
            if request_response["success"] is True:
                return {"OTP": True}
        return {"OTP": False}


@shared_task(queue="tasks")
def user_created(request, user):
    user_login = UserLogins.objects.create(user=user, no_logins=1)
    UserIP.objects.create(user_login=user_login, ip=get_client_ip(request))
    device = UserDevice.get_user_device(request, user)
    device.save()
    return {"user_created": True}


@shared_task(queue="tasks")
def user_logged_in(request, user):
    try:
        user_login = UserLogins.objects.get(user=user)
        user_login.no_logins += 1
        user_login.save()
        user_login.ips.ip = get_client_ip(request)
        user_login.ips.save()
        user_login.devices.get_user_device(request, user)
        user_login.devices.save()
        return {"user_logged_in": True}
    except UserLogins.DoesNotExist:
        return {"user_logged_in": False}


@shared_task(queue="tasks")
def user_logged_in_failed(request, user):
    try:
        user_login = UserLogins.objects.get(user=user)
        user_login.failed_attempts += 1
        user_login.save()
        user_login.ips.ip = get_client_ip(request)
        user_login.ips.failed = True
        user_login.ips.save()
        user_login.devices.get_user_device(request, user)
        user_login.devices.save()
        return {"user_logged_in_failed": True}
    except UserLogins.DoesNotExist:
        return {"user_logged_in_failed": False}

