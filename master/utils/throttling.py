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