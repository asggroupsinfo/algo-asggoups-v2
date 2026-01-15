"""
Shadow Mode Telegram Commands
Commands for controlling and monitoring shadow mode

Part of Plan 11: Shadow Mode Testing
Version: 1.0.0
Date: 2026-01-15
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ShadowModeCommands:
    """
    Telegram commands for shadow mode control and monitoring.
    
    Commands:
    - /shadow_status - Show shadow mode status
    - /shadow_enable - Enable shadow mode (legacy executes, plugins shadow)
    - /shadow_disable - Disable shadow mode (legacy only)
    - /shadow_mode <mode> - Set specific shadow mode
    - /shadow_report - Generate shadow mode report
    - /shadow_discrepancies - Show recent discrepancies
    - /shadow_plugin_on <plugin_id> - Enable plugin for shadow mode
    - /shadow_plugin_off <plugin_id> - Disable plugin from shadow mode
    - /shadow_export - Export shadow mode data
    - /shadow_virtual_orders - Show virtual orders
    - /shadow_reset - Reset shadow mode statistics
    """
    
    def __init__(self, shadow_manager, telegram_bot):
        self.shadow_manager = shadow_manager
        self.bot = telegram_bot
        
        # Register commands
        self._register_commands()
    
    def _register_commands(self):
        """Register shadow mode commands with the bot"""
        commands = {
            'shadow_status': self.cmd_shadow_status,
            'shadow_enable': self.cmd_shadow_enable,
            'shadow_disable': self.cmd_shadow_disable,
            'shadow_mode': self.cmd_shadow_mode,
            'shadow_report': self.cmd_shadow_report,
            'shadow_discrepancies': self.cmd_shadow_discrepancies,
            'shadow_plugin_on': self.cmd_shadow_plugin_on,
            'shadow_plugin_off': self.cmd_shadow_plugin_off,
            'shadow_export': self.cmd_shadow_export,
            'shadow_virtual_orders': self.cmd_shadow_virtual_orders,
            'shadow_reset': self.cmd_shadow_reset,
        }
        
        for cmd, handler in commands.items():
            if hasattr(self.bot, 'register_command'):
                self.bot.register_command(cmd, handler)
            else:
                logger.warning(f"Bot does not support register_command for: {cmd}")
    
    async def cmd_shadow_status(self, update, context):
        """Show shadow mode status"""
        stats = self.shadow_manager.get_stats()
        
        message = f"""
🔍 Shadow Mode Status

Mode: {stats['mode']}
Signals Processed: {stats['signals_processed']}
Match Rate: {stats['match_rate']:.1f}%

Matches: {stats['matches']}
Discrepancies: {stats['discrepancies']}
Shadow Signals: {stats['shadow_signals']}
Virtual Orders: {stats['virtual_orders_count']}

Shadow Plugins: {', '.join(stats['shadow_plugins']) or 'None'}
"""
        await update.message.reply_text(message)
    
    async def cmd_shadow_enable(self, update, context):
        """Enable shadow mode"""
        from src.core.shadow_mode_manager import ExecutionMode
        self.shadow_manager.set_mode(ExecutionMode.SHADOW)
        await update.message.reply_text(
            "🔍 Shadow mode ENABLED.\n"
            "Legacy executes trades, plugins run in shadow.\n"
            "Decisions will be compared and logged."
        )
    
    async def cmd_shadow_disable(self, update, context):
        """Disable shadow mode (legacy only)"""
        from src.core.shadow_mode_manager import ExecutionMode
        self.shadow_manager.set_mode(ExecutionMode.LEGACY_ONLY)
        await update.message.reply_text(
            "⏹️ Shadow mode DISABLED.\n"
            "Legacy only mode active."
        )
    
    async def cmd_shadow_mode(self, update, context):
        """Set shadow mode"""
        from src.core.shadow_mode_manager import ExecutionMode
        
        if not context.args:
            modes = [m.value for m in ExecutionMode]
            current = self.shadow_manager.get_mode().value
            await update.message.reply_text(
                f"Usage: /shadow_mode <mode>\n\n"
                f"Available modes:\n"
                f"- legacy_only: Only legacy executes\n"
                f"- shadow: Both run, only legacy executes\n"
                f"- plugin_shadow: Both run, only plugins execute\n"
                f"- plugin_only: Only plugins execute\n\n"
                f"Current mode: {current}"
            )
            return
        
        mode_str = context.args[0].lower()
        try:
            mode = ExecutionMode(mode_str)
            self.shadow_manager.set_mode(mode)
            await update.message.reply_text(f"✅ Shadow mode set to: {mode.value}")
        except ValueError:
            await update.message.reply_text(f"❌ Invalid mode: {mode_str}")
    
    async def cmd_shadow_report(self, update, context):
        """Generate shadow mode report"""
        report = self.shadow_manager.generate_report()
        
        # Split report if too long for Telegram
        if len(report) > 4000:
            # Send in chunks
            chunks = [report[i:i+4000] for i in range(0, len(report), 4000)]
            for chunk in chunks:
                await update.message.reply_text(chunk)
        else:
            await update.message.reply_text(report)
    
    async def cmd_shadow_discrepancies(self, update, context):
        """Show recent discrepancies"""
        limit = 5
        if context.args:
            try:
                limit = int(context.args[0])
            except ValueError:
                pass
        
        discrepancies = self.shadow_manager.get_discrepancies(limit)
        
        if not discrepancies:
            await update.message.reply_text("✅ No discrepancies found.")
            return
        
        message = f"⚠️ Recent Discrepancies ({len(discrepancies)}):\n\n"
        for d in discrepancies:
            message += f"Signal: {d.signal_id}\n"
            message += f"Time: {d.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            message += f"Type: {d.discrepancy_type}\n"
            message += f"Details: {d.discrepancy_details}\n"
            message += f"Legacy: {d.legacy_decision.action}\n"
            message += f"Plugin: {d.plugin_decision.action}\n"
            message += "---\n"
        
        await update.message.reply_text(message)
    
    async def cmd_shadow_plugin_on(self, update, context):
        """Enable plugin for shadow mode"""
        if not context.args:
            plugins = self.shadow_manager.get_shadow_plugins()
            await update.message.reply_text(
                f"Usage: /shadow_plugin_on <plugin_id>\n\n"
                f"Currently enabled: {', '.join(plugins) or 'None'}\n\n"
                f"Available plugins:\n"
                f"- v3_combined\n"
                f"- v6_price_action_1m\n"
                f"- v6_price_action_5m\n"
                f"- v6_price_action_15m\n"
                f"- v6_price_action_1h"
            )
            return
        
        plugin_id = context.args[0]
        self.shadow_manager.enable_shadow_plugin(plugin_id)
        await update.message.reply_text(f"✅ Plugin {plugin_id} enabled for shadow mode.")
    
    async def cmd_shadow_plugin_off(self, update, context):
        """Disable plugin from shadow mode"""
        if not context.args:
            plugins = self.shadow_manager.get_shadow_plugins()
            await update.message.reply_text(
                f"Usage: /shadow_plugin_off <plugin_id>\n\n"
                f"Currently enabled: {', '.join(plugins) or 'None'}"
            )
            return
        
        plugin_id = context.args[0]
        self.shadow_manager.disable_shadow_plugin(plugin_id)
        await update.message.reply_text(f"⏹️ Plugin {plugin_id} disabled from shadow mode.")
    
    async def cmd_shadow_export(self, update, context):
        """Export shadow mode data"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Export comparisons
        comparisons_path = f"data/shadow_comparisons_{timestamp}.json"
        self.shadow_manager.export_comparisons(comparisons_path)
        
        # Export virtual orders
        virtual_orders_path = f"data/shadow_virtual_orders_{timestamp}.json"
        self.shadow_manager.export_virtual_orders(virtual_orders_path)
        
        await update.message.reply_text(
            f"📁 Shadow data exported:\n"
            f"- Comparisons: {comparisons_path}\n"
            f"- Virtual Orders: {virtual_orders_path}"
        )
    
    async def cmd_shadow_virtual_orders(self, update, context):
        """Show virtual orders (shadow trades)"""
        limit = 10
        if context.args:
            try:
                limit = int(context.args[0])
            except ValueError:
                pass
        
        virtual_orders = self.shadow_manager.get_virtual_orders(limit)
        
        if not virtual_orders:
            await update.message.reply_text("📋 No virtual orders recorded.")
            return
        
        message = f"📋 Virtual Orders ({len(virtual_orders)}):\n\n"
        for order in virtual_orders:
            params = order.get('order_params', {})
            message += f"Plugin: {order.get('plugin_id', 'N/A')}\n"
            message += f"Signal: {order.get('signal_id', 'N/A')}\n"
            message += f"Symbol: {params.get('symbol', 'N/A')}\n"
            message += f"Direction: {params.get('direction', 'N/A')}\n"
            message += f"Time: {order.get('timestamp', 'N/A')}\n"
            message += "---\n"
        
        await update.message.reply_text(message)
    
    async def cmd_shadow_reset(self, update, context):
        """Reset shadow mode statistics"""
        self.shadow_manager.reset_stats()
        await update.message.reply_text(
            "🔄 Shadow mode statistics reset.\n"
            "All decisions, comparisons, and virtual orders cleared."
        )


# Helper function to create and register shadow commands
def setup_shadow_commands(shadow_manager, telegram_bot) -> ShadowModeCommands:
    """
    Create and register shadow mode commands with the Telegram bot.
    
    Args:
        shadow_manager: ShadowModeManager instance
        telegram_bot: Telegram bot instance
        
    Returns:
        ShadowModeCommands instance
    """
    return ShadowModeCommands(shadow_manager, telegram_bot)
