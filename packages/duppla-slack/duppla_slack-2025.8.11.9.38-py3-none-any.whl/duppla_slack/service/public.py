# pyright: reportOptionalIterable=false, reportOptionalSubscript=false
import asyncio
import json
from collections.abc import Iterator
from typing import Any, Callable, Optional, Union, cast, overload
from warnings import warn

import requests
from slack_sdk import WebClient as SlackLibClient
from typing_extensions import Unpack

from duppla_slack.constants.channels import AIRFLOW_CHANNEL
from duppla_slack.constants.templates import Filetype
from duppla_slack.models import (
    Bookmark,
    EphemeralMessage,
    LongMessage,
    Message,
    ScheduledMessage,
    SlackApiError,
    SlackProfile,
    SlackResponse,
)
from duppla_slack.models.message import MultiFileUpload, RemoteFile, SingleFileUpload
from duppla_slack.models.slack_types import User
from duppla_slack.service.listeners import MessageListener
from duppla_slack.utils.rate_limiter import (
    EVENTS as EVENTS,
    INCOMING_WEBHOOK as INCOMING_WEBHOOK,
    POST_MSG as POST_MSG,
    TIER_1 as TIER_1,
    TIER_2 as TIER_2,
    TIER_3 as TIER_3,
    TIER_4 as TIER_4,
    WORKFLOW_EVENT_TRIGGER as WORKFLOW_EVENT_TRIGGER,
    WORKFLOW_WEBHOOK_TRIGGER as WORKFLOW_WEBHOOK_TRIGGER,
    rate_limited as rate_limited,
)


class SlackService(SlackLibClient):
    """
    This class extends the SlackLibClient and provides methods for sending messages, updating messages, sending ephemeral messages, scheduling messages, and more.
    It simplifies the interaction with Slack by offering higher-level abstractions over the raw API calls, making it easier to perform common tasks such as sending messages, managing channels, and handling user interactions.

    The SlackService class is designed to be flexible and extensible, allowing us, as the owners, to customize and extend its functionality as needed.
    It includes various utility functions that cover a wide range of use cases, from basic message sending to more complex operations like scheduling messages and managing channel memberships.

    Additionally, the class provides overloads for certain methods to handle different types of inputs, ensuring that the correct API calls are made based on the provided arguments.
    This helps to reduce errors and improve the overall developer experience when working with the Slack API.

    For more detailed information on the available methods and their usage, please refer to the official Slack API documentation: https://api.slack.com/
    SlackService is a wrapper around the Slack API that provides utility functions for interacting with Slack.

    Examples:
    ```python
    from duppla_slack import SlackService

    slack_service = SlackService(token="xox")

    # Send a simple message
    slack_service.send_msg_(text="Hello, world!", channel="C1234567890")

    # Sends a simple message using the Message object
    from duppla_slack.models import Message

    slack_service.send_msg(Message(text="Hello, world!", channel="C1234567890"))

    # Get channel information by ID
    channel_info = slack_service.get_channel(channel_id="C1234567890")

    # Get channel information by name
    channel_info = slack_service.get_channel(channel_name="general")

    # Get a list of all channels
    channels = slack_service.get_channels()

    # Get a list of all members
    members = slack_service.get_members()
    ```

    # Add message listener
    def on_message_sent(response):
        print(f"Message sent: {response}")

    slack_service.add_message_listener(on_message_sent)
    """

    def __init__(self, token: str):
        super().__init__(token=token)
        self._message_listener = MessageListener()

    def add_message_listener(self, listener: Callable[[SlackResponse], None]) -> None:
        """Add a listener that will be called with the result of send_msg.

        Args:
            listener: A callable that takes a SlackResponse as argument
        """
        self._message_listener.add_listener(listener)

    def remove_message_listener(
        self, listener: Callable[[SlackResponse], None]
    ) -> None:
        """Remove a previously added message listener.

        Args:
            listener: The listener function to remove
        """
        self._message_listener.remove_listener(listener)

    @overload
    def send_msg_(
        self,
        *,
        text: str,
        channel: str = AIRFLOW_CHANNEL,
        thread_ts: Optional[str] = None,
        reply_broadcast: bool = False,
        **kwargs: Any,  # attachments, blocks or metadata
    ) -> SlackResponse:
        """
        Utility function that sends a message to a Slack channel.
        If the channel is a user ID, the message will be sent as a direct message to that user.
        If the thread_ts is set, the message will be sent as a reply to the specified thread and if the reply_broadcast is set to True, the message will also be sent to the entire channel.

        Args:
            text (str): The text of the message.
            channel (str): The ID of the channel to send the message to. Default is the AIRFLOW_CHANNEL.
            thread_ts (str): The timestamp of the parent message to reply to.
            reply_broadcast (bool): Whether to send the message to the entire channel. Default is False.
            **kwargs: Additional arguments for the message. \
                <However, discouraged, use `send_msg(message=Message(...))` instead>\
                attachments (list[Attatchments]), blocks (list[dict[str, Any]]), metadata (MessageMetadata)

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/chat.postMessage
        """

    @overload
    def send_msg_(
        self,
        *,
        content: str,
        channel: str = AIRFLOW_CHANNEL,
        thread_ts: Optional[str] = None,
        reply_broadcast: bool = False,
        initial_comment: Optional[str] = None,
        snippet_type: Filetype = "auto",
        **kwargs: Any,
    ) -> SlackResponse:
        """
        Utility function that sends a long message to a Slack channel.
        The message is sent as a file, to avoid the truncate originated from the 4000 characters limit of the text field.

        Args:
            content (str): The text of the message.
            channel (str): The ID of the channel to send the message to. Default is the AIRFLOW_CHANNEL.
            thread_ts (str): The timestamp of the parent message to reply to.
            reply_broadcast (bool): Whether to send the message to the entire channel. Default is False.
            initial_comment (str): The text of the initial comment.
            snippet_type (str): The type of the snippet. Default is None.

        > Check the official documentation of the Slack API for more information:
            > https://api.slack.com/methods/files.upload  [Deprecated but shows the use of files.uploadv2]
            > https://api.slack.com/methods/files.getUploadURLExternal
            > https://api.slack.com/methods/files.completeUploadExternal
        """

    def send_msg_(
        self,
        *,
        text: Optional[str] = None,
        channel: str = AIRFLOW_CHANNEL,
        thread_ts: Optional[str] = None,
        reply_broadcast: bool = False,
        initial_comment: Optional[str] = None,
        snippet_type: Filetype = "auto",
        **kwargs: Any,
    ) -> SlackResponse:
        kwargs.update(
            {
                "text": text,
                "channel": channel,
                "thread_ts": thread_ts,
                "reply_broadcast": reply_broadcast,
                "initial_comment": initial_comment,
                "snippet_type": snippet_type,
            }
        )
        if "attachments" in kwargs or "blocks" in kwargs:
            warn("Use the `send_msg` method for rich content messages")

        if "content" in kwargs:
            result = self.files_upload_v2(**kwargs)
        elif "text" in kwargs:
            result = self.chat_postMessage(**kwargs)
        else:
            raise ValueError("Invalid message type")
        response = SlackResponse.from_sdk(result)
        self._message_listener.notify_listeners(response)
        return response

    @overload
    def send_msg(self, message: Message) -> SlackResponse:
        """
        Sends a message to a Slack channel.
        If the channel is a user ID, the message will be sent as a direct message to that user.
        If the thread_ts is set, the message will be sent as a reply to the specified thread and if the reply_broadcast is set to True, the message will also be sent to the entire channel.

        Args:
            message (Message): The message to send.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/chat.postMessage
        """

    @overload
    def send_msg(self, message: LongMessage) -> SlackResponse:
        """
        Sends a long message to a Slack channel.
        The message is sent as a file, to avoid the truncate originated from the 4000 characters limit of the text field.

        Args:
            message (LongMessage): The message to send.

        > Check the official documentation of the Slack API for more information:
            > https://api.slack.com/methods/files.upload  [Deprecated but shows the use of files.uploadv2]
            > https://api.slack.com/methods/files.getUploadURLExternal
            > https://api.slack.com/methods/files.completeUploadExternal
        """

    def send_msg(self, message: Union[Message, LongMessage]) -> SlackResponse:
        if isinstance(message, LongMessage):
            result = self.files_upload_v2(**message.model_dump(exclude_none=True))
        else:
            result = self.chat_postMessage(**message.model_dump(exclude_none=True))
        response = SlackResponse.from_sdk(result)
        self._message_listener.notify_listeners(response)
        return response

    def update_message(
        self,
        *,
        channel: str,
        timestamp: str,
        text: str,
        **kwargs: Any,
    ) -> SlackResponse:
        """
        Updates message in a slack channel
        :param channel: the channel id where the message is located.
        :param timestamp: the timestamp of the message to update. This is used to identify the message to be updated (like an id).
        :param text: the new text for the message.
        :param blocks: the new blocks for the message, provides the new structured content for the message.
        :return: The updated message response.
        """
        kwargs.update(
            {
                "channel": channel,
                "ts": timestamp,
                "text": text,
            }
        )
        result = self.chat_update(**kwargs)
        return SlackResponse.from_sdk(result)

    update_msg = update_message

    def send_ephemeral_(
        self,
        *,
        user: str,
        channel: str = AIRFLOW_CHANNEL,
        text: str,
        thread_ts: Optional[str] = None,
        reply_broadcast: bool = False,
        **kwargs: Any,  # attachments or blocks
    ) -> SlackResponse:
        """
        Utility function that sends an ephemeral message to a user in a Slack channel.

        Args:
            user (str): The ID of the user to send the message to.
            channel (str): The ID of the channel to send the message to.
            text (str): The text of the message.
            **kwargs: Additional arguments for the message. It can be attachments (list[Attatchments]) or blocks (list[dict[str, Any]]) <However, discouraged, use `send_ephemeral(message=EphemeralMessage(...))` instead>.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/chat.postEphemeral
        """
        result = self.chat_postEphemeral(
            user=user,
            channel=channel,
            text=text,
            thread_ts=thread_ts,
            reply_broadcast=reply_broadcast,
            **kwargs,
        )
        return SlackResponse.from_sdk(result)

    def send_ephemeral(self, message: EphemeralMessage) -> SlackResponse:
        """
        Sends an ephemeral message to a user in a Slack channel.

        Args:
            message (EphemeralMessage): The message to send.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/chat.postEphemeral
        """
        result = self.chat_postEphemeral(**message.model_dump(exclude_none=True))
        return SlackResponse.from_sdk(result)

    def send_scheduled_(
        self,
        *,
        post_at: int,
        channel: str = AIRFLOW_CHANNEL,
        text: str,
        thread_ts: Optional[str] = None,
        reply_broadcast: bool = False,
        **kwargs: Any,
    ) -> SlackResponse:
        """
        Utility function that sends a scheduled message to a Slack channel.

        Args:
            post_at (int): The timestamp of the scheduled message.
            channel (str): The ID of the channel to send the message to.
            text (str): The text of the message.
            **kwargs: Additional arguments for the message. It can be attachments (list[Attatchments]) or blocks (list[dict[str, Any]]) <However, discouraged, use `send_scheduled(message=ScheduledMessage(...))` instead>.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/chat.scheduleMessage
        """
        result = self.chat_scheduleMessage(
            post_at=post_at,
            channel=channel,
            text=text,
            thread_ts=thread_ts,
            reply_broadcast=reply_broadcast,
            **kwargs,
        )
        return SlackResponse.from_sdk(result)

    def send_scheduled(self, message: ScheduledMessage) -> SlackResponse:
        """
        Sends a scheduled message to a Slack channel.

        Args:
            message (ScheduledMessage): The message to send.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/chat.scheduleMessage
        """
        result = self.chat_scheduleMessage(**message.model_dump(exclude_none=True))
        return SlackResponse.from_sdk(result)

    def fetch_scheduled_messages(
        self,
        *,
        channel: Optional[str] = None,
        latest: Optional[str] = None,
        limit: Optional[int] = None,
        oldest: Optional[str] = None,
        **kwargs: Any,
    ) -> SlackResponse:
        """
        Fetches a list of scheduled messages from Slack.

        Args:
            channel (str): The ID of the channel to fetch messages from. (If None, fetches from all channels)
            latest (str): The latest timestamp to fetch messages from. (If None, fetches till the end)
            limit (int): The maximum number of original entries to return. (If None, there's no limit)
            oldest (str): The oldest timestamp to fetch messages from. (If None, fetches from the beginning)

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/chat.scheduledMessages.list
        """
        kwargs.update(
            {
                "channel": channel,
                "latest": latest,
                "limit": limit,
                "oldest": oldest,
            }
        )
        result = self.chat_scheduledMessages_list(**kwargs)
        return SlackResponse.from_sdk(result)

    def send_and_pin_msg_(self, **kwargs: Any) -> SlackResponse:
        """
        Utility function that sends a message to a Slack channel and pins it.

        Args:
            **kwargs: The arguments for the message. It can be attachments (list[Attatchments]) or blocks (list[dict[str, Any]]) <However, discouraged, use `send_and_pin_msg(message=Message(...))` instead>.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/chat.postMessage
        """
        result = self.send_msg_(**kwargs)
        result += SlackResponse.from_sdk(
            self.pins_add(
                channel=kwargs.get("channel", AIRFLOW_CHANNEL),
                timestamp=result["ts"],
            )
        )
        return result

    def send_and_pin_msg(self, message: Message) -> SlackResponse:
        """
        Sends a message to a Slack channel and pins it.

        Args:
            message (Message): The message to send.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/chat.postMessage
        """
        result = self.send_msg(message)
        result += SlackResponse.from_sdk(
            self.pins_add(
                channel=message.channel,
                timestamp=result["ts"],
            )
        )
        return result

    def bookmark_add_(
        self,
        *,
        channel_id: str,
        title: str,
        type: str,
        **bookmark: Any,
    ) -> SlackResponse:
        """
        Utility function to add a bookmark without having to create a Bookmark object.

        Args:
            *bookmark: The bookmark arguments to add. (channel)

        Returns:
            dict: The response from the Slack API.
        """
        bookmark.update(
            {
                "channel_id": channel_id,
                "title": title,
                "type": type,
            }
        )
        result = self.bookmarks_add(**bookmark)
        return SlackResponse.from_sdk(result)

    def bookmark_add(self, bookmark: Bookmark) -> SlackResponse:
        """
        Adds a new bookmark to a Slack channel.

        Args:
            bookmark (Bookmark | None): The bookmark object to add. If None, a new bookmark will be created using the bookmark_kwargs.

        Returns:
            dict: The response from the Slack API.
        """
        result = self.bookmarks_add(**bookmark.model_dump(exclude_none=True))
        return SlackResponse.from_sdk(result)

    def bookmark_upsert_(
        self,
        *,
        channel_id: str,
        title: str,
        type: str,
        **bookmark: Any,
    ) -> SlackResponse:
        """
        This function first check if a bookmark exists with the same title
        If the bookmark exists: Update the value
        Else: Just create the bookmark
        """
        bookmark.update(
            {
                "channel_id": channel_id,
                "title": title,
                "type": type,
            }
        )
        response = self.bookmarks_list(channel_id=channel_id)
        if not response["ok"]:
            raise SlackApiError(
                message=f"Not available method, further analysis is required {response['error']}",
                response=response,
            )

        bm_id = next(
            (
                bm["id"]
                for bm in cast(list[dict[str, Any]], response["bookmarks"])
                if bm["title"] == title
            ),
            None,
        )
        if bm_id:
            sdk_response = self.bookmarks_edit(bookmark_id=bm_id, **bookmark)
        else:
            sdk_response = self.bookmarks_add(**bookmark)
        return SlackResponse.from_sdk(sdk_response)

    def bookmark_upsert(self, bookmark: Bookmark) -> SlackResponse:
        """
        This function first check if a bookmark exists with the same title
        If the bookmark exists: Update the value
        Else: Just create the bookmark
        """
        response = self.bookmarks_list(channel_id=bookmark.channel_id)
        if not response["ok"]:
            raise SlackApiError(
                message=f"Not available method, further analysis is required {response['error']}",
                response=response,
            )

        bm_id = next(
            (
                bm["id"]
                for bm in cast(list[dict[str, Any]], response["bookmarks"])
                if bm["title"] == bookmark.title
            ),
            None,
        )

        if bm_id:
            sdk_response = self.bookmarks_edit(bookmark_id=bm_id, **bookmark.model_dump(exclude_none=True))  # fmt:skip
        else:
            sdk_response = self.bookmarks_add(**bookmark.model_dump(exclude_none=True))
        return SlackResponse.from_sdk(sdk_response)

    def send_image(
        self,
        *,
        channel: str,
        image: bytes,
        image_name: str,
        image_extension: str,
        message: str,
        thread_ts: Optional[str] = None,
        **kwargs: Any,  # Is for ignoring the rest of the named arguments
    ) -> str:
        """
        This functions first uploads an image to slack and then sends it to a channel.
        NOTE: The bot must be in the channel to send the image.

        Args:
            channel (str): the slack channel id
            image (bytes): the image
            image_name (str): the image name
            image_extension (str): the image extension
            thread_ts (str): the thread timestamp
            message (str): the message to send with the image

        > Check the official documentation of the Slack API for more information:
            > https://api.slack.com/methods/files.getUploadURLExternal
            > https://api.slack.com/methods/files.completeUploadExternal
        """
        try:
            file_id, _ = self.file_upload(
                filename=f"{image_name}.{image_extension}",
                body=image,
                channel_id=channel,
                initial_comment=message,
                thread_ts=thread_ts,
                **kwargs,
            )

            return file_id
        except SlackApiError as e:
            raise e
        except Exception as e:
            raise SlackApiError(message="Error uploading image", response=str(e))

    def file_upload(
        self,
        filename: str,
        body: bytes,
        *,
        snippet_type: Optional[Filetype] = None,
        publicly_available: bool = False,
        **extra_file_data: Any,
    ) -> tuple[str, str]:
        """
        Wrapper to update from files_uploadV2 and files_upload to the Slack's recommended flow
        for uploading files. This method uploads a file to Slack and returns the file ID and permalink.

        It uses the files.getUploadURLExternal and files.completeUploadExternal methods to upload the file.

        Args:
            filename (str): The name of the file to upload.
            body (bytes): The content of the file to upload.
            snippet_type (str): The type of the snippet. Default is None.
            publicly_available (bool): Whether the file should be publicly available. Default is False.

        extra_file_data: Any additional data to include in the file upload request. This can include fields like initial_comment, channel_id, etc.

        Returns:
            tuple: file_id, permalink (whether public or not)
        """
        alt_txt = extra_file_data.pop("alt_txt", None)

        u_response = cast(
            dict[str, Any],
            self.files_getUploadURLExternal(
                filename=filename,
                length=len(body),
                alt_txt=alt_txt,
                snippet_type=snippet_type,
            ),
        )
        requests.post(u_response["upload_url"], data=body)
        c_response = cast(
            dict[str, Any],
            self.files_completeUploadExternal(
                files=[{"id": u_response["file_id"], "title": filename}],
                **extra_file_data,
            ),
        )

        file_info: dict[str, Any] = c_response["files"][0]
        file_id: str = file_info["id"]
        permalink: str = file_info["permalink"]
        if publicly_available and not file_info.get("is_public"):
            p_response = cast(dict[str, Any], self.files_sharedPublicURL(file=file_id))
            permalink = p_response["file"]["permalink_public"]

        return file_id, permalink

    def crear_canal(self, name: str, is_private: bool = False) -> SlackResponse:
        """
        Creates a new channel.

        Args:
            name (str): The name of the channel.
            is_private (bool): Whether the channel is private. Default is False.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/conversations.create
        """
        result = self.conversations_create(
            name=name,
            is_private=is_private,
        )
        return SlackResponse.from_sdk(result)

    create_channel = crear_canal

    @overload
    def get_channel(
        self,
        *,
        channel_id: str,
        include_num_members: bool = False,
        raise_exception: bool = False,
        return_archived: bool = False,
    ) -> Optional[dict[str, Any]]:
        """
        Gets information about a channel.

        Args:
            channel_id (str): The ID of the channel.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/conversations.info
        """

    @overload
    def get_channel(
        self,
        *,
        channel_name: str,
        include_num_members: bool = False,
        raise_exception: bool = False,
        return_archived: bool = False,
    ) -> Optional[dict[str, Any]]:
        """
        Gets information about a channel.

        Args:
            channel_name (str): The name of the channel.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/conversations.info
        """

    def get_channel(
        self,
        *,
        channel_id: Optional[str] = None,
        channel_name: Optional[str] = None,
        include_num_members: bool = False,
        raise_exception: bool = False,
        return_archived: bool = False,
    ) -> Optional[dict[str, Any]]:
        if not channel_id and not channel_name:
            raise ValueError("Either channel_id or channel_name must be provided")

        if channel_id:
            result = self.conversations_info(
                channel=channel_id,
                include_num_members=include_num_members,
            ).data
            if not isinstance(result, dict):
                raise TypeError("Invalid response from Slack API")
        else:
            result = next(
                (
                    channel
                    for channel in self._get_channels()
                    if channel["name"] == channel_name
                    and (return_archived or not channel["is_archived"])
                ),
                None,
            )
            if raise_exception and not result:
                raise ValueError(f"Channel with name {channel_name} not found")

        return result

    def _get_channels(self) -> Iterator[dict[str, Any]]:
        """
        Lazy function that gets a list of all channels in the workspace.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/conversations.list
        """
        scope = "public_channel,private_channel"
        result = self.conversations_list(types=scope, limit=300)
        yield from result["channels"]
        while next_c := cast(Optional[str], result["response_metadata"]["next_cursor"]):
            result = self.conversations_list(types=scope, cursor=next_c, limit=300)
            yield from result["channels"]

    def get_channels(self) -> list[dict[str, Any]]:
        """
        Gets a list of all channels in the workspace.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/conversations.list
        """
        return list(self._get_channels())

    def get_channel_id(
        self, channel_name: str, return_archived: bool = False
    ) -> Optional[str]:
        """
        Gets the channel ID by channel name.

        Args:
            channel_name (str): The name of the channel.
        """
        channel = self.get_channel(
            channel_name=channel_name, return_archived=return_archived
        )
        return channel["channel"]["id"] if channel and channel["ok"] else None

    channel_exists = get_channel_id

    def get_channel_name(
        self, channel_id: str, return_archived: bool = False
    ) -> Optional[str]:
        """
        Gets the channel name by channel ID.

        Args:
            channel_id (str): The ID of the channel.
        """
        channel = self.get_channel(
            channel_id=channel_id, return_archived=return_archived
        )
        return channel["channel"]["name"] if channel and channel["ok"] else None

    def upsert_channel(self, name: str, is_private: bool = False) -> str:
        """
        Creates a new channel if it does not exist, otherwise returns the ID of the existing channel.

        Args:
            name (str): The name of the channel.
            is_private (bool): Whether the channel is private. Default is False.
        """
        c_id = self.get_channel_id(name)
        if c_id:
            return c_id
        else:
            return self.crear_canal(name=name, is_private=is_private)["channel"]["id"]

    def invitar_canal(self, channel: str, *users: str, force: bool = True) -> dict[str, Any]:
        """
        Invites users to a channel.

        Args:
            channel (str): The ID of the channel.
            *users (str): The IDs of the users to invite.
            force (bool): Whether to ignore certain errors and return the response anyway.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/conversations.invite
        """
        if not users:
            raise ValueError("At least one user must be provided")

        try:
            return self.conversations_invite(channel=channel, users=users, force=force).data  # pyright: ignore[reportReturnType]
        except SlackApiError as e:
            e.response = cast(dict[str, Any], e.response)
            if e.response["error"] in ("already_in_channel", "cant_invite") and force:
                return e.response
            raise SlackApiError(
                message="Error inviting users to channel",
                response=e.response,
            )

    invite_channel = invitar_canal

    def uninvitar_canal(self, channel: str, *users: str, force: bool = True) -> list[dict[str, Any]]:
        """
        Removes (kicks) users from a channel.

        Args:
            channel (str): The ID of the channel.
            *users (str): The IDs of the users to uninvite.
            force (bool): Whether to ignore non-critical errors like 'not_in_channel'.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/conversations.kick
        """
        if not users:
            raise ValueError("At least one user must be provided")

        results: list[dict[str, Any]] = []
        for user in users:
            try:
                result = self.conversations_kick(channel=channel, user=user).data
                if isinstance(result, bytes):
                    result = json.loads(result)
                results.append(cast(dict[str, Any], result))
            except SlackApiError as e:
                e.response = cast(dict[str, Any], e.response)
                if e.response["error"] in ("cant_kick_self", "not_in_channel") and force:
                    results.append(e.response)
                else:
                    raise SlackApiError(
                        message="Error uninviting users from channel",
                        response=e.response,
                    )
        return results

    uninvite_channel = uninvitar_canal
    kick_channel = uninvitar_canal

    def get_members(self, exclude_bots: bool = True) -> dict[str, SlackProfile]:
        """
        Gets a list of all users in the workspace.

        Args:
            exclude_bots (bool): Whether to exclude bots. Default is True.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/users.list
        """
        return {
            member.id: member
            for member in self._get_users(
                exclude_bots=exclude_bots,
                exclude_deleted=True,
            )
        }

    def get_users_id_name(self, exclude_bots: bool = True) -> dict[str, str]:
        """
        Retrieves a dictionary of Slack user IDs and names. Previously known as get_users_id
        """
        return {
            user.id: user.real_name
            for user in self._get_users(
                exclude_bots=exclude_bots,
                exclude_deleted=True,
            )
        }

    def get_user_info_by_id(self, user_id: str, **kwargs: Any) -> SlackProfile:
        """
        Gets the user profile by user ID.

        Args:
            user_id (str): The Slack ID of the user.
            **kwargs: Additional arguments to pass to the users_info method.

        Returns:
            SlackProfile: The profile information of the user.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/users.info
        """
        if user_id == "USLACKBOT":
            raise ValueError("Cannot get user info for USLACKBOT")
        kwargs.update({"user": user_id})
        result = cast(User, self.users_info(**kwargs)["user"])
        return SlackProfile(**result)  # type: ignore

    def get_user_id_email(
        self,
        email: str,
        exclude_bots: bool = False,
        exclude_deleted: bool = False,
    ) -> Optional[str]:
        """
        Gets the user ID by email.

        Args:
            email (str): The email of the user.
        """
        return next(
            (
                user.id
                for user in self._get_users(
                    exclude_bots=exclude_bots,
                    exclude_deleted=exclude_deleted,
                )
                if user.email == email
            ),
            None,
        )
    
    get_user_id_by_email = get_user_id_email
    
    def get_user_data_by_email(self, email: str) -> Optional[SlackProfile]:
        """
        Gets the full user data by a given email

        Args:
            email (str): The email of the user.
        """
        return next(
            (
                user
                for user in self._get_users(
                    exclude_bots=True,
                    exclude_deleted=True,
                )
                if user.email == email
            ),
            None,
        )

    def get_user_email_by_id(self, user_id: str) -> Optional[str]:
        """
        Gets the user email by user ID.

        Args:
            user_id (str): The Slack ID of the user.

        Returns:
            Optional[str]: The email of the user, or None if not found.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/users.info
        """
        user = cast(User, self.users_info(user=user_id)["user"])
        return SlackProfile(**user).email  # type: ignore

    def _get_users(self, *, exclude_bots: bool, exclude_deleted: bool) -> Iterator[SlackProfile]:
        """
        Lazy function that gets a list of all users in the workspace.

        Args:
            exclude_bots (bool): Whether to exclude bots. Default is True.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/users.list
        """
        cursor: Optional[str] = None
        params: dict[str, Any] = {"limit": 300}
        while True:
            if cursor:
                params["cursor"] = cursor
            result = self.users_list(**params)
            yield from (
                SlackProfile(**member)  # type: ignore
                for member in cast(Iterator[User], result["members"])
                if not (exclude_bots and (member["is_bot"] or member["id"] == "USLACKBOT"))
                and not (exclude_deleted and member["deleted"])
            )
            cursor = result.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break

    def fetch_members(self, exclude_bots: bool = True, exclude_deleted: bool = True) -> list[SlackProfile]:
        """
        Gets a list of all users in the workspace.

        Args:
            exclude_bots (bool): Whether to exclude bots. Default is True.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/users.list
        """
        return list(self._get_users(exclude_bots=exclude_bots, exclude_deleted=exclude_deleted))

    # fmt:off
    @overload
    def upload_file(self, **single: Unpack[SingleFileUpload]) -> list[SlackResponse]: ...
    @overload
    def upload_file(self, **multi: Unpack[MultiFileUpload]) -> list[SlackResponse]: ...
    # fmt:on
    def upload_file(self, **data: Any) -> list[SlackResponse]:
        thread_ts: Optional[str] = data.get("thread_ts")
        channel = data["channel"]

        file_ids: list[str] = []

        # Handle MultiFileUpload
        if "files" in data:
            multi: MultiFileUpload = data  # pyright: ignore[reportAssignmentType]

            # Send initial comment if provided
            if initial := multi.get("initial_comment"):
                response = self.send_msg_(
                    text=initial,
                    channel=channel,
                    thread_ts=thread_ts,
                )
                thread_ts = thread_ts or response.ts

            for s_file in multi["files"]:
                s_file["thread_ts"] = thread_ts
                s_file["channel"] = channel
                file_responses = self.upload_file(**s_file)
                file_ids.extend([resp.file["id"] for resp in file_responses])

        # Handle SingleFileUpload
        elif "filename" in data:
            single: SingleFileUpload = data  # pyright: ignore[reportAssignmentType]

            getup_response = self.files_getUploadURLExternal(
                filename=single["filename"],
                length=len(single["content"]),
                alt_txt=None,
                snippet_type=single.get("snippet_type", "auto"),
            )

            content_bytes = (
                single["content"].encode()
                if isinstance(single["content"], str)
                else single["content"]
            )

            response = requests.post(getup_response["upload_url"], data=content_bytes)  # pyright: ignore[reportArgumentType]
            if response.status_code != 200:
                raise ValueError("Upload failed")

            completeup_response = self.files_completeUploadExternal(
                files=[{"id": getup_response["file_id"], "title": single["filename"]}],  # pyright: ignore[reportArgumentType]
                channel_id=single["channel"],
                initial_comment=single.get("initial_comment"),
                thread_ts=thread_ts,
            )

            file_ids.extend([f["id"] for f in completeup_response["files"]])  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType]

        else:
            raise ValueError("Invalid keys passed")

        return [
            SlackResponse.from_sdk(self.files_info(file=file_id))
            for file_id in file_ids
        ]

    def add_remote_file(self, **remote_file: Unpack[RemoteFile]) -> SlackResponse:
        """
        Adds a remote file to Slack.
        Args:
            remote_file (RemoteFile): The remote file to add.
        Returns:
            SlackResponse: The response from the Slack API.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/files.remote.add
        """
        result = self.files_remote_add(**remote_file)
        return SlackResponse.from_sdk(result)

    def share_remote_file(self, external_id: str, *channels: str) -> SlackResponse:
        """
        Shares a remote file with specified channels.
        Args:
            external_id (str): The external ID of the file.
            channels (str): Comma-separated list of channel IDs where the file will be shared.
        Returns:
            SlackResponse: The response from the Slack API.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/files.remote.share
        """
        assert channels and all(channels), "At least one valid channel ID must be provided"  # fmt:skip
        # Force channels to be rightfully splitted (The scenario where the user sends a channels by commas)
        channels_ = ",".join(channels).split(",")
        if len(channels_) != len(channels):
            warn(
                "Channels were not properly splitted, check the channels argument passed to the function"
            )
        result = self.files_remote_share(external_id=external_id, channels=channels)
        return SlackResponse.from_sdk(result)

    update_remote_file = SlackLibClient.files_remote_update
    remove_remote_file = SlackLibClient.files_remote_remove

    def open_modal(self, trigger_id: str, view: dict[str, Any]) -> SlackResponse:
        """
        Opens a modal in Slack.

        Args:
            trigger_id (str): The trigger ID.
            view (dict): The view to open.

        Returns:
            dict: The response from the Slack API.
        """
        result = self.views_open(trigger_id=trigger_id, view=view)
        return SlackResponse.from_sdk(result)

    def update_modal(self, view_id: str, view: dict[str, Any]) -> SlackResponse:
        """
        Updates a modal in Slack.

        Args:
            view_id (str): The view ID.
            view (dict): The view to update.

        Returns:
            dict: The response from the Slack API.
        """
        result = self.views_update(view_id=view_id, view=view)
        return SlackResponse.from_sdk(result)

    # fmt:off
    bookmarks_add = rate_limited(TIER_2)(SlackLibClient.bookmarks_add)
    bookmarks_edit = rate_limited(TIER_2)(SlackLibClient.bookmarks_edit)
    bookmarks_list = rate_limited(TIER_3)(SlackLibClient.bookmarks_list)
    bookmarks_remove = rate_limited(TIER_2)(SlackLibClient.bookmarks_remove)

    chat_delete = rate_limited(TIER_3)(SlackLibClient.chat_delete)
    chat_postEphemeral = rate_limited(TIER_4)(SlackLibClient.chat_postEphemeral)
    chat_postMessage = rate_limited(POST_MSG)(SlackLibClient.chat_postMessage)
    chat_scheduleMessage = rate_limited(TIER_3)(SlackLibClient.chat_scheduleMessage)
    chat_update = rate_limited(TIER_3)(SlackLibClient.chat_update)

    chat_scheduledMessages_list = rate_limited(TIER_3)(SlackLibClient.chat_scheduledMessages_list)

    conversations_archive = rate_limited(TIER_2)(SlackLibClient.conversations_archive)
    conversations_create = rate_limited(TIER_2)(SlackLibClient.conversations_create)
    conversations_history = rate_limited(TIER_3)(SlackLibClient.conversations_history)
    conversations_info = rate_limited(TIER_3)(SlackLibClient.conversations_info)
    conversations_invite = rate_limited(TIER_3)(SlackLibClient.conversations_invite)
    conversations_kick = rate_limited(TIER_3)(SlackLibClient.conversations_kick)
    conversations_list = rate_limited(TIER_3)(SlackLibClient.conversations_list)
    conversations_members = rate_limited(TIER_4)(SlackLibClient.conversations_members)
    conversations_rename = rate_limited(TIER_2)(SlackLibClient.conversations_rename)

    files_getUploadURLExternal = rate_limited(TIER_4)(SlackLibClient.files_getUploadURLExternal)
    files_completeUploadExternal = rate_limited(TIER_4)(SlackLibClient.files_completeUploadExternal)
    files_sharedPublicURL = rate_limited(TIER_3)(SlackLibClient.files_sharedPublicURL)
    files_upload = rate_limited(TIER_2)(SlackLibClient.files_upload)
    files_upload_v2 = rate_limited(TIER_4)(SlackLibClient.files_upload_v2)
    files_info = rate_limited(TIER_4)(SlackLibClient.files_info)

    users_info = rate_limited(TIER_4)(SlackLibClient.users_info)
    users_list = rate_limited(TIER_2)(SlackLibClient.users_list)
    users_lookupByEmail = rate_limited(TIER_3)(SlackLibClient.users_lookupByEmail)

    views_open = rate_limited(TIER_4)(SlackLibClient.views_open)
    views_publish = rate_limited(TIER_4)(SlackLibClient.views_publish)
    views_push = rate_limited(TIER_4)(SlackLibClient.views_push)
    views_update = rate_limited(TIER_4)(SlackLibClient.views_update)
    # fmt:on

    @overload
    async def asend_msg_(
        self,
        *,
        text: str,
        channel: str = AIRFLOW_CHANNEL,
        thread_ts: Optional[str] = None,
        reply_broadcast: bool = False,
        **kwargs: Any,  # attachments, blocks or metadata
    ) -> SlackResponse:
        """
        ASYNC VERSION
        Utility function that sends a message to a Slack channel.
        If the channel is a user ID, the message will be sent as a direct message to that user.
        If the thread_ts is set, the message will be sent as a reply to the specified thread and if the reply_broadcast is set to True, the message will also be sent to the entire channel.

        Args:
            text (str): The text of the message.
            channel (str): The ID of the channel to send the message to. Default is the AIRFLOW_CHANNEL.
            thread_ts (str): The timestamp of the parent message to reply to.
            reply_broadcast (bool): Whether to send the message to the entire channel. Default is False.
            **kwargs: Additional arguments for the message. \
                <However, discouraged, use `send_msg(message=Message(...))` instead>\
                attachments (list[Attatchments]), blocks (list[dict[str, Any]]), metadata (MessageMetadata)

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/chat.postMessage
        """

    @overload
    async def asend_msg_(
        self,
        *,
        content: str,
        channel: str = AIRFLOW_CHANNEL,
        thread_ts: Optional[str] = None,
        reply_broadcast: bool = False,
        initial_comment: Optional[str] = None,
        snippet_type: Filetype = "auto",
        **kwargs: Any,
    ) -> SlackResponse:
        """
        ASYNC VERSION
        Utility function that sends a long message to a Slack channel.
        The message is sent as a file, to avoid the truncate originated from the 4000 characters limit of the text field.

        Args:
            content (str): The text of the message.
            channel (str): The ID of the channel to send the message to. Default is the AIRFLOW_CHANNEL.
            thread_ts (str): The timestamp of the parent message to reply to.
            reply_broadcast (bool): Whether to send the message to the entire channel. Default is False.
            initial_comment (str): The text of the initial comment.
            snippet_type (str): The type of the snippet. Default is None.

        > Check the official documentation of the Slack API for more information:
            > https://api.slack.com/methods/files.upload  [Deprecated but shows the use of files.uploadv2]
            > https://api.slack.com/methods/files.getUploadURLExternal
            > https://api.slack.com/methods/files.completeUploadExternal
        """

    async def asend_msg_(
        self,
        *,
        text: Optional[str] = None,
        channel: str = AIRFLOW_CHANNEL,
        thread_ts: Optional[str] = None,
        reply_broadcast: bool = False,
        initial_comment: Optional[str] = None,
        snippet_type: Filetype = "auto",
        **kwargs: Any,
    ) -> SlackResponse:
        kwargs.update(
            {
                "text": text,
                "channel": channel,
                "thread_ts": thread_ts,
                "reply_broadcast": reply_broadcast,
                "initial_comment": initial_comment,
                "snippet_type": snippet_type,
            }
        )
        if "attachments" in kwargs or "blocks" in kwargs:
            warn("Use the `send_msg` method for rich content messages")

        if "content" in kwargs:
            result = await asyncio.to_thread(self.files_upload_v2, **kwargs)
        elif "text" in kwargs:
            result = await asyncio.to_thread(self.chat_postMessage, **kwargs)
        else:
            raise ValueError("Invalid message type")
        response = SlackResponse.from_sdk(result)
        self._message_listener.notify_listeners(response)
        return response

    @overload
    async def asend_msg(self, message: Message) -> SlackResponse:
        """
        ASYNC VERSION
        Sends a message to a Slack channel.
        If the channel is a user ID, the message will be sent as a direct message to that user.
        If the thread_ts is set, the message will be sent as a reply to the specified thread and if the reply_broadcast is set to True, the message will also be sent to the entire channel.

        Args:
            message (Message): The message to send.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/chat.postMessage
        """

    @overload
    async def asend_msg(self, message: LongMessage) -> SlackResponse:
        """
        ASYNC VERSION
        Sends a long message to a Slack channel.
        The message is sent as a file, to avoid the truncate originated from the 4000 characters limit of the text field.

        Args:
            message (LongMessage): The message to send.

        > Check the official documentation of the Slack API for more information:
            > https://api.slack.com/methods/files.upload  [Deprecated but shows the use of files.uploadv2]
            > https://api.slack.com/methods/files.getUploadURLExternal
            > https://api.slack.com/methods/files.completeUploadExternal
        """

    async def asend_msg(self, message: Union[Message, LongMessage]) -> SlackResponse:
        if isinstance(message, LongMessage):
            result = await asyncio.to_thread(self.files_upload_v2, **message.model_dump(exclude_none=True))
        else:
            result = await asyncio.to_thread(self.chat_postMessage, **message.model_dump(exclude_none=True))
        response = SlackResponse.from_sdk(result)
        self._message_listener.notify_listeners(response)
        return response
    

    async def aopen_modal(self, trigger_id: str, view: dict[str, Any]) -> SlackResponse:
        """
        ASYNC VERSION
        Opens a modal in Slack.

        Args:
            trigger_id (str): The trigger ID.
            view (dict): The view to open.

        Returns:
            dict: The response from the Slack API.
        """
        result = await asyncio.to_thread(self.views_open, trigger_id=trigger_id, view=view)
        return SlackResponse.from_sdk(result)

    async def aupdate_modal(self, view_id: str, view: dict[str, Any]) -> SlackResponse:
        """
        Updates a modal in Slack.

        Args:
            view_id (str): The view ID.
            view (dict): The view to update.

        Returns:
            dict: The response from the Slack API.
        """
        result = await asyncio.to_thread(self.views_update, view_id=view_id, view=view)
        return SlackResponse.from_sdk(result)