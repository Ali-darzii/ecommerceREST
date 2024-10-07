from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from auth_module.models import User, PhoneMessage
from utils.ErrorResponses import ErrorResponses

from auth_module.serializers import RegisterRequestSerializer, LoginRequestSerializer
from utils.utils import NotAuthenticated
from django.utils import timezone
from rest_framework import status


# todo:need test


class EmailAuthentication(APIView):
    permission_classes = (NotAuthenticated,)

    def post(self, request):
        """ user register with phone and password """
        serializer = RegisterRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User(is_active=True)
        user.set_password(serializer.validated_data["password"])
        user.last_login = timezone.now()
        user.save()
        PhoneMessage.objects.create(user_id=user.id, phone_no=serializer.validated_data["phone_no"])
        # todo: celery for user logged in
        data = {
            "access_token": str(AccessToken.for_user(user)),
            "refresh_token": str(RefreshToken.for_user(user)),
        }
        return Response(data, status=status.HTTP_201_CREATED)

    def put(self, request):
        """ user login with phone and password """
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # phone exist
        try:
            phone = PhoneMessage.objects.get(phone_no=serializer.validated_data["phone_no"])
        except PhoneMessage.DoesNotExist:
            return Response(ErrorResponses.WRONG_LOGIN_DATA)
        # password check
        if not phone.user.check_password(serializer.validated_data["password"]):
            return Response(ErrorResponses.WRONG_LOGIN_DATA)
        # todo: celery for user logged in
        data = {
            "access_token": str(AccessToken.for_user(phone.user)),
            "refresh_token": str(RefreshToken.for_user(phone.user)),
        }
        return Response(data, status=status.HTTP_200_OK)
