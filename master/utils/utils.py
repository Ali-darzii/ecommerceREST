def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class NotAuthenticated(BasePermission):
    """
    Allows access only to not authenticated clients.
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return False
        return True
