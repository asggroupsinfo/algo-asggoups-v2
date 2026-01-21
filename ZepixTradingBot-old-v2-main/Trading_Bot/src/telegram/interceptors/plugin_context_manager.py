"""
Plugin Context Manager - V5 Plugin Selection System

Manages user plugin selection context for command execution.
Implements session-based context storage with automatic expiry.

Version: 1.1.0 (Expiry Warning)
Created: 2026-01-21
Part of: TELEGRAM_V5_PLUGIN_SELECTION_UPGRADE
"""

import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from threading import Lock

logger = logging.getLogger(__name__)


class PluginContextManager:
    """
    Manages plugin selection context for each user session.

    Features:
    - Per-user plugin context storage
    - Automatic 5-minute expiry
    - Thread-safe operations
    - Context validation
    - Cleanup of expired contexts
    """

    # Class-level storage
    _user_contexts: Dict[int, Dict] = {}
    _lock = Lock()  # Thread safety

    # Configuration
    DEFAULT_EXPIRY_SECONDS = 300  # 5 minutes
    WARNING_THRESHOLD_SECONDS = 60 # Warn if < 60s remain
    VALID_PLUGINS = ['v3', 'v6', 'both']

    @classmethod
    def set_plugin_context(
        cls,
        chat_id: int,
        plugin: str,
        command: str = None,
        expiry_seconds: int = None
    ) -> bool:
        """Set plugin context for user session."""
        if plugin not in cls.VALID_PLUGINS:
            logger.error(f"[PluginContext] Invalid plugin: {plugin}")
            return False

        expiry = expiry_seconds or cls.DEFAULT_EXPIRY_SECONDS

        with cls._lock:
            cls._user_contexts[chat_id] = {
                'plugin': plugin,
                'timestamp': datetime.now(),
                'expires_in': expiry,
                'command': command,
                'warning_sent': False
            }

        logger.info(
            f"[PluginContext] Set context for chat {chat_id}: "
            f"plugin={plugin}, cmd={command}, expiry={expiry}s"
        )
        return True

    @classmethod
    def get_plugin_context(cls, chat_id: int) -> Optional[str]:
        """Get current plugin context for user."""
        with cls._lock:
            if chat_id not in cls._user_contexts:
                return None

            context = cls._user_contexts[chat_id]
            elapsed = (datetime.now() - context['timestamp']).total_seconds()

            if elapsed > context['expires_in']:
                logger.debug(f"[PluginContext] Context expired for chat {chat_id}")
                del cls._user_contexts[chat_id]
                return None

            return context['plugin']

    @classmethod
    def check_expiry_warnings(cls) -> Dict[int, str]:
        """
        Check for contexts nearing expiry.
        Returns dict {chat_id: plugin_name} of users to warn.
        """
        warnings = {}
        with cls._lock:
            for chat_id, ctx in cls._user_contexts.items():
                if ctx.get('warning_sent'):
                    continue

                elapsed = (datetime.now() - ctx['timestamp']).total_seconds()
                remaining = ctx['expires_in'] - elapsed

                if 0 < remaining < cls.WARNING_THRESHOLD_SECONDS:
                    warnings[chat_id] = ctx['plugin']
                    ctx['warning_sent'] = True

        return warnings

    @classmethod
    def clear_plugin_context(cls, chat_id: int) -> bool:
        """Clear plugin context for user."""
        with cls._lock:
            if chat_id in cls._user_contexts:
                del cls._user_contexts[chat_id]
                return True
            return False

    @classmethod
    def has_active_context(cls, chat_id: int) -> bool:
        return cls.get_plugin_context(chat_id) is not None

# Convenience functions
def set_user_plugin(chat_id: int, plugin: str, command: str = None) -> bool:
    return PluginContextManager.set_plugin_context(chat_id, plugin, command)

def get_user_plugin(chat_id: int) -> Optional[str]:
    return PluginContextManager.get_plugin_context(chat_id)

def clear_user_plugin(chat_id: int) -> bool:
    return PluginContextManager.clear_plugin_context(chat_id)

def has_plugin_selection(chat_id: int) -> bool:
    return PluginContextManager.has_active_context(chat_id)
