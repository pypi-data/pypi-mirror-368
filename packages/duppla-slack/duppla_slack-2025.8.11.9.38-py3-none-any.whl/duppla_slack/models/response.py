import json
import warnings
from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ConfigDict
from requests import HTTPError
from slack_sdk.web import SlackResponse as SlackResponseSDK


class SlackResponse(BaseModel, Mapping[str, Any]):
    model_config = ConfigDict(extra="allow")
    ok: bool

    def __getitem__(self, key: str) -> Any:
        if self.model_extra and key in self.model_extra:
            return self.model_extra[key]
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any):
        if not self.model_extra:
            setattr(self, key, value)
        else:
            self.model_extra[key] = value

    def __getattr__(self, name: str) -> Any:
        """Fallback to attribute access if the atribute is not found"""
        return self[name]

    def __str__(self) -> str:
        return self.model_dump_json()

    def __add__(self, other: "SlackResponse") -> "SlackResponse":
        return SlackResponse(**(self.model_dump() | other.model_dump()))

    def __len__(self) -> int:
        return len(self.model_dump())

    def raise_v(self):
        if not self.ok:
            if hasattr(self, "error"):
                raise HTTPError(f"Slack API request failed: {self.error}")  # pyright: ignore[reportUnknownMemberType,reportAttributeAccessIssue]
            warnings.warn("Slack API request failed")
        return self

    @classmethod
    def from_sdk(cls, sdk_response: SlackResponseSDK) -> "SlackResponse":
        if isinstance(sdk_response.data, bytes):
            try:
                sdk_response.data = json.loads(sdk_response.data)
            except Exception:
                sdk_response.data = {}
        return cls(**sdk_response.data)  # pyright: ignore[reportCallIssue]
