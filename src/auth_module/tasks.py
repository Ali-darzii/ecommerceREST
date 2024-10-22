import simplejson
from celery import shared_task
from django.conf import settings
import requests
from rest_framework import status
from auth_module.models import UserLogins, UserIP, UserDevice
from django.core.mail import send_mail as django_send_email


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
def user_created_signal(user_agent, user_ip, user_id):
    user_logins = UserLogins.objects.create(user_id=user_id)
    UserIP.objects.create(user_logins=user_logins, ip=user_ip)
    device = UserDevice.get_user_device(user_agent, user_logins.id)
    device.save()
    return {"user_created": True}


@shared_task(queue="tasks")
def user_login_signal(user_agent, user_ip, user_id):
    try:
        user_logins = UserLogins.objects.get(user_id=user_id)
        user_logins.no_logins += 1
        user_logins.save()
        UserIP.objects.create(user_logins=user_logins, ip=user_ip)
        devices = UserDevice.get_user_device(user_agent, user_logins.id)
        devices.save()
        return {"user_logged_in": True}
    except UserLogins.DoesNotExist:
        return {"user_logged_in": False}


@shared_task(queue="tasks")
def user_login_failed_signal(user_agent, user_ip, user_id):
    try:
        user_logins = UserLogins.objects.get(user_id=user_id)
        user_logins.failed_attempts += 1
        user_logins.save()
        UserIP.objects.create(user_logins=user_logins, ip=user_ip, failed=True)
        device = UserDevice.get_user_device(user_agent, user_logins.id)
        device.save()

        return {"user_logged_in_failed": True}
    except UserLogins.DoesNotExist:
        return {"user_logged_in_failed": False}


@shared_task(queue="tasks")
def send_email(email, subject, body):
    for i in range(2):
        try:
            host_email = settings.EMAIL_HOST_USER
            django_send_email(subject, body, host_email, [email], fail_silently=False)
            break
        except Exception as e:
            pass
