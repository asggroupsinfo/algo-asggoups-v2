"""
Command Interceptor - V5 Plugin Selection System

Intercepts commands that require plugin context (V3/V6).
If context is missing, pauses command execution and shows selection menu.
Resumes command after selection.

Version: 1.0.0
Created: 2026-01-21
Part of: TELEGRAM_V5_PLUGIN_LAYER
"""

import logging
from typing import Dict, Optional, Any, List
from ..interceptors.plugin_context_manager import PluginContextManager
from ..core.plugin_selection_menu import PluginSelectionMenu

logger = logging.getLogger(__name__)

class CommandInterceptor:
    """
    Intercepts commands to ensure plugin context exists.
    """

    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.plugin_manager = PluginContextManager
        self.selection_menu = PluginSelectionMenu(bot_instance)

        # Define which commands require plugin context
        self.plugin_aware_commands = [
            # Trading
            '/buy', '/sell', '/close', '/closeall', '/positions', '/orders',
            '/history', '/pnl', '/profit', '/booking', '/levels', '/partial',
            '/dualorder', '/orderb',

            # Risk
            '/risk', '/setlot', '/setsl', '/settp', '/dailylimit',
            '/maxloss', '/maxprofit', '/risktier', '/slsystem',
            '/trailsl', '/breakeven', '/protection',

            # Re-entry
            '/reentry', '/slhunt', '/tpcontinue', '/recovery',
            '/cooldown', '/chains', '/autonomous',

            # Strategy/Analysis
            '/strategy', '/signals', '/filters', '/multiplier',
            '/trends', '/timeframe',
            '/tf1m', '/tf5m', '/tf15m', '/tf30m',
            '/tf1h', '/tf4h', '/tf1d'
        ]

        # Commands that are implicitly V3 (no selection needed)
        self.v3_commands = [
            '/v3', '/logic1', '/logic2', '/logic3',
            '/logic1_config', '/logic2_config', '/logic3_config',
            '/v3_config', '/v3_toggle'
        ]

        # Commands that are implicitly V6 (no selection needed)
        self.v6_commands = [
            '/v6', '/v6_status', '/v6_control', '/v6_config',
            '/v6_1m_config', '/v6_5m_config', '/v6_15m_config', '/v6_1h_config',
            '/tf15m_on', '/tf15m_off', '/tf30m_on', '/tf30m_off',
            '/tf1h_on', '/tf1h_off', '/tf4h_on', '/tf4h_off'
        ]

    def is_plugin_aware(self, command: str) -> bool:
        """Check if command requires plugin context"""
        cmd = command.split(' ')[0].lower() # Handle arguments
        return cmd in self.plugin_aware_commands

    def get_implicit_context(self, command: str) -> Optional[str]:
        """Get implicit context for specific commands"""
        cmd = command.split(' ')[0].lower()
        if cmd in self.v3_commands:
            return 'v3'
        if cmd in self.v6_commands:
            return 'v6'
        return None

    async def intercept(self, update: Any, context: Any, command: str, args: List[str] = None) -> bool:
        """
        Intercept command execution.

        Returns:
            True if intercepted (execution stopped for selection).
            False if execution should proceed.
        """
        chat_id = update.effective_chat.id

        # 1. Check implicit context
        implicit = self.get_implicit_context(command)
        if implicit:
            self.plugin_manager.set_plugin_context(chat_id, implicit, command)
            return False # Proceed with implicit context

        # 2. Check if plugin aware
        if not self.is_plugin_aware(command):
            return False # Not plugin aware, proceed

        # 3. Check if context exists
        if self.plugin_manager.has_active_context(chat_id):
            # Refresh timestamp
            current = self.plugin_manager.get_plugin_context(chat_id)
            self.plugin_manager.set_plugin_context(chat_id, current, command)
            return False # Context exists, proceed

        # 4. No context -> Intercept and show selection
        logger.info(f"[CommandInterceptor] Intercepting {command} for chat {chat_id}")
        await self.selection_menu.show_selection_menu(update, command, args)
        return True

    async def handle_selection(self, update: Any, context: Any) -> Optional[Dict]:
        """
        Handle selection callback.
        Returns dict with {command, args, plugin} to resume execution.
        """
        query = update.callback_query
        data = query.data

        # Format: plugin_select_{type}_{command_encoded}
        if not data.startswith('plugin_select_'):
            return None

        parts = data.split('_')
        if len(parts) < 3:
            return None

        plugin_type = parts[2] # v3, v6, both

        # Decode command (might have underscores)
        # We need to store command in a way that retrieves it easily.
        # Simple approach: The command is stored in the menu callback data.
        # But callback data limit is 64 bytes.
        # Better: Store pending command in PluginContextManager or a temp cache?
        # Actually, PluginContextManager stores 'command' in set_plugin_context.

        # Let's parse command from data if short enough, or assume flow managed externally.
        # In this implementation, we will use the 'command' stored in the selection menu generator.

        # Reconstruct command from parts[3:]
        command_name = "_".join(parts[3:])

        chat_id = update.effective_chat.id

        # Set context
        self.plugin_manager.set_plugin_context(chat_id, plugin_type, command_name)

        return {
            'command': command_name,
            'plugin': plugin_type
        }
