"""
Plugin Context Manager - V5 Plugin Selection System

Manages user plugin selection context for command execution.
Implements session-based context storage with automatic expiry.

Version: 1.0.0
Created: 2026-01-20
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
    
    Context Structure:
    {
        chat_id: {
            'plugin': 'v3' | 'v6' | 'both',
            'timestamp': datetime,
            'expires_in': 300 (seconds),
            'command': str (original command)
        }
    }
    """
    
    # Class-level storage
    _user_contexts: Dict[int, Dict] = {}
    _lock = Lock()  # Thread safety
    
    # Configuration
    DEFAULT_EXPIRY_SECONDS = 300  # 5 minutes
    VALID_PLUGINS = ['v3', 'v6', 'both']
    
    @classmethod
    def set_plugin_context(
        cls,
        chat_id: int,
        plugin: str,
        command: str = None,
        expiry_seconds: int = None
    ) -> bool:
        """
        Set plugin context for user session.
        
        Args:
            chat_id: Telegram chat ID
            plugin: Plugin selection ('v3', 'v6', 'both')
            command: Command being executed (optional)
            expiry_seconds: Custom expiry time (default: 300)
        
        Returns:
            True if context set successfully
        """
        # Validate plugin
        if plugin not in cls.VALID_PLUGINS:
            logger.error(f"[PluginContext] Invalid plugin: {plugin}")
            return False
        
        expiry = expiry_seconds or cls.DEFAULT_EXPIRY_SECONDS
        
        with cls._lock:
            cls._user_contexts[chat_id] = {
                'plugin': plugin,
                'timestamp': datetime.now(),
                'expires_in': expiry,
                'command': command
            }
        
        logger.info(
            f"[PluginContext] Set context for chat {chat_id}: "
            f"plugin={plugin}, cmd={command}, expiry={expiry}s"
        )
        return True
    
    @classmethod
    def get_plugin_context(cls, chat_id: int) -> Optional[str]:
        """
        Get current plugin context for user.
        
        Args:
            chat_id: Telegram chat ID
        
        Returns:
            Plugin selection ('v3', 'v6', 'both') or None if expired/missing
        """
        with cls._lock:
            if chat_id not in cls._user_contexts:
                return None
            
            context = cls._user_contexts[chat_id]
            
            # Check expiry
            elapsed = (datetime.now() - context['timestamp']).total_seconds()
            if elapsed > context['expires_in']:
                # Context expired
                logger.debug(f"[PluginContext] Context expired for chat {chat_id}")
                del cls._user_contexts[chat_id]
                return None
            
            plugin = context['plugin']
            logger.debug(f"[PluginContext] Retrieved context for chat {chat_id}: {plugin}")
            return plugin
    
    @classmethod
    def get_full_context(cls, chat_id: int) -> Optional[Dict]:
        """
        Get full context data for user.
        
        Args:
            chat_id: Telegram chat ID
        
        Returns:
            Full context dict or None if expired/missing
        """
        with cls._lock:
            if chat_id not in cls._user_contexts:
                return None
            
            context = cls._user_contexts[chat_id]
            
            # Check expiry
            elapsed = (datetime.now() - context['timestamp']).total_seconds()
            if elapsed > context['expires_in']:
                del cls._user_contexts[chat_id]
                return None
            
            return context.copy()
    
    @classmethod
    def clear_plugin_context(cls, chat_id: int) -> bool:
        """
        Clear plugin context for user.
        
        Args:
            chat_id: Telegram chat ID
        
        Returns:
            True if context was cleared
        """
        with cls._lock:
            if chat_id in cls._user_contexts:
                del cls._user_contexts[chat_id]
                logger.debug(f"[PluginContext] Cleared context for chat {chat_id}")
                return True
            return False
    
    @classmethod
    def has_active_context(cls, chat_id: int) -> bool:
        """
        Check if user has active (non-expired) context.
        
        Args:
            chat_id: Telegram chat ID
        
        Returns:
            True if active context exists
        """
        return cls.get_plugin_context(chat_id) is not None
    
    @classmethod
    def get_remaining_time(cls, chat_id: int) -> Optional[int]:
        """
        Get remaining time (seconds) for context expiry.
        
        Args:
            chat_id: Telegram chat ID
        
        Returns:
            Remaining seconds or None if no context
        """
        with cls._lock:
            if chat_id not in cls._user_contexts:
                return None
            
            context = cls._user_contexts[chat_id]
            elapsed = (datetime.now() - context['timestamp']).total_seconds()
            remaining = max(0, context['expires_in'] - elapsed)
            
            return int(remaining)
    
    @classmethod
    def cleanup_expired_contexts(cls) -> int:
        """
        Clean up all expired contexts.
        
        Returns:
            Number of contexts cleaned up
        """
        with cls._lock:
            expired_chats = []
            
            for chat_id, context in cls._user_contexts.items():
                elapsed = (datetime.now() - context['timestamp']).total_seconds()
                if elapsed > context['expires_in']:
                    expired_chats.append(chat_id)
            
            for chat_id in expired_chats:
                del cls._user_contexts[chat_id]
            
            if expired_chats:
                logger.info(f"[PluginContext] Cleaned up {len(expired_chats)} expired contexts")
            
            return len(expired_chats)
    
    @classmethod
    def get_stats(cls) -> Dict:
        """
        Get context manager statistics.
        
        Returns:
            Dict with stats
        """
        with cls._lock:
            total_contexts = len(cls._user_contexts)
            
            # Count by plugin
            plugin_counts = {'v3': 0, 'v6': 0, 'both': 0}
            active_count = 0
            
            for context in cls._user_contexts.values():
                elapsed = (datetime.now() - context['timestamp']).total_seconds()
                if elapsed <= context['expires_in']:
                    active_count += 1
                    plugin = context['plugin']
                    plugin_counts[plugin] = plugin_counts.get(plugin, 0) + 1
            
            return {
                'total_contexts': total_contexts,
                'active_contexts': active_count,
                'expired_contexts': total_contexts - active_count,
                'v3_contexts': plugin_counts['v3'],
                'v6_contexts': plugin_counts['v6'],
                'both_contexts': plugin_counts['both']
            }
    
    @classmethod
    def reset_all_contexts(cls) -> int:
        """
        Reset all contexts (for testing/admin).
        
        Returns:
            Number of contexts cleared
        """
        with cls._lock:
            count = len(cls._user_contexts)
            cls._user_contexts.clear()
            logger.warning(f"[PluginContext] Reset all contexts ({count} cleared)")
            return count


# Convenience functions for common operations

def set_user_plugin(chat_id: int, plugin: str, command: str = None) -> bool:
    """Set plugin context for user (convenience function)."""
    return PluginContextManager.set_plugin_context(chat_id, plugin, command)


def get_user_plugin(chat_id: int) -> Optional[str]:
    """Get plugin context for user (convenience function)."""
    return PluginContextManager.get_plugin_context(chat_id)


def clear_user_plugin(chat_id: int) -> bool:
    """Clear plugin context for user (convenience function)."""
    return PluginContextManager.clear_plugin_context(chat_id)


def has_plugin_selection(chat_id: int) -> bool:
    """Check if user has active plugin selection (convenience function)."""
    return PluginContextManager.has_active_context(chat_id)
