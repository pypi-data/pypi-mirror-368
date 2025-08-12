import pkgutil

def fun(filename: str) -> bytes:
    return pkgutil.get_data(__name__, f"fun/{filename}")

def list_fun() -> list[str]:
    return [
        "alaki.json.enc",
        "chandsaletbod.json.enc",
        "chanvaghte.json.enc",
        "dastan.json.enc",
        "deghatkardin.json.enc",
        "dialog.json.enc",
        "eteraf.json.enc",
        "fantezi.json.enc",
        "khaterat.json.enc",
        "mrghazi.json.enc",
        "panapa.json.enc",
        "ravanshenasi.json.enc",
    ]

from .bot import (
    Bot,
    BotInfo,
)
from .filter import Filters
from .ReplyKeyboard import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo as ReplyWebAppInfo
from .InlineKeyboard import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo as InlineWebAppInfo, CopyTextButton
from .update_wrapper import (
    UpdateWrapper,
    CallbackQuery,
    Message,
    Chat,
    ChatMember,
    PhotoSize,
    Audio,
    Document,
    Voice,
    Location,
    Video,
    Invoice,
    Sticker,
    Contact,
    InputMedia,
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaAnimation,
    InputMediaAudio,
    InputMediaDocument,
    InputFile,
    User,
    File,
    ChatPhoto,
    SuccessfulPayment
)
from .Database import Database

__all__ = [
    'Bot',
    'BotInfo',

    'ReplyKeyboardMarkup',
    'KeyboardButton',
    'ReplyWebAppInfo',
    'InlineKeyboardMarkup',
    'InlineKeyboardButton',
    'InlineWebAppInfo',
    'CopyTextButton',

    'InputMedia',
    'InputMediaPhoto',
    'InputMediaVideo',
    'InputMediaAnimation',
    'InputMediaAudio',
    'InputMediaDocument',
    'InputFile',
    'ChatPhoto',

    'Filters',

    'UpdateWrapper',
    'CallbackQuery',
    'Message',
    'User',
    'Chat',
    'ChatMember',
    'PhotoSize',
    'Audio',
    'Document',
    'Voice',
    'Location',
    'Video',
    'Invoice',
    'Sticker',
    'Contact',
    'SuccessfulPayment',
    'File',

    'Database'
]

__version__ = "1.0.3"
__author__ = "BaleCore Team"
__license__ = "MIT"
__description__ = "A modern Python framework for building Bale bots"