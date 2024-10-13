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


# parse_rate -> (<allowed number of requests>, <period of time in seconds>)
class OTPPostThrottle(BaseThrottle):
    scope = 'phone_login_post'

    def parse_rate(self, rate):
        return (5, 120)


class OTPPutThrottle(BaseThrottle):
    scope = 'phone_login_put'

    def parse_rate(self, rate):
        return (10, 60)


class SetPasswordThrottle(BaseThrottle):
    scope = 'set_password'

    def parse_rate(self, rate):
        return (5, 60)


class LoginThrottle(BaseThrottle):
    # phone or email
    scope = 'login'

    def parse_rate(self, rate):
        return (10, 60)
