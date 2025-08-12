from typing import List, Optional, Callable, Dict, Any
from functools import wraps


class Filter:
    """
    A class representing a filter condition for message handling.
    
    Args:
        filter_func: A callable that takes an update and returns a boolean
    """
    def __init__(self, filter_func: Callable[[Dict], bool]):
        self.filter_func = filter_func

    def __call__(self, update: Dict) -> bool:
        """Execute the filter on an update"""
        try:
            return bool(self.filter_func(update))
        except Exception:
            return False

    def __and__(self, other: 'Filter') -> 'Filter':
        """Combine two filters with AND logic"""
        return Filter(lambda update: self(update) and other(update))

    def __or__(self, other: 'Filter') -> 'Filter':
        """Combine two filters with OR logic"""
        return Filter(lambda update: self(update) or other(update))

    def __invert__(self) -> 'Filter':
        """Invert the filter logic"""
        return Filter(lambda update: not self(update))


class Filters:
    """
    A collection of pre-defined filters for message handling.
    
    Args:
        bot: The bot instance associated with these filters
    """
    def __init__(self, bot: Any):
        self.bot = bot

    def state(self, state: str) -> Filter:
        """Filter updates based on user state"""
        return Filter(
            lambda update: (
                ("message" in update 
                 and "from" in update["message"] 
                 and self.bot.get_user_state(update["message"]["from"]["id"]) == state)
                or
                ("callback_query" in update 
                 and "from" in update["callback_query"]
                 and self.bot.get_user_state(update["callback_query"]["from"]["id"]) == state)
            )
        )

    @property
    def any_message(self) -> Filter:
        """Filter any message update"""
        return Filter(lambda update: "message" in update)

    @property
    def private(self) -> Filter:
        """Filter private chat messages"""
        return Filter(
            lambda update: (
                "message" in update
                and "chat" in update["message"]
                and update["message"]["chat"]["type"] == "private"
            )
        )

    @property
    def group(self) -> Filter:
        """Filter group chat messages"""
        return Filter(
            lambda update: (
                "message" in update
                and "chat" in update["message"]
                and update["message"]["chat"]["type"] == "group"
            )
        )

    @property
    def channel(self) -> Filter:
        """Filter channel messages"""
        return Filter(
            lambda update: (
                "message" in update
                and "chat" in update["message"]
                and update["message"]["chat"]["type"] == "channel"
            )
        )

    @property
    def text(self) -> Filter:
        """Filter text messages"""
        return Filter(
            lambda update: (
                "message" in update 
                and "text" in update["message"]
                and isinstance(update["message"]["text"], str)
            )
        )

    @property
    def video(self) -> Filter:
        """Filter video messages"""
        return Filter(
            lambda update: (
                "message" in update 
                and "video" in update["message"]
            )
        )

    @property
    def location(self) -> Filter:
        """Filter location messages"""
        return Filter(
            lambda update: (
                "message" in update 
                and "location" in update["message"]
            )
        )

    @property
    def photo(self) -> Filter:
        """Filter photo messages"""
        return Filter(
            lambda update: (
                "message" in update 
                and "photo" in update["message"]
            )
        )

    @property
    def reply(self) -> Filter:
        """Filter reply messages"""
        return Filter(
            lambda update: (
                "message" in update
                and "reply_to_message" in update["message"]
            )
        )

    @property
    def supergroup_chat_created(self) -> Filter:
        """Filter supergroup creation messages"""
        return Filter(
            lambda update: (
                "message" in update
                and "supergroup_chat_created" in update["message"]
            )
        )

    @property
    def pinned_message(self) -> Filter:
        """Filter pinned message notifications"""
        return Filter(
            lambda update: (
                "message" in update
                and "pinned_message" in update["message"]
            )
        )

    @property
    def new_chat_title(self) -> Filter:
        """Filter new chat title changes"""
        return Filter(
            lambda update: (
                "message" in update
                and "new_chat_title" in update["message"]
            )
        )

    @property
    def new_chat_photo(self) -> Filter:
        """Filter new chat photo changes"""
        return Filter(
            lambda update: (
                "message" in update
                and "new_chat_photo" in update["message"]
            )
        )

    @property
    def new_chat_members(self) -> Filter:
        """Filter new chat member notifications"""
        return Filter(
            lambda update: (
                "message" in update
                and "new_chat_members" in update["message"]
            )
        )

    @property
    def media(self) -> Filter:
        """Filter media messages (photo, video, document, audio, voice)"""
        return Filter(
            lambda update: (
                "message" in update
                and (
                    "photo" in update["message"]
                    or "video" in update["message"]
                    or "document" in update["message"]
                    or "audio" in update["message"]
                    or "voice" in update["message"]
                )
            )
        )

    @property
    def left_chat_member(self) -> Filter:
        """Filter left chat member notifications"""
        return Filter(
            lambda update: (
                "message" in update
                and "left_chat_member" in update["message"]
            )
        )

    @property
    def group_chat_created(self) -> Filter:
        """Filter group creation messages"""
        return Filter(
            lambda update: (
                "message" in update
                and "group_chat_created" in update["message"]
            )
        )

    @property
    def forward(self) -> Filter:
        """Filter forwarded messages"""
        return Filter(
            lambda update: (
                "message" in update
                and "forward_from" in update["message"]
            )
        )

    @property
    def document(self) -> Filter:
        """Filter document messages"""
        return Filter(
            lambda update: (
                "message" in update
                and "document" in update["message"]
            )
        )

    @property
    def contact(self) -> Filter:
        """Filter contact messages"""
        return Filter(
            lambda update: (
                "message" in update
                and "contact" in update["message"]
            )
        )

    @property
    def channel_chat_created(self) -> Filter:
        """Filter channel creation messages"""
        return Filter(
            lambda update: (
                "message" in update
                and "channel_chat_created" in update["message"]
            )
        )

    @property
    def caption(self) -> Filter:
        """Filter messages with captions"""
        return Filter(
            lambda update: (
                "message" in update
                and "caption" in update["message"]
            )
        )

    @property
    def all(self) -> Filter:
        """Filter all updates (no filtering)"""
        return Filter(lambda update: True)

    @property
    def audio(self) -> Filter:
        """Filter audio messages"""
        return Filter(
            lambda update: (
                "message" in update 
                and "audio" in update["message"]
            )
        )

    @property
    def sticker(self) -> Filter:
        """Filter sticker messages"""
        return Filter(
            lambda update: (
                "message" in update 
                and "sticker" in update["message"]
            )
        )

    @property
    def voice(self) -> Filter:
        """Filter voice messages"""
        return Filter(
            lambda update: (
                "message" in update 
                and "voice" in update["message"]
            )
        )

    def command(self, command: str) -> Filter:
        """Filter messages starting with a specific command"""
        return Filter(
            lambda update: (
                "message" in update
                and "text" in update["message"]
                and update["message"]["text"].startswith(f"/{command}")
            )
        )

    def pattern(self, pattern: str) -> Filter:
        """Filter messages starting with a specific pattern"""
        return Filter(
            lambda update: (
                "message" in update
                and "text" in update["message"]
                and update["message"]["text"].startswith(pattern)
            )
        )

    def multi_command(self, commands: List[str]) -> Filter:
        """Filter messages starting with any of multiple commands"""
        return Filter(
            lambda update: (
                "message" in update
                and "text" in update["message"]
                and any(
                    update["message"]["text"].startswith(f"/{cmd}")
                    or update["message"]["text"].startswith(cmd)
                    for cmd in commands
                )
            )
        )

    def callback_query(self, data: Optional[str] = None) -> Filter:
        """Filter callback queries, optionally with specific data"""
        return Filter(
            lambda update: (
                "callback_query" in update
                and (data is None or update["callback_query"].get("data") == data)
            )
        )

    def callback_query_data_startswith(self, prefix: str) -> Filter:
        """Filter callback queries with data starting with prefix"""
        return Filter(
            lambda update: (
                "callback_query" in update
                and update["callback_query"].get("data", "").startswith(prefix)
            )
        )

    @property
    def callback_query_all(self) -> Filter:
        """Filter all callback queries"""
        return Filter(lambda update: "callback_query" in update)

    @property
    def pre_checkout_query(self) -> Filter:
        """Filter pre-checkout queries"""
        return Filter(lambda update: "pre_checkout_query" in update)

    @property
    def successful_payment(self) -> Filter:
        """Filter successful payment messages"""
        return Filter(
            lambda update: (
                "message" in update
                and "successful_payment" in update["message"]
            )
        )

    def contains_keywords(self, keywords: List[str]) -> Filter:
        """Filter messages containing any of the specified keywords"""
        return Filter(
            lambda update: (
                "message" in update
                and "text" in update["message"]
                and any(
                    keyword.lower() in update["message"]["text"].lower()
                    for keyword in keywords
                )
            )
        )

    def long_message(self, min_length: int) -> Filter:
        """Filter messages longer than min_length"""
        return Filter(
            lambda update: (
                "message" in update
                and "text" in update["message"]
                and len(update["message"]["text"]) >= min_length
            )
        )

    def custom(self, filter_func: Callable[[Dict], bool]) -> Filter:
        """Create a custom filter from a function"""
        @wraps(filter_func)
        def wrapper(update: Dict) -> bool:
            try:
                return bool(filter_func(update))
            except Exception:
                return False
        return Filter(wrapper)