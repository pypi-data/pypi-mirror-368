import base64 as BASE64
import inspect
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Dict, List, Optional, Union

from .bot_enums import *

funcs = {}

name_map = {
    "message_direct": "messageDirect",
    "message_add": "messageAdd",
    "bot_hourly": "botHourly",
    "file_create": "fileCreate",
    "conversation_hourly": "conversationHourly",
    "conversation_start": "conversationStart",
    "conversation_user_add": "conversationUserAdd",
    "conversation_user_show": "conversationUserShow",
    "user_visible": "userVisible",
    "thread_stop": "threadStop",
    "input_changed": "inputChanged",
    "web_page_updated": "webPageUpdated",
    "tool_start": "toolStart",
}


def export(name: str):
    """
    Decorator to export functions from your bot
    """

    def inner(func):
        global funcs

        sig = inspect.signature(func)
        parameters = sig.parameters.values()

        # Check if function accepts arbitrary kwargs (**kwargs)
        accepts_kwargs = any(
            p.kind == inspect.Parameter.VAR_KEYWORD for p in parameters
        )

        # Collect allowed parameter names if no **kwargs
        allowed_params = set()
        if not accepts_kwargs:
            for param in parameters:
                if param.kind in (
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    inspect.Parameter.KEYWORD_ONLY,
                ):
                    allowed_params.add(param.name)

        def wrapper(**kwargs):
            if not accepts_kwargs:
                # Filter kwargs to only allowed parameters
                filtered_kwargs = {
                    k: v for k, v in kwargs.items() if k in allowed_params
                }
                return func(**filtered_kwargs)
            return func(**kwargs)

        mapped_name = name_map.get(name)

        funcs[mapped_name if mapped_name is not None else name] = wrapper

        return func

    return inner


class ImageType(StrEnum):
    PUBLIC = "public"
    """public"""

    URI = "uri"
    """uri"""

    BASE64 = "base64"
    """base64"""


class ImageMimeType(StrEnum):
    JPG = "image/jpeg"
    """image/jpeg"""

    PNG = "image/png"
    """image/png"""

    GIF = "image/gif"
    """image/gif"""

    WEBP = "image/webp"
    """image/webp"""


@dataclass
class Image:
    type: ImageType
    width: int
    height: int
    base64: Optional[str] = None
    mime_type: Optional[ImageMimeType] = None
    uri: Optional[str] = None
    prompt: Optional[str] = None

    def __init__(
        self,
        type: Optional[ImageType] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        base64: Optional[str] = None,
        mime_type: Optional[ImageMimeType] = None,
        uri: Optional[str] = None,
        prompt: Optional[str] = None,
        file: Optional[str] = None,
        buffer: Optional[bytes] = None,
    ):
        if file is not None:
            with open(file, "rb") as f:
                type = ImageType.BASE64
                base64 = BASE64.b64encode(f.read()).decode()

        if buffer is not None:
            type = ImageType.BASE64
            base64 = BASE64.b64encode(buffer).decode()

        self.type = (
            type
            if type is not None
            else (ImageType.URI if uri is not None else ImageType.BASE64)
        )
        self.width = width if width is not None else 1024
        self.height = height if height is not None else 1024
        self.base64 = base64
        self.mime_type = (
            mime_type
            if mime_type is not None
            else (ImageMimeType.JPG if base64 is not None else None)
        )
        self.uri = uri
        self.prompt = prompt


@dataclass
class Thread:
    id: str
    type: str
    meeting_id: Optional[str] = None
    message_id: Optional[str] = None
    section_id: Optional[str] = None


class ButtonType(StrEnum):
    LINK = "link"
    """link"""

    TEXT = "text"
    """text"""

    BUTTON = "button"
    """button"""

    MENU = "menu"
    """menu"""


@dataclass
class Button:
    type: ButtonType
    icon: Optional[Icon] = None
    text: Optional[str] = None
    lang: Optional[UserLang] = None
    func: Optional[str] = None
    uri: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    buttons: Optional[List["Button"]] = None
    selected: Optional[bool] = None
    disabled: Optional[bool] = None


@dataclass
class MenuItem:
    func: str
    title: str
    params: Optional[Dict[str, Any]] = None
    checked: Optional[bool] = None
    enabled: Optional[bool] = None


@dataclass
class Message:
    id: str
    created: int
    user_id: str
    text: str
    is_bot: bool
    markdown: Optional[str] = None
    system: Optional[bool] = None
    mention_user_ids: Optional[List[str]] = None
    lang: Optional[UserLang] = None
    only_user_ids: Optional[List[str]] = None
    visibility: Optional[MessageVisibility] = None
    color: Optional[MessageColor] = None
    buttons: Optional[List[Button]] = None
    mood: Optional[Mood] = None
    impersonate_user_id: Optional[str] = None
    file_ids: Optional[List[str]] = None
    context_file_id: Optional[str] = None
    thread: Optional[Thread] = None


TextGenMessageContent = Union[str, Image]


@dataclass
class TextGenMessage:
    role: TextGenRole
    content: Union[str, List[TextGenMessageContent]]


@dataclass
class TextGenTool:
    name: str
    description: str
    parameters: Optional[Dict[str, Any]] = None


@dataclass
class Avatar:
    image: Image
    background: Optional[Image]


@dataclass
class User:
    id: str
    name: str
    bio: str
    avatar: Avatar
    voice_id: Optional[str]
    birthday: Optional[int]
    type: str
    lang: UserLang
    timezone: Timezone


@dataclass
class Emotion:
    neutral: int
    happy: int
    sad: int
    angry: int
    fearful: int
    disgusted: int
    surprised: int


@dataclass
class LiveUser:
    id: str
    emotion: Optional[Emotion]
    image: Optional[Image]


@dataclass
class Bot:
    id: str
    name: str
    bio: str
    tags: List[BotTag]


@dataclass
class Character:
    image: Image
    name: str
    voice_id: str


@dataclass
class File:
    id: str
    user_id: str
    type: FileType
    title: str
    text: Optional[str] = None
    image: Optional[Image] = None
    thumbnail: Optional[Image] = None
    markdown: Optional[str] = None
    uri: Optional[str] = None
    characters: Optional[Dict[str, Character]] = None


@dataclass
class Conversation:
    id: str
    type: ConversationType
    title: str
    file_id: Optional[str] = None


@dataclass
class NewsArticle:
    title: str
    content: str
    uri: Optional[str]


@dataclass
class FileChunk:
    file_id: str
    text: str


@dataclass
class SearchArticle:
    title: str
    synopsis: str
    uri: Optional[str]


class ConversationContentType(StrEnum):
    FILE = "file"
    """file"""

    URI = "uri"
    """uri"""


@dataclass
class ConversationContent:
    type: ConversationContentType
    file_id: Optional[str] = None
    disabled: Optional[bool] = None
    uri: Optional[str] = None


class FileSectionType(StrEnum):
    MARKDOWN = "markdown"
    """markdown"""


@dataclass
class FileSection:
    id: str
    type: FileSectionType
    title: Optional[str] = None
    thread: Optional[bool] = None
    markdown: Optional[str] = None
    placeholder: Optional[str] = None
    editable: Optional[bool] = None


@dataclass
class WebPageData:
    html: str
    url: str
    title: str


@dataclass
class KagiSearchItem:
    url: str
    title: str
    snippet: str
    published: Optional[int] = None
    thumbnail: Optional[Image] = None

    def __init__(
        self,
        url: str,
        title: str,
        snippet: str,
        published: Optional[int] = None,
        thumbnail: Optional[Union[Image, dict]] = None,
    ):
        self.url = url
        self.title = title
        self.snippet = snippet
        self.published = published
        self.thumbnail = (
            Image(**thumbnail)
            if thumbnail is not None and isinstance(thumbnail, dict)
            else thumbnail
        )


@dataclass
class KagiSearchOutput:
    items: List[KagiSearchItem]
    related: Optional[List[str]] = None

    def __init__(
        self,
        items: List[Union[KagiSearchItem, dict]],
        related: Optional[List[str]] = None,
    ):
        self.related = related
        self.items = list(
            map(lambda x: KagiSearchItem(**x) if isinstance(x, dict) else x, items)
        )


@dataclass
class Padding:
    left: int
    top: int
    right: int
    bottom: int
