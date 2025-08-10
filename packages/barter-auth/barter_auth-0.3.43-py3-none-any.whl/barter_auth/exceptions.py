

import typing

# import warnings
# import http
# from rest_framework.exceptions import APIException

__all__ = (
    "BAuthAPIException",
    "HTTPException",
    "NotAuthenticated" ,
    "AuthenticationFailed",
    "PermissionDenied",
    "WebSocketException",
)


class ErrorDetail(str):
    """
    A string-like object that can additionally have a code.
    """
    code = None
    def __new__(cls, string, code=None):
        self = super().__new__(cls, string)
        self.code = code
        return self

    def __eq__(self, other):
        result = super().__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        try:
            return result and self.code == other.code
        except AttributeError:
            return result

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __repr__(self):
        return 'ErrorDetail(string=%r, code=%r)' % (
            str(self),
            self.code,
        )
    def __hash__(self):
        return hash(str(self))

def _get_codes(detail):
    if isinstance(detail, list):
        return [_get_codes(item) for item in detail]
    elif isinstance(detail, dict):
        return {key: _get_codes(value) for key, value in detail.items()}
    return detail.code

def _get_full_details(detail):
    if isinstance(detail, list):
        return [_get_full_details(item) for item in detail]
    elif isinstance(detail, dict):
        return {key: _get_full_details(value) for key, value in detail.items()}
    return {
        'message': detail,
        'code': detail.code
    }

class BAuthAPIException(Exception):
    """
    Base class for REST framework exceptions.
    Subclasses should provide `.status_code` and `.default_detail` properties.
    """
    status_code = 500
    default_detail = 'A server error occurred.'
    default_code = 'error'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        self.detail = ErrorDetail(detail, code)
    def __str__(self):
        return str(self.detail)
    def get_codes(self):
        return self.detail.code
    def get_full_details(self):
        return {'message': self.detail, 'code': self.detail.code}

class HTTPException(BAuthAPIException):
    status_code = 500
    default_detail = 'A server error occurred.'
    default_code = 'error'

class NotAuthenticated(BAuthAPIException):
    status_code = 401
    default_detail = 'Authentication credentials were not provided.'
    default_code = 'not_authenticated'

class AuthenticationFailed(BAuthAPIException):
    status_code = 401
    default_detail = 'Incorrect authentication credentials.'
    default_code = 'authentication_failed'

class PermissionDenied(BAuthAPIException):
    status_code = 403
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'permission_denied'

class WebSocketException(Exception):
    def __init__(self, code: int, reason: typing.Optional[str] = None) -> None:
        self.code = code
        self.reason = reason or ""

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(code={self.code!r}, reason={self.reason!r})"


class RuntimeError(Exception):
    """ Unspecified run-time error. """
    def __init__(self, *args, **kwargs): # real signature unknown
        pass

    @staticmethod # known case of __new__
    def __new__(*args, **kwargs): # real signature unknown
        """ Create and return a new object.  See help(type) for accurate signature. """
        pass


class NotImplementedError(RuntimeError):
    """ Method or function hasn't been implemented yet. """
    def __init__(self, *args, **kwargs): # real signature unknown
        pass

    @staticmethod # known case of __new__
    def __new__(*args, **kwargs): # real signature unknown
        """ Create and return a new object.  See help(type) for accurate signature. """
        pass
