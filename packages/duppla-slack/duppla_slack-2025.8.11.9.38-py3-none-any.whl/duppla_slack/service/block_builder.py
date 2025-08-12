from typing import Any, Literal, Mapping, Sequence, TypedDict, Union, overload

from typing_extensions import NotRequired, Unpack

from duppla_slack.constants.templates import Filetype


# region General
class _PlainText(TypedDict):
    type: str
    text: str
    emoji: NotRequired[bool]
    verbatim: NotRequired[bool]


class _Option(TypedDict):
    text: _PlainText
    value: str
    description: NotRequired[_PlainText]
    url: NotRequired[str]


class _OptionGroup(TypedDict):
    label: _PlainText
    options: Sequence[_Option]


class _ConversationFilter(TypedDict):
    include: NotRequired[Sequence[str]]
    exclude_external_shared_channels: NotRequired[bool]
    exclude_bot_users: NotRequired[bool]


class _Trigger(TypedDict):
    url: str
    customizable_input_parameters: NotRequired[Sequence[Any]]


# endregion General


# region Button
class _Button(TypedDict):
    text: _PlainText
    action_id: NotRequired[str]
    url: NotRequired[str]
    value: NotRequired[str]
    style: NotRequired[Literal["primary", "danger"]]


class _WorkflowButton(TypedDict):
    text: _PlainText
    action_id: NotRequired[str]
    workflow: Mapping[Literal["trigger"], _Trigger]
    style: NotRequired[Literal["primary", "danger"]]
    """`style` is only available for `workflow` buttons."""


@overload
def Button(
    type: Literal["button"],
    **button: Unpack[_Button],
) -> Mapping[str, Any]: ...
@overload
def Button(
    type: Literal["workflow_button"],
    **workflow_button: Unpack[_WorkflowButton],
) -> Mapping[str, Any]: ...
def Button(
    type: Literal[
        "button",
        "workflow_button",
    ],
    **kwargs: Any,
) -> Mapping[str, Any]:
    return {"type": type, **kwargs}


# endregion Button


# region Checkbox & Radio Button
class _Checkbox(TypedDict):
    action_id: NotRequired[str]
    options: Sequence[_Option]
    initial_options: NotRequired[Sequence[_Option]]


class _RadioButton(TypedDict):
    action_id: NotRequired[str]
    options: Sequence[_Option]
    initial_option: NotRequired[_Option]


def Checkbox(**checkbox: Unpack[_Checkbox]) -> Mapping[str, Any]:
    return {"type": "checkboxes", **checkbox}


def RadioButton(**radio_button: Unpack[_RadioButton]) -> Mapping[str, Any]:
    return {"type": "radio_buttons", **radio_button}


# endregion Checkbox & Radio Button


# region Date, Time and DateTime Picker
class _DatePicker(TypedDict):
    action_id: NotRequired[str]
    initial_date: NotRequired[str]
    """`initial_date` is defined as a date object in isoformat `date.isoformat()`"""
    placeholder: NotRequired[_PlainText]


class _TimePicker(TypedDict):
    action_id: NotRequired[str]
    initial_time: NotRequired[str]
    """`initial_time` is defined as a time object in isoformat `time.isoformat()`"""
    timezone: NotRequired[str]
    placeholder: NotRequired[_PlainText]


class _DateTimePicker(TypedDict):
    action_id: NotRequired[str]
    initial_date_time: NotRequired[str]
    """`initial_date_time` is defined as a datetime object in isoformat `datetime.isoformat()`"""
    placeholder: NotRequired[_PlainText]


def DatePicker(**date_picker: Unpack[_DatePicker]) -> Mapping[str, Any]:
    return {"type": "datepicker", **date_picker}


def TimePicker(**time_picker: Unpack[_TimePicker]) -> Mapping[str, Any]:
    return {"type": "timepicker", **time_picker}


def DateTimePicker(**date_time_picker: Unpack[_DateTimePicker]) -> Mapping[str, Any]:
    return {"type": "datetimepicker", **date_time_picker}


# endregion DatePicker


# region File
class _FileInput(TypedDict):
    action_id: NotRequired[str]
    filetypes: NotRequired[Sequence[Filetype]]
    """If `filetypes` is not provided, all file types are accepted."""
    max_files: NotRequired[int]


class _PublicImage(TypedDict):
    alt_text: str
    image_url: str


class _SlackImage(TypedDict):
    alt_text: str
    slack_file: Mapping[Literal["url"], str]
    """`slack_file` is a dictionary with a single key `url` and the value is the URL of the file."""


def FileInput(**file_input: Unpack[_FileInput]) -> Mapping[str, Any]:
    return {"type": "file_input", **file_input}


@overload
def Image(
    type: Literal["public"],
    **p_image: Unpack[_PublicImage],
) -> Mapping[str, Any]: ...
@overload
def Image(
    type: Literal["slack"],
    **s_image: Unpack[_SlackImage],
) -> Mapping[str, Any]: ...
def Image(
    type: Literal[
        "public",
        "slack",
    ],
    **kwargs: Any,
) -> Mapping[str, Any]:
    return {"type": "image", **kwargs}


# endregion File


# region Select
class __BaseSelect(TypedDict):
    action_id: NotRequired[str]
    placeholder: NotRequired[_PlainText]


class __BaseMultiSelect(TypedDict):
    action_id: NotRequired[str]
    max_selected_items: NotRequired[int]
    placeholder: NotRequired[_PlainText]


class _StaticSelect(__BaseSelect):
    options: Sequence[_Option]
    option_groups: NotRequired[Sequence[_OptionGroup]]
    """`option_groups` and `options` are mutually exclusive."""
    initial_option: NotRequired[Union[_Option, _OptionGroup]]


class _StaticMultiselect(__BaseMultiSelect):
    options: Sequence[_Option]
    option_groups: NotRequired[Sequence[_OptionGroup]]
    """`option_groups` and `options` are mutually exclusive."""
    initial_options: NotRequired[Sequence[Union[_Option, _OptionGroup]]]


class _UsersSelect(__BaseSelect):
    initial_user: NotRequired[str]


class _UserMultiSelect(__BaseMultiSelect):
    initial_users: NotRequired[Sequence[str]]


class _ConversationsSelect(__BaseSelect):
    initial_conversation: NotRequired[str]
    default_to_current_conversation: NotRequired[bool]
    """If true, the current conversation will be selected by default."""


class _ConversationMultiSelect(__BaseMultiSelect):
    initial_conversations: NotRequired[Sequence[str]]
    default_to_current_conversation: NotRequired[bool]
    """If true, the current conversation will be selected by default."""
    filter: NotRequired[_ConversationFilter]


class _PublicChannelSelect(__BaseSelect):
    initial_channel: NotRequired[str]
    """`initial_channel` is the ID of the channel to be selected by default."""


class _PublicChannelMultiSelect(__BaseMultiSelect):
    initial_channels: NotRequired[Sequence[str]]


@overload
def Select(
    type: Literal["static_select"],
    **ss: Unpack[_StaticSelect],
) -> Mapping[str, Any]: ...
@overload
def Select(
    type: Literal["users_select"],
    **us: Unpack[_UsersSelect],
) -> Mapping[str, Any]: ...
@overload
def Select(
    type: Literal["conversations_select"],
    **cs: Unpack[_ConversationsSelect],
) -> Mapping[str, Any]: ...
@overload
def Select(
    type: Literal["channels_select"],
    **cs: Unpack[_PublicChannelSelect],
) -> Mapping[str, Any]: ...
def Select(
    type: Literal[
        "static_select",
        "users_select",
        "conversations_select",
        "channels_select",
    ],
    **kwargs: Any,
) -> Mapping[str, Any]:
    return {"type": type, **kwargs}


@overload
def Multiselect(
    type: Literal["multi_static_select"],
    **mss: Unpack[_StaticMultiselect],
) -> Mapping[str, Any]: ...
@overload
def Multiselect(
    type: Literal["multi_users_select"],
    **mus: Unpack[_UserMultiSelect],
) -> Mapping[str, Any]: ...
@overload
def Multiselect(
    type: Literal["multi_conversations_select"],
    **mcs: Unpack[_ConversationMultiSelect],
) -> Mapping[str, Any]: ...
@overload
def Multiselect(
    type: Literal["multi_channels_select"],
    **mcs: Unpack[_PublicChannelMultiSelect],
) -> Mapping[str, Any]: ...
def Multiselect(
    type: Literal[
        "multi_static_select",
        "multi_users_select",
        "multi_conversations_select",
        "multi_channels_select",
    ],
    **kwargs: Any,
) -> Mapping[str, Any]:
    return {"type": type, **kwargs}


# endregion Select


# region Input
class _TextInput(TypedDict):
    action_id: NotRequired[str]
    initial_value: NotRequired[str]
    multiline: NotRequired[bool]
    min_length: NotRequired[int]
    max_length: NotRequired[int]
    placeholder: NotRequired[_PlainText]


class _RichTextInput(TypedDict):
    action_id: str
    initial_value: NotRequired[str]
    placeholder: NotRequired[_PlainText]


class _NumberInput(TypedDict):
    is_decimal_allowed: bool
    action_id: NotRequired[str]
    initial_value: NotRequired[str]
    min_value: NotRequired[str]
    max_value: NotRequired[str]
    placeholder: NotRequired[_PlainText]


class _URLInput(TypedDict):
    action_id: NotRequired[str]
    initial_value: NotRequired[str]
    placeholder: NotRequired[_PlainText]


@overload
def Input(
    type: Literal["plain_text_input"],
    **text_input: Unpack[_TextInput],
) -> Mapping[str, Any]: ...
@overload
def Input(
    type: Literal["rich_text_input"],
    **rich_text_input: Unpack[_RichTextInput],
) -> Mapping[str, Any]: ...
@overload
def Input(
    type: Literal["number_input"],
    **number_input: Unpack[_NumberInput],
) -> Mapping[str, Any]: ...
@overload
def Input(
    type: Literal["url_text_input"],
    **url_input: Unpack[_URLInput],
) -> Mapping[str, Any]: ...
def Input(
    type: Literal[
        "plain_text_input",
        "rich_text_input",
        "number_input",
        "url_text_input",
    ],
    **kwargs: Any,
) -> Mapping[str, Any]:
    return {"type": type, **kwargs}


# endregion Input


# region Overflow
class _Overflow(TypedDict):
    action_id: NotRequired[str]
    options: Sequence[_Option]


def Overflow(**overflow: Unpack[_Overflow]) -> Mapping[str, Any]:
    return {"type": "overflow", **overflow}


# endregion Overflow
