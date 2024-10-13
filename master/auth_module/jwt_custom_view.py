from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from auth_module.models import User
from .tasks import user_login_failed_signal, user_login_signal


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except:
            user = User.objects.filter(phone_no=request.data['phone_no']).first()
            if user:
                user_login_failed_signal(,,.apply_async(priority=5)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user_login_signal(request, serializer.user, ).apply_async(priority=5)
        return super(CustomTokenObtainPairView, self).post(request)
