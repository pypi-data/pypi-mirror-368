from datetime import date
from typing import Any, Sequence, TypedDict

from typing_extensions import NotRequired


class EnterpriseGridUser(TypedDict):
    id: str
    is_admin: bool
    is_owner: bool
    teams: Sequence[str]


class Profile(TypedDict):
    avatar_hash: str
    display_name: str
    display_name_normalized: str
    email: str
    fields: NotRequired[dict[str, Any]]
    first_name: str
    last_name: str
    phone: str  # May be empty
    pronouns: NotRequired[str]
    real_name: str
    """Computed from first_name and last_name. Even though those fields are also computed from this field"""
    real_name_normalized: str
    skype: str  # May be empty
    start_date: NotRequired[date]
    status_emoji: str
    status_expiration: int
    status_text: str
    team: str
    title: str

    image_original: str
    image_24: NotRequired[str]
    image_32: NotRequired[str]
    image_48: NotRequired[str]
    image_72: NotRequired[str]
    image_192: NotRequired[str]
    image_512: NotRequired[str]
    image_1024: NotRequired[str]


class User(TypedDict):
    always_active: bool
    color: str
    deleted: bool
    enterprise_user: NotRequired[EnterpriseGridUser]
    has_2fa: bool
    id: str
    is_admin: bool
    is_app_user: bool
    is_bot: bool
    is_invited_user: bool
    is_owner: bool
    is_primary_owner: bool
    is_restricted: bool
    is_ultra_restricted: bool
    is_stranger: bool
    locale: str
    tz: str
    tz_label: str
    tz_offset: int
    updated: str
    # name: str
    profile: Profile
