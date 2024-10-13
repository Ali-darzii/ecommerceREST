from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from auth_module.models import User, UserProfile
from auth_module.tasks import send_message, user_login_signal, user_login_failed_signal, user_created_signal
from utils.Responses import ErrorResponses, NotAuthenticated
from utils.utils import otp_code_generator, create_user_agent
from django.conf import settings
from auth_module.serializers import OTPSerializer, SetPasswordSerializer, LoginSerializer
from utils.utils import get_client_ip
from django.utils import timezone
from rest_framework import status
from django.core.cache import cache as redis
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, throttle_classes, action
from throttling import OTPPostThrottle, OTPPutThrottle, SetPasswordThrottle, LoginThrottle


class OTPRegisterView(APIView):
    """ Register """

    permission_classes = [NotAuthenticated]

    @action(methods=["POST"], detail=True, throttle_classes=[OTPPostThrottle])
    def post(self, request):
        """  Send OTP """
        serializer = OTPSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        phone_no = serializer.validated_data.get("phone_no")
        otp_exp = settings.OTP_TIME_EXPIRE_DATA
        token = otp_code_generator()

        # Handle test user login
        if phone_no.startswith("0950"):
            # This is test user
            token = "5555"

            redis.set(f'{phone_no}_otp', token)
            redis.expire(f'{phone_no}_otp', otp_exp)
            return Response(data={'detail': 'Sent.'}, status=status.HTTP_201_CREATED)

        last_code = redis.get(f"{phone_no}_otp")
        if last_code is None:
            redis.set(f'{phone_no}_otp', token)
            redis.expire(f'{phone_no}_otp', otp_exp)
        else:
            return Response(data={'detail': "not sent, please wait."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        send_message.apply_async(args=(phone_no, token))

        return Response(data={"detail": "Sent."}, status=status.HTTP_201_CREATED)

    @action(methods=["PUT"], detail=True, throttle_classes=[OTPPutThrottle])
    def put(self, request):
        """ Check OTP and create_user or user(not active) """
        serializer = OTPSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        phone_no = serializer.validated_data.get('phone_no')
        tk = serializer.validated_data.get('tk')
        token = redis.get(f'{phone_no}_otp')

        # expire time and token match check
        if token is None or int(token) != int(tk):
            return Response(data=ErrorResponses.TOKEN_IS_EXPIRED_OR_INVALID, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(phone_no=phone_no)
            if not user.is_active:
                return Response(data={"data": "User is not active.", "user_id": user.id}, status=status.HTTP_200_OK)
            return Response(data={ErrorResponses.WRONG_LOGIN_DATA})

        except User.DoesNotExist:
            user = User.objects.create(phone_no=phone_no, is_active=False)
            user_created_signal.apply_async(args=(create_user_agent(request), get_client_ip(request), user.id))
            return Response(data={"data": "User created.", "user_id": user.id}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@throttle_classes([SetPasswordThrottle])
def set_password(request, pk=None):
    """ for first time, SetPassword and login """

    if request.headers.get("Authorization") is not None:
        return Response(data={"detail": "Client could not be authenticated."}, status=status.HTTP_401_UNAUTHORIZED)

    if pk is None:
        return Response(data={"detail": "Need pk parameter in url."}, status=status.HTTP_400_BAD_REQUEST)

    serializer = SetPasswordSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    password = serializer.validated_data.get('password')
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(data=ErrorResponses.OBJECT_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
    if user.is_active:
        user_login_failed_signal.apply_async(args=(create_user_agent(request), get_client_ip(request), user.id))
        return Response(data=ErrorResponses.WRONG_LOGIN_DATA, status=status.HTTP_400_BAD_REQUEST)
    user.is_active = True
    user.set_password(password)
    user.last_login = timezone.now()
    user.save()
    user_login_signal.apply_async(args=(create_user_agent(request), get_client_ip(request), user.id,))
    UserProfile.objects.create(user=user)
    data = {
        "access_token": str(AccessToken.for_user(user)),
        "refresh_token": str(RefreshToken.for_user(user)),
    }

    return Response(data=data, status=status.HTTP_200_OK)


# todo:need test
class UserLoginView(APIView):
    permission_classes = [NotAuthenticated]
    throttle_classes = [LoginThrottle]

    def post(self, request):
        """ User Login (phone_no) """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_no = serializer.validated_data.get("phone_no")
        password = serializer.validated_data.get("password")
        try:
            user = User.objects.get(phone_no=phone_no)
        except User.DoesNotExist:
            return Response(data=ErrorResponses.WRONG_LOGIN_DATA, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active or not user.check_password(password):
            user_login_failed_signal.apply_async(args=(create_user_agent(request), get_client_ip(request), user.id))
            return Response(data=ErrorResponses.WRONG_LOGIN_DATA, status=status.HTTP_400_BAD_REQUEST)

        user_login_signal.apply_async(args=(create_user_agent(request), get_client_ip(request), user.id,))
        data = {
            "access_token": str(AccessToken.for_user(user)),
            "refresh_token": str(RefreshToken.for_user(user)),
        }

        return Response(data=data, status=status.HTTP_200_OK)

    def put(self, request):
        """ User Login (email) """
        pass


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
        """ user remove """
        request.user.delete()
        return Response(data={"data": "user deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
