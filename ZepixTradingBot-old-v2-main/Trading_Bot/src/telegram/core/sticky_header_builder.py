"""
Sticky Header Builder - Fixed Header System

Generates standard headers for all bot messages with:
- Clock (GMT)
- Session Status
- Live Prices
- Bot Status

Version: 1.0.0
Created: 2026-01-21
Part of: TELEGRAM_V5_STICKY_HEADER
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class StickyHeaderBuilder:
    """Sticky header builder for all bot messages"""

    def __init__(self, mt5_client=None, trading_engine=None):
        self.mt5_client = mt5_client
        self.trading_engine = trading_engine

        # Session Config
        self.TRADING_SESSIONS = {
            'SYDNEY': {'start': '22:00', 'end': '07:00'}, # GMT
            'TOKYO': {'start': '00:00', 'end': '09:00'},
            'LONDON': {'start': '08:00', 'end': '17:00'},
            'NEW YORK': {'start': '13:00', 'end': '22:00'}
        }

        self.DEFAULT_SYMBOLS = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']

    def set_dependencies(self, mt5_client, trading_engine):
        """Inject dependencies"""
        self.mt5_client = mt5_client
        self.trading_engine = trading_engine

    async def build_header(self, style: str = 'full', custom_symbols: Optional[List[str]] = None) -> str:
        """
        Build header based on style.

        Args:
            style: 'full', 'compact', or 'minimal'
            custom_symbols: Custom symbol list (None = use default)

        Returns:
            Formatted header string
        """
        if style == 'full':
            return await self._build_full_header(custom_symbols)
        elif style == 'compact':
            return await self._build_compact_header(custom_symbols)
        else:
            return await self._build_minimal_header()

    async def _build_full_header(self, symbols=None):
        """Build full header"""
        status_text = self._get_bot_status()
        time_text = self._get_current_time_display()
        session_text = self._get_current_session_display()
        symbols_text = await self._get_formatted_prices(symbols or self.DEFAULT_SYMBOLS)

        header = f"""╔══════════════════════════════════════╗
║   🤖 ZEPIX TRADING BOT V5.0          ║
╠══════════════════════════════════════╣
║  📊 Status: {status_text:<23}║
║  {time_text:<35}║
║  📈 Session: {session_text:<23}║
║  💱 {symbols_text:<33}║
╚══════════════════════════════════════╝
"""
        return header

    async def _build_compact_header(self, symbols=None):
        """Build compact header"""
        status_text = self._get_bot_status().split()[0] # Short status
        time_text = datetime.utcnow().strftime("%H:%M")
        session_text = self._get_current_session_display().split('(')[0].strip()
        symbols_text = await self._get_formatted_prices(symbols or self.DEFAULT_SYMBOLS, compact=True)

        header = f"""🤖 {status_text} | 🕐 {time_text} | 📈 {session_text}
💱 {symbols_text}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return header

    async def _build_minimal_header(self):
        """Build minimal header"""
        status_text = self._get_bot_status().split()[0]
        time_text = datetime.utcnow().strftime("%H:%M")
        return f"🤖 {status_text} | 🕐 {time_text} GMT\n"

    def _get_current_time_display(self) -> str:
        """Get formatted current time"""
        time_str = datetime.utcnow().strftime("%H:%M:%S")
        return f"🕐 Time: {time_str} GMT"

    def _get_current_session_display(self) -> str:
        """Get active trading session(s)"""
        current_time = datetime.utcnow().time()
        active_sessions = []

        for session_name, details in self.TRADING_SESSIONS.items():
            start = datetime.strptime(details['start'], '%H:%M').time()
            end = datetime.strptime(details['end'], '%H:%M').time()

            # Handle overnight sessions (e.g. Sydney 22:00 - 07:00)
            if start > end:
                if current_time >= start or current_time < end:
                    active_sessions.append(session_name)
            else:
                if start <= current_time < end:
                    active_sessions.append(session_name)

        if not active_sessions:
            return "After Hours ⛔"
        elif len(active_sessions) == 1:
            return f"{active_sessions[0]} (Active)"
        else:
            return f"{'+'.join(active_sessions)} (Overlap)"

    def _get_bot_status(self) -> str:
        """Get bot status string"""
        if not self.mt5_client or not self.mt5_client.initialized:
             # In simulation mode mt5_client might be initialized but MT5_AVAILABLE false
             # Assuming checking initialized is enough
             if not self.mt5_client:
                 return "ERROR ❌"

        if self.trading_engine and self.trading_engine.is_paused:
            return "PAUSED ⏸️"

        return "ACTIVE ✅"

    async def _get_formatted_prices(self, symbols: List[str], compact: bool = False) -> str:
        """Get and format live prices"""
        if not self.mt5_client:
            return "Prices Unavailable"

        prices = []
        for sym in symbols:
            price = self.mt5_client.get_current_price(sym)
            if price:
                # Format: remove 'USD', 'JPY' for compact display
                if compact:
                    short_sym = sym.replace('USD', '').replace('JPY', '')
                    if not short_sym: short_sym = sym[:3]
                    fmt_price = f"{price:.2f}" if 'JPY' in sym or 'XAU' in sym else f"{price:.4f}"
                    prices.append(f"{short_sym}:{fmt_price}")
                else:
                    fmt_price = f"{price:.2f}" if 'JPY' in sym or 'XAU' in sym else f"{price:.4f}"
                    prices.append(f"{sym}: {fmt_price}")

        if not prices:
            return "No Data"

        if compact:
            return " ".join(prices[:3]) # Limit for compact

        # Split for full header if too long
        full_str = " | ".join(prices)
        if len(full_str) > 33:
             # Just take first 2
             return " | ".join(prices[:2])
        return full_str
