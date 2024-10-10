from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from auth_module.models import User
from auth_module.tasks import send_message
from utils.ErrorResponses import ErrorResponses
from utils.utils import otp_code_generator
from django.conf import settings
from auth_module.serializers import OTPRequestSerializer
from utils.utils import NotAuthenticated
from django.utils import timezone
from rest_framework import status
from django.core.cache import cache as redis


# todo:need test


class PhoneAuthentication(APIView):
    permission_classes = (NotAuthenticated,)

    def post(self, request):
        """ send phone msg with db data creation """
        serializer = OTPRequestSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        phone_no = serializer.validated_data.get("phone_no")
        otp_exp = settings.OTP_TIME_EXPIRE_DATA
        token = otp_code_generator()

        last_code = redis.get(f"{phone_no}_otp")
        if not last_code:
            redis.set(f'{phone_no}_otp', token)
            redis.expire(f'{phone_no}_otp', otp_exp)
        else:
            return Response(data={'detail': "not sent, please wait."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        send_message(phone_no, token).apply_async()

        is_signup = True
        if User.objects.filter(phone_no=phone_no).exists():
            is_signup = False

        return Response(data={"detail": "Sent", "is_signup": is_signup}, status=status.HTTP_201_CREATED)

    # def put(self, request):
    #     """check if tk is correct and then create or login user"""
    #     serializer = OTPRequestSerializer(data=request.data, context={"request": request})
    #     serializer.is_valid(raise_exception=True)
    #     phone_no = serializer.validated_data.get("phone_no")
    #     tk = serializer.validated_data.get("tk")
    #     token = redis.get(f"{phone_no}_otp")
    #
    #     # phone exist
    #     # try:
    #     #     phone = PhoneMessage.objects.get(phone_no=serializer.validated_data["phone_no"])
    #     # except PhoneMessage.DoesNotExist:
    #     #     return Response(ErrorResponses.WRONG_LOGIN_DATA)
    #     # password check
    #     if not phone.user.check_password(serializer.validated_data["password"]):
    #         return Response(ErrorResponses.WRONG_LOGIN_DATA)
    #     # todo: celery for user logged in
    #     data = {
    #         "access_token": str(AccessToken.for_user(phone.user)),
    #         "refresh_token": str(RefreshToken.for_user(phone.user)),
    #     }
    #     return Response(data, status=status.HTTP_200_OK)
