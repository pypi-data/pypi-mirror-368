from slack_sdk.errors import SlackApiError as SlackApiError

from .duppla import SlackProfile as SlackProfile, FormInput as FormInput

from .message import Message as Message  # isort:skip
from .message import (
    Attachment as Attachment,
    AttachmentOld as AttachmentOld,
    Bookmark as Bookmark,
    EphemeralMessage as EphemeralMessage,
    LongMessage as LongMessage,
    ScheduledMessage as ScheduledMessage,
    MessageMetadata as MessageMetadata,
)
from .response import SlackResponse as SlackResponse

MessageResponse = SlackResponse
Metadata = MessageMetadata

__all__ = [
    "SlackApiError",
    "SlackProfile",
    "FormInput",
    "Message",
    "Attachment",
    "AttachmentOld",
    "Bookmark",
    "EphemeralMessage",
    "LongMessage",
    "ScheduledMessage",
    "SlackResponse", "MessageResponse", # for backwards compatibility
    "MessageMetadata", "Metadata" # for backwards compatibility
]  # fmt:skip
