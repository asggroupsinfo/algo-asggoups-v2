"""
Analytics Menu Handler - Telegram V5 Upgrade

This module provides the Analytics Menu Handler for displaying trading performance
analytics via Telegram menu interface.

Features:
- Daily/Weekly/Monthly performance views
- Performance by trading pair
- Performance by logic/plugin
- Export functionality

Version: 1.0.0
Date: 2026-01-19
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


class AnalyticsMenuHandler:
    """
    Analytics Menu Handler for displaying trading performance analytics.
    
    Provides:
    - Daily/Weekly/Monthly performance summaries
    - Performance breakdown by trading pair
    - Performance breakdown by logic/plugin
    - Export functionality for analytics data
    """
    
    def __init__(self, telegram_bot, config: Dict[str, Any] = None):
        """
        Initialize AnalyticsMenuHandler.
        
        Args:
            telegram_bot: Telegram bot instance
            config: Bot configuration dictionary
        """
        self._bot = telegram_bot
        self._config = config or {}
        logger.info("[AnalyticsMenuHandler] Initialized")
    
    def set_config(self, config: Dict[str, Any]):
        """Update configuration reference"""
        self._config = config
    
    def _get_analytics_data(self) -> Dict[str, Any]:
        """
        Get analytics data from database or config.
        
        Returns:
            Dictionary with analytics data
        """
        # Try to get from ServiceAPI if available
        if hasattr(self._bot, 'service_api') and self._bot.service_api:
            try:
                return self._bot.service_api.get_analytics_summary()
            except Exception as e:
                logger.warning(f"[AnalyticsMenuHandler] Could not get analytics from ServiceAPI: {e}")
        
        # Fallback to config-based data
        return self._config.get("analytics", {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "total_pnl": 0.0,
            "win_rate": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "best_trade": 0.0,
            "worst_trade": 0.0,
            "by_pair": {},
            "by_logic": {},
            "daily": [],
            "weekly": [],
            "monthly": []
        })
    
    def _send_message(self, text: str, reply_markup: Dict = None, message_id: int = None):
        """Send or edit message"""
        try:
            if message_id and hasattr(self._bot, 'edit_message'):
                self._bot.edit_message(text, message_id, reply_markup)
            elif hasattr(self._bot, 'send_message_with_keyboard') and reply_markup:
                self._bot.send_message_with_keyboard(text, reply_markup)
            elif hasattr(self._bot, 'send_message'):
                self._bot.send_message(text)
            else:
                logger.warning("[AnalyticsMenuHandler] No send method available")
        except Exception as e:
            logger.error(f"[AnalyticsMenuHandler] Error sending message: {e}")
    
    # =========================================================================
    # MAIN ANALYTICS MENU
    # =========================================================================
    
    def show_analytics_menu(self, user_id: int, message_id: int = None):
        """
        Show main analytics menu.
        
        Args:
            user_id: Telegram user ID
            message_id: Message ID to edit (optional)
        """
        logger.info(f"[AnalyticsMenuHandler] Showing analytics menu for user {user_id}")
        
        # Get summary data
        data = self._get_analytics_data()
        total_trades = data.get("total_trades", 0)
        win_rate = data.get("win_rate", 0)
        total_pnl = data.get("total_pnl", 0)
        
        # Build menu text
        text = f"""📈 <b>ANALYTICS DASHBOARD</b>
━━━━━━━━━━━━━━━━━━━━━━━━

📊 <b>Quick Summary:</b>
  • Total Trades: {total_trades}
  • Win Rate: {win_rate:.1f}%
  • Total P&L: ${total_pnl:.2f}

━━━━━━━━━━━━━━━━━━━━━━━━
<i>Select a view below:</i>"""
        
        # Build keyboard
        keyboard = [
            # Time-based views
            [
                {"text": "📅 Daily", "callback_data": "analytics_daily"},
                {"text": "📆 Weekly", "callback_data": "analytics_weekly"},
                {"text": "🗓️ Monthly", "callback_data": "analytics_monthly"}
            ],
            # Breakdown views
            [
                {"text": "💱 By Pair", "callback_data": "analytics_by_pair"},
                {"text": "🧠 By Logic", "callback_data": "analytics_by_logic"}
            ],
            # Export and refresh
            [
                {"text": "📤 Export", "callback_data": "analytics_export"},
                {"text": "🔄 Refresh", "callback_data": "menu_analytics"}
            ],
            # Navigation
            [
                {"text": "🏠 Main Menu", "callback_data": "menu_main"}
            ]
        ]
        
        reply_markup = {"inline_keyboard": keyboard}
        self._send_message(text, reply_markup, message_id)
    
    # =========================================================================
    # TIME-BASED VIEWS
    # =========================================================================
    
    def show_daily_analytics(self, user_id: int, message_id: int = None):
        """Show daily analytics view"""
        logger.info(f"[AnalyticsMenuHandler] Showing daily analytics for user {user_id}")
        
        data = self._get_analytics_data()
        daily_data = data.get("daily", [])
        
        # Get today's data or generate placeholder
        today = datetime.now().strftime("%Y-%m-%d")
        today_data = next((d for d in daily_data if d.get("date") == today), {
            "date": today,
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "pnl": 0.0,
            "win_rate": 0.0
        })
        
        trades = today_data.get("trades", 0)
        wins = today_data.get("wins", 0)
        losses = today_data.get("losses", 0)
        pnl = today_data.get("pnl", 0)
        win_rate = today_data.get("win_rate", 0)
        
        text = f"""📅 <b>DAILY ANALYTICS</b>
━━━━━━━━━━━━━━━━━━━━━━━━

📆 <b>Date:</b> {today}

📊 <b>Performance:</b>
  • Total Trades: {trades}
  • Wins: {wins} ✅
  • Losses: {losses} ❌
  • Win Rate: {win_rate:.1f}%
  • P&L: ${pnl:.2f}

━━━━━━━━━━━━━━━━━━━━━━━━

📈 <b>Recent Days:</b>"""
        
        # Add last 5 days summary
        for day_data in daily_data[-5:]:
            date = day_data.get("date", "N/A")
            day_pnl = day_data.get("pnl", 0)
            day_trades = day_data.get("trades", 0)
            emoji = "🟢" if day_pnl >= 0 else "🔴"
            text += f"\n  {emoji} {date}: ${day_pnl:.2f} ({day_trades} trades)"
        
        if not daily_data:
            text += "\n  <i>No historical data available</i>"
        
        keyboard = [
            [
                {"text": "◀️ Previous Day", "callback_data": "analytics_daily_prev"},
                {"text": "Next Day ▶️", "callback_data": "analytics_daily_next"}
            ],
            [
                {"text": "📈 Analytics Menu", "callback_data": "menu_analytics"},
                {"text": "🏠 Main Menu", "callback_data": "menu_main"}
            ]
        ]
        
        reply_markup = {"inline_keyboard": keyboard}
        self._send_message(text, reply_markup, message_id)
    
    def show_weekly_analytics(self, user_id: int, message_id: int = None):
        """Show weekly analytics view"""
        logger.info(f"[AnalyticsMenuHandler] Showing weekly analytics for user {user_id}")
        
        data = self._get_analytics_data()
        weekly_data = data.get("weekly", [])
        
        # Get current week data or generate placeholder
        today = datetime.now()
        week_start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        week_end = (today + timedelta(days=6-today.weekday())).strftime("%Y-%m-%d")
        
        current_week = next((w for w in weekly_data if w.get("week_start") == week_start), {
            "week_start": week_start,
            "week_end": week_end,
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "pnl": 0.0,
            "win_rate": 0.0
        })
        
        trades = current_week.get("trades", 0)
        wins = current_week.get("wins", 0)
        losses = current_week.get("losses", 0)
        pnl = current_week.get("pnl", 0)
        win_rate = current_week.get("win_rate", 0)
        
        text = f"""📆 <b>WEEKLY ANALYTICS</b>
━━━━━━━━━━━━━━━━━━━━━━━━

📅 <b>Week:</b> {week_start} to {week_end}

📊 <b>Performance:</b>
  • Total Trades: {trades}
  • Wins: {wins} ✅
  • Losses: {losses} ❌
  • Win Rate: {win_rate:.1f}%
  • P&L: ${pnl:.2f}

━━━━━━━━━━━━━━━━━━━━━━━━

📈 <b>Recent Weeks:</b>"""
        
        # Add last 4 weeks summary
        for week_data in weekly_data[-4:]:
            w_start = week_data.get("week_start", "N/A")
            w_pnl = week_data.get("pnl", 0)
            w_trades = week_data.get("trades", 0)
            emoji = "🟢" if w_pnl >= 0 else "🔴"
            text += f"\n  {emoji} {w_start}: ${w_pnl:.2f} ({w_trades} trades)"
        
        if not weekly_data:
            text += "\n  <i>No historical data available</i>"
        
        keyboard = [
            [
                {"text": "◀️ Previous Week", "callback_data": "analytics_weekly_prev"},
                {"text": "Next Week ▶️", "callback_data": "analytics_weekly_next"}
            ],
            [
                {"text": "📈 Analytics Menu", "callback_data": "menu_analytics"},
                {"text": "🏠 Main Menu", "callback_data": "menu_main"}
            ]
        ]
        
        reply_markup = {"inline_keyboard": keyboard}
        self._send_message(text, reply_markup, message_id)
    
    def show_monthly_analytics(self, user_id: int, message_id: int = None):
        """Show monthly analytics view"""
        logger.info(f"[AnalyticsMenuHandler] Showing monthly analytics for user {user_id}")
        
        data = self._get_analytics_data()
        monthly_data = data.get("monthly", [])
        
        # Get current month data or generate placeholder
        today = datetime.now()
        month_str = today.strftime("%Y-%m")
        
        current_month = next((m for m in monthly_data if m.get("month") == month_str), {
            "month": month_str,
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "pnl": 0.0,
            "win_rate": 0.0
        })
        
        trades = current_month.get("trades", 0)
        wins = current_month.get("wins", 0)
        losses = current_month.get("losses", 0)
        pnl = current_month.get("pnl", 0)
        win_rate = current_month.get("win_rate", 0)
        
        text = f"""🗓️ <b>MONTHLY ANALYTICS</b>
━━━━━━━━━━━━━━━━━━━━━━━━

📅 <b>Month:</b> {today.strftime("%B %Y")}

📊 <b>Performance:</b>
  • Total Trades: {trades}
  • Wins: {wins} ✅
  • Losses: {losses} ❌
  • Win Rate: {win_rate:.1f}%
  • P&L: ${pnl:.2f}

━━━━━━━━━━━━━━━━━━━━━━━━

📈 <b>Recent Months:</b>"""
        
        # Add last 6 months summary
        for month_data in monthly_data[-6:]:
            m_str = month_data.get("month", "N/A")
            m_pnl = month_data.get("pnl", 0)
            m_trades = month_data.get("trades", 0)
            emoji = "🟢" if m_pnl >= 0 else "🔴"
            text += f"\n  {emoji} {m_str}: ${m_pnl:.2f} ({m_trades} trades)"
        
        if not monthly_data:
            text += "\n  <i>No historical data available</i>"
        
        keyboard = [
            [
                {"text": "◀️ Previous Month", "callback_data": "analytics_monthly_prev"},
                {"text": "Next Month ▶️", "callback_data": "analytics_monthly_next"}
            ],
            [
                {"text": "📈 Analytics Menu", "callback_data": "menu_analytics"},
                {"text": "🏠 Main Menu", "callback_data": "menu_main"}
            ]
        ]
        
        reply_markup = {"inline_keyboard": keyboard}
        self._send_message(text, reply_markup, message_id)
    
    # =========================================================================
    # BREAKDOWN VIEWS
    # =========================================================================
    
    def show_analytics_by_pair(self, user_id: int, message_id: int = None):
        """Show analytics breakdown by trading pair"""
        logger.info(f"[AnalyticsMenuHandler] Showing analytics by pair for user {user_id}")
        
        data = self._get_analytics_data()
        by_pair = data.get("by_pair", {})
        
        text = """💱 <b>ANALYTICS BY PAIR</b>
━━━━━━━━━━━━━━━━━━━━━━━━

📊 <b>Performance by Symbol:</b>
"""
        
        if by_pair:
            # Sort by P&L descending
            sorted_pairs = sorted(by_pair.items(), key=lambda x: x[1].get("pnl", 0), reverse=True)
            
            for pair, pair_data in sorted_pairs[:10]:  # Top 10 pairs
                trades = pair_data.get("trades", 0)
                pnl = pair_data.get("pnl", 0)
                win_rate = pair_data.get("win_rate", 0)
                emoji = "🟢" if pnl >= 0 else "🔴"
                text += f"\n{emoji} <b>{pair}</b>"
                text += f"\n   {trades} trades | {win_rate:.1f}% WR | ${pnl:.2f}"
        else:
            text += "\n<i>No pair data available</i>"
        
        text += "\n\n━━━━━━━━━━━━━━━━━━━━━━━━"
        
        keyboard = [
            [
                {"text": "📈 Analytics Menu", "callback_data": "menu_analytics"},
                {"text": "🏠 Main Menu", "callback_data": "menu_main"}
            ]
        ]
        
        reply_markup = {"inline_keyboard": keyboard}
        self._send_message(text, reply_markup, message_id)
    
    def show_analytics_by_logic(self, user_id: int, message_id: int = None):
        """Show analytics breakdown by logic/plugin"""
        logger.info(f"[AnalyticsMenuHandler] Showing analytics by logic for user {user_id}")
        
        data = self._get_analytics_data()
        by_logic = data.get("by_logic", {})
        
        text = """🧠 <b>ANALYTICS BY LOGIC</b>
━━━━━━━━━━━━━━━━━━━━━━━━

📊 <b>Performance by Strategy:</b>
"""
        
        if by_logic:
            # Sort by P&L descending
            sorted_logics = sorted(by_logic.items(), key=lambda x: x[1].get("pnl", 0), reverse=True)
            
            for logic, logic_data in sorted_logics:
                trades = logic_data.get("trades", 0)
                pnl = logic_data.get("pnl", 0)
                win_rate = logic_data.get("win_rate", 0)
                emoji = "🟢" if pnl >= 0 else "🔴"
                text += f"\n{emoji} <b>{logic}</b>"
                text += f"\n   {trades} trades | {win_rate:.1f}% WR | ${pnl:.2f}"
        else:
            # Show default logics with placeholder data
            default_logics = [
                ("V3 Logic 1 (5m)", "v3_logic1"),
                ("V3 Logic 2 (15m)", "v3_logic2"),
                ("V3 Logic 3 (1h)", "v3_logic3"),
                ("V6 15M", "v6_15m"),
                ("V6 30M", "v6_30m"),
                ("V6 1H", "v6_1h"),
                ("V6 4H", "v6_4h")
            ]
            
            for name, _ in default_logics:
                text += f"\n⚪ <b>{name}</b>"
                text += f"\n   0 trades | 0.0% WR | $0.00"
        
        text += "\n\n━━━━━━━━━━━━━━━━━━━━━━━━"
        
        keyboard = [
            [
                {"text": "📈 Analytics Menu", "callback_data": "menu_analytics"},
                {"text": "🏠 Main Menu", "callback_data": "menu_main"}
            ]
        ]
        
        reply_markup = {"inline_keyboard": keyboard}
        self._send_message(text, reply_markup, message_id)
    
    # =========================================================================
    # EXPORT FUNCTIONALITY
    # =========================================================================
    
    def export_analytics(self, user_id: int, message_id: int = None):
        """Export analytics data"""
        logger.info(f"[AnalyticsMenuHandler] Exporting analytics for user {user_id}")
        
        text = """📤 <b>EXPORT ANALYTICS</b>
━━━━━━━━━━━━━━━━━━━━━━━━

Select export format:
"""
        
        keyboard = [
            [
                {"text": "📊 CSV", "callback_data": "analytics_export_csv"},
                {"text": "📋 JSON", "callback_data": "analytics_export_json"}
            ],
            [
                {"text": "📄 PDF Report", "callback_data": "analytics_export_pdf"},
                {"text": "📧 Email", "callback_data": "analytics_export_email"}
            ],
            [
                {"text": "📈 Analytics Menu", "callback_data": "menu_analytics"},
                {"text": "🏠 Main Menu", "callback_data": "menu_main"}
            ]
        ]
        
        reply_markup = {"inline_keyboard": keyboard}
        self._send_message(text, reply_markup, message_id)
    
    def handle_export_csv(self, user_id: int, message_id: int = None):
        """Handle CSV export"""
        logger.info(f"[AnalyticsMenuHandler] Exporting CSV for user {user_id}")
        
        # Generate CSV data
        data = self._get_analytics_data()
        
        # Create CSV content
        csv_lines = ["Date,Trades,Wins,Losses,Win Rate,P&L"]
        for day in data.get("daily", []):
            csv_lines.append(f"{day.get('date')},{day.get('trades')},{day.get('wins')},{day.get('losses')},{day.get('win_rate')},{day.get('pnl')}")
        
        csv_content = "\n".join(csv_lines)
        
        text = f"""✅ <b>CSV Export Ready</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<code>{csv_content[:500]}{'...' if len(csv_content) > 500 else ''}</code>

<i>Copy the data above or use the file export option.</i>"""
        
        keyboard = [
            [
                {"text": "📈 Analytics Menu", "callback_data": "menu_analytics"},
                {"text": "🏠 Main Menu", "callback_data": "menu_main"}
            ]
        ]
        
        reply_markup = {"inline_keyboard": keyboard}
        self._send_message(text, reply_markup, message_id)
    
    # =========================================================================
    # CALLBACK HANDLER
    # =========================================================================
    
    def handle_callback(self, callback_data: str, user_id: int, message_id: int = None) -> bool:
        """
        Handle analytics menu callback.
        
        Args:
            callback_data: Callback data from button press
            user_id: Telegram user ID
            message_id: Message ID to edit
        
        Returns:
            True if handled, False otherwise
        """
        logger.info(f"[AnalyticsMenuHandler] Handling callback: {callback_data}")
        
        handlers = {
            "menu_analytics": lambda: self.show_analytics_menu(user_id, message_id),
            "analytics_daily": lambda: self.show_daily_analytics(user_id, message_id),
            "analytics_weekly": lambda: self.show_weekly_analytics(user_id, message_id),
            "analytics_monthly": lambda: self.show_monthly_analytics(user_id, message_id),
            "analytics_by_pair": lambda: self.show_analytics_by_pair(user_id, message_id),
            "analytics_by_logic": lambda: self.show_analytics_by_logic(user_id, message_id),
            "analytics_export": lambda: self.export_analytics(user_id, message_id),
            "analytics_export_csv": lambda: self.handle_export_csv(user_id, message_id),
        }
        
        handler = handlers.get(callback_data)
        if handler:
            handler()
            return True
        
        return False
    
    # =========================================================================
    # HANDLER REGISTRATION
    # =========================================================================
    
    def get_callback_handlers(self) -> Dict[str, callable]:
        """Get all callback handlers for registration"""
        return {
            "menu_analytics": self.show_analytics_menu,
            "analytics_daily": self.show_daily_analytics,
            "analytics_weekly": self.show_weekly_analytics,
            "analytics_monthly": self.show_monthly_analytics,
            "analytics_by_pair": self.show_analytics_by_pair,
            "analytics_by_logic": self.show_analytics_by_logic,
            "analytics_export": self.export_analytics,
            "analytics_export_csv": self.handle_export_csv,
        }
