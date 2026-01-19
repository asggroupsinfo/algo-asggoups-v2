"""
V6 Control Menu Handler - Telegram V5 Upgrade

Manages V6 Price Action plugin timeframes (15M, 30M, 1H, 4H) via Telegram menu.

Features:
- Enable/disable individual V6 timeframes
- View per-timeframe performance stats
- Enable All / Disable All buttons
- Per-timeframe configuration

Version: 1.0.0
Date: 2026-01-19
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class V6ControlMenuHandler:
    """
    Handles V6 Price Action plugin control via Telegram menu.
    
    Provides:
    - Timeframe toggle buttons (15M, 30M, 1H, 4H)
    - Per-timeframe status display
    - Performance stats per timeframe
    - Enable All / Disable All functionality
    """
    
    V6_TIMEFRAMES = ["15m", "30m", "1h", "4h"]
    
    def __init__(self, telegram_bot):
        """
        Initialize V6ControlMenuHandler.
        
        Args:
            telegram_bot: The Telegram bot instance
        """
        self.bot = telegram_bot
        self._logger = logger
    
    def _get_v6_config(self) -> Dict[str, Any]:
        """Get V6 plugin configuration from bot config"""
        try:
            plugins_config = self.bot.config.get("plugins", {})
            return plugins_config.get("v6_price_action", {})
        except Exception as e:
            self._logger.error(f"[V6Menu] Error getting V6 config: {e}")
            return {}
    
    def _get_timeframe_status(self, timeframe: str) -> bool:
        """
        Get enabled status for a specific timeframe.
        
        Args:
            timeframe: Timeframe (15m, 30m, 1h, 4h)
        
        Returns:
            True if enabled, False otherwise
        """
        try:
            v6_config = self._get_v6_config()
            timeframes_config = v6_config.get("timeframes", {})
            tf_config = timeframes_config.get(timeframe, {})
            return tf_config.get("enabled", False)
        except Exception as e:
            self._logger.error(f"[V6Menu] Error getting timeframe status: {e}")
            return False
    
    def _get_timeframe_stats(self, timeframe: str) -> Dict[str, Any]:
        """
        Get performance stats for a specific timeframe.
        
        Args:
            timeframe: Timeframe (15m, 30m, 1h, 4h)
        
        Returns:
            Dict with trades, pnl, win_rate
        """
        try:
            if hasattr(self.bot, 'trading_engine') and self.bot.trading_engine:
                db = getattr(self.bot.trading_engine, 'database', None)
                if db:
                    today = datetime.now().strftime("%Y-%m-%d")
                    stats = db.get_v6_timeframe_stats(timeframe, today)
                    if stats:
                        return stats
            
            return {"trades": 0, "pnl": 0.0, "win_rate": 0.0}
        except Exception as e:
            self._logger.error(f"[V6Menu] Error getting timeframe stats: {e}")
            return {"trades": 0, "pnl": 0.0, "win_rate": 0.0}
    
    def show_v6_main_menu(self, user_id: int, message_id: int):
        """
        Show main V6 control menu with timeframe toggles.
        
        Args:
            user_id: Telegram user ID
            message_id: Message ID to edit
        """
        v6_config = self._get_v6_config()
        v6_enabled = v6_config.get("enabled", False)
        
        # Build status text
        status_emoji = "" if v6_enabled else ""
        status_text = "ENABLED" if v6_enabled else "DISABLED"
        
        # Build timeframe status rows
        tf_status_lines = []
        all_enabled = True
        any_enabled = False
        
        for tf in self.V6_TIMEFRAMES:
            enabled = self._get_timeframe_status(tf)
            stats = self._get_timeframe_stats(tf)
            
            if enabled:
                any_enabled = True
            else:
                all_enabled = False
            
            emoji = "" if enabled else ""
            pnl_emoji = "" if stats["pnl"] >= 0 else ""
            
            tf_status_lines.append(
                f"  {emoji} {tf.upper()}: {stats['trades']} trades, "
                f"{pnl_emoji}${stats['pnl']:+.2f} ({stats['win_rate']:.0f}% WR)"
            )
        
        text = (
            f" <b>V6 PRICE ACTION CONTROL</b>\n"
            f"{'=' * 28}\n\n"
            f"<b>System Status:</b> {status_emoji} {status_text}\n\n"
            f"<b>Timeframe Status (Today):</b>\n"
            + "\n".join(tf_status_lines) +
            f"\n\n<b>Quick Actions:</b>\n"
            f"Toggle individual timeframes or use Enable/Disable All."
        )
        
        # Build keyboard
        keyboard = {"inline_keyboard": []}
        
        # V6 System Toggle
        toggle_text = " Disable V6 System" if v6_enabled else " Enable V6 System"
        keyboard["inline_keyboard"].append([
            {"text": toggle_text, "callback_data": "v6_toggle_system"}
        ])
        
        # Individual timeframe toggles (2 per row)
        tf_row1 = []
        tf_row2 = []
        
        for i, tf in enumerate(self.V6_TIMEFRAMES):
            enabled = self._get_timeframe_status(tf)
            emoji = "" if enabled else ""
            button = {
                "text": f"{emoji} {tf.upper()}",
                "callback_data": f"v6_toggle_tf_{tf}"
            }
            if i < 2:
                tf_row1.append(button)
            else:
                tf_row2.append(button)
        
        keyboard["inline_keyboard"].append(tf_row1)
        keyboard["inline_keyboard"].append(tf_row2)
        
        # Enable All / Disable All
        keyboard["inline_keyboard"].append([
            {"text": " Enable All", "callback_data": "v6_enable_all"},
            {"text": " Disable All", "callback_data": "v6_disable_all"}
        ])
        
        # View Stats / Configure
        keyboard["inline_keyboard"].append([
            {"text": " View Stats", "callback_data": "v6_view_stats"},
            {"text": " Configure", "callback_data": "v6_configure"}
        ])
        
        # Back button
        keyboard["inline_keyboard"].append([
            {"text": " Back to Main Menu", "callback_data": "menu_main"}
        ])
        
        if message_id:
            self.bot.edit_message(text, message_id, keyboard, parse_mode="HTML")
        else:
            self.bot.send_message_with_keyboard(text, keyboard)
    
    def handle_toggle_system(self, user_id: int, message_id: int) -> bool:
        """
        Toggle V6 system enabled/disabled.
        
        Args:
            user_id: Telegram user ID
            message_id: Message ID to edit
        
        Returns:
            True if toggled successfully
        """
        try:
            v6_config = self._get_v6_config()
            current_state = v6_config.get("enabled", False)
            new_state = not current_state
            
            # Update config
            if hasattr(self.bot, 'config'):
                if "plugins" not in self.bot.config:
                    self.bot.config["plugins"] = {}
                if "v6_price_action" not in self.bot.config["plugins"]:
                    self.bot.config["plugins"]["v6_price_action"] = {}
                
                self.bot.config["plugins"]["v6_price_action"]["enabled"] = new_state
                
                # Save config if method exists
                if hasattr(self.bot, 'save_config'):
                    self.bot.save_config()
            
            # Send notification
            action = "enabled" if new_state else "disabled"
            self.bot.send_message(f" V6 Price Action system {action}")
            
            # Refresh menu
            self.show_v6_main_menu(user_id, message_id)
            
            return True
        except Exception as e:
            self._logger.error(f"[V6Menu] Error toggling system: {e}")
            return False
    
    def handle_toggle_timeframe(self, user_id: int, message_id: int, timeframe: str) -> bool:
        """
        Toggle a specific V6 timeframe.
        
        Args:
            user_id: Telegram user ID
            message_id: Message ID to edit
            timeframe: Timeframe to toggle (15m, 30m, 1h, 4h)
        
        Returns:
            True if toggled successfully
        """
        try:
            current_state = self._get_timeframe_status(timeframe)
            new_state = not current_state
            
            # Update config
            if hasattr(self.bot, 'config'):
                if "plugins" not in self.bot.config:
                    self.bot.config["plugins"] = {}
                if "v6_price_action" not in self.bot.config["plugins"]:
                    self.bot.config["plugins"]["v6_price_action"] = {}
                if "timeframes" not in self.bot.config["plugins"]["v6_price_action"]:
                    self.bot.config["plugins"]["v6_price_action"]["timeframes"] = {}
                if timeframe not in self.bot.config["plugins"]["v6_price_action"]["timeframes"]:
                    self.bot.config["plugins"]["v6_price_action"]["timeframes"][timeframe] = {}
                
                self.bot.config["plugins"]["v6_price_action"]["timeframes"][timeframe]["enabled"] = new_state
                
                # Save config if method exists
                if hasattr(self.bot, 'save_config'):
                    self.bot.save_config()
            
            # Send notification
            action = "enabled" if new_state else "disabled"
            self.bot.send_message(f" V6 {timeframe.upper()} timeframe {action}")
            
            # Refresh menu
            self.show_v6_main_menu(user_id, message_id)
            
            return True
        except Exception as e:
            self._logger.error(f"[V6Menu] Error toggling timeframe {timeframe}: {e}")
            return False
    
    def handle_enable_all(self, user_id: int, message_id: int) -> bool:
        """
        Enable all V6 timeframes.
        
        Args:
            user_id: Telegram user ID
            message_id: Message ID to edit
        
        Returns:
            True if enabled successfully
        """
        try:
            if hasattr(self.bot, 'config'):
                if "plugins" not in self.bot.config:
                    self.bot.config["plugins"] = {}
                if "v6_price_action" not in self.bot.config["plugins"]:
                    self.bot.config["plugins"]["v6_price_action"] = {}
                if "timeframes" not in self.bot.config["plugins"]["v6_price_action"]:
                    self.bot.config["plugins"]["v6_price_action"]["timeframes"] = {}
                
                for tf in self.V6_TIMEFRAMES:
                    if tf not in self.bot.config["plugins"]["v6_price_action"]["timeframes"]:
                        self.bot.config["plugins"]["v6_price_action"]["timeframes"][tf] = {}
                    self.bot.config["plugins"]["v6_price_action"]["timeframes"][tf]["enabled"] = True
                
                # Also enable the system
                self.bot.config["plugins"]["v6_price_action"]["enabled"] = True
                
                # Save config if method exists
                if hasattr(self.bot, 'save_config'):
                    self.bot.save_config()
            
            self.bot.send_message(" All V6 timeframes enabled (15M, 30M, 1H, 4H)")
            
            # Refresh menu
            self.show_v6_main_menu(user_id, message_id)
            
            return True
        except Exception as e:
            self._logger.error(f"[V6Menu] Error enabling all timeframes: {e}")
            return False
    
    def handle_disable_all(self, user_id: int, message_id: int) -> bool:
        """
        Disable all V6 timeframes.
        
        Args:
            user_id: Telegram user ID
            message_id: Message ID to edit
        
        Returns:
            True if disabled successfully
        """
        try:
            if hasattr(self.bot, 'config'):
                if "plugins" not in self.bot.config:
                    self.bot.config["plugins"] = {}
                if "v6_price_action" not in self.bot.config["plugins"]:
                    self.bot.config["plugins"]["v6_price_action"] = {}
                if "timeframes" not in self.bot.config["plugins"]["v6_price_action"]:
                    self.bot.config["plugins"]["v6_price_action"]["timeframes"] = {}
                
                for tf in self.V6_TIMEFRAMES:
                    if tf not in self.bot.config["plugins"]["v6_price_action"]["timeframes"]:
                        self.bot.config["plugins"]["v6_price_action"]["timeframes"][tf] = {}
                    self.bot.config["plugins"]["v6_price_action"]["timeframes"][tf]["enabled"] = False
                
                # Save config if method exists
                if hasattr(self.bot, 'save_config'):
                    self.bot.save_config()
            
            self.bot.send_message(" All V6 timeframes disabled")
            
            # Refresh menu
            self.show_v6_main_menu(user_id, message_id)
            
            return True
        except Exception as e:
            self._logger.error(f"[V6Menu] Error disabling all timeframes: {e}")
            return False
    
    def show_v6_stats_menu(self, user_id: int, message_id: int):
        """
        Show detailed V6 performance stats.
        
        Args:
            user_id: Telegram user ID
            message_id: Message ID to edit
        """
        # Gather stats for all timeframes
        total_trades = 0
        total_pnl = 0.0
        total_winners = 0
        
        tf_details = []
        
        for tf in self.V6_TIMEFRAMES:
            stats = self._get_timeframe_stats(tf)
            total_trades += stats["trades"]
            total_pnl += stats["pnl"]
            
            if stats["trades"] > 0:
                winners = int(stats["trades"] * stats["win_rate"] / 100)
                total_winners += winners
            
            pnl_emoji = "" if stats["pnl"] >= 0 else ""
            tf_details.append(
                f"<b>{tf.upper()}:</b>\n"
                f"  Trades: {stats['trades']}\n"
                f"  P&L: {pnl_emoji}${stats['pnl']:+.2f}\n"
                f"  Win Rate: {stats['win_rate']:.1f}%"
            )
        
        # Calculate overall win rate
        overall_win_rate = (total_winners / total_trades * 100) if total_trades > 0 else 0.0
        total_emoji = "" if total_pnl >= 0 else ""
        
        text = (
            f" <b>V6 PERFORMANCE STATS</b>\n"
            f"{'=' * 28}\n\n"
            f"<b>Today's Summary:</b>\n"
            f"  Total Trades: {total_trades}\n"
            f"  {total_emoji} Total P&L: ${total_pnl:+.2f}\n"
            f"  Overall Win Rate: {overall_win_rate:.1f}%\n\n"
            f"<b>By Timeframe:</b>\n\n"
            + "\n\n".join(tf_details)
        )
        
        keyboard = {
            "inline_keyboard": [
                [{"text": " Refresh Stats", "callback_data": "v6_view_stats"}],
                [{"text": " Back to V6 Menu", "callback_data": "menu_v6"}]
            ]
        }
        
        if message_id:
            self.bot.edit_message(text, message_id, keyboard, parse_mode="HTML")
        else:
            self.bot.send_message_with_keyboard(text, keyboard)
    
    def show_v6_configure_menu(self, user_id: int, message_id: int):
        """
        Show V6 configuration menu.
        
        Args:
            user_id: Telegram user ID
            message_id: Message ID to edit
        """
        v6_config = self._get_v6_config()
        
        text = (
            f" <b>V6 CONFIGURATION</b>\n"
            f"{'=' * 28}\n\n"
            f"<b>Per-Timeframe Settings:</b>\n"
            f"Configure lot multipliers, SL/TP ratios, and other settings "
            f"for each V6 timeframe.\n\n"
            f"Select a timeframe to configure:"
        )
        
        keyboard = {"inline_keyboard": []}
        
        # Timeframe config buttons
        for tf in self.V6_TIMEFRAMES:
            enabled = self._get_timeframe_status(tf)
            emoji = "" if enabled else ""
            keyboard["inline_keyboard"].append([
                {"text": f"{emoji} Configure {tf.upper()}", "callback_data": f"v6_config_tf_{tf}"}
            ])
        
        # Global settings
        keyboard["inline_keyboard"].append([
            {"text": " Global V6 Settings", "callback_data": "v6_config_global"}
        ])
        
        # Back button
        keyboard["inline_keyboard"].append([
            {"text": " Back to V6 Menu", "callback_data": "menu_v6"}
        ])
        
        if message_id:
            self.bot.edit_message(text, message_id, keyboard, parse_mode="HTML")
        else:
            self.bot.send_message_with_keyboard(text, keyboard)
    
    def show_timeframe_config(self, user_id: int, message_id: int, timeframe: str):
        """
        Show configuration for a specific timeframe.
        
        Args:
            user_id: Telegram user ID
            message_id: Message ID to edit
            timeframe: Timeframe to configure
        """
        v6_config = self._get_v6_config()
        tf_config = v6_config.get("timeframes", {}).get(timeframe, {})
        
        enabled = tf_config.get("enabled", False)
        lot_mult = tf_config.get("lot_multiplier", 1.0)
        sl_mult = tf_config.get("sl_multiplier", 1.0)
        tp_mult = tf_config.get("tp_multiplier", 1.0)
        
        status_emoji = "" if enabled else ""
        
        text = (
            f" <b>V6 {timeframe.upper()} CONFIGURATION</b>\n"
            f"{'=' * 28}\n\n"
            f"<b>Status:</b> {status_emoji} {'Enabled' if enabled else 'Disabled'}\n\n"
            f"<b>Current Settings:</b>\n"
            f"  Lot Multiplier: {lot_mult}x\n"
            f"  SL Multiplier: {sl_mult}x\n"
            f"  TP Multiplier: {tp_mult}x\n\n"
            f"<b>Adjust Settings:</b>"
        )
        
        keyboard = {
            "inline_keyboard": [
                [{"text": f" Lot: {lot_mult}x", "callback_data": f"v6_adj_lot_{timeframe}"}],
                [{"text": f" SL: {sl_mult}x", "callback_data": f"v6_adj_sl_{timeframe}"}],
                [{"text": f" TP: {tp_mult}x", "callback_data": f"v6_adj_tp_{timeframe}"}],
                [{"text": " Back to Configure", "callback_data": "v6_configure"}]
            ]
        }
        
        if message_id:
            self.bot.edit_message(text, message_id, keyboard, parse_mode="HTML")
        else:
            self.bot.send_message_with_keyboard(text, keyboard)
    
    def show_adjustment_menu(self, user_id: int, message_id: int, timeframe: str, param_type: str):
        """
        Show adjustment options for a parameter.
        
        Args:
            user_id: Telegram user ID
            message_id: Message ID to edit
            timeframe: Timeframe being configured
            param_type: Parameter type (lot, sl, tp)
        """
        v6_config = self._get_v6_config()
        tf_config = v6_config.get("timeframes", {}).get(timeframe, {})
        
        param_map = {
            "lot": ("lot_multiplier", "Lot Multiplier", [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]),
            "sl": ("sl_multiplier", "SL Multiplier", [0.75, 1.0, 1.25, 1.5, 2.0, 2.5]),
            "tp": ("tp_multiplier", "TP Multiplier", [0.75, 1.0, 1.25, 1.5, 2.0, 2.5])
        }
        
        config_key, title, options = param_map.get(param_type, ("lot_multiplier", "Lot", [1.0]))
        current = tf_config.get(config_key, 1.0)
        
        text = (
            f" <b>Adjust {title} for {timeframe.upper()}</b>\n"
            f"{'=' * 28}\n\n"
            f"<b>Current Value:</b> {current}x\n\n"
            f"Select a new value:"
        )
        
        # Build button grid (3 per row)
        keyboard = {"inline_keyboard": []}
        row = []
        
        for i, opt in enumerate(options):
            marker = "" if abs(opt - current) < 0.01 else ""
            row.append({
                "text": f"{marker} {opt}x",
                "callback_data": f"v6_set_{param_type}_{timeframe}_{opt}"
            })
            if len(row) == 3 or i == len(options) - 1:
                keyboard["inline_keyboard"].append(row)
                row = []
        
        keyboard["inline_keyboard"].append([
            {"text": " Back", "callback_data": f"v6_config_tf_{timeframe}"}
        ])
        
        if message_id:
            self.bot.edit_message(text, message_id, keyboard, parse_mode="HTML")
        else:
            self.bot.send_message_with_keyboard(text, keyboard)
    
    def handle_set_parameter(self, user_id: int, message_id: int, timeframe: str, param_type: str, value: float) -> bool:
        """
        Set a parameter value for a timeframe.
        
        Args:
            user_id: Telegram user ID
            message_id: Message ID to edit
            timeframe: Timeframe being configured
            param_type: Parameter type (lot, sl, tp)
            value: New value
        
        Returns:
            True if set successfully
        """
        try:
            param_map = {
                "lot": "lot_multiplier",
                "sl": "sl_multiplier",
                "tp": "tp_multiplier"
            }
            config_key = param_map.get(param_type, "lot_multiplier")
            
            if hasattr(self.bot, 'config'):
                if "plugins" not in self.bot.config:
                    self.bot.config["plugins"] = {}
                if "v6_price_action" not in self.bot.config["plugins"]:
                    self.bot.config["plugins"]["v6_price_action"] = {}
                if "timeframes" not in self.bot.config["plugins"]["v6_price_action"]:
                    self.bot.config["plugins"]["v6_price_action"]["timeframes"] = {}
                if timeframe not in self.bot.config["plugins"]["v6_price_action"]["timeframes"]:
                    self.bot.config["plugins"]["v6_price_action"]["timeframes"][timeframe] = {}
                
                self.bot.config["plugins"]["v6_price_action"]["timeframes"][timeframe][config_key] = value
                
                # Save config if method exists
                if hasattr(self.bot, 'save_config'):
                    self.bot.save_config()
            
            self.bot.send_message(f" V6 {timeframe.upper()} {param_type.upper()} set to {value}x")
            
            # Show timeframe config
            self.show_timeframe_config(user_id, message_id, timeframe)
            
            return True
        except Exception as e:
            self._logger.error(f"[V6Menu] Error setting parameter: {e}")
            return False
    
    def handle_callback(self, callback_data: str, user_id: int, message_id: int) -> bool:
        """
        Handle V6 menu callback.
        
        Args:
            callback_data: Callback data from button press
            user_id: Telegram user ID
            message_id: Message ID to edit
        
        Returns:
            True if handled, False otherwise
        """
        try:
            if callback_data == "menu_v6":
                self.show_v6_main_menu(user_id, message_id)
                return True
            
            elif callback_data == "v6_toggle_system":
                return self.handle_toggle_system(user_id, message_id)
            
            elif callback_data.startswith("v6_toggle_tf_"):
                timeframe = callback_data.replace("v6_toggle_tf_", "")
                return self.handle_toggle_timeframe(user_id, message_id, timeframe)
            
            elif callback_data == "v6_enable_all":
                return self.handle_enable_all(user_id, message_id)
            
            elif callback_data == "v6_disable_all":
                return self.handle_disable_all(user_id, message_id)
            
            elif callback_data == "v6_view_stats":
                self.show_v6_stats_menu(user_id, message_id)
                return True
            
            elif callback_data == "v6_configure":
                self.show_v6_configure_menu(user_id, message_id)
                return True
            
            elif callback_data.startswith("v6_config_tf_"):
                timeframe = callback_data.replace("v6_config_tf_", "")
                self.show_timeframe_config(user_id, message_id, timeframe)
                return True
            
            elif callback_data.startswith("v6_adj_"):
                # Format: v6_adj_{param}_{timeframe}
                parts = callback_data.replace("v6_adj_", "").split("_")
                if len(parts) >= 2:
                    param_type = parts[0]
                    timeframe = parts[1]
                    self.show_adjustment_menu(user_id, message_id, timeframe, param_type)
                    return True
            
            elif callback_data.startswith("v6_set_"):
                # Format: v6_set_{param}_{timeframe}_{value}
                parts = callback_data.replace("v6_set_", "").split("_")
                if len(parts) >= 3:
                    param_type = parts[0]
                    timeframe = parts[1]
                    value = float(parts[2])
                    return self.handle_set_parameter(user_id, message_id, timeframe, param_type, value)
            
            return False
        except Exception as e:
            self._logger.error(f"[V6Menu] Error handling callback {callback_data}: {e}")
            return False
