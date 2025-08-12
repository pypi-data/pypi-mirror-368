from typing import Dict, List, Optional, Any, Union
from threading import Lock
import asyncio
import time

class State:
    def __init__(self, name: str, default_data: Optional[Dict] = None):
        self.name = name
        self.default_data = default_data or {}
        self._user_states: Dict[int, Dict] = {}
        self._lock = Lock()
    
    def set_state(self, user_id: int, data: Optional[Dict] = None) -> None:
        with self._lock:
            self._user_states[user_id] = {**self.default_data, **(data or {})}
    
    def get_state(self, user_id: int) -> Optional[Dict]:
        with self._lock:
            return self._user_states.get(user_id)
    
    def update_state(self, user_id: int, updates: Dict) -> bool:
        with self._lock:
            if user_id not in self._user_states:
                return False
            self._user_states[user_id].update(updates)
            return True
    
    def clear_state(self, user_id: int) -> bool:
        with self._lock:
            if user_id in self._user_states:
                del self._user_states[user_id]
                return True
            return False
    
    def has_state(self, user_id: int) -> bool:
        with self._lock:
            return user_id in self._user_states


class TimedState(State):
    def __init__(self, name: str, default_data: Optional[Dict] = None, timeout: int = 3600):
        super().__init__(name, default_data)
        self._timeouts: Dict[int, float] = {}
        self.timeout = timeout
    
    def set_state(self, user_id: int, data: Optional[Dict] = None) -> None:
        super().set_state(user_id, data)
        with self._lock:
            self._timeouts[user_id] = time.time() + self.timeout
    
    def get_state(self, user_id: int) -> Optional[Dict]:
        with self._lock:
            if user_id in self._timeouts and time.time() > self._timeouts[user_id]:
                del self._timeouts[user_id]
                if user_id in self._user_states:
                    del self._user_states[user_id]
                return None
        return super().get_state(user_id)
    
    def clear_state(self, user_id: int) -> bool:
        with self._lock:
            if user_id in self._timeouts:
                del self._timeouts[user_id]
        return super().clear_state(user_id)


class ChatState:
    def __init__(self, name: str, default_data: Optional[Dict] = None):
        self.name = name
        self.default_data = default_data or {}
        self._chat_states: Dict[int, Dict] = {}
        self._user_states_in_chat: Dict[int, Dict[int, Dict]] = {}
        self._lock = Lock()
    
    def set_chat_state(self, chat_id: int, data: Optional[Dict] = None) -> None:
        with self._lock:
            self._chat_states[chat_id] = {**self.default_data, **(data or {})}
    
    def get_chat_state(self, chat_id: int) -> Optional[Dict]:
        with self._lock:
            return self._chat_states.get(chat_id)
    
    def set_user_state_in_chat(self, chat_id: int, user_id: int, data: Optional[Dict] = None) -> None:
        with self._lock:
            if chat_id not in self._user_states_in_chat:
                self._user_states_in_chat[chat_id] = {}
            self._user_states_in_chat[chat_id][user_id] = {**self.default_data, **(data or {})}
    
    def get_user_state_in_chat(self, chat_id: int, user_id: int) -> Optional[Dict]:
        with self._lock:
            return self._user_states_in_chat.get(chat_id, {}).get(user_id)
    
    def clear_chat_state(self, chat_id: int) -> bool:
        with self._lock:
            if chat_id in self._chat_states:
                del self._chat_states[chat_id]
                if chat_id in self._user_states_in_chat:
                    del self._user_states_in_chat[chat_id]
                return True
            return False
    
    def clear_user_state_in_chat(self, chat_id: int, user_id: int) -> bool:
        with self._lock:
            if chat_id in self._user_states_in_chat and user_id in self._user_states_in_chat[chat_id]:
                del self._user_states_in_chat[chat_id][user_id]
                return True
            return False


class StateMachine:
    def __init__(self):
        self._states: Dict[str, Union[State, TimedState, ChatState]] = {}
        self._lock = Lock()
    
    def add_state(self, state: Union[State, TimedState, ChatState]) -> None:
        with self._lock:
            self._states[state.name] = state
    
    def get_state(self, name: str) -> Optional[Union[State, TimedState, ChatState]]:
        with self._lock:
            return self._states.get(name)
    
    def remove_state(self, name: str) -> bool:
        with self._lock:
            if name in self._states:
                del self._states[name]
                return True
            return False
    
    def clear_all_states(self) -> None:
        with self._lock:
            self._states.clear()


class AsyncState(State):
    async def set_state(self, user_id: int, data: Optional[Dict] = None) -> None:
        async with asyncio.Lock():
            self._user_states[user_id] = {**self.default_data, **(data or {})}
    
    async def get_state(self, user_id: int) -> Optional[Dict]:
        async with asyncio.Lock():
            return self._user_states.get(user_id)
    
    async def update_state(self, user_id: int, updates: Dict) -> bool:
        async with asyncio.Lock():
            if user_id not in self._user_states:
                return False
            self._user_states[user_id].update(updates)
            return True
    
    async def clear_state(self, user_id: int) -> bool:
        async with asyncio.Lock():
            if user_id in self._user_states:
                del self._user_states[user_id]
                return True
            return False
    
    async def has_state(self, user_id: int) -> bool:
        async with asyncio.Lock():
            return user_id in self._user_states


class AsyncChatState(ChatState):
    async def set_chat_state(self, chat_id: int, data: Optional[Dict] = None) -> None:
        async with asyncio.Lock():
            self._chat_states[chat_id] = {**self.default_data, **(data or {})}
    
    async def get_chat_state(self, chat_id: int) -> Optional[Dict]:
        async with asyncio.Lock():
            return self._chat_states.get(chat_id)
    
    async def set_user_state_in_chat(self, chat_id: int, user_id: int, data: Optional[Dict] = None) -> None:
        async with asyncio.Lock():
            if chat_id not in self._user_states_in_chat:
                self._user_states_in_chat[chat_id] = {}
            self._user_states_in_chat[chat_id][user_id] = {**self.default_data, **(data or {})}
    
    async def get_user_state_in_chat(self, chat_id: int, user_id: int) -> Optional[Dict]:
        async with asyncio.Lock():
            return self._user_states_in_chat.get(chat_id, {}).get(user_id)
    
    async def clear_chat_state(self, chat_id: int) -> bool:
        async with asyncio.Lock():
            if chat_id in self._chat_states:
                del self._chat_states[chat_id]
                if chat_id in self._user_states_in_chat:
                    del self._user_states_in_chat[chat_id]
                return True
            return False
    
    async def clear_user_state_in_chat(self, chat_id: int, user_id: int) -> bool:
        async with asyncio.Lock():
            if chat_id in self._user_states_in_chat and user_id in self._user_states_in_chat[chat_id]:
                del self._user_states_in_chat[chat_id][user_id]
                return True
            return False


class StateManager:
    def __init__(self):
        self._state_machine = StateMachine()
        self._async_state_machine = StateMachine()
    
    def register_state(self, state: Union[State, TimedState, ChatState]) -> None:
        self._state_machine.add_state(state)
    
    def register_async_state(self, state: Union[AsyncState, AsyncChatState]) -> None:
        self._async_state_machine.add_state(state)
    
    def get_state(self, name: str) -> Optional[Union[State, TimedState, ChatState]]:
        return self._state_machine.get_state(name)
    
    async def get_async_state(self, name: str) -> Optional[Union[AsyncState, AsyncChatState]]:
        return self._async_state_machine.get_state(name)
    
    def clear_all_states(self) -> None:
        self._state_machine.clear_all_states()
        self._async_state_machine.clear_all_states()