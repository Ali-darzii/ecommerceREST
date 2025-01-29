from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from auth_module.models import User, UserProfile
from auth_module.tasks import send_message, user_login_signal, user_login_failed_signal, user_created_signal, send_email
from order_module.models import Order
from utils import document
from utils.Responses import ErrorResponses, NotAuthenticated
from utils.utils import otp_code_generator, create_user_agent
from django.conf import settings
from auth_module.serializers import PhoneOTPSerializer, SetPasswordSerializer, LoginSerializer, EmailSerializer, \
    UserProfileSerializer, UserSerializer
from utils.utils import get_client_ip
from django.utils import timezone
from rest_framework import status
from django.core.cache import cache as redis
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, throttle_classes, action, permission_classes
from utils.throttling import OTPPostThrottle, OTPPutThrottle, SetPasswordThrottle, PhoneLoginThrottle, \
    EmailLoginThrottle, EmailSendCodeThrottle, EmailCheckCodeThrottle
from django.utils.crypto import get_random_string
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class PhoneOTPRegisterView(APIView):
    """ Register """

    permission_classes = [NotAuthenticated]

    @swagger_auto_schema(operation_id="send_phone_msg",
                         responses={
                             201: document.OTPSuccessful,  # Define success response
                             400: openapi.Response(
                                 description="Bad Format",
                                 schema=document.general_error_schema,),
                             429: openapi.Response(
                                 description="Not Found",
                                 schema=document.general_error_schema),
                         },
                         request_body=openapi.Schema(
                             type=openapi.TYPE_OBJECT,
                             required=['phone_no'],
                             properties={
                                 'phone_no': openapi.Schema(type=openapi.TYPE_STRING),
                             })
                         )
    def post(self, request):

        """  Send OTP """
        serializer = PhoneOTPSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        phone_no = serializer.validated_data.get("phone_no")
        otp_exp = settings.OTP_TIME_EXPIRE_DATA
        # Handle test user login
        if phone_no.startswith("0950"):
            # This is test user
            token = "5555"

            redis.set(f'{phone_no}_otp', token)
            redis.expire(f'{phone_no}_otp', otp_exp)
            return Response(data={'detail': 'Sent.'}, status=status.HTTP_201_CREATED)

        last_code = redis.get(f"{phone_no}_otp")
        if last_code is None:
            token = otp_code_generator()
            redis.set(f'{phone_no}_otp', token)
            redis.expire(f'{phone_no}_otp', otp_exp)
        else:
            return Response(data={'detail': "not sent, please wait."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        send_message.apply_async(args=(phone_no, token))

        return Response(data={"detail": "Sent."}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(operation_id="send_phone_msg",
                         responses={
                             201: document.OTPCheckSuccessful,
                             200: document.OTPCheckNotActiveSuccessful,
                             400: openapi.Response(
                                 description="Bad Format",
                                 schema=document.general_error_schema,),
                             429: openapi.Response(
                                 description="Not Found",
                                 schema=document.general_error_schema),
                         },
                         request_body=openapi.Schema(
                             type=openapi.TYPE_OBJECT,
                             required=['phone_no', "tk"],
                             properties={
                                 'phone_no': openapi.Schema(type=openapi.TYPE_STRING),
                                 'tk': openapi.Schema(type=openapi.TYPE_STRING),
                             })
                         )
    def put(self, request):
        """ Check OTP and create_user or user(not active) """
        serializer = PhoneOTPSerializer(data=request.data, context={"request": request})
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

    def get_throttles(self):
        if self.request.method == 'POST':
            self.throttle_classes = [OTPPostThrottle]
        elif self.request.method == 'PUT':
            self.throttle_classes = [OTPPutThrottle]
        return super(PhoneOTPRegisterView, self).get_throttles()


@api_view(['POST'])
@permission_classes([NotAuthenticated])
@throttle_classes([SetPasswordThrottle])
def set_password(request, pk=None):
    """ for first time, SetPassword and login """
    if pk is None:
        return Response(ErrorResponses.MISSING_PARAMS, status=status.HTTP_400_BAD_REQUEST)

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
    Order.objects.create(user=user)
    data = {
        "access_token": str(AccessToken.for_user(user)),
        "refresh_token": str(RefreshToken.for_user(user)),
    }

    return Response(data=data, status=status.HTTP_200_OK)


class UserLoginView(APIView):
    permission_classes = [NotAuthenticated]

    def post(self, request):
        """ User Login (phone_no) """
        serializer = LoginSerializer(data=request.data, context={"request": request})
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
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")
        try:
            user = User.objects.get(email)
        except User.DoesNotExist:
            return Response(data=ErrorResponses.WRONG_LOGIN_DATA, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active or not user.check_password(password) or not user.email_activate:
            user_login_failed_signal.apply_async(args=(create_user_agent(request), get_client_ip(request), user.id))
            return Response(data=ErrorResponses.WRONG_LOGIN_DATA, status=status.HTTP_400_BAD_REQUEST)

        user_login_signal.apply_async(args=(create_user_agent(request), get_client_ip(request), user.id,))
        data = {
            "access_token": str(AccessToken.for_user(user)),
            "refresh_token": str(RefreshToken.for_user(user)),
        }

        return Response(data=data, status=status.HTTP_200_OK)

    def get_throttles(self):
        if self.request.method == 'POST':
            self.throttle_classes = [PhoneLoginThrottle]
        elif self.request.method == 'PUT':
            self.throttle_classes = [EmailLoginThrottle]
        return super(UserLoginView, self).get_throttles()


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


class EmailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, code=None):
        """ Send Email Activation code """
        if code is not None:
            return Response(ErrorResponses.BAD_FORMAT, status=status.HTTP_400_BAD_REQUEST)
        serializer = EmailSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        code_expire = settings.EMAIL_CODE_TIME_OUT
        active_code = redis.get(f"{email}_code")
        if active_code is None:
            code = get_random_string(72)
            redis.set(f"{email}_code", code)
            redis.expire(f"{email}_code", code_expire)
        else:
            return Response(data={'detail': "not sent, please wait."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        url = f"you need to click {settings.ALLOWED_HOSTS[0]}/api/v1/auth/email_code/{code} to activate your email."
        send_email.aplly_async(args=(email, "Ecommerce Email Verification", url))

    def get(self, request, code=None):
        """ Check Email Activation code """
        if code is None:
            return Response(ErrorResponses.MISSING_PARAMS, status=status.HTTP_400_BAD_REQUEST)
        serializer = EmailSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        activate_code = redis.get(f"{email}_code")
        if activate_code is None or activate_code != code:
            return Response(data=ErrorResponses.CODE_IS_EXPIRED_OR_INVALID, status=status.HTTP_400_BAD_REQUEST)
        request.user.email_activate = True
        return Response(data={"detail": "Email activated."}, status=status.HTTP_200_OK)

    def get_throttles(self):
        if self.request.method == "POST":
            self.throttle_classes = EmailSendCodeThrottle
        if self.request.method == "GET":
            self.throttle_classes = EmailCheckCodeThrottle
        return super(EmailView, self).get_throttles()


class UserProfileViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()
    lookup_field = 'user_id'

    def perform_create(self, serializer):
        queryset = UserProfile.objects.filter(user=self.request.user)
        if queryset.exists():
            raise ValidationError('You already have a profile.')
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise ValidationError("You cannot update another user's profile.")
        serializer.save(user=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def UserInformation(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
