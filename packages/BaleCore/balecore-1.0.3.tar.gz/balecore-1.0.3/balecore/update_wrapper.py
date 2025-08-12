from typing import Optional, List, Dict, Tuple, Any, Union
from datetime import datetime

class User:
    def __init__(self, user_data: dict):
        self.id = user_data.get("id")
        self.is_bot = user_data.get("is_bot")
        self.first_name = user_data.get("first_name")
        self.last_name = user_data.get("last_name")
        self.username = user_data.get("username")
        self.language_code = user_data.get("language_code")

    def __str__(self):
        fields = []
        fields.append(f"id={self.id}")
        fields.append(f"is_bot={self.is_bot}")
        if self.first_name is not None:
            fields.append(f"first_name={self.first_name}")
        if self.last_name is not None:
            fields.append(f"last_name={self.last_name}")
        if self.username is not None:
            fields.append(f"username={self.username}")
        if self.language_code is not None:
            fields.append(f"language_code={self.language_code}")
        
        return "User(\n    " + ",\n    ".join(fields) + "\n)"

class File:
    def __init__(self, file_data: dict):
        self.file_id = file_data.get("file_id")
        self.file_unique_id = file_data.get("file_unique_id")
        self.file_size = file_data.get("file_size")
        self.file_path = file_data.get("file_path")

    def __str__(self):
        fields = []
        fields.append(f"file_id={self.file_id}")
        fields.append(f"file_unique_id={self.file_unique_id}")
        if self.file_size is not None:
            fields.append(f"file_size={self.file_size}")
        if self.file_path is not None:
            fields.append(f"file_path={self.file_path}")
        
        return "File(\n    " + ",\n    ".join(fields) + "\n)"

class SuccessfulPayment:
    def __init__(self, successful_payment_data: dict):
        self.currency = successful_payment_data.get("currency")
        self.total_amount = successful_payment_data.get("total_amount")
        self.invoice_payload = successful_payment_data.get("invoice_payload")
        self.telegram_payment_charge_id = successful_payment_data.get("telegram_payment_charge_id")

    def __str__(self):
        fields = []
        if self.currency is not None:
            fields.append(f"currency={self.currency}")
        if self.total_amount is not None:
            fields.append(f"total_amount={self.total_amount}")
        if self.invoice_payload is not None:
            fields.append(f"invoice_payload={self.invoice_payload}")
        if self.telegram_payment_charge_id is not None:
            fields.append(f"telegram_payment_charge_id={self.telegram_payment_charge_id}")
        
        return "SuccessfulPayment(\n    " + ",\n    ".join(fields) + "\n)"


class ChatPhoto:
    def __init__(self, small_file_id: str, big_file_id: str):
        self.small_file_id = small_file_id
        self.big_file_id = big_file_id

    def to_dict(self):
        return {
            "small_file_id": self.small_file_id,
            "big_file_id": self.big_file_id
        }

class ChatParameter:
    def __init__(self, chat_data: dict):
        self.id = chat_data.get("id")
        self.type = chat_data.get("type")
        self.title = chat_data.get("title")
        self.username = chat_data.get("username")
        self.photo = chat_data.get("photo")
        self.description = chat_data.get("description")
        self.invite_link = chat_data.get("invite_link")
        self.permissions = chat_data.get("permissions")

    def __str__(self):
        fields = []
        fields.append(f"id={self.id}")
        fields.append(f"type={self.type}")
        if self.title is not None:
            fields.append(f"title={self.title}")
        if self.username is not None:
            fields.append(f"username={self.username}")
        if self.photo is not None:
            fields.append(f"photo={self.photo}")
        if self.description is not None:
            fields.append(f"description={self.description}")
        if self.invite_link is not None:
            fields.append(f"invite_link={self.invite_link}")
        if self.permissions is not None:
            fields.append(f"permissions={self.permissions}")
        
        return "ChatParameter(\n    " + ",\n    ".join(fields) + "\n)"

class InputMedia:
    def __init__(self, type: str, media: str, caption: str = None, parse_mode: str = None):
        self.type = type
        self.media = media
        self.caption = caption
        self.parse_mode = parse_mode

    def to_dict(self):
        data = {
            "type": self.type,
            "media": self.media
        }
        if self.caption:
            data["caption"] = self.caption
        if self.parse_mode:
            data["parse_mode"] = self.parse_mode
        return data

class InputMediaPhoto(InputMedia):
    def __init__(self, media: str, caption: str = None, parse_mode: str = None):
        super().__init__("photo", media, caption, parse_mode)

class InputMediaVideo(InputMedia):
    def __init__(self, media: str, caption: str = None, parse_mode: str = None, width: int = None, height: int = None, duration: int = None):
        super().__init__("video", media, caption, parse_mode)
        self.width = width
        self.height = height
        self.duration = duration

    def to_dict(self):
        data = super().to_dict()
        if self.width:
            data["width"] = self.width
        if self.height:
            data["height"] = self.height
        if self.duration:
            data["duration"] = self.duration
        return data

class InputMediaAnimation(InputMedia):
    def __init__(
        self,
        media: str,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        duration: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> None:
        super().__init__("animation", media, caption, parse_mode)
        self.duration = duration
        self.width = width
        self.height = height

    def to_dict(self):
        data = super().to_dict()
        if self.duration:
            data["duration"] = self.duration
        if self.width:
            data["width"] = self.width
        if self.height:
            data["height"] = self.height
        return data

class InputMediaAudio(InputMedia):
    def __init__(
        self,
        media: str,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        duration: Optional[int] = None,
        performer: Optional[str] = None,
        title: Optional[str] = None
    ) -> None:
        super().__init__("audio", media, caption, parse_mode)
        self.duration = duration
        self.performer = performer
        self.title = title

    def to_dict(self):
        data = super().to_dict()
        if self.duration:
            data["duration"] = self.duration
        if self.performer:
            data["performer"] = self.performer
        if self.title:
            data["title"] = self.title
        return data

class InputMediaDocument(InputMedia):
    def __init__(self, media: str, caption: str = None, parse_mode: str = None, disable_content_type_detection: bool = None):
        super().__init__("document", media, caption, parse_mode)
        self.disable_content_type_detection = disable_content_type_detection

    def to_dict(self):
        data = super().to_dict()
        if self.disable_content_type_detection is not None:
            data["disable_content_type_detection"] = self.disable_content_type_detection
        return data

class InputFile:
    def __init__(self, file_path: str, file_name: str = None, mime_type: str = None):
        self.file_path = file_path
        self.file_name = file_name
        self.mime_type = mime_type

    def to_dict(self):
        data = {
            "file_path": self.file_path
        }
        if self.file_name:
            data["file_name"] = self.file_name
        if self.mime_type:
            data["mime_type"] = self.mime_type
        return data


class Chat:
    def __init__(self, chat_data: dict):
        self.id = chat_data.get("id")
        self.type = chat_data.get("type")
        self.title = chat_data.get("title")
        self.username = chat_data.get("username")
        
        photo_data = chat_data.get("photo", {})
        self.photo = (
            (
                PhotoSize({
                    "file_id": photo_data.get("small_file_id"),
                    "file_unique_id": photo_data.get("small_file_unique_id")
                }),
                PhotoSize({
                    "file_id": photo_data.get("big_file_id"),
                    "file_unique_id": photo_data.get("big_file_unique_id")
                })
            )
            if photo_data
            else None
        )
        
        self.description = chat_data.get("description")
        self.invite_link = chat_data.get("invite_link")
        self.permissions = chat_data.get("permissions")

    def __str__(self):
        fields = []
        fields.append(f"id={self.id}")
        fields.append(f"type={self.type}")
        if self.title is not None:
            fields.append(f"title={self.title}")
        if self.username is not None:
            fields.append(f"username={self.username}")
        if self.photo is not None:
            photos = ",\n        ".join(str(p) for p in self.photo)
            fields.append(f"photo=(\n        {photos}\n    )")
        if self.description is not None:
            fields.append(f"description={self.description}")
        if self.invite_link is not None:
            fields.append(f"invite_link={self.invite_link}")
        if self.permissions is not None:
            fields.append(f"permissions={self.permissions}")
        
        return "Chat(\n    " + ",\n    ".join(fields) + "\n)"

class ChatMember:
    def __init__(self, chat_member_data: dict):
        self.user = User(chat_member_data.get("user", {}))
        self.status = chat_member_data.get("status")
        self.custom_title = chat_member_data.get("custom_title")
        self.until_date = chat_member_data.get("until_date")
        self.can_be_edited = chat_member_data.get("can_be_edited")
        self.can_post_messages = chat_member_data.get("can_post_messages")
        self.can_edit_messages = chat_member_data.get("can_edit_messages")
        self.can_delete_messages = chat_member_data.get("can_delete_messages")
        self.can_restrict_members = chat_member_data.get("can_restrict_members")
        self.can_promote_members = chat_member_data.get("can_promote_members")
        self.can_change_info = chat_member_data.get("can_change_info")
        self.can_invite_users = chat_member_data.get("can_invite_users")
        self.can_pin_messages = chat_member_data.get("can_pin_messages")
        self.is_member = chat_member_data.get("is_member")
        self.can_send_messages = chat_member_data.get("can_send_messages")
        self.can_send_media_messages = chat_member_data.get("can_send_media_messages")
        self.can_send_polls = chat_member_data.get("can_send_polls")
        self.can_send_other_messages = chat_member_data.get("can_send_other_messages")
        self.can_add_web_page_previews = chat_member_data.get("can_add_web_page_previews")

    def __str__(self):
        fields = []
        fields.append(f"user={self.user}")
        if self.status is not None:
            fields.append(f"status={self.status}")
        if self.custom_title is not None:
            fields.append(f"custom_title={self.custom_title}")
        if self.until_date is not None:
            fields.append(f"until_date={self.until_date}")
        if self.can_be_edited is not None:
            fields.append(f"can_be_edited={self.can_be_edited}")
        if self.can_post_messages is not None:
            fields.append(f"can_post_messages={self.can_post_messages}")
        if self.can_edit_messages is not None:
            fields.append(f"can_edit_messages={self.can_edit_messages}")
        if self.can_delete_messages is not None:
            fields.append(f"can_delete_messages={self.can_delete_messages}")
        if self.can_restrict_members is not None:
            fields.append(f"can_restrict_members={self.can_restrict_members}")
        if self.can_promote_members is not None:
            fields.append(f"can_promote_members={self.can_promote_members}")
        if self.can_change_info is not None:
            fields.append(f"can_change_info={self.can_change_info}")
        if self.can_invite_users is not None:
            fields.append(f"can_invite_users={self.can_invite_users}")
        if self.can_pin_messages is not None:
            fields.append(f"can_pin_messages={self.can_pin_messages}")
        if self.is_member is not None:
            fields.append(f"is_member={self.is_member}")
        if self.can_send_messages is not None:
            fields.append(f"can_send_messages={self.can_send_messages}")
        if self.can_send_media_messages is not None:
            fields.append(f"can_send_media_messages={self.can_send_media_messages}")
        if self.can_send_polls is not None:
            fields.append(f"can_send_polls={self.can_send_polls}")
        if self.can_send_other_messages is not None:
            fields.append(f"can_send_other_messages={self.can_send_other_messages}")
        if self.can_add_web_page_previews is not None:
            fields.append(f"can_add_web_page_previews={self.can_add_web_page_previews}")
        
        return "ChatMember(\n    " + ",\n    ".join(fields) + "\n)"

class PhotoSize:
    def __init__(self, photo_data: dict):
        self.file_id = photo_data.get("file_id")
        self.file_unique_id = photo_data.get("file_unique_id")
        self.width = photo_data.get("width")
        self.height = photo_data.get("height")
        self.file_size = photo_data.get("file_size")

    def __str__(self):
        fields = []
        fields.append(f"file_id={self.file_id}")
        fields.append(f"file_unique_id={self.file_unique_id}")
        if self.width is not None:
            fields.append(f"width={self.width}")
        if self.height is not None:
            fields.append(f"height={self.height}")
        if self.file_size is not None:
            fields.append(f"file_size={self.file_size}")
        
        return "PhotoSize(\n    " + ",\n    ".join(fields) + "\n)"

class Audio:
    def __init__(self, audio_data: dict):
        self.file_id = audio_data.get("file_id")
        self.file_unique_id = audio_data.get("file_unique_id")
        self.duration = audio_data.get("duration")
        self.performer = audio_data.get("performer")
        self.title = audio_data.get("title")
        self.file_name = audio_data.get("file_name")
        self.mime_type = audio_data.get("mime_type")
        self.file_size = audio_data.get("file_size")
        
        thumbnail_data = audio_data.get("thumbnail", {})
        self.thumbnail = (
            PhotoSize(thumbnail_data)
            if thumbnail_data
            else None
        )

    def __str__(self):
        fields = []
        fields.append(f"file_id={self.file_id}")
        fields.append(f"file_unique_id={self.file_unique_id}")
        if self.duration is not None:
            fields.append(f"duration={self.duration}")
        if self.performer is not None:
            fields.append(f"performer={self.performer}")
        if self.title is not None:
            fields.append(f"title={self.title}")
        if self.file_name is not None:
            fields.append(f"file_name={self.file_name}")
        if self.mime_type is not None:
            fields.append(f"mime_type={self.mime_type}")
        if self.file_size is not None:
            fields.append(f"file_size={self.file_size}")
        if self.thumbnail is not None:
            fields.append(f"thumbnail={self.thumbnail}")
        
        return "Audio(\n    " + ",\n    ".join(fields) + "\n)"

class Document:
    def __init__(self, document_data: dict):
        self.file_id = document_data.get("file_id")
        self.file_unique_id = document_data.get("file_unique_id")
        self.file_name = document_data.get("file_name")
        self.mime_type = document_data.get("mime_type")
        self.file_size = document_data.get("file_size")
        
        thumbnail_data = document_data.get("thumbnail", {})
        self.thumbnail = (
            PhotoSize(thumbnail_data)
            if thumbnail_data
            else None
        )

    def __str__(self):
        fields = []
        fields.append(f"file_id={self.file_id}")
        fields.append(f"file_unique_id={self.file_unique_id}")
        if self.file_name is not None:
            fields.append(f"file_name={self.file_name}")
        if self.mime_type is not None:
            fields.append(f"mime_type={self.mime_type}")
        if self.file_size is not None:
            fields.append(f"file_size={self.file_size}")
        if self.thumbnail is not None:
            fields.append(f"thumbnail={self.thumbnail}")
        
        return "Document(\n    " + ",\n    ".join(fields) + "\n)"

class Voice:
    def __init__(self, voice_data: dict):
        self.file_id = voice_data.get("file_id")
        self.file_unique_id = voice_data.get("file_unique_id")
        self.duration = voice_data.get("duration")
        self.mime_type = voice_data.get("mime_type")
        self.file_size = voice_data.get("file_size")

    def __str__(self):
        fields = []
        fields.append(f"file_id={self.file_id}")
        fields.append(f"file_unique_id={self.file_unique_id}")
        if self.duration is not None:
            fields.append(f"duration={self.duration}")
        if self.mime_type is not None:
            fields.append(f"mime_type={self.mime_type}")
        if self.file_size is not None:
            fields.append(f"file_size={self.file_size}")
        
        return "Voice(\n    " + ",\n    ".join(fields) + "\n)"

class Location:
    def __init__(self, location_data: dict):
        self.longitude = location_data.get("longitude")
        self.latitude = location_data.get("latitude")
        self.horizontal_accuracy = location_data.get("horizontal_accuracy")
        self.live_period = location_data.get("live_period")
        self.heading = location_data.get("heading")
        self.proximity_alert_radius = location_data.get("proximity_alert_radius")

    def __str__(self):
        fields = []
        fields.append(f"longitude={self.longitude}")
        fields.append(f"latitude={self.latitude}")
        if self.horizontal_accuracy is not None:
            fields.append(f"horizontal_accuracy={self.horizontal_accuracy}")
        if self.live_period is not None:
            fields.append(f"live_period={self.live_period}")
        if self.heading is not None:
            fields.append(f"heading={self.heading}")
        if self.proximity_alert_radius is not None:
            fields.append(f"proximity_alert_radius={self.proximity_alert_radius}")
        
        return "Location(\n    " + ",\n    ".join(fields) + "\n)"

class Video:
    def __init__(self, video_data: dict):
        self.file_id = video_data.get("file_id")
        self.file_unique_id = video_data.get("file_unique_id")
        self.width = video_data.get("width")
        self.height = video_data.get("height")
        self.duration = video_data.get("duration")
        self.file_size = video_data.get("file_size")
        
        thumbnail_data = video_data.get("thumbnail", {})
        self.thumbnail = (
            PhotoSize(thumbnail_data)
            if thumbnail_data
            else None
        )

    def __str__(self):
        fields = []
        fields.append(f"file_id={self.file_id}")
        fields.append(f"file_unique_id={self.file_unique_id}")
        if self.width is not None:
            fields.append(f"width={self.width}")
        if self.height is not None:
            fields.append(f"height={self.height}")
        if self.duration is not None:
            fields.append(f"duration={self.duration}")
        if self.file_size is not None:
            fields.append(f"file_size={self.file_size}")
        if self.thumbnail is not None:
            fields.append(f"thumbnail={self.thumbnail}")
        
        return "Video(\n    " + ",\n    ".join(fields) + "\n)"

class Invoice:
    def __init__(self, invoice_data: dict):
        self.title = invoice_data.get("title")
        self.description = invoice_data.get("description")
        self.start_parameter = invoice_data.get("start_parameter")
        self.currency = invoice_data.get("currency")
        self.total_amount = invoice_data.get("total_amount")

    def __str__(self):
        fields = []
        if self.title is not None:
            fields.append(f"title={self.title}")
        if self.description is not None:
            fields.append(f"description={self.description}")
        if self.start_parameter is not None:
            fields.append(f"start_parameter={self.start_parameter}")
        if self.currency is not None:
            fields.append(f"currency={self.currency}")
        if self.total_amount is not None:
            fields.append(f"total_amount={self.total_amount}")
        
        return "Invoice(\n    " + ",\n    ".join(fields) + "\n)"

class Sticker:
    def __init__(self, sticker_data: dict):
        self.file_id = sticker_data.get("file_id")
        self.file_unique_id = sticker_data.get("file_unique_id")
        self.width = sticker_data.get("width")
        self.height = sticker_data.get("height")
        self.is_animated = sticker_data.get("is_animated")
        self.is_video = sticker_data.get("is_video")
        self.emoji = sticker_data.get("emoji")
        self.set_name = sticker_data.get("set_name")
        self.mask_position = sticker_data.get("mask_position")
        self.file_size = sticker_data.get("file_size")
        
        thumbnail_data = sticker_data.get("thumbnail", {})
        self.thumbnail = (
            PhotoSize(thumbnail_data)
            if thumbnail_data
            else None
        )

    def __str__(self):
        fields = []
        fields.append(f"file_id={self.file_id}")
        fields.append(f"file_unique_id={self.file_unique_id}")
        if self.width is not None:
            fields.append(f"width={self.width}")
        if self.height is not None:
            fields.append(f"height={self.height}")
        if self.is_animated is not None:
            fields.append(f"is_animated={self.is_animated}")
        if self.is_video is not None:
            fields.append(f"is_video={self.is_video}")
        if self.emoji is not None:
            fields.append(f"emoji={self.emoji}")
        if self.set_name is not None:
            fields.append(f"set_name={self.set_name}")
        if self.mask_position is not None:
            fields.append(f"mask_position={self.mask_position}")
        if self.file_size is not None:
            fields.append(f"file_size={self.file_size}")
        if self.thumbnail is not None:
            fields.append(f"thumbnail={self.thumbnail}")
        
        return "Sticker(\n    " + ",\n    ".join(fields) + "\n)"

class CallbackQuery:
    def __init__(self, callback_query_data: dict):
        self.id = callback_query_data.get("id")
        self.from_user = User(callback_query_data.get("from", {}))
        message_data = callback_query_data.get("message", {})
        self.message = Message(message_data) if message_data else None
        self.inline_message_id = callback_query_data.get("inline_message_id")
        self.chat_instance = callback_query_data.get("chat_instance")
        self.data = callback_query_data.get("data")
        self.game_short_name = callback_query_data.get("game_short_name")

    def __str__(self):
        fields = []
        fields.append(f"id={self.id}")
        fields.append(f"from_user={self.from_user}")
        if self.message is not None:
            fields.append(f"message={self.message}")
        if self.inline_message_id is not None:
            fields.append(f"inline_message_id={self.inline_message_id}")
        if self.chat_instance is not None:
            fields.append(f"chat_instance={self.chat_instance}")
        if self.data is not None:
            fields.append(f"data={self.data}")
        if self.game_short_name is not None:
            fields.append(f"game_short_name={self.game_short_name}")
        
        return "CallbackQuery(\n    " + ",\n    ".join(fields) + "\n)"

class Contact:
    def __init__(self, contact_data: dict):
        self.phone_number = contact_data.get("phone_number")
        self.first_name = contact_data.get("first_name")
        self.last_name = contact_data.get("last_name")
        self.user_id = contact_data.get("user_id")
        self.vcard = contact_data.get("vcard")

    def __str__(self):
        fields = []
        fields.append(f"phone_number={self.phone_number}")
        fields.append(f"first_name={self.first_name}")
        if self.last_name is not None:
            fields.append(f"last_name={self.last_name}")
        if self.user_id is not None:
            fields.append(f"user_id={self.user_id}")
        if self.vcard is not None:
            fields.append(f"vcard={self.vcard}")
        
        return "Contact(\n    " + ",\n    ".join(fields) + "\n)"


class Message:
    def __init__(self, message_data: Dict[str, Any]):
        self.message_id: Optional[int] = message_data.get("message_id")
        self.from_user: Optional[User] = User(message_data.get("from", {})) if message_data.get("from") else None
        self.date: Optional[datetime] = message_data.get("date")
        self.chat: Chat = Chat(message_data.get("chat", {}))
        self.text: Optional[str] = message_data.get("text")
        self.caption: Optional[str] = message_data.get("caption")
        self.data: Dict[str, Any] = message_data
        self.bot: Optional[Any] = None

        self.photo: Optional[Tuple[PhotoSize, ...]] = tuple(PhotoSize(p) for p in message_data.get("photo", [])) if message_data.get("photo") else None
        self.video: Optional[Video] = Video(message_data.get("video", {})) if message_data.get("video") else None
        self.document: Optional[Document] = Document(message_data.get("document", {})) if message_data.get("document") else None
        self.audio: Optional[Audio] = Audio(message_data.get("audio", {})) if message_data.get("audio") else None
        self.voice: Optional[Voice] = Voice(message_data.get("voice", {})) if message_data.get("voice") else None
        self.sticker: Optional[Sticker] = Sticker(message_data.get("sticker", {})) if message_data.get("sticker") else None
        self.contact: Optional[Contact] = Contact(message_data.get("contact", {})) if message_data.get("contact") else None
        self.location: Optional[Location] = Location(message_data.get("location", {})) if message_data.get("location") else None
        self.reply_to_message: Optional[Message] = Message(message_data.get("reply_to_message", {})) if message_data.get("reply_to_message") else None

    async def reply(self, text: str, reply_markup=None, **kwargs) -> 'Message':
        """Reply to this message with text"""
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        result = await self.bot.send_message(
            chat_id=self.chat.id,
            text=text,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )
        return result

    async def reply_text(self, text: str, reply_markup=None, **kwargs) -> 'Message':
        """Alias for reply()"""
        return await self.reply(text, reply_markup, **kwargs)

    async def edit_text(self, text: str, reply_markup=None, **kwargs) -> bool:
        """Edit the text of this message"""
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.edit_message_text(
            chat_id=self.chat.id,
            message_id=self.message_id,
            text=text,
            reply_markup=reply_markup,
            **kwargs
        )

    async def edit_caption(self, caption: str, reply_markup=None, **kwargs) -> bool:
        """Edit the caption of this message"""
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.edit_message_caption(
            chat_id=self.chat.id,
            message_id=self.message_id,
            caption=caption,
            reply_markup=reply_markup,
            **kwargs
        )

    async def delete(self, **kwargs) -> bool:
        """Delete this message"""
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.delete_message(
            chat_id=self.chat.id,
            message_id=self.message_id,
            **kwargs
        )

    async def pin(self, disable_notification: bool = False, **kwargs) -> bool:
        """Pin this message in the chat"""
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.pin_chat_message(
            chat_id=self.chat.id,
            message_id=self.message_id,
            disable_notification=disable_notification,
            **kwargs
        )

    async def copy(self, chat_id: int, reply_markup=None, **kwargs) -> 'Message':
        """Copy this message to another chat"""
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.copy_message(
            chat_id=chat_id,
            from_chat_id=self.chat.id,
            message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def forward(self, chat_id: int, **kwargs) -> 'Message':
        """Forward this message to another chat"""
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.forward_message(
            chat_id=chat_id,
            from_chat_id=self.chat.id,
            message_id=self.message_id,
            **kwargs
        )

    async def reply_photo(self, photo: str, caption: str = None, reply_markup=None, **kwargs) -> 'Message':
        """Reply to this message with a photo"""
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.send_photo(
            chat_id=self.chat.id,
            photo=photo,
            caption=caption,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_video(self, video: str, caption: str = None, reply_markup=None, **kwargs) -> 'Message':
        """Reply to this message with a video"""
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.send_video(
            chat_id=self.chat.id,
            video=video,
            caption=caption,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_document(self, document: str, caption: str = None, reply_markup=None, **kwargs) -> 'Message':
        """Reply to this message with a document"""
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.send_document(
            chat_id=self.chat.id,
            document=document,
            caption=caption,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_audio(self, audio: str, caption: str = None, reply_markup=None, **kwargs) -> 'Message':
        """Reply to this message with an audio file"""
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.send_audio(
            chat_id=self.chat.id,
            audio=audio,
            caption=caption,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_voice(self, voice: str, caption: str = None, reply_markup=None, **kwargs) -> 'Message':
        """Reply to this message with a voice message"""
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.send_voice(
            chat_id=self.chat.id,
            voice=voice,
            caption=caption,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_sticker(self, sticker: str, reply_markup=None, **kwargs) -> 'Message':
        """Reply to this message with a sticker"""
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.send_sticker(
            chat_id=self.chat.id,
            sticker=sticker,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_animation(self, animation: str, caption: str = None, reply_markup=None, **kwargs) -> 'Message':
        """Reply to this message with an animation"""
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.send_animation(
            chat_id=self.chat.id,
            animation=animation,
            caption=caption,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_contact(
        self,
        phone_number: str,
        first_name: str,
        last_name: str = None,
        reply_markup=None,
        **kwargs
    ) -> 'Message':
        """Reply to this message with a contact"""
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.send_contact(
            chat_id=self.chat.id,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_location(
        self,
        latitude: float,
        longitude: float,
        reply_markup=None,
        **kwargs
    ) -> 'Message':
        """Reply to this message with a location"""
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.send_location(
            chat_id=self.chat.id,
            latitude=latitude,
            longitude=longitude,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_media_group(
        self,
        media: List[Union[InputMediaPhoto, InputMediaVideo]],
        reply_markup=None,
        **kwargs
    ) -> List['Message']:
        """Reply to this message with a media group"""
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.send_media_group(
            chat_id=self.chat.id,
            media=media,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    def __str__(self) -> str:
        return f"Message(chat={self.chat}, message_id={self.message_id}, text={self.text})"

class UpdateWrapper:
    def __init__(self, update: dict):
        self.update = update
        self.update_id = update.get("update_id")
        self.message = (
            Message(update.get("message", {}))
            if update.get("message")
            else None
        )
        callback_query_data = update.get("callback_query", {})
        self.callback_query = (
            CallbackQuery(callback_query_data)
            if callback_query_data
            else None
        )

    def __str__(self):
        fields = []
        fields.append(f"update_id={self.update_id}")
        if self.message is not None:
            fields.append(f"message={self.message}")
        if self.callback_query is not None:
            fields.append(f"callback_query={self.callback_query}")
        
        return "UpdateWrapper(\n    " + ",\n    ".join(fields) + "\n)"