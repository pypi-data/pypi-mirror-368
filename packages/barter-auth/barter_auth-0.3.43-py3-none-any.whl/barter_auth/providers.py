import json
import os

import redis

from .models import *
from .settings import app_settings

DEFAULT_TTL = 300
DEFAULT_ACCESS_TTL = 259200

class RedisClient:
    _prefix = "basic"
    _ttl = DEFAULT_TTL

    def __init__(self, host: str or tuple, port: int or tuple, db: int, password: str):
        host = host if type(host) is not tuple else host[0]
        port = port if type(port) is not tuple else port[0]
        self.__redis_client = redis.StrictRedis(host=host, port=port, db=db, password=password)

    @property
    def conn(self):
        return self.__redis_client

    def __get(self, name: str) -> str | None:
        value = self.conn.get(name)
        return value

    def __put(self, name: str, value: str, ttl: int) -> None:
        '''

        :param name:  redis key
        :param value: json string
        :param ttl:
        :return:
        '''
        if type(value) is dict:
            value_data = json.dumps(value)
        else:
            value_data = value
        self.conn.set(name=name, value=value_data, ex=ttl)

    def is_token_exist(self, token: str, prefix: bool = True) -> str | None:
        key = f"{self._prefix}:{token}" if prefix else token
        return self.__get(key)

    def add_token(self, token: str, json_data: str = None, ttl: int = None, prefix: bool = True):
        key = f"{self._prefix}:{token}" if prefix else token
        ttl = ttl if ttl is not None else self._ttl
        value = json_data if json_data is not None else json.dumps({"token": key})
        self.__put(name=key, value=value, ttl=ttl)


class RedisAccessClient(RedisClient):
    _prefix = app_settings.ACCESS_PREFIX
    _ttl = int(os.getenv("ACCESS_TOKEN_LIFETIME", DEFAULT_ACCESS_TTL))

    def __init__(self,
                 host: str = app_settings.HOST,
                 port: int = app_settings.PORT,
                 db: int = app_settings.DB,
                 password: str = app_settings.PASSWORD):
        super().__init__(host=host, port=port, db=db, password=password)

    def get_user(self, token: str, prefix: bool = True) -> BaseUser | None:
        user_json = self.is_token_exist(token, prefix=prefix)
        if user_json:
            return BaseUser.parse_raw(user_json)
        return None


class RedisRefreshClient(RedisClient):
    _prefix = app_settings.REFRESH_PREFIX
    _ttl = int(os.getenv("REFRESH_TOKEN_LIFETIME", DEFAULT_TTL))

    def __init__(self,
                 host: str = app_settings.HOST,
                 port: int = app_settings.PORT,
                 db: int = app_settings.DB,
                 password: str = app_settings.PASSWORD):
        super().__init__(host=host, port=port, db=db, password=password)


class RedisTotpClient(RedisClient):
    _prefix = app_settings.TOTP_PREFIX

    def __init__(self, host: str, port: int, db: int, password: str):
        super().__init__(host=host, port=port, db=db, password=password)

class RedisModelClient(RedisClient):
    _prefix = ''
    _ttl = None
    _db = app_settings.DB
    model = None
    non_model = None
    def __init__(self,
                 host: str = app_settings.HOST,
                 port: int = app_settings.PORT,
                 db: int = None,
                 password: str = app_settings.PASSWORD):
        if not db:
            db = self._db
        if not self.model or not self.non_model:
            raise ValueError("Invalid data.")
        super().__init__(host=host, port=port, db=db, password=password)

    def is_data_exist(self, key: str | int, prefix: bool = True) -> str | None:
        return super(RedisModelClient, self).is_token_exist(key, prefix=prefix)

    def get_model(self, key: str | int, prefix: bool = True):
        data_json = self.is_data_exist(key, prefix=prefix)
        if data_json:
            return self.model.parse_raw(data_json)
        return self.non_model()

    def add_model(self, key: str | int, json_data: str = None, ttl: int = None, prefix: bool = True):
        return super().add_token(key, json_data=json_data, ttl=ttl, prefix=prefix)

    def add_token(self, *args, **kwargs):
        raise NotImplementedError("Not declared here.")
    def is_token_exist(self, *args, **kwargs):
        raise NotImplementedError("Not declared here.")

class RedisAuthProfileClient(RedisModelClient):
    _prefix = app_settings.PROFILE_PREFIX
    _ttl = None
    _db = app_settings.DB
    model = Profile
    non_model = AnonymousProfile



