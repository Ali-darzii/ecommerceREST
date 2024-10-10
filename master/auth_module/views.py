from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from auth_module.models import User, UserProfile
from auth_module.tasks import send_message, user_logged_in
from utils.ErrorResponses import ErrorResponses
from utils.utils import otp_code_generator
from django.conf import settings
from auth_module.serializers import OTPRequestSerializer, SetPasswordSerializer
from utils.utils import NotAuthenticated
from django.utils import timezone
from rest_framework import status
from django.core.cache import cache as redis
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view


# todo:all api need test
class OTPRegisterAuthentication(APIView):
    """ Register """

    # permission_classes = (NotAuthenticated,)

    def post(self, request):
        """  Send OTP """
        if request.user.is_authenticated:
            return Response(data="User should not be authenticated.", status=status.HTTP_400_BAD_REQUEST)
        serializer = OTPRequestSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        phone_no = serializer.validated_data.get("phone_no")
        otp_exp = settings.OTP_TIME_EXPIRE_DATA
        token = otp_code_generator()

        last_code = redis.get(f"{phone_no}_otp")
        if last_code is None:
            redis.set(f'{phone_no}_otp', token)
            redis.expire(f'{phone_no}_otp', otp_exp)
        else:
            return Response(data={'detail': "not sent, please wait."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        send_message.apply_async(args=(phone_no, token))

        return Response(data={"detail": "Sent"}, status=status.HTTP_201_CREATED)

    def put(self, request):
        """ Check OTP and create_user or user(not active) """
        if request.user.is_authenticated:
            return Response(data="User should not be authenticated.", status=status.HTTP_400_BAD_REQUEST)
        serializer = OTPRequestSerializer(request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer = OTPRequestSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        phone_no = serializer.validated_data.get('phone_no')
        tk = serializer.validated_data.get('tk')
        token = redis.get(f'{phone_no}_otp')

        # expire time and token match check
        if token is None or int(token) != int(tk):
            return Response(data=ErrorResponses.TOKEN_IS_EXPIRED_OR_INVALID, status=status.HTTP_400_BAD_REQUEST)
        try:
            User.objects.get(phone_no=phone_no, is_active=False)
            return Response(data={"data": "User is not active."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            User.objects.create(phone_no=phone_no, is_active=False)
            return Response(data={"data": "User created."}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def set_password(request):
    """ SetPassword and login """
    if request.user.is_authenticated:
        return Response(data="User should not be authenticated.", status=status.HTTP_400_BAD_REQUEST)
    serializer = SetPasswordSerializer(request.data)
    serializer.is_valid(raise_exception=True)
    phone_no = serializer.validated_data.get('phone_no')
    password = serializer.validated_data.get('password')
    try:
        user = User.objects.get(phone_no=phone_no, is_active=False)
    except User.DoesNotExist:
        return Response(data=ErrorResponses.OBJECT_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
    user.set_password(password)
    user.last_login = timezone.now()
    user.save()
    user_logged_in(request, user).apply_async(priority=8)
    UserProfile.objects.create(user=user)
    data = {
        "access_token": str(AccessToken.for_user(user)),
        "refresh_token": str(RefreshToken.for_user(user)),
    }

    return Response(data=data, status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """ user logout """
        try:
            refresh_token = request.data['refresh_token']
            tk = RefreshToken(refresh_token)
            tk.blacklist()
            return Response(data='Successfully logged out.', status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(data=ErrorResponses.TOKEN_IS_EXPIRED_OR_INVALID, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        request.user.is_active = False
        request.user.user_profiles.delete()
        return Response(data={"data": "user deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
