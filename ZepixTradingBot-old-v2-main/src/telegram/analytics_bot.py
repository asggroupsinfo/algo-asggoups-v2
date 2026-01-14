"""
Analytics Bot - Handles reports and statistics

This bot handles all analytics and reporting:
- Performance reports
- Statistics summaries
- Trade history
- Trend analysis
- Plugin performance

Version: 1.0.0
Date: 2026-01-14
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from .base_telegram_bot import BaseTelegramBot

logger = logging.getLogger(__name__)


class AnalyticsBot(BaseTelegramBot):
    """
    Analytics Bot for reports and statistics.
    
    Responsibilities:
    - Performance reports
    - Statistics summaries
    - Trade history reports
    - Trend analysis reports
    - Plugin performance reports
    - Weekly/Monthly summaries
    """
    
    def __init__(self, token: str, chat_id: str = None):
        super().__init__(token, chat_id, bot_name="AnalyticsBot")
        
        self._report_cache: Dict[str, Any] = {}
        self._last_report_time: Dict[str, datetime] = {}
        
        logger.info("[AnalyticsBot] Initialized")
    
    def send_performance_report(self, report_data: Dict) -> Optional[int]:
        """
        Send performance report
        
        Args:
            report_data: Dict with performance metrics
                - period: Report period (daily, weekly, monthly)
                - start_date: Period start
                - end_date: Period end
                - total_trades: Total trades
                - winning_trades: Winning trades
                - losing_trades: Losing trades
                - win_rate: Win rate percentage
                - total_profit: Total profit
                - total_pips: Total pips
                - avg_profit_per_trade: Average profit per trade
                - avg_pips_per_trade: Average pips per trade
                - profit_factor: Profit factor
                - max_drawdown: Maximum drawdown
                - best_day: Best day profit
                - worst_day: Worst day loss
                - by_plugin: Dict of plugin-specific stats
        
        Returns:
            Message ID if successful
        """
        message = self._format_performance_report(report_data)
        return self.send_message(message)
    
    def _format_performance_report(self, report_data: Dict) -> str:
        """Format performance report message"""
        period = report_data.get('period', 'Period')
        start_date = report_data.get('start_date', 'N/A')
        end_date = report_data.get('end_date', 'N/A')
        
        total_trades = report_data.get('total_trades', 0)
        winning = report_data.get('winning_trades', 0)
        losing = report_data.get('losing_trades', 0)
        win_rate = report_data.get('win_rate', 0)
        total_profit = report_data.get('total_profit', 0)
        
        emoji = "🟢" if total_profit >= 0 else "🔴"
        
        message = (
            f"📊 <b>PERFORMANCE REPORT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>Period:</b> {period.upper()}\n"
            f"<b>Range:</b> {start_date} → {end_date}\n\n"
            f"<b>📈 Trade Statistics</b>\n"
            f"├─ Total Trades: {total_trades}\n"
            f"├─ ✅ Winning: {winning}\n"
            f"├─ ❌ Losing: {losing}\n"
            f"└─ 📊 Win Rate: {win_rate:.1f}%\n\n"
            f"<b>💰 Financial Summary</b>\n"
            f"├─ {emoji} Total P&L: ${total_profit:+.2f}\n"
            f"├─ Total Pips: {report_data.get('total_pips', 0):+.1f}\n"
            f"├─ Avg/Trade: ${report_data.get('avg_profit_per_trade', 0):+.2f}\n"
            f"├─ Profit Factor: {report_data.get('profit_factor', 0):.2f}\n"
            f"└─ Max Drawdown: ${report_data.get('max_drawdown', 0):.2f}\n\n"
            f"<b>🏆 Highlights</b>\n"
            f"├─ Best Day: ${report_data.get('best_day', 0):+.2f}\n"
            f"└─ Worst Day: ${report_data.get('worst_day', 0):+.2f}\n"
        )
        
        by_plugin = report_data.get('by_plugin', {})
        if by_plugin:
            message += "\n<b>📦 By Plugin</b>\n"
            for plugin_name, stats in by_plugin.items():
                plugin_profit = stats.get('profit', 0)
                plugin_emoji = "🟢" if plugin_profit >= 0 else "🔴"
                message += f"├─ {plugin_name}: {plugin_emoji} ${plugin_profit:+.2f} ({stats.get('trades', 0)} trades)\n"
        
        message += f"\n<i>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        
        return message
    
    def send_statistics_summary(self, stats_data: Dict) -> Optional[int]:
        """
        Send statistics summary
        
        Args:
            stats_data: Dict with statistics
                - account_balance: Current balance
                - account_equity: Current equity
                - open_positions: Number of open positions
                - open_profit: Unrealized P&L
                - today_profit: Today's realized profit
                - today_trades: Today's trade count
                - week_profit: This week's profit
                - month_profit: This month's profit
                - all_time_profit: All-time profit
                - active_plugins: List of active plugins
        
        Returns:
            Message ID if successful
        """
        message = self._format_statistics_summary(stats_data)
        return self.send_message(message)
    
    def _format_statistics_summary(self, stats_data: Dict) -> str:
        """Format statistics summary message"""
        balance = stats_data.get('account_balance', 0)
        equity = stats_data.get('account_equity', 0)
        open_positions = stats_data.get('open_positions', 0)
        open_profit = stats_data.get('open_profit', 0)
        
        today_profit = stats_data.get('today_profit', 0)
        today_emoji = "🟢" if today_profit >= 0 else "🔴"
        
        message = (
            f"📈 <b>STATISTICS SUMMARY</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>💼 Account Status</b>\n"
            f"├─ Balance: ${balance:,.2f}\n"
            f"├─ Equity: ${equity:,.2f}\n"
            f"├─ Open Positions: {open_positions}\n"
            f"└─ Unrealized P&L: ${open_profit:+.2f}\n\n"
            f"<b>📊 Performance</b>\n"
            f"├─ {today_emoji} Today: ${today_profit:+.2f} ({stats_data.get('today_trades', 0)} trades)\n"
            f"├─ This Week: ${stats_data.get('week_profit', 0):+.2f}\n"
            f"├─ This Month: ${stats_data.get('month_profit', 0):+.2f}\n"
            f"└─ All Time: ${stats_data.get('all_time_profit', 0):+.2f}\n"
        )
        
        active_plugins = stats_data.get('active_plugins', [])
        if active_plugins:
            message += f"\n<b>📦 Active Plugins:</b> {', '.join(active_plugins)}\n"
        
        message += f"\n<i>Updated: {datetime.now().strftime('%H:%M:%S')}</i>"
        
        return message
    
    def send_trade_history(self, trades: List[Dict], page: int = 1, total_pages: int = 1) -> Optional[int]:
        """
        Send trade history report
        
        Args:
            trades: List of trade dicts
                - ticket: MT5 ticket
                - symbol: Trading symbol
                - direction: BUY/SELL
                - entry_price: Entry price
                - exit_price: Exit price
                - profit: Trade profit
                - pips: Trade pips
                - close_time: Close time
            page: Current page number
            total_pages: Total pages
        
        Returns:
            Message ID if successful
        """
        message = self._format_trade_history(trades, page, total_pages)
        return self.send_message(message)
    
    def _format_trade_history(self, trades: List[Dict], page: int, total_pages: int) -> str:
        """Format trade history message"""
        message = (
            f"📜 <b>TRADE HISTORY</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Page {page}/{total_pages}\n\n"
        )
        
        for trade in trades:
            profit = trade.get('profit', 0)
            emoji = "✅" if profit >= 0 else "❌"
            
            message += (
                f"{emoji} <b>#{trade.get('ticket', 'N/A')}</b> | {trade.get('symbol', 'N/A')}\n"
                f"   {trade.get('direction', 'N/A')} @ {trade.get('entry_price', 'N/A')} → {trade.get('exit_price', 'N/A')}\n"
                f"   P&L: ${profit:+.2f} ({trade.get('pips', 0):+.1f} pips)\n"
                f"   Closed: {trade.get('close_time', 'N/A')}\n\n"
            )
        
        if not trades:
            message += "<i>No trades found for this period.</i>\n"
        
        return message
    
    def send_trend_analysis(self, trend_data: Dict) -> Optional[int]:
        """
        Send trend analysis report
        
        Args:
            trend_data: Dict with trend analysis
                - symbol: Trading symbol
                - timeframes: Dict of timeframe trends
                - overall_bias: Overall market bias
                - strength: Trend strength (0-100)
                - recommendation: Trading recommendation
                - key_levels: Important price levels
        
        Returns:
            Message ID if successful
        """
        message = self._format_trend_analysis(trend_data)
        return self.send_message(message)
    
    def _format_trend_analysis(self, trend_data: Dict) -> str:
        """Format trend analysis message"""
        symbol = trend_data.get('symbol', 'N/A')
        overall_bias = trend_data.get('overall_bias', 'NEUTRAL')
        strength = trend_data.get('strength', 0)
        
        bias_emoji = "🟢" if overall_bias == "BULLISH" else ("🔴" if overall_bias == "BEARISH" else "⚪")
        
        message = (
            f"📊 <b>TREND ANALYSIS</b> | {symbol}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Overall Bias:</b> {bias_emoji} {overall_bias}\n"
            f"<b>Strength:</b> {strength}%\n\n"
            f"<b>📈 Timeframe Breakdown</b>\n"
        )
        
        timeframes = trend_data.get('timeframes', {})
        for tf, trend in timeframes.items():
            tf_emoji = "🟢" if trend == "BULLISH" else ("🔴" if trend == "BEARISH" else "⚪")
            message += f"├─ {tf}: {tf_emoji} {trend}\n"
        
        key_levels = trend_data.get('key_levels', {})
        if key_levels:
            message += (
                f"\n<b>🎯 Key Levels</b>\n"
                f"├─ Resistance: {key_levels.get('resistance', 'N/A')}\n"
                f"├─ Support: {key_levels.get('support', 'N/A')}\n"
                f"└─ Pivot: {key_levels.get('pivot', 'N/A')}\n"
            )
        
        recommendation = trend_data.get('recommendation', 'No recommendation')
        message += f"\n<b>💡 Recommendation:</b> {recommendation}\n"
        message += f"\n<i>Analysis Time: {datetime.now().strftime('%H:%M:%S')}</i>"
        
        return message
    
    def send_plugin_performance(self, plugin_data: Dict) -> Optional[int]:
        """
        Send plugin performance report
        
        Args:
            plugin_data: Dict with plugin performance
                - plugin_name: Plugin name
                - plugin_version: Plugin version
                - status: Active/Inactive
                - total_trades: Total trades
                - win_rate: Win rate
                - total_profit: Total profit
                - avg_trade_duration: Average trade duration
                - best_trade: Best trade
                - worst_trade: Worst trade
                - signals_processed: Signals processed
                - signals_executed: Signals executed
        
        Returns:
            Message ID if successful
        """
        message = self._format_plugin_performance(plugin_data)
        return self.send_message(message)
    
    def _format_plugin_performance(self, plugin_data: Dict) -> str:
        """Format plugin performance message"""
        plugin_name = plugin_data.get('plugin_name', 'Unknown Plugin')
        status = plugin_data.get('status', 'Unknown')
        status_emoji = "🟢" if status == "Active" else "🔴"
        
        total_profit = plugin_data.get('total_profit', 0)
        profit_emoji = "🟢" if total_profit >= 0 else "🔴"
        
        message = (
            f"📦 <b>PLUGIN PERFORMANCE</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Plugin:</b> {plugin_name}\n"
            f"<b>Version:</b> {plugin_data.get('plugin_version', 'N/A')}\n"
            f"<b>Status:</b> {status_emoji} {status}\n\n"
            f"<b>📊 Statistics</b>\n"
            f"├─ Total Trades: {plugin_data.get('total_trades', 0)}\n"
            f"├─ Win Rate: {plugin_data.get('win_rate', 0):.1f}%\n"
            f"├─ {profit_emoji} Total P&L: ${total_profit:+.2f}\n"
            f"├─ Avg Duration: {plugin_data.get('avg_trade_duration', 'N/A')}\n"
            f"├─ 🏆 Best Trade: ${plugin_data.get('best_trade', 0):+.2f}\n"
            f"└─ 📉 Worst Trade: ${plugin_data.get('worst_trade', 0):+.2f}\n\n"
            f"<b>📡 Signal Processing</b>\n"
            f"├─ Signals Received: {plugin_data.get('signals_processed', 0)}\n"
            f"└─ Signals Executed: {plugin_data.get('signals_executed', 0)}\n"
        )
        
        message += f"\n<i>Report Time: {datetime.now().strftime('%H:%M:%S')}</i>"
        
        return message
    
    def send_weekly_summary(self, summary_data: Dict) -> Optional[int]:
        """
        Send weekly summary report
        
        Args:
            summary_data: Dict with weekly summary
                - week_number: Week number
                - start_date: Week start
                - end_date: Week end
                - total_trades: Total trades
                - win_rate: Win rate
                - total_profit: Total profit
                - best_day: Best day
                - worst_day: Worst day
                - by_day: Dict of daily stats
        
        Returns:
            Message ID if successful
        """
        week_num = summary_data.get('week_number', 0)
        start_date = summary_data.get('start_date', 'N/A')
        end_date = summary_data.get('end_date', 'N/A')
        total_profit = summary_data.get('total_profit', 0)
        
        emoji = "🟢" if total_profit >= 0 else "🔴"
        
        message = (
            f"📅 <b>WEEKLY SUMMARY</b> | Week {week_num}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>Period:</b> {start_date} → {end_date}\n\n"
            f"<b>📊 Overview</b>\n"
            f"├─ Total Trades: {summary_data.get('total_trades', 0)}\n"
            f"├─ Win Rate: {summary_data.get('win_rate', 0):.1f}%\n"
            f"├─ {emoji} Total P&L: ${total_profit:+.2f}\n"
            f"├─ 🏆 Best Day: ${summary_data.get('best_day', 0):+.2f}\n"
            f"└─ 📉 Worst Day: ${summary_data.get('worst_day', 0):+.2f}\n\n"
            f"<b>📆 Daily Breakdown</b>\n"
        )
        
        by_day = summary_data.get('by_day', {})
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        for day in days:
            day_stats = by_day.get(day, {})
            day_profit = day_stats.get('profit', 0)
            day_emoji = "🟢" if day_profit >= 0 else "🔴"
            trades = day_stats.get('trades', 0)
            message += f"├─ {day[:3]}: {day_emoji} ${day_profit:+.2f} ({trades} trades)\n"
        
        message += f"\n<i>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        
        return self.send_message(message)
