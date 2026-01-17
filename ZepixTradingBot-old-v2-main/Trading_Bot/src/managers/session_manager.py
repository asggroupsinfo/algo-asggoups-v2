"""
Session Manager - Tracks trading sessions from entry to exit
"""

import uuid
import logging
from datetime import datetime, time
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages trading sessions - from entry signal to complete exit"""
    
    # Session time definitions (IST - Asia/Kolkata timezone)
    SESSIONS = {
        'asian': {'start': time(5, 30), 'end': time(14, 30), 'name': 'Asian'},
        'london': {'start': time(13, 0), 'end': time(22, 0), 'name': 'London'},
        'overlap': {'start': time(18, 0), 'end': time(20, 30), 'name': 'Overlap'},
        'dead_zone': {'start': time(2, 0), 'end': time(5, 30), 'name': 'Dead Zone'}
    }
    
    def __init__(self, config, db, mt5_client):
        self.config = config
        self.db = db
        self.mt5_client = mt5_client
        self.active_session_id: Optional[str] = None
        
        # Session configuration
        session_config = config.get("session_manager", {})
        self.master_switch = session_config.get("master_switch", True)
        self.timezone = session_config.get("timezone", "Asia/Kolkata")
        self.allowed_symbols = session_config.get("allowed_symbols", ["XAUUSD", "USDJPY", "AUDUSD", "EURJPY"])
        self.advance_alert_enabled = session_config.get("advance_alert_enabled", True)
        self.force_close_enabled = session_config.get("force_close_enabled", False)
        
        # Try to recover active session on startup
        active = self.db.get_active_session()
        if active:
            self.active_session_id = active.get('session_id')
            logger.info(f"Recovered active session: {self.active_session_id}")
    
    def create_session(self, symbol: str, direction: str, signal: str, logic: str = "combinedlogic-1") -> str:
        """
        Create new trading session
        
        Args:
            symbol: Trading symbol (e.g. XAUUSD)
            direction: buy or sell
            signal: Entry signal name (e.g. BEARISH, BULLISH)
            logic: Trading logic type (combinedlogic-1, combinedlogic-2, combinedlogic-3) - Phase 6 tracking
            
        Returns:
            session_id
        """
        try:
            # Check if session already active
            if self.active_session_id:
                logger.warning(f"Session already active: {self.active_session_id}")
                return self.active_session_id
            
            # Generate unique session ID
            session_id = f"SES_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
            
            # Create session in database
            self.db.create_session(session_id, symbol, direction, signal)
            
            # Store logic-specific metadata (Phase 6)
            import json
            metadata = {
                "logic_type": logic,
                "logic_stats": {
                    logic: {
                        "trades": 0,
                        "wins": 0,
                        "losses": 0,
                        "pnl": 0.0,
                        "avg_lot_multiplier": 0.0,
                        "avg_sl_multiplier": 0.0
                    }
                }
            }
            cursor = self.db.conn.cursor()
            cursor.execute(
                "UPDATE trading_sessions SET metadata = ? WHERE session_id = ?",
                (json.dumps(metadata), session_id)
            )
            self.db.conn.commit()
            
            self.active_session_id = session_id
            
            logger.info(
                f"📊 SESSION STARTED: {session_id}\n"
                f"   Symbol: {symbol}\n"
                f"   Direction: {direction}\n"
                f"   Signal: {signal}\n"
                f"   Logic: {logic}"
            )
            
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            return None
    
    def close_session(self, reason: str = "COMPLETE_EXIT"):
        """
        Close active session
        
        Args:
            reason: Exit reason (REVERSAL, EXIT_SIGNAL, LOSS_LIMIT, MANUAL, etc.)
        """
        try:
            if not self.active_session_id:
                logger.warning("No active session to close")
                return
            
            # Update final stats
            self.db.update_session_stats(self.active_session_id)
            
            # Close session
            self.db.close_session(self.active_session_id, reason)
            
            # Get final stats for logging
            details = self.db.get_session_details(self.active_session_id)
            
            logger.info(
                f"🏁 SESSION CLOSED: {self.active_session_id}\n"
                f"   Exit Reason: {reason}\n"
                f"   Total PnL: ${details.get('total_pnl', 0):.2f}\n"
                f"   Win Rate: {details.get('breakdown', {}).get('win_rate', 0):.1f}%"
            )
            
            self.active_session_id = None
            return details
            
        except Exception as e:
            logger.error(f"Error closing session: {str(e)}")
            return None
    
    def get_active_session(self) -> Optional[str]:
        """Get current active session ID"""
        return self.active_session_id
    
    def get_current_session(self) -> str:
        """
        Get the current trading session based on time.
        
        Returns:
            Session name: 'asian', 'london', 'overlap', 'dead_zone', or 'off_hours'
        """
        now = datetime.now().time()
        
        for session_name, session_times in self.SESSIONS.items():
            start = session_times['start']
            end = session_times['end']
            
            # Handle sessions that don't cross midnight
            if start <= end:
                if start <= now <= end:
                    return session_name
            else:
                # Handle sessions that cross midnight
                if now >= start or now <= end:
                    return session_name
        
        return 'off_hours'
    
    def is_symbol_allowed(self, symbol: str) -> bool:
        """
        Check if a symbol is allowed for trading in current session.
        
        Args:
            symbol: Trading symbol (e.g., 'XAUUSD')
            
        Returns:
            True if symbol is allowed, False otherwise
        """
        if not self.master_switch:
            return False
        
        current_session = self.get_current_session()
        if current_session == 'dead_zone':
            return False
        
        return symbol in self.allowed_symbols
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get current session information.
        
        Returns:
            Dict with session details
        """
        current_session = self.get_current_session()
        session_data = self.SESSIONS.get(current_session, {})
        
        return {
            'current_session': current_session,
            'session_name': session_data.get('name', 'Off Hours'),
            'master_switch': self.master_switch,
            'timezone': self.timezone,
            'allowed_symbols': self.allowed_symbols,
            'advance_alert_enabled': self.advance_alert_enabled,
            'force_close_enabled': self.force_close_enabled,
            'active_session_id': self.active_session_id
        }
    
    def check_advance_alerts(self) -> Optional[str]:
        """
        Check if advance alert should be sent for upcoming session.
        
        Returns:
            Alert message if alert should be sent, None otherwise
        """
        if not self.advance_alert_enabled:
            return None
        
        now = datetime.now().time()
        
        # Check if we're 15 minutes before any session start
        for session_name, session_times in self.SESSIONS.items():
            start = session_times['start']
            
            # Calculate 15 minutes before start
            start_minutes = start.hour * 60 + start.minute
            alert_minutes = start_minutes - 15
            if alert_minutes < 0:
                alert_minutes += 24 * 60
            
            now_minutes = now.hour * 60 + now.minute
            
            # Check if we're within the alert window (15 min before)
            if abs(now_minutes - alert_minutes) <= 1:
                return f"Session Alert: {session_times['name']} session starting in 15 minutes"
        
        return None
    
    def update_session(self):
        """Update session stats (call after trades close)"""
        if self.active_session_id:
            self.db.update_session_stats(self.active_session_id)
            
    def update_logic_stats(self, trade):
        """
        Update logic-specific statistics in session metadata
        
        Args:
            trade: Trade object with logic_type and outcome
        """
        if not self.active_session_id:
            return
        
        try:
            import json
            
            # Get current session
            cursor = self.db.conn.cursor()
            cursor.execute(
                "SELECT metadata FROM trading_sessions WHERE session_id = ?",
                (self.active_session_id,)
            )
            result = cursor.fetchone()
            
            if not result or not result[0]:
                return
            
            metadata = json.loads(result[0])
            logic_stats = metadata.get("logic_stats", {})
            logic_type = getattr(trade, 'logic_type', getattr(trade, 'strategy', 'combinedlogic-1'))
            
            # Initialize logic stats if not exists
            if logic_type not in logic_stats:
                logic_stats[logic_type] = {
                    "trades": 0,
                    "wins": 0,
                    "losses": 0,
                    "pnl": 0.0,
                    "avg_lot_multiplier": 0.0,
                    "avg_sl_multiplier": 0.0
                }
            
            stats = logic_stats[logic_type]
            
            # Update stats
            stats["trades"] += 1
            stats["pnl"] += getattr(trade, 'pnl', 0.0) or 0.0
            
            if getattr(trade, 'pnl', 0) > 0:
                stats["wins"] += 1
            else:
                stats["losses"] += 1
            
            # Update multiplier averages
            lot_mult = getattr(trade, 'lot_multiplier', 1.0)
            sl_mult = getattr(trade, 'sl_multiplier', 1.0)
            
            # Calculate running average
            n = stats["trades"]
            stats["avg_lot_multiplier"] = ((stats["avg_lot_multiplier"] * (n-1)) + lot_mult) / n
            stats["avg_sl_multiplier"] = ((stats["avg_sl_multiplier"] * (n-1)) + sl_mult) / n
            
            # Save updated metadata
            metadata["logic_stats"] = logic_stats
            cursor.execute(
                "UPDATE trading_sessions SET metadata = ? WHERE session_id = ?",
                (json.dumps(metadata), self.active_session_id)
            )
            self.db.conn.commit()
            
            logger.info(
                f"📈 Logic Stats Updated: {logic_type}\n"
                f"   Trades: {stats['trades']} | Wins: {stats['wins']} | Losses: {stats['losses']}\n"
                f"   PnL: ${stats['pnl']:.2f} | Avg Lot Mult: {stats['avg_lot_multiplier']:.2f}x"
            )
            
        except Exception as e:
            logger.error(f"Error updating logic stats: {str(e)}")
    
    def check_session_end(self, open_trades: list):
        """
        Check if session should end (all positions closed)
        
        Args:
            open_trades: List of currently open trades
        """
        if not self.active_session_id:
            return
        
        # Get session
        session = self.db.get_active_session(self.active_session_id)
        if not session:
            return
        
        # Check if any trades for this session are still open
        session_has_open_trades = any(
            t.session_id == self.active_session_id and t.status == 'open'
            for t in open_trades
        )
        
        if not session_has_open_trades:
            total_trades = session.get('total_trades', 0)
            if total_trades > 0:  # Only close if trades were actually made
                logger.info(f"All positions closed for session {self.active_session_id}")
                return self.close_session("AUTO_COMPLETE")
            return None
    
    def get_today_sessions(self) -> List[Dict[str, Any]]:
        """Get all sessions for today"""
        from datetime import date
        return self.db.get_sessions_by_date(date.today())
    
    def get_session_report(self, session_id: str) -> Dict[str, Any]:
        """Get detailed session report"""
        return self.db.get_session_details(session_id)
