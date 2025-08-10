from dataclasses import asdict, dataclass, field
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from ..constants import Role

__all__ = [
    'Profile', 'AnonymousProfile',
    'Advertiser', 'Instagram', 'Anonymous',
    'Category',
]

class Advertiser(BaseModel):
    class Config:
        # pydantic.config.BaseConfig
        frozen = True

    uuid: UUID
    id: int
    user_id: int
    profile_id: int
    profile_uuid: UUID

    moderate: int
    premoderate_booking: bool

    created_at: datetime
    updated_at: datetime
    moderate_datetime: datetime | None = None

    company_name: str | None = ''
    name: str | None = ''
    email: str | None = ''
    phone: str | None = ''
    whatsapp: str | None = ''
    telegram: str | None = ''
    note: str | None = ''
    weblink: str | None = ''
    instagram: str | None = ''

    balance_reach: int | None = None
    balance_reach_all: int | None = None
    description: str | None = ''
    group_payer_id: int | None = None
    premoderate_limit: int | None = None


class Category(BaseModel):
    class Config:
        frozen = True
    id: int
    type: int
    name: str
    parent_id: int | None = None


class BloggerAlias(BaseModel):
    class Config:
        frozen = True

    id: int
    uuid: UUID
    instagram_id: int
    instagram_uuid: UUID
    user_id: int | None = None
    user_uuid: UUID | None = None
    type: str
    value: str | None = None
    link: str | None = None
    reach: int | None = None
    post_reach: int | None = None
    is_verified: bool | None = False
    code: str | None = None

class Instagram(BaseModel):
    class Config:
        frozen = True

    uuid: UUID
    id: int
    user_id: int
    profile_id: int
    profile_uuid: UUID

    created_at: datetime
    updated_at: datetime

    status: int
    moderate: int
    moderate_datetime: datetime | None = None
    is_confirmed: bool | None = False
    is_private: bool | None = False
    is_verified: bool | None = False
    checked_at: datetime | None = None

    reach: int | None = None
    followers: int | None = 0
    follows: int | None = 0
    username: str | None = ''
    link: str | None = None
    type: str | None = ''
    post_reach: int | None = None
    booking_limit: int | None = None
    picture: str | None = ''
    pkid: str | None = ''
    categories: list[Category] = []
    side_analytics_uuid: UUID | None = None

    blogger_aliases: list[BloggerAlias] = []

    count_media: int | None = 0
    full_name: str | None = ''
    external_url: str | None = ''
    phone: str | None = ''

    firstname: str | None = ''
    age: int | None = None
    city: str | None = None
    data: dict | None = None
    is_barter_recommend: bool | None = False


class TestM(BaseModel):
    class Config:
        frozen = True

    id: int
    categories: list[Category] = []


class Anonymous(BaseModel):
    class Config:
        frozen = True

    id: int | None = None
    uuid: UUID | None = None
    profile_id: int | None = None

    def __str__(self):
        return "Anonymous"

class AnonymousProfile(BaseModel):
    class Config:
        frozen = True

    id: int | None = None
    uuid: UUID | None = None
    user_id: int | None = None
    role: int = Role.ANONYMOUS
    advertiser: Advertiser | None = None
    instagram: Instagram | None = None

    def __str__(self):
        return "AnonymousProfile"

    def is_blogger(self):
        return False

    def is_advertiser(self):
        return False

class Profile(BaseModel):
    class Config:
        frozen = True

    id: int
    uuid: UUID
    user_id: int

    role: int

    advertiser: Advertiser | None = None
    instagram: Instagram | None = None

    user_fio: str | None = None
    advertiser_id: int | None = None
    instagram_id: int | None = None

    def __post_init__(self):
        if self.role == Role.ADVERTISER and not self.advertiser:
            raise ValueError('Advertiser must be set')
        elif self.role == Role.INSTAGRAM and not self.instagram:
            raise ValueError('Instagram must be set')

    def is_blogger(self):
        return self.role == Role.INSTAGRAM

    def is_advertiser(self):
        return self.role == Role.ADVERTISER


