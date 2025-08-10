from datetime import datetime
from typing import Tuple
from uuid import UUID

from pydantic import BaseModel, ValidationError, field_validator
from pydantic_core.core_schema import FieldValidationInfo


class MiniProfile(BaseModel):
    class Config:
        frozen = True

    id: int
    uuid: UUID
    role: int

class MiniAliase(BaseModel):
    class Config:
        frozen = True

    id: int
    uuid: UUID
    type: str
    value: str | None = None
    code: str | None = None

class BaseUser(BaseModel):
    class Config:
        # from pydantic.config import BaseConfig
        frozen = True

    uuid: UUID
    id: int
    phone: str

    is_active: bool = False
    is_staff: bool = False
    email_active: bool = False
    phone_active: bool = False

    created_at: datetime
    updated_at: datetime
    last_login: datetime

    permissions: Tuple[str, ...] = tuple
    groups: Tuple[str, ...] = tuple
    profiles: Tuple[MiniProfile, ...] = tuple
    aliases: Tuple[MiniAliase, ...] = tuple

    group_payer_id: int | None = None
    position: int | None = None
    firstname: str | None = ''
    lastname: str | None = ''
    avatar: str | None = ''
    email: str | None = ''
    tg_username: str | None = ''
    locale: str | None = 'ru'

    is_superuser: bool = False

    @field_validator('position')
    def validate_position(cls, val: int, info: FieldValidationInfo) -> int:
        #  в качестве работающего примера валидации
        if (val and val < 1) or val == 0:
            raise ValueError('position must be greater then 0')
        return val

    @property
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    @property
    def TestP(self):
        return 'TestP'

    def has_perm(self, perm):
        """
        Return True if the user has the specified permission.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        return perm in self.permissions

    def has_perms(self, perm_list):
        """
        Return True if the user has each of the specified permissions.
        """
        set_perm_list = set(perm_list)
        return set(self.permissions).intersection(set_perm_list) == set_perm_list



class AdminUser(BaseUser):
    pass


__all__ = ['AdminUser', 'BaseUser']
