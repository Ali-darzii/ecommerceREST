from rest_framework.permissions import BasePermission


class ErrorResponses:
    BAD_FORMAT = {'detail': 'BAD_FORMAT', 'error_code': 1}
    OBJECT_NOT_FOUND = {'detail': 'OBJECT_NOT_FOUND', 'error_code': 2}
    WRONG_LOGIN_DATA = {'detail': 'PHONE_OR_PASSWORD_IS_INCORRECT', 'error_code': 3}
    MISSING_PARAMS = {'detail': 'MISSING_PARAMS', 'error_code': 4}
    TOKEN_IS_EXPIRED_OR_INVALID = {'detail': 'TOKEN_IS_EXPIRED_OR_INVALID', 'error_code': 5}


class NotAuthenticated(BasePermission):
    message = "Client could not be authenticated."

    def has_permission(self, request, view):
        if request.headers.get("Authorization") is not None:
            return False
        return True
