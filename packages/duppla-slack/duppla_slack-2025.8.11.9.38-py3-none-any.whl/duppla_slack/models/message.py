from typing import Any, Literal, Optional, Sequence, Union

from pydantic import AliasChoices, BaseModel, Field
from typing_extensions import NotRequired, TypedDict

from duppla_slack.constants.channels import AIRFLOW_CHANNEL
from duppla_slack.constants.templates import Filetype


class Attachment(TypedDict, total=False):
    """
    Represents an attachment for a message to send to a Slack channel.
    Check the official documentation of the Slack API for more information: https://api.slack.com/reference/messaging/attachments
    """

    title: Optional[str]
    value: Optional[str]
    short: bool
    blocks: list[dict[str, Any]]
    color: Union[Literal["good", "warning", "danger"], str]


class AttachmentOld(TypedDict, total=False):
    """
    Represents an attachment for a message to send to a Slack channel.
    Check the official documentation of the Slack API for more information: https://api.slack.com/reference/messaging/attachments
    """

    author_icon: str
    author_link: str
    author_name: str
    fallback: str
    fields: list[dict[str, Any]]
    footer: str
    footer_icon: str
    image_url: str
    mrkdwn_in: list[str]
    pretext: str
    text: str
    thumb_url: str
    title: str
    title_link: str
    ts: Union[str, int]


class MessageMetadata(TypedDict):
    """
    Represents metadata for a Slack message.
    This metadata is not visible to the user but can be used to store additional information.

    > For more details, refer to the official Slack API documentation: https://api.slack.com/metadata/using
    """

    event_type: str
    event_payload: dict[str, Any]


class Message(BaseModel):
    """
    Represents the body of the request to send a message to a Slack channel.
    The body may contain attachments or blocks for rich content.
    # NOTE:
        - If the channel is a user ID, the message will be sent as a direct message to that user.
        - If the thread_ts is set, the message will be sent as a reply to the specified thread and if the reply_broadcast is set to True, the message will also be sent to the entire channel.

    > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/chat.postMessage
    """

    text: str = Field(validation_alias=AliasChoices("text", "msg"))
    channel: str = Field(default=AIRFLOW_CHANNEL, validation_alias=AliasChoices("channel", "channel_id"))  # fmt:skip
    thread_ts: Optional[str] = None
    reply_broadcast: Optional[bool] = False
    attachments: Optional[list[Union[Attachment, AttachmentOld]]] = None
    blocks: Optional[list[dict[str, Any]]] = None
    unfurl_links: Optional[bool] = None
    unfurl_media: Optional[bool] = None
    metadata: Optional[MessageMetadata] = None


class LongMessage(BaseModel):
    """
    Represents the body of the request to send a long message to a Slack channel.
    The message is sent as a file, to avoid the truncate originated from the 4000 characters limit of the text field.

    # NOTE:
        - If the channel is a user ID, it will thrown an error, pass instead a Direct Channel ID.
        - The original method will be deprecated soon, so it is recommended to use the wrapper `files.uploadv2` of the actual two methods: `files.getUploadURLExternal` and `files.completeUploadExternal`

    > Check the official documentation of the Slack API for more information:
        > https://api.slack.com/methods/files.upload  [Deprecated but shows the use of files.uploadv2]
        > https://api.slack.com/methods/files.getUploadURLExternal
        > https://api.slack.com/methods/files.completeUploadExternal
    """

    initial_comment: Optional[str] = Field(default=None, validation_alias=AliasChoices("initial_comment", "msg", "text"))  # fmt:skip
    """The message to be sent as a header before the file."""
    content: str
    """A string representing the file content."""
    channel: str = Field(default=AIRFLOW_CHANNEL, validation_alias=AliasChoices("channel", "channel_id"))  # fmt:skip
    """The channel ID or name where the message will be sent. (It must start with 'C', 'G', 'D' or 'Z', meaning channel, group, direct message or user respectively.)"""
    thread_ts: Union[str, int, None] = None
    reply_broadcast: bool = False
    snippet_type: Filetype = Field(default="auto", validation_alias=AliasChoices("snippet_type", "type", "filetype"))  # fmt:skip
    """The type of the file content to display following the snippet format, see https://api.slack.com/types/file#types"""


class EphemeralMessage(Message):
    """
    Represents the body of the request to send an ephemeral message to a Slack user.
    The body (like the parent class Message) may contain attachments or blocks for rich content.
    # NOTE: If the channel is a user ID, the message will be sent as a direct message to that user.
    > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/chat.postEphemeral
    """

    user: str


class ScheduledMessage(Message):
    """
    Represents the body of the request to schedule a message to a Slack channel.
    The body (like the parent class Message) may contain attachments or blocks for rich content.
    # NOTE: If the channel is a user ID, the message will be sent as a direct message to that user.
    > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/chat.scheduleMessage
    """

    post_at: int  # Unix time
    reply_broadcast: Optional[bool] = False


class Bookmark(BaseModel):
    """
    Represents a bookmark for a message to send to a Slack channel.
    Check the official documentation of the Slack API for more information: https://api.slack.com/reference/messaging/blocks
    """

    channel_id: str
    title: str
    type: str
    emoji: Optional[str] = None
    link: Optional[str] = None


class RemoteFile(TypedDict):
    """
    Represents the parameters for a remote file that can be sent to a Slack channel.
    """

    external_id: str  # Unique ID you assign
    external_url: str  # Public URL
    title: str
    filetype: NotRequired[Filetype]
    indexable_file_contents: NotRequired[str]  # Optional search text
    preview_image_url: NotRequired[str]


class _FileUpload(TypedDict):
    channel: str
    thread_ts: NotRequired[Optional[str]]
    initial_comment: NotRequired[str]


class SingleFileUpload(_FileUpload):
    filename: str
    content: Union[str, bytes]
    snippet_type: NotRequired[Filetype]


class MultiFileUpload(_FileUpload):
    files: Sequence[SingleFileUpload]
