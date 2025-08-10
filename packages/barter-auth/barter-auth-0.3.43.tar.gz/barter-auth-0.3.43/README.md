# Barter authentication package

This package allows you to authorize users through a shared redis

## Install package
```shell
pip install barter-auth
```

## Define env variables

- `REDIS_AUTH_URL` default 'redis://localhost:6378/1' # depracated
- `REDIS_AUTH_HOST` default '127.0.0.1'
- `REDIS_AUTH_PORT` default 6379
- `REDIS_AUTH_PASSWORD` default None
- `REDIS_AUTH_DB` default 0
- `REDIS_AUTH_ACCESS_PREFIX` default = 'access'
- `REDIS_AUTH_REFRESH_PREFIX` default = 'refresh'
- `REDIS_AUTH_TOTP_PREFIX` default = 'totp'
- `REDIS_AUTH_PROFILE_PREFIX` default = 'profile'
- `REDIS_AUTH_TOKEN_STORAGE` default = 'headers'

## Use in view

```python
# in django 
from rest_framework.permissions import AllowAny, IsAuthenticated
from barter_auth.auth import ApiTokenRedisAuthentication
class SomeView(APIView):
    authentication_classes = [ApiTokenRedisAuthentication]
    permission_classes = [IsAuthenticated]
    
# barter_auth BaseUser() is available in request.user  in DRF APIView 

```
## Use in AppConfig   for  request.extuser  and  request.profie
```python
# you can add request user or profile in apps django config  <app_name>.apps.py

class BloggerConfig(AppConfig):
    name = 'apps.base'

    def ready(self):
        HttpRequest.extuser = property(get_user)
        HttpRequest.profile = property(get_profile)


def get_user(self):
    from barter_auth.auth import get_token_from_cookies, get_token_from_header
    from barter_auth.providers import RedisAccessClient
    from django.contrib.auth.models import AnonymousUser
    from django.conf import settings
    
    token = get_token_from_header(self)
    if not token:
        token = get_token_from_cookies(self)
    if token:
        token_service = RedisAccessClient(host=settings.REDIS_AUTH_HOST)
        user = token_service.get_user(token)
        return user or AnonymousUser()
    return AnonymousUser()

def get_profile(self):
    from barter_auth.models import AnonymousProfile
    extuser = self.extuser
    if extuser.is_authenticated:
        try:
            profile = RedisProfileClient().get_model(key=self.headers.get('Profile'))
        except:
            profile = AnonymousProfile()
        if profile.user_id and profile.user_id == extuser.id:
            # print(f'profile: {profile.id}')
            return profile
    return AnonymousProfile()

```


```python
# in settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "barter_auth.auth.ApiTokenRedisAuthentication",
    ],
    "EXCEPTION_HANDLER": '<your path>.api_exception_handler',
    # ...
}

# file with  api_exception_handler
from rest_framework.response import Response
from rest_framework.views import exception_handler, set_rollback
from barter_auth.exceptions import BAuthAPIException

def api_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    if isinstance(exc, BAuthAPIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        if isinstance(exc.detail, (list, dict)):
            data = exc.detail
        else:
            data = {'detail': exc.detail}
        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)

    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code

    return response

```
