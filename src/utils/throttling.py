from rest_framework.throttling import SimpleRateThrottle

class BaseThrottle(SimpleRateThrottle):

    def get_ident(self, request):
        xci = request.META.get('X-Client-IP', None)
        return xci

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            return None  # Only throttle unauthenticated requests.

        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }


class OTPPostThrottle(BaseThrottle):
    scope = 'phone_otp_post'


class OTPPutThrottle(BaseThrottle):
    scope = 'phone_otp_put'


class SetPasswordThrottle(BaseThrottle):
    scope = 'set_password'


class PhoneLoginThrottle(BaseThrottle):
    scope = 'phone_login'


class EmailLoginThrottle(BaseThrottle):
    scope = 'email_login'


class EmailSendCodeThrottle(BaseThrottle):
    scope = 'email_send_code'


class EmailCheckCodeThrottle(BaseThrottle):
    scope = 'email_check_code'
