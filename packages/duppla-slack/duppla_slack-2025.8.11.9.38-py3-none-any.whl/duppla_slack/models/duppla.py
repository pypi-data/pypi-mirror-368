import html
from datetime import date
from typing import Any, Optional, cast

from pydantic import (
    BaseModel, Field,
    EmailStr, AliasChoices, 
    field_validator, model_validator
)
from pydantic.networks import AnyUrl as Url

from .slack_types import Profile, User


class SlackProfile(BaseModel):
    model_config = {"from_attributes": True, "extra": "allow"}

    id: str
    is_bot: bool

    real_name: str = Field(validation_alias=AliasChoices("real_name", "real_name_normalized"))
    display_name: str = Field(validation_alias=AliasChoices("display_name", "display_name_normalized"))

    status_text: str
    status_emoji: str
    email: EmailStr
    images: list[str]
    role: str = Field(alias="title")
    pronouns: Optional[str] = None

    start_date: Optional[date] = None

    deleted: bool = Field(exclude=True)

    @model_validator(mode="before")
    def validate_images(cls, vals: User):
        profile = cast(Profile, vals.pop("profile", {}))
        values: dict[str, Any] = {**vals, **profile}

        def sort_key(url: str):
            if url.endswith("original.jpg"):
                return (0, 0)
            parts = url.rsplit("_", 1)
            if len(parts) == 2:
                num_part = parts[1].split(".")[0]
                if num_part.isdigit():
                    return (1, -int(num_part))
            return (2, 0)

        images = [str(v) for k, v in values.items() if k.startswith("image_")]
        values["images"] = sorted(images, key=sort_key)
        return values


class FormInput(BaseModel):
    token: str
    team_id: str
    team_domain: str
    channel: str
    channel_name: str
    user_id: str
    user_name: str
    command: str
    text: str = ""
    api_app_id: str
    is_enterprise_install: bool
    response_url: Url
    trigger_id: str

    @field_validator("command")
    def command_validate(cls, value: str):
        value = html.unescape(value)
        if value.startswith("/"):
            return value[1:]
        raise ValueError("A slash command must start with a '/' character.")
