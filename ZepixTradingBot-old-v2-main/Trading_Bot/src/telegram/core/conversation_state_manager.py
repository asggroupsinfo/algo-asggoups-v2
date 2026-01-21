"""
Conversation State Manager - Multi-step Flow State Management

Manages state for multi-step interactions (e.g., Buy flow, Settings flow).
Includes thread-safe locking and state storage.

Version: 1.0.0
Created: 2026-01-21
Part of: TELEGRAM_V5_ZERO_TYPING_UI
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ConversationState:
    """Store state for multi-step flows"""

    def __init__(self, command: str = None):
        self.command = command  # e.g., 'buy', 'setlot'
        self.step = 0  # Current step number
        self.data = {}  # Collected data
        self.breadcrumb = []  # Navigation path
        self.timestamp = datetime.now()

    def add_data(self, key: str, value: Any):
        """Add data collected in this step"""
        self.data[key] = value
        self.timestamp = datetime.now() # Update timestamp on activity

    def next_step(self):
        """Move to next step"""
        self.step += 1

    def get_data(self, key: str, default=None):
        """Get previously collected data"""
        return self.data.get(key, default)

    def add_breadcrumb(self, label: str):
        """Add navigation breadcrumb"""
        self.breadcrumb.append(label)

class ConversationStateManager:
    """Thread-safe state management"""

    def __init__(self):
        self.states: Dict[int, ConversationState] = {}  # {chat_id: ConversationState}
        self.locks: Dict[int, asyncio.Lock] = {}  # Per-user locks

    def get_lock(self, chat_id: int) -> asyncio.Lock:
        """Get or create lock for user"""
        if chat_id not in self.locks:
            self.locks[chat_id] = asyncio.Lock()
        return self.locks[chat_id]

    def get_state(self, chat_id: int) -> ConversationState:
        """Get or create state for user"""
        if chat_id not in self.states:
            self.states[chat_id] = ConversationState()
        return self.states[chat_id]

    def start_flow(self, chat_id: int, command: str) -> ConversationState:
        """Start a new flow, clearing old state"""
        self.states[chat_id] = ConversationState(command)
        return self.states[chat_id]

    def clear_state(self, chat_id: int):
        """Clear state after completion"""
        if chat_id in self.states:
            del self.states[chat_id]

    async def update_state(self, chat_id: int, updater_func):
        """Update state with lock"""
        lock = self.get_lock(chat_id)

        async with lock:
            state = self.get_state(chat_id)
            await updater_func(state)

# Global instance
state_manager = ConversationStateManager()
