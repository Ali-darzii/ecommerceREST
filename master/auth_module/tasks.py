import simplejson
from celery import shared_task
from django.conf import settings
import requests
from rest_framework import status
from utils.utils import get_sms_text_message


@shared_task(queue="tasks")
def send_message(phone_no, token):
    # sms_text_message = get_sms_text_message(str(token))
    # sender_number = settings.SMS_SERVICE_NUMBER
    url = settings.SMS_SERVICE_DOMAIN
    api_key = settings.SMS_SERVICE_API_KEY
    payload_json = {
        "OtpId": "805",
        "ReplaceToken": [token],
        "MobileNumber": phone_no
    }

    for i in range(3):
        request = requests.post(url=url, json=payload_json, headers={"apiKey": api_key})
        request_response = simplejson.loads(request.text)
        if request.status_code == status.HTTP_200_OK:
            if request_response["success"] is True:
                break


@shared_task(queue="tasks")
def user_logged_in():
    pass
