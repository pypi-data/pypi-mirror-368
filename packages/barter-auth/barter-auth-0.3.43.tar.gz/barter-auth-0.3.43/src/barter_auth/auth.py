
from .exceptions import AuthenticationFailed, HTTPException, NotAuthenticated
from .providers import RedisAccessClient

# Header encoding (see RFC5987)
HTTP_HEADER_ENCODING = 'iso-8859-1'


def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.
    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    # auth = request.headers.get('Authorization', b'')
    if isinstance(auth, str):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth

def get_token_from_cookies(request) -> str:
    # cookie = request.headers.get('Cookie', '')
    cookie = request.META.get('HTTP_COOKIE', '')
    token = None
    try:
        cookie_dict = dict([val.split('=') for val in cookie.split()])
        token = cookie_dict.get('auth_token', '').rstrip(';')
    except:
        pass
    return token

def get_token_from_header(request) -> str:
    auth = get_authorization_header(request).split()
    token = None
    if len(auth) == 2:
        try:
            token = auth[1].decode()
        except UnicodeError:
            token = None
    return token

class BaseAuthentication:
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        raise NotImplementedError(".authenticate() must be overridden.")

    def authenticate_header(self, request):
        pass

class ApiTokenRedisAuthentication(BaseAuthentication):
    """
    Simple token based authentication.
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:
        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """
    keyword = 'Token'
    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise AuthenticationFailed(msg)
        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise AuthenticationFailed(msg)
        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        token_service = RedisAccessClient()
        user = token_service.get_user(key)
        if not user:
            raise NotAuthenticated('Invalid token.')

        if not user.is_active:
            raise NotAuthenticated('User inactive or deleted.')

        return (user, key)

    def authenticate_header(self, request):
        return self.keyword


__all__ = [
    'ApiTokenRedisAuthentication',
    'get_token_from_cookies',
    'get_token_from_header',
]
