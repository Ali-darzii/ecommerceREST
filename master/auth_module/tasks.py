from celery import shared_task
from django.conf import settings
import requests
from rest_framework import status
from utils.utils import get_sms_text_message


@shared_task(queue="tasks")
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


@shared_task(queue="tasks")
def user_logged_in():
    pass
