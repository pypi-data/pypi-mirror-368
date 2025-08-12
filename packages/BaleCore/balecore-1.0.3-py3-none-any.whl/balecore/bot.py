import aiohttp
import asyncio
from typing import Callable, Optional, Dict, Any, List, Union, defaultdict

from .filter import Filters
from .update_wrapper import UpdateWrapper
from .InlineKeyboard import InlineKeyboardButton, InlineKeyboardMarkup
from .ReplyKeyboard import KeyboardButton, ReplyKeyboardMarkup
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
from dataclasses import dataclass


@dataclass
class BotInfo:
    id: int
    is_bot: bool
    first_name: str
    last_name: str
    username: str
    language_code: str
    can_join_groups: bool
    can_read_all_group_messages: bool
    supports_inline_queries: bool


class Bot:
    def __init__(
        self,
        token: str,
        url: Optional[str] = None,
        concurrency_limit: Optional[int] = None,
        proxy: Optional[str] = None,
    ) -> None:
        self.token = token
        self.base_url = url if url is not None else "https://tapi.bale.ai"
        self.handlers: List[Dict] = []
        self.callback_handlers: List[Dict] = []
        self.running = asyncio.Event()
        self.user_states: Dict[str, Dict[int, str]] = {}
        self.user_data: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.filters = Filters(self)
        self.initialize_handlers: List[Callable] = []
        self.concurrency_limit = concurrency_limit
        self.active_tasks = set()
        self.proxy = proxy

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
            return (
                f"ChatParameter(\n"
                f"    id={self.id},\n"
                f"    type={self.type},\n"
                f"    title={self.title},\n"
                f"    username={self.username},\n"
                f"    photo={self.photo},\n"
                f"    description={self.description},\n"
                f"    invite_link={self.invite_link},\n"
                f"    permissions={self.permissions}\n"
                f")"
            )

    async def get_chat(self, chat_id: int) -> tuple:
        """
        Get chat information and return as a structured tuple.
        
        Args:
            chat_id: Unique identifier for the target chat.
            
        Returns:
            tuple: Structured chat information in the following format:
                (
                    id,
                    type,
                    title,
                    username,
                    first_name,
                    last_name,
                    photo (tuple of PhotoSize objects or None),
                    description,
                    invite_link
                )
        """
        url = f"{self.base_url}/bot{self.token}/getChat"
        params = {"chat_id": chat_id}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=params, proxy=self.proxy) as response:
                    response_data = await response.json()
                    
                    if not response_data.get("ok"):
                        print(f"API Error in get_chat: {response_data.get('description')}")
                        return tuple()
                    
                    result = response_data["result"]
                    photo_data = result.get("photo", {})
                    
                    photo = (
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
                    
                    fields = [
                        f"id={result.get('id')}",
                        f"type={result.get('type')}",
                        f"title={result.get('title')}" if result.get('title') is not None else None,
                        f"username={result.get('username')}" if result.get('username') is not None else None,
                        f"first_name={result.get('first_name')}" if result.get('first_name') is not None else None,
                        f"last_name={result.get('last_name')}" if result.get('last_name') is not None else None,
                        f"photo={photo}" if photo is not None else None,
                        f"description={result.get('description')}" if result.get('description') is not None else None,
                        f"invite_link={result.get('invite_link')}" if result.get('invite_link') is not None else None,
                        f"permissions={result.get('permissions')}" if result.get('permissions') is not None else None
                    ]
                    
                    filtered_fields = [field for field in fields if field is not None]
                    field_string = ",\n    ".join(filtered_fields)
                    
                    output = f"Chat(\n    {field_string}\n)"
                    return output
                    
        except Exception as e:
            print(f"Error in get_chat: {str(e)}")
            return tuple()

    def set_user_state(self, user_id: int, state: str) -> None:
        """
        Sets the state for a specific user.
        
        Args:
            user_id: The ID of the user
            state: The state to set for the user
        """
        if self.token not in self.user_states:
            self.user_states[self.token] = {}
        self.user_states[self.token][user_id] = state

    def get_user_state(self, user_id: int) -> Optional[str]:
        """
        Gets the current state of a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            The current state of the user or None if not found
        """
        return self.user_states.get(self.token, {}).get(user_id)

    def clear_user_state(self, user_id: int) -> None:
        """
        Clears the state for a specific user.
        
        Args:
            user_id: The ID of the user to clear
        """
        if self.token in self.user_states and user_id in self.user_states[self.token]:
            del self.user_states[self.token][user_id]

    def set_user_data(
        self,
        user_id: str,
        key: str,
        value: Any,
    ) -> None:
        """
        Sets user data in the storage dictionary.
        
        Args:
            user_id: Unique identifier for the user
            key: Data key to store
            value: Value to store (can be any type)
        """
        self.user_data[user_id][key] = value

    def get_user_data(self, user_id: str, key: str) -> Optional[Any]:
        """
        Gets user data from the storage dictionary.
        
        Args:
            user_id: Unique identifier for the user
            key: Data key to retrieve
            
        Returns:
            The stored value or None if not found
        """
        return self.user_data.get(user_id, {}).get(key)

    def clear_user_data(self, user_id: str, key: str) -> None:
        """
        Clears specific user data.
        
        Args:
            user_id: Unique identifier for the user
            key: Data key to remove
        """
        if user_id in self.user_data and key in self.user_data[user_id]:
            del self.user_data[user_id][key]

    def Message(self, _filter: Filters = None):
        if _filter is None:
            _filter = self.filters.any_message()

        def decorator(func: Callable):
            self.handlers.append({"filter": _filter, "func": func})
            return func
        return decorator

    async def get_me(self):
        url = f"{self.base_url}/bot{self.token}/getMe"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    if data.get("ok"):
                        result = data["result"]
                        return BotInfo(
                            id=result.get("id"),
                            is_bot=result.get("is_bot", False),
                            first_name=result.get("first_name", ""),
                            last_name=result.get("last_name", ""),
                            username=result.get("username", ""),
                            language_code=result.get("language_code", "en"),
                            can_join_groups=result.get("can_join_groups", False),
                            can_read_all_group_messages=result.get("can_read_all_group_messages", False),
                            supports_inline_queries=result.get("supports_inline_queries", False)
                        )
                    return BotInfo(0, False, "", "", "", "en", False, False, False)
        except Exception as e:
            print(f"Error in getMe: {e}")
            return BotInfo(0, False, "", "", "", "en", False, False, False)

    async def get_updates(self, offset=None, timeout=30):
        url = f"{self.base_url}/bot{self.token}/getUpdates"
        params = {"timeout": timeout}
        if offset is not None:
            params["offset"] = offset

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, proxy=self.proxy) as response:
                    if response.status != 200:
                        print(f"HTTP Error: {response.status}")
                        return None

                    response_data = await response.json()

                    if response_data is None:
                        print("Empty response from server")
                        return None

                    if not isinstance(response_data, dict) or "ok" not in response_data:
                        print("Invalid response format")
                        return None

                    if not response_data.get("ok"):
                        print(f"API Error: {response_data.get('description', 'Unknown error')}")
                        return None

                    return response_data.get("result", [])
        except Exception as e:
            print(f"An error occurred in get_updates: {e}")
            return None

    async def process_updates(self):
        offset = None
        while self.running.is_set():
            try:
                updates = await self.get_updates(offset=offset)
                if updates is None:
                    print("No updates received or invalid response.")
                    continue
                for update in updates:
                    offset = update["update_id"] + 1
                    update_wrapper = UpdateWrapper(update)
                    if self.concurrency_limit is not None and len(self.active_tasks) >= self.concurrency_limit:
                        print("Concurrency limit reached, skipping update.")
                        continue
                    task = asyncio.create_task(self._process_update(update_wrapper))
                    self.active_tasks.add(task)
                    task.add_done_callback(self.active_tasks.discard)
            except Exception as e:
                print(f"An error occurred in process_updates: {e}")

    async def _process_update(self, update_wrapper):
        try:
            if update_wrapper.callback_query:
                callback_data = update_wrapper.callback_query.data

                for handler in self.callback_handlers:
                    if handler["filter"](update_wrapper.update):
                        result = await handler["func"](
                            self, 
                            update_wrapper.update,
                            update_wrapper.callback_query
                        )
                        if result and not result.get("ok"):
                            print(f"Handler failed: {result.get('description')}")
                        return

            if update_wrapper.message:
                update_wrapper.message.bot = self
                
                for handler in self.handlers:
                    if handler["filter"](update_wrapper.update):
                        result = await handler["func"](
                            self, 
                            update_wrapper.update, 
                            update_wrapper.message
                        )
                        if result and not result.get("ok"):
                            print(f"Handler failed: {result.get('description')}")
                        return
        except Exception as e:
            print(f"Error in _process_update: {str(e)}")

    def Initialize(self):
        def decorator(func: Callable):
            self.initialize_handlers.append(func)
            return func
        return decorator

    async def run_initialize_handlers(self):
        for handler in self.initialize_handlers:
            await handler(self)

    async def start(self):
        self.running.set()
        try:
            bot_info = await self.get_me()
            if bot_info:
                print(f"Bot is running! Username: @{bot_info.username}")
            else:
                print("Failed to start the bot. Please check your token and API URL.")
                return
        except Exception as e:
            print(f"An error occurred while starting the bot: {e}")
            return

        await self.run_initialize_handlers()
        await self.process_updates()

    async def stop(self):
        self.running.clear()
        print("Bot has been stopped.")

    async def delete_message_auto(self, message: dict):
        chat_id = message["chat"]["id"]
        message_id = message["message_id"]
        return await self.delete_message(chat_id=chat_id, message_id=message_id)

    async def edit_message_text_auto(self, message: dict, text: str, reply_markup=None):
        chat_id = message["chat"]["id"]
        message_id = message["message_id"]
        return await self.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=reply_markup)

    async def edit_message_caption_auto(
        self,
        chat_id: int,
        message_id: int,
        caption: str,
        reply_markup=None,
    ):
        url = f"{self.base_url}/bot{self.token}/editMessageCaption"
        params = {"chat_id": chat_id, "message_id": message_id, "caption": caption}
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def schedule_message(
        self,
        chat_id: int,
        text: str,
        delay_seconds: int,
        reply_to_message_id: int = None,
        reply_markup=None,
        edit_message_id: int = None,
    ):
        await asyncio.sleep(delay_seconds)
        return await self.send_message(
            chat_id=chat_id,
            text=text,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            edit_message_id=edit_message_id,
        )

    async def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[Dict[str, Any]] = None,
    ) -> Message:
        params = {"chat_id": chat_id, "text": text}
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict() if hasattr(reply_markup, 'to_dict') else reply_markup

        url = f"{self.base_url}/bot{self.token}/sendMessage"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=params,
                    proxy=self.proxy,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    response_text = await response.text()
                    try:
                        response_data = await response.json()
                    except:
                        print(f"Failed to decode JSON. Raw response: {response_text}")
                        response_data = {"ok": False, "description": response_text}

                    if not response_data.get("ok"):
                        print(f"API Error: {response_data.get('description')}")
                        return Message({"chat": {"id": chat_id}})

                    message = Message(response_data["result"])
                    message.bot = self
                    return message
        except Exception as e:
            print(f"Network error in send_message: {str(e)}")
            return Message({"chat": {"id": chat_id}})

    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: Optional[bool] = False,
        url: Optional[str] = None,
        cache_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Send an answer to a callback query sent from inline keyboards.
        
        Args:
            callback_query_id (str): Unique identifier for the query to be answered.
            text (str, optional): Text of the notification. If not specified, nothing will be shown.
            show_alert (bool, optional): If True, an alert will be shown instead of a notification.
            url (str, optional): URL that will be opened by the user's client.
            cache_time (int, optional): Maximum time in seconds that the result may be cached.
            
        Returns:
            dict: Response from the API containing the result of the operation.
            
        Raises:
            ValueError: If callback_query_id is empty or not a string.
        """
        if not isinstance(callback_query_id, str) or not callback_query_id.strip():
            raise ValueError("callback_query_id must be a non-empty string")
            
        url = f"{self.base_url}/bot{self.token}/answerCallbackQuery"
        params = {"callback_query_id": callback_query_id}
        
        if text is not None:
            params["text"] = text
        if show_alert:
            params["show_alert"] = True
        if url is not None:
            params["url"] = url
        if cache_time is not None:
            params["cache_time"] = cache_time

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=params,
                    proxy=self.proxy,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    response_text = await response.text()
                    try:
                        response_data = await response.json()
                    except:
                        print(f"Failed to decode JSON. Raw response: {response_text}")
                        response_data = {"ok": False, "description": response_text}

                    if not response_data.get("ok"):
                        print(f"API Error: {response_data.get('description')}")

                    return response_data
        except Exception as e:
            print(f"Network error in answer_callback_query: {str(e)}")
            return {"ok": False, "error": str(e)}

    async def pin_chat_message(
        self,
        chat_id: int,
        message_id: int,
        disable_notification: bool = False
    ):
        url = f"{self.base_url}/bot{self.token}/pinChatMessage"
        params = {
            "chat_id": chat_id,
            "message_id": message_id,
            "disable_notification": disable_notification
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()
                return response_data.get("ok", False)

    async def unpin_chat_message(
        self,
        chat_id: int,
        message_id: int = None
    ):
        url = f"{self.base_url}/bot{self.token}/unpinChatMessage"
        params = {"chat_id": chat_id}
        if message_id is not None:
            params["message_id"] = message_id
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()
                return response_data.get("ok", False)

    async def unpin_all_chat_messages(
        self,
        chat_id: int
    ):
        url = f"{self.base_url}/bot{self.token}/unpinAllChatMessages"
        params = {"chat_id": chat_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()
                return response_data.get("ok", False)

    async def pin_message_auto(
        self,
        message: dict,
        disable_notification: bool = False
    ):
        chat_id = message["chat"]["id"]
        message_id = message["message_id"]
        return await self.pin_chat_message(
            chat_id=chat_id,
            message_id=message_id,
            disable_notification=disable_notification
        )

    async def unpin_message_auto(
        self,
        message: dict
    ):
        chat_id = message["chat"]["id"]
        message_id = message["message_id"]
        return await self.unpin_chat_message(
            chat_id=chat_id,
            message_id=message_id
        )

    async def send_animation(
        self,
        chat_id: int,
        animation: str,
        caption: str = None,
        reply_to_message_id: int = None,
        reply_markup=None,
    ):
        url = f"{self.base_url}/bot{self.token}/sendAnimation"
        params = {"chat_id": chat_id, "animation": animation}
        if caption:
            params["caption"] = caption
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def send_audio(
        self,
        chat_id: int,
        audio: str,
        caption: str = None,
        reply_to_message_id: int = None,
        reply_markup=None,
    ):
        url = f"{self.base_url}/bot{self.token}/sendAudio"
        params = {"chat_id": chat_id, "audio": audio}
        if caption:
            params["caption"] = caption
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def send_contact(
        self,
        chat_id: int,
        phone_number: str,
        first_name: str,
        last_name: str = None,
        reply_to_message_id: int = None,
        reply_markup=None,
    ):
        url = f"{self.base_url}/bot{self.token}/sendContact"
        params = {"chat_id": chat_id, "phone_number": phone_number, "first_name": first_name}
        if last_name:
            params["last_name"] = last_name
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def send_document(
        self,
        chat_id: int,
        document: str,
        caption: str = None,
        reply_to_message_id: int = None,
        reply_markup=None,
    ):
        url = f"{self.base_url}/bot{self.token}/sendDocument"
        params = {"chat_id": chat_id, "document": document}
        if caption:
            params["caption"] = caption
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def send_location(
        self,
        chat_id: int,
        latitude: float,
        longitude: float,
        reply_to_message_id: int = None,
        reply_markup=None,
    ):
        url = f"{self.base_url}/bot{self.token}/sendLocation"
        params = {"chat_id": chat_id, "latitude": latitude, "longitude": longitude}
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def send_media_group(
        self,
        chat_id: int,
        media: List[Union[InputMediaPhoto, InputMediaVideo, InputMediaAnimation, InputMediaAudio, InputMediaDocument]],
        reply_to_message_id: int = None,
        reply_markup=None,
    ):
        url = f"{self.base_url}/bot{self.token}/sendMediaGroup"
        params = {
            "chat_id": chat_id,
            "media": [m.to_dict() for m in media]
        }
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                return await response.json()

    async def send_input_file(
        self,
        chat_id: int,
        input_file: InputFile,
        caption: str = None,
        reply_to_message_id: int = None,
        reply_markup=None,
    ):
        url = f"{self.base_url}/bot{self.token}/sendDocument"
        params = {
            "chat_id": chat_id,
            "document": input_file.to_dict()
        }
        if caption:
            params["caption"] = caption
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                return await response.json()

    async def send_photo(
        self,
        chat_id: int,
        photo: str,
        caption: str = None,
        reply_to_message_id: int = None,
        reply_markup=None,
        edit_message_id: int = None,
    ):
        if edit_message_id:
            return await self.edit_message_caption(chat_id=chat_id, message_id=edit_message_id, caption=caption, reply_markup=reply_markup)
        else:
            url = f"{self.base_url}/bot{self.token}/sendPhoto"
            params = {"chat_id": chat_id, "photo": photo}
            if caption:
                params["caption"] = caption
            if reply_to_message_id:
                params["reply_to_message_id"] = reply_to_message_id
            if reply_markup:
                params["reply_markup"] = reply_markup.to_dict()
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=params, proxy=self.proxy) as response:
                    response_data = await response.json()

    async def send_video(
        self,
        chat_id: int,
        video: str,
        caption: str = None,
        reply_to_message_id: int = None,
        reply_markup=None,
    ):
        url = f"{self.base_url}/bot{self.token}/sendVideo"
        params = {"chat_id": chat_id, "video": video}
        if caption:
            params["caption"] = caption
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def send_voice(
        self,
        chat_id: int,
        voice: str,
        caption: str = None,
        reply_to_message_id: int = None,
        reply_markup=None,
    ):
        url = f"{self.base_url}/bot{self.token}/sendVoice"
        params = {"chat_id": chat_id, "voice": voice}
        if caption:
            params["caption"] = caption
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def send_sticker(
        self,
        chat_id: int,
        sticker: str,
        reply_to_message_id: int = None,
        reply_markup=None,
    ):
        url = f"{self.base_url}/bot{self.token}/sendSticker"
        params = {"chat_id": chat_id, "sticker": sticker}
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def send_chat_action(self, chat_id: int, action: str):
        url = f"{self.base_url}/bot{self.token}/sendChatAction"
        params = {"chat_id": chat_id, "action": action}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def edit_message_text(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        reply_markup=None,
    ):
        url = f"{self.base_url}/bot{self.token}/editMessageText"
        params = {"chat_id": chat_id, "message_id": message_id, "text": text}
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def delete_message(self, chat_id: int, message_id: int):
        url = f"{self.base_url}/bot{self.token}/deleteMessage"
        params = {"chat_id": chat_id, "message_id": message_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def forward_message(
        self,
        chat_id: int,
        from_chat_id: int,
        message_id: int,
    ):
        url = f"{self.base_url}/bot{self.token}/forwardMessage"
        params = {"chat_id": chat_id, "from_chat_id": from_chat_id, "message_id": message_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def get_chat_administrators(self, chat_id: str) -> tuple:
        url = f"{self.base_url}/bot{self.token}/getChatAdministrators"
        params = {"chat_id": chat_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()
                if response_data.get("ok"):
                    admins = []
                    for admin in response_data["result"]:
                        user = admin.get("user", {})
                        admins.append((
                            user.get("id"),
                            user.get("is_bot"),
                            user.get("first_name"),
                            user.get("last_name"),
                            user.get("username"),
                            admin.get("status"),
                            admin.get("custom_title"),
                            admin.get("until_date"),
                            admin.get("can_be_edited"),
                            admin.get("can_post_messages"),
                            admin.get("can_edit_messages"),
                            admin.get("can_delete_messages"),
                            admin.get("can_restrict_members"),
                            admin.get("can_promote_members"),
                            admin.get("can_change_info"),
                            admin.get("can_invite_users"),
                            admin.get("can_pin_messages"),
                            admin.get("is_member"),
                            admin.get("can_send_messages"),
                            admin.get("can_send_media_messages"),
                            admin.get("can_send_polls"),
                            admin.get("can_send_other_messages"),
                            admin.get("can_add_web_page_previews")
                        ))
                    return tuple(admins)
                return tuple()

    async def get_chat_member(self, chat_id: int, user_id: int) -> tuple:
        url = f"{self.base_url}/bot{self.token}/getChatMember"
        params = {"chat_id": chat_id, "user_id": user_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()
                if response_data.get("ok"):
                    result = response_data["result"]
                    user = result.get("user", {})
                    return (
                        user.get("id"),
                        user.get("is_bot"),
                        user.get("first_name"),
                        user.get("last_name"),
                        user.get("username"),
                        result.get("status"),
                        result.get("custom_title"),
                        result.get("until_date"),
                        result.get("can_be_edited"),
                        result.get("can_post_messages"),
                        result.get("can_edit_messages"),
                        result.get("can_delete_messages"),
                        result.get("can_restrict_members"),
                        result.get("can_promote_members"),
                        result.get("can_change_info"),
                        result.get("can_invite_users"),
                        result.get("can_pin_messages"),
                        result.get("is_member"),
                        result.get("can_send_messages"),
                        result.get("can_send_media_messages"),
                        result.get("can_send_polls"),
                        result.get("can_send_other_messages"),
                        result.get("can_add_web_page_previews")
                    )
                return tuple()

    async def get_chat_members_count(self, chat_id: int) -> tuple:
        url = f"{self.base_url}/bot{self.token}/getChatMembersCount"
        params = {"chat_id": chat_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()
                if response_data.get("ok"):
                    return (response_data["result"],)
                return tuple()

    async def get_file(self, file_id: str) -> tuple:
        url = f"{self.base_url}/bot{self.token}/getFile"
        params = {"file_id": file_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()
                if response_data.get("ok"):
                    result = response_data["result"]
                    return (
                        result.get("file_id"),
                        result.get("file_unique_id"),
                        result.get("file_size"),
                        result.get("file_path")
                    )
                return tuple()

    async def get_sticker_set(self, name: str) -> tuple:
        url = f"{self.base_url}/bot{self.token}/getStickerSet"
        params = {"name": name}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()
                if response_data.get("ok"):
                    result = response_data["result"]
                    stickers = []
                    for sticker in result.get("stickers", []):
                        stickers.append((
                            sticker.get("file_id"),
                            sticker.get("file_unique_id"),
                            sticker.get("width"),
                            sticker.get("height"),
                            sticker.get("is_animated"),
                            sticker.get("is_video"),
                            sticker.get("emoji"),
                            sticker.get("set_name"),
                            sticker.get("mask_position"),
                            sticker.get("file_size"),
                            sticker.get("thumbnail")
                        ))
                    return (
                        result.get("name"),
                        result.get("title"),
                        result.get("is_animated"),
                        result.get("is_video"),
                        result.get("contains_masks"),
                        tuple(stickers)
                    )
                return tuple()

    async def invite_user(self, chat_id: int, user_id: int):
        url = f"{self.base_url}/bot{self.token}/inviteUser"
        params = {"chat_id": chat_id, "user_id": user_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def leave_chat(self, chat_id: int):
        url = f"{self.base_url}/bot{self.token}/leaveChat"
        params = {"chat_id": chat_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def promote_chat_member(
        self,
        chat_id: int,
        user_id: int,
        can_change_info: bool = None,
        can_post_messages: bool = None,
        can_edit_messages: bool = None,
        can_delete_messages: bool = None,
        can_invite_users: bool = None,
        can_restrict_members: bool = None,
        can_pin_messages: bool = None,
        can_promote_members: bool = None,
    ):
        url = f"{self.base_url}/bot{self.token}/promoteChatMember"
        params = {"chat_id": chat_id, "user_id": user_id}
        if can_change_info is not None:
            params["can_change_info"] = can_change_info
        if can_post_messages is not None:
            params["can_post_messages"] = can_post_messages
        if can_edit_messages is not None:
            params["can_edit_messages"] = can_edit_messages
        if can_delete_messages is not None:
            params["can_delete_messages"] = can_delete_messages
        if can_invite_users is not None:
            params["can_invite_users"] = can_invite_users
        if can_restrict_members is not None:
            params["can_restrict_members"] = can_restrict_members
        if can_pin_messages is not None:
            params["can_pin_messages"] = can_pin_messages
        if can_promote_members is not None:
            params["can_promote_members"] = can_promote_members
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def set_chat_photo(self, chat_id: int, photo: str):
        url = f"{self.base_url}/bot{self.token}/setChatPhoto"
        params = {"chat_id": chat_id, "photo": photo}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def ban_chat_member(self, chat_id: int, user_id: int):
        url = f"{self.base_url}/bot{self.token}/banChatMember"
        params = {"chat_id": chat_id, "user_id": user_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def unban_chat_member(self, chat_id: int, user_id: int):
        url = f"{self.base_url}/bot{self.token}/unbanChatMember"
        params = {"chat_id": chat_id, "user_id": user_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def copy_message(
        self,
        chat_id: int,
        from_chat_id: int,
        message_id: int,
        caption: str = None,
        reply_to_message_id: int = None,
        reply_markup=None,
    ):
        url = f"{self.base_url}/bot{self.token}/copyMessage"
        params = {"chat_id": chat_id, "from_chat_id": from_chat_id, "message_id": message_id}
        if caption:
            params["caption"] = caption
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def add_sticker_to_set(
        self,
        user_id: int,
        name: str,
        png_sticker: str,
        emojis: str,
        mask_position: dict = None,
    ):
        url = f"{self.base_url}/bot{self.token}/addStickerToSet"
        params = {"user_id": user_id, "name": name, "png_sticker": png_sticker, "emojis": emojis}
        if mask_position:
            params["mask_position"] = mask_position
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def create_new_sticker_set(
        self,
        user_id: int,
        name: str,
        title: str,
        png_sticker: str,
        emojis: str,
        contains_masks: bool = None,
        mask_position: dict = None,
    ):
        url = f"{self.base_url}/bot{self.token}/createNewStickerSet"
        params = {"user_id": user_id, "name": name, "title": title, "png_sticker": png_sticker, "emojis": emojis}
        if contains_masks is not None:
            params["contains_masks"] = contains_masks
        if mask_position:
            params["mask_position"] = mask_position
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def upload_sticker_file(self, user_id: int, png_sticker: str):
        url = f"{self.base_url}/bot{self.token}/uploadStickerFile"
        params = {"user_id": user_id, "png_sticker": png_sticker}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def create_chat_invite_link(
        self,
        chat_id: int,
        expire_date: int = None,
        member_limit: int = None,
    ):
        url = f"{self.base_url}/bot{self.token}/createChatInviteLink"
        params = {"chat_id": chat_id}
        if expire_date:
            params["expire_date"] = expire_date
        if member_limit:
            params["member_limit"] = member_limit
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def delete_chat_photo(self, chat_id: int):
        url = f"{self.base_url}/bot{self.token}/deleteChatPhoto"
        params = {"chat_id": chat_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def delete_sticker_from_set(self, sticker: str):
        url = f"{self.base_url}/bot{self.token}/deleteStickerFromSet"
        params = {"sticker": sticker}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def edit_message_caption(
        self,
        chat_id: int,
        message_id: int,
        caption: str,
        reply_markup=None,
    ):
        url = f"{self.base_url}/bot{self.token}/editMessageCaption"
        params = {"chat_id": chat_id, "message_id": message_id, "caption": caption}
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def export_chat_invite_link(self, chat_id: int):
        url = f"{self.base_url}/bot{self.token}/exportChatInviteLink"
        params = {"chat_id": chat_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def pin_chat_message(
        self,
        chat_id: int,
        message_id: int,
        disable_notification: bool = None,
    ):
        url = f"{self.base_url}/bot{self.token}/pinChatMessage"
        params = {"chat_id": chat_id, "message_id": message_id}
        if disable_notification is not None:
            params["disable_notification"] = disable_notification
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def revoke_chat_invite_link(self, chat_id: int, invite_link: str):
        url = f"{self.base_url}/bot{self.token}/revokeChatInviteLink"
        params = {"chat_id": chat_id, "invite_link": invite_link}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def set_chat_description(self, chat_id: int, description: str):
        url = f"{self.base_url}/bot{self.token}/setChatDescription"
        params = {"chat_id": chat_id, "description": description}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def set_chat_title(self, chat_id: int, title: str):
        url = f"{self.base_url}/bot{self.token}/setChatTitle"
        params = {"chat_id": chat_id, "title": title}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def unpin_all_chat_messages(self, chat_id: int):
        url = f"{self.base_url}/bot{self.token}/unpinAllChatMessages"
        params = {"chat_id": chat_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def unpin_chat_message(self, chat_id: int, message_id: int = None):
        url = f"{self.base_url}/bot{self.token}/unpinChatMessage"
        params = {"chat_id": chat_id}
        if message_id:
            params["message_id"] = message_id
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def reply_message_auto(self, update: dict, text: str, reply_markup=None):
        update_wrapper = UpdateWrapper(update)
        if update_wrapper.message:
            chat_id = update_wrapper.message.chat.id
            message_id = update_wrapper.message.message_id
            return await self.send_message(
                chat_id=chat_id,
                text=text,
                reply_to_message_id=message_id,
                reply_markup=reply_markup,
            )
        return {"ok": False, "error": "Invalid update format"}

    async def reply_video_auto(self, update: dict, video: str, caption: str = None, reply_markup=None):
        update_wrapper = UpdateWrapper(update)
        if update_wrapper.message:
            return await self.send_video(
                chat_id=update_wrapper.message.chat.id,
                video=video,
                caption=caption,
                reply_to_message_id=update_wrapper.message.message_id,
                reply_markup=reply_markup,
            )
        return {"ok": False, "error": "Invalid update format"}

    async def reply_voice_auto(self, update: dict, voice: str, caption: str = None, reply_markup=None):
        update_wrapper = UpdateWrapper(update)
        if update_wrapper.message:
            chat_id = update_wrapper.message.chat.id
            message_id = update_wrapper.message.message_id
            return await self.send_voice(
                chat_id=chat_id,
                voice=voice,
                caption=caption,
                reply_to_message_id=message_id,
                reply_markup=reply_markup,
            )
        return {"ok": False, "error": "Invalid update format"}

    async def reply_sticker_auto(self, update: dict, sticker: str, reply_markup=None):
        update_wrapper = UpdateWrapper(update)
        if update_wrapper.message:
            chat_id = update_wrapper.message.chat.id
            message_id = update_wrapper.message.message_id
            return await self.send_sticker(
                chat_id=chat_id,
                sticker=sticker,
                reply_to_message_id=message_id,
                reply_markup=reply_markup,
            )
        return {"ok": False, "error": "Invalid update format"}

    async def reply_document_auto(self, update: dict, document: str, caption: str = None, reply_markup=None):
        update_wrapper = UpdateWrapper(update)
        if update_wrapper.message:
            chat_id = update_wrapper.message.chat.id
            message_id = update_wrapper.message.message_id
            return await self.send_document(
                chat_id=chat_id,
                document=document,
                caption=caption,
                reply_to_message_id=message_id,
                reply_markup=reply_markup,
            )
        return {"ok": False, "error": "Invalid update format"}

    async def reply_animation_auto(self, update: dict, animation: str, caption: str = None, reply_markup=None):
        update_wrapper = UpdateWrapper(update)
        if update_wrapper.message:
            chat_id = update_wrapper.message.chat.id
            message_id = update_wrapper.message.message_id
            return await self.send_animation(
                chat_id=chat_id,
                animation=animation,
                caption=caption,
                reply_to_message_id=message_id,
                reply_markup=reply_markup,
            )
        return {"ok": False, "error": "Invalid update format"}

    async def reply_audio_auto(self, update: dict, audio: str, caption: str = None, reply_markup=None):
        update_wrapper = UpdateWrapper(update)
        if update_wrapper.message:
            chat_id = update_wrapper.message.chat.id
            message_id = update_wrapper.message.message_id
            return await self.send_audio(
                chat_id=chat_id,
                audio=audio,
                caption=caption,
                reply_to_message_id=message_id,
                reply_markup=reply_markup,
            )
        return {"ok": False, "error": "Invalid update format"}

    async def reply_photo_auto(self, update: dict, photo: str, caption: str = None, reply_markup=None):
        update_wrapper = UpdateWrapper(update)
        if update_wrapper.message:
            chat_id = update_wrapper.message.chat.id
            message_id = update_wrapper.message.message_id
            return await self.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption,
                reply_to_message_id=message_id,
                reply_markup=reply_markup,
            )
        return {"ok": False, "error": "Invalid update format"}

    async def reply_message(
        self,
        chat_id: int,
        text: str,
        message_id: int,
        reply_markup=None,
        **kwargs
    ) -> Dict[str, Any]:
        """Reply to a message with text."""
        return await self.send_message(
            chat_id=chat_id,
            text=text,
            reply_to_message_id=message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_video(
        self,
        chat_id: int,
        video: str,
        message_id: int,
        caption: str = None,
        reply_markup=None,
        **kwargs
    ) -> Dict[str, Any]:
        """Reply to a message with video."""
        return await self.send_video(
            chat_id=chat_id,
            video=video,
            caption=caption,
            reply_to_message_id=message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_voice(
        self,
        chat_id: int,
        voice: str,
        message_id: int,
        caption: str = None,
        reply_markup=None,
        **kwargs
    ) -> Dict[str, Any]:
        """Reply to a message with voice."""
        return await self.send_voice(
            chat_id=chat_id,
            voice=voice,
            caption=caption,
            reply_to_message_id=message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_sticker(
        self,
        chat_id: int,
        sticker: str,
        message_id: int,
        reply_markup=None,
        **kwargs
    ) -> Dict[str, Any]:
        """Reply to a message with sticker."""
        return await self.send_sticker(
            chat_id=chat_id,
            sticker=sticker,
            reply_to_message_id=message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_document(
        self,
        chat_id: int,
        document: str,
        message_id: int,
        caption: str = None,
        reply_markup=None,
        **kwargs
    ) -> Dict[str, Any]:
        """Reply to a message with document."""
        return await self.send_document(
            chat_id=chat_id,
            document=document,
            caption=caption,
            reply_to_message_id=message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_animation(
        self,
        chat_id: int,
        animation: str,
        message_id: int,
        caption: str = None,
        reply_markup=None,
        **kwargs
    ) -> Dict[str, Any]:
        """Reply to a message with animation."""
        return await self.send_animation(
            chat_id=chat_id,
            animation=animation,
            caption=caption,
            reply_to_message_id=message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_audio(
        self,
        chat_id: int,
        audio: str,
        message_id: int,
        caption: str = None,
        reply_markup=None,
        **kwargs
    ) -> Dict[str, Any]:
        """Reply to a message with audio."""
        return await self.send_audio(
            chat_id=chat_id,
            audio=audio,
            caption=caption,
            reply_to_message_id=message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_photo(
        self,
        chat_id: int,
        photo: str,
        message_id: int,
        caption: str = None,
        reply_markup=None,
        **kwargs
    ) -> Dict[str, Any]:
        """Reply to a message with photo."""
        return await self.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            reply_to_message_id=message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    def CallbackQuery(self, _filter: Filters = None) -> Callable:
        """Decorator to register callback query handler."""
        if _filter is None:
            _filter = self.filters.callback_query_all()

        def decorator(func: Callable) -> Callable:
            self.callback_handlers.append({
                "filter": _filter,
                "func": func
            })
            return func
        
        return decorator

    @staticmethod
    def LabeledPrice(label: str, amount: int) -> Callable:
        """Decorator to add labeled price to payment."""
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                prices = [{"label": label, "amount": amount}]
                return func(*args, prices=prices, **kwargs)
            return wrapper
        return decorator


    def PreCheckoutQuery(self) -> Callable:
        """Decorator to register pre-checkout query handler"""
        def decorator(func: Callable) -> Callable:
            self.callback_handlers.append({
                "filter": self.filters.pre_checkout_query,
                "func": func
            })
            return func
        return decorator


    class SuccessfulPayment:
        """Class representing successful payment data."""
        def __init__(self, successful_payment_data: dict):
            self.currency = successful_payment_data.get("currency")
            self.total_amount = successful_payment_data.get("total_amount")
            self.invoice_payload = successful_payment_data.get("invoice_payload")
            self.telegram_payment_charge_id = successful_payment_data.get(
                "telegram_payment_charge_id"
            )

    async def send_invoice(
        self,
        chat_id: int,
        title: str,
        description: str,
        payload: str,
        provider_token: str,
        prices: list,
        photo_url: str = None,
        reply_to_message_id: int = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send invoice to user."""
        url = f"{self.base_url}/bot{self.token}/sendInvoice"
        params = {
            "chat_id": chat_id,
            "title": title,
            "description": description,
            "payload": payload,
            "provider_token": provider_token,
            "prices": prices,
            **kwargs
        }

        if photo_url:
            params["photo_url"] = photo_url
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                return await response.json()

    async def answer_pre_checkout_query(
        self,
        pre_checkout_query_id: str,
        ok: bool,
        error_message: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Answer pre-checkout query."""
        url = f"{self.base_url}/bot{self.token}/answerPreCheckoutQuery"
        params = {
            "pre_checkout_query_id": pre_checkout_query_id,
            "ok": ok,
            **kwargs
        }
        if error_message:
            params["error_message"] = error_message

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                return await response.json()

class Chat:
    def __init__(self, chat_data: dict):
        self.id = chat_data.get("id")
        self.type = chat_data.get("type")


class Message:
    def __init__(self, message_data: dict):
        self.chat = Chat(message_data.get("chat", {}))
        self.message_id = message_data.get("message_id")
        self.text = message_data.get("text")
        self.data = message_data
        self.bot = None

    async def reply(self, text: str, reply_markup=None, **kwargs):
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.send_message(
            chat_id=self.chat.id,
            text=text,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_text(self, text: str, reply_markup=None, **kwargs):
        return await self.reply(text, reply_markup, **kwargs)

    async def copy(self, chat_id: int, reply_markup=None, **kwargs):
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.copy_message(
            chat_id=chat_id,
            from_chat_id=self.chat.id,
            message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def forward(self, chat_id: int, **kwargs):
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.forward_message(
            chat_id=chat_id,
            from_chat_id=self.chat.id,
            message_id=self.message_id,
            **kwargs
        )

    async def reply_video(self, video: str, caption: str = None, reply_markup=None, **kwargs):
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

    async def reply_photo(self, photo: str, caption: str = None, reply_markup=None, **kwargs):
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

    async def reply_document(self, document: str, caption: str = None, reply_markup=None, **kwargs):
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

    async def reply_voice(self, voice: str, caption: str = None, reply_markup=None, **kwargs):
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

    async def reply_audio(self, audio: str, caption: str = None, reply_markup=None, **kwargs):
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

    async def reply_animation(self, animation: str, caption: str = None, reply_markup=None, **kwargs):
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

    async def reply_sticker(self, sticker: str, reply_markup=None, **kwargs):
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.send_sticker(
            chat_id=self.chat.id,
            sticker=sticker,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_contact(self, phone_number: str, first_name: str, last_name: str = None, reply_markup=None, **kwargs):
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

    async def reply_location(self, latitude: float, longitude: float, reply_markup=None, **kwargs):
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

    async def delete(self, **kwargs):
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.delete_message(
            chat_id=self.chat.id,
            message_id=self.message_id,
            **kwargs
        )

    async def edit_text(self, text: str, reply_markup=None, **kwargs):
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.edit_message_text(
            chat_id=self.chat.id,
            message_id=self.message_id,
            text=text,
            reply_markup=reply_markup,
            **kwargs
        )

    async def edit_caption(self, caption: str, reply_markup=None, **wargs):
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.edit_message_caption(
            chat_id=self.chat.id,
            message_id=self.message_id,
            caption=caption,
            reply_markup=reply_markup,
            **kwargs
        )

    async def pin(self, disable_notification: bool = False, **kwargs):
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.pin_chat_message(
            chat_id=self.chat.id,
            message_id=self.message_id,
            disable_notification=disable_notification,
            **kwargs
        )