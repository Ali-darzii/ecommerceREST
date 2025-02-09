from rest_framework.permissions import BasePermission

class NotAuthenticated(BasePermission):
    message = "Client could not be authenticated."

    def has_permission(self, request, view):
        return True if request.headers.get("Authorization") is None else False


class IsOwner(BasePermission):
    """
    Allows users to retrieve or update their own data
    """

    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id