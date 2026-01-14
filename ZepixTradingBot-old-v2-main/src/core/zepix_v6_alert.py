"""
Zepix V6 Alert Models - Data classes for V6 Price Action alerts

Handles parsing and validation of V6 alerts from Pine Script.
V6 alerts have enhanced fields: ADX, Spread, Momentum, Confidence Score.

Alert Types:
- BULLISH_ENTRY / BEARISH_ENTRY: Entry signals
- EXIT_BULLISH / EXIT_BEARISH: Exit signals
- TREND_PULSE: Market state updates

Version: 1.0.0
Date: 2026-01-14
"""

from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)


class V6AlertType(Enum):
    """V6 Alert type classifications"""
    BULLISH_ENTRY = "BULLISH_ENTRY"
    BEARISH_ENTRY = "BEARISH_ENTRY"
    EXIT_BULLISH = "EXIT_BULLISH"
    EXIT_BEARISH = "EXIT_BEARISH"
    TREND_PULSE = "TREND_PULSE"
    TRENDLINE_BULLISH_BREAK = "TRENDLINE_BULLISH_BREAK"
    TRENDLINE_BEARISH_BREAK = "TRENDLINE_BEARISH_BREAK"
    MOMENTUM_CHANGE = "MOMENTUM_CHANGE"
    STATE_CHANGE = "STATE_CHANGE"
    SCREENER_FULL_BULLISH = "SCREENER_FULL_BULLISH"
    SCREENER_FULL_BEARISH = "SCREENER_FULL_BEARISH"
    UNKNOWN = "UNKNOWN"


class ADXStrength(Enum):
    """ADX strength classifications"""
    STRONG = "STRONG"      # ADX >= 25
    MODERATE = "MODERATE"  # ADX >= 20
    WEAK = "WEAK"          # ADX >= 15
    NONE = "NONE"          # ADX < 15


class ConfidenceLevel(Enum):
    """Confidence level classifications"""
    HIGH = "HIGH"          # Score >= 80
    MODERATE = "MODERATE"  # Score >= 60
    LOW = "LOW"            # Score < 60


@dataclass
class ZepixV6Alert:
    """
    V6 Enhanced Alert Payload - 15+ Fields
    
    Source: Pine Script Signals & Overlays V6
    
    Attributes:
        type: Alert type (BULLISH_ENTRY, BEARISH_ENTRY, EXIT_*, TREND_PULSE)
        ticker: Trading symbol (e.g., "XAUUSD")
        tf: Timeframe string ("1", "5", "15", "60")
        price: Current price
        direction: Trade direction (BUY, SELL)
        conf_level: Confidence level (HIGH, MODERATE, LOW)
        conf_score: Confidence score (0-100)
        adx: ADX value (optional, can be NA)
        adx_strength: ADX strength classification
        sl: Stop loss price
        tp1: Take profit 1 price
        tp2: Take profit 2 price
        tp3: Take profit 3 price
        alignment: Bull/Bear count string (e.g., "5/1")
        tl_status: Trendline status (TL_OK, TL_BROKEN)
    """
    type: str
    ticker: str
    tf: str
    price: float
    direction: str
    conf_level: str = "MODERATE"
    conf_score: int = 50
    adx: Optional[float] = None
    adx_strength: str = "NONE"
    sl: Optional[float] = None
    tp1: Optional[float] = None
    tp2: Optional[float] = None
    tp3: Optional[float] = None
    alignment: str = "0/0"
    tl_status: str = "TL_OK"
    momentum_state: str = "NEUTRAL"
    spread_pips: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    raw_payload: str = ""
    
    def __post_init__(self):
        """Validate and normalize fields after initialization"""
        if isinstance(self.adx, str):
            if self.adx.upper() == 'NA' or self.adx == '':
                self.adx = None
            else:
                try:
                    self.adx = float(self.adx)
                except ValueError:
                    self.adx = None
        
        self.adx_strength = self._calculate_adx_strength()
        
        if isinstance(self.conf_score, str):
            try:
                self.conf_score = int(self.conf_score)
            except ValueError:
                self.conf_score = 50
        
        self.conf_level = self._calculate_conf_level()
        
        self.direction = self.direction.upper() if self.direction else "BUY"
        self.type = self.type.upper() if self.type else "UNKNOWN"
    
    def _calculate_adx_strength(self) -> str:
        """Calculate ADX strength classification"""
        if self.adx is None:
            return ADXStrength.NONE.value
        if self.adx >= 25:
            return ADXStrength.STRONG.value
        if self.adx >= 20:
            return ADXStrength.MODERATE.value
        if self.adx >= 15:
            return ADXStrength.WEAK.value
        return ADXStrength.NONE.value
    
    def _calculate_conf_level(self) -> str:
        """Calculate confidence level classification"""
        if self.conf_score >= 80:
            return ConfidenceLevel.HIGH.value
        if self.conf_score >= 60:
            return ConfidenceLevel.MODERATE.value
        return ConfidenceLevel.LOW.value
    
    def get_pulse_counts(self) -> Tuple[int, int]:
        """
        Parse alignment string to get bull/bear counts.
        
        Format: "5/1" -> (5, 1) meaning 5 bullish, 1 bearish
        
        Returns:
            Tuple of (bull_count, bear_count)
        """
        try:
            parts = self.alignment.split('/')
            if len(parts) == 2:
                return int(parts[0]), int(parts[1])
        except (ValueError, AttributeError):
            pass
        return 0, 0
    
    @property
    def bull_count(self) -> int:
        """Get bull count from alignment"""
        return self.get_pulse_counts()[0]
    
    @property
    def bear_count(self) -> int:
        """Get bear count from alignment"""
        return self.get_pulse_counts()[1]
    
    @property
    def is_entry(self) -> bool:
        """Check if this is an entry signal"""
        return self.type in ["BULLISH_ENTRY", "BEARISH_ENTRY"]
    
    @property
    def is_exit(self) -> bool:
        """Check if this is an exit signal"""
        return self.type in ["EXIT_BULLISH", "EXIT_BEARISH"]
    
    @property
    def is_trend_pulse(self) -> bool:
        """Check if this is a trend pulse update"""
        return self.type == "TREND_PULSE"
    
    @property
    def is_bullish(self) -> bool:
        """Check if signal direction is bullish"""
        return self.direction.upper() == "BUY" or "BULLISH" in self.type
    
    @property
    def is_bearish(self) -> bool:
        """Check if signal direction is bearish"""
        return self.direction.upper() == "SELL" or "BEARISH" in self.type
    
    @property
    def timeframe_minutes(self) -> int:
        """Get timeframe in minutes"""
        tf_map = {"1": 1, "5": 5, "15": 15, "60": 60, "240": 240, "1440": 1440}
        return tf_map.get(self.tf, 15)
    
    def validate_for_timeframe(self, expected_tf: str) -> bool:
        """Check if alert matches expected timeframe"""
        return self.tf == expected_tf
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": self.type,
            "ticker": self.ticker,
            "symbol": self.ticker,
            "tf": self.tf,
            "timeframe": self.tf,
            "price": self.price,
            "direction": self.direction,
            "conf_level": self.conf_level,
            "conf_score": self.conf_score,
            "confidence_score": self.conf_score,
            "adx": self.adx,
            "adx_strength": self.adx_strength,
            "sl": self.sl,
            "sl_price": self.sl,
            "tp1": self.tp1,
            "tp1_price": self.tp1,
            "tp2": self.tp2,
            "tp2_price": self.tp2,
            "tp3": self.tp3,
            "tp3_price": self.tp3,
            "alignment": self.alignment,
            "bull_count": self.bull_count,
            "bear_count": self.bear_count,
            "tl_status": self.tl_status,
            "momentum_state": self.momentum_state,
            "spread_pips": self.spread_pips,
            "timestamp": self.timestamp.isoformat(),
            "is_entry": self.is_entry,
            "is_exit": self.is_exit
        }


@dataclass
class TrendPulseAlert:
    """
    Separate alert type for Trend Pulse updates.
    
    Trend Pulse alerts update the market_trends table with
    bull/bear counts and market state.
    """
    type: str = "TREND_PULSE"
    symbol: str = ""
    tf: str = ""
    bull_count: int = 0
    bear_count: int = 0
    changes: str = ""
    state: str = "UNKNOWN"
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def market_state(self) -> str:
        """Get market state classification"""
        if self.bull_count > self.bear_count + 2:
            return "TRENDING_BULLISH"
        elif self.bear_count > self.bull_count + 2:
            return "TRENDING_BEARISH"
        elif abs(self.bull_count - self.bear_count) <= 1:
            return "SIDEWAYS"
        elif self.bull_count > self.bear_count:
            return "WEAK_BULLISH"
        else:
            return "WEAK_BEARISH"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": self.type,
            "symbol": self.symbol,
            "tf": self.tf,
            "bull_count": self.bull_count,
            "bear_count": self.bear_count,
            "changes": self.changes,
            "state": self.state,
            "market_state": self.market_state,
            "timestamp": self.timestamp.isoformat()
        }


def parse_v6_payload(payload: str) -> ZepixV6Alert:
    """
    Parse V6 alert payload string into ZepixV6Alert.
    
    Expected format (pipe-delimited):
    TYPE|SYMBOL|TF|PRICE|DIRECTION|CONF_LEVEL|CONF_SCORE|ADX|ADX_STRENGTH|SL|TP1|TP2|TP3|ALIGNMENT|TL_STATUS
    
    Example:
    "BULLISH_ENTRY|XAUUSD|5|2030.50|BUY|HIGH|85|25.5|STRONG|2028.00|2032.00|2035.00|2038.00|5/1|TL_OK"
    
    Args:
        payload: Pipe-delimited alert string
    
    Returns:
        ZepixV6Alert instance
    """
    try:
        parts = payload.strip().split('|')
        
        if len(parts) < 5:
            logger.warning(f"[V6_PARSE] Insufficient fields in payload: {len(parts)}")
            return ZepixV6Alert(
                type="UNKNOWN",
                ticker="UNKNOWN",
                tf="15",
                price=0.0,
                direction="BUY",
                raw_payload=payload
            )
        
        def safe_float(val, default=None):
            if val is None or val == '' or val.upper() == 'NA':
                return default
            try:
                return float(val)
            except (ValueError, AttributeError):
                return default
        
        def safe_int(val, default=0):
            if val is None or val == '' or val.upper() == 'NA':
                return default
            try:
                return int(val)
            except (ValueError, AttributeError):
                return default
        
        alert = ZepixV6Alert(
            type=parts[0] if len(parts) > 0 else "UNKNOWN",
            ticker=parts[1] if len(parts) > 1 else "UNKNOWN",
            tf=parts[2] if len(parts) > 2 else "15",
            price=safe_float(parts[3], 0.0) if len(parts) > 3 else 0.0,
            direction=parts[4] if len(parts) > 4 else "BUY",
            conf_level=parts[5] if len(parts) > 5 else "MODERATE",
            conf_score=safe_int(parts[6], 50) if len(parts) > 6 else 50,
            adx=safe_float(parts[7]) if len(parts) > 7 else None,
            adx_strength=parts[8] if len(parts) > 8 else "NONE",
            sl=safe_float(parts[9]) if len(parts) > 9 else None,
            tp1=safe_float(parts[10]) if len(parts) > 10 else None,
            tp2=safe_float(parts[11]) if len(parts) > 11 else None,
            tp3=safe_float(parts[12]) if len(parts) > 12 else None,
            alignment=parts[13] if len(parts) > 13 else "0/0",
            tl_status=parts[14] if len(parts) > 14 else "TL_OK",
            raw_payload=payload
        )
        
        logger.debug(
            f"[V6_PARSE] Parsed: {alert.type} {alert.ticker} {alert.tf}m "
            f"ADX={alert.adx} Conf={alert.conf_score}"
        )
        
        return alert
        
    except Exception as e:
        logger.error(f"[V6_PARSE] Error parsing payload: {e}")
        return ZepixV6Alert(
            type="UNKNOWN",
            ticker="UNKNOWN",
            tf="15",
            price=0.0,
            direction="BUY",
            raw_payload=payload
        )


def parse_trend_pulse(payload: str) -> TrendPulseAlert:
    """
    Parse Trend Pulse alert payload.
    
    Expected format:
    TREND_PULSE|SYMBOL|TF|BULL_COUNT|BEAR_COUNT|CHANGES|STATE
    
    Example:
    "TREND_PULSE|XAUUSD|15|5|1|5m,15m|TRENDING_BULLISH"
    
    Args:
        payload: Pipe-delimited trend pulse string
    
    Returns:
        TrendPulseAlert instance
    """
    try:
        parts = payload.strip().split('|')
        
        if len(parts) < 5:
            logger.warning(f"[PULSE_PARSE] Insufficient fields: {len(parts)}")
            return TrendPulseAlert()
        
        return TrendPulseAlert(
            type=parts[0] if len(parts) > 0 else "TREND_PULSE",
            symbol=parts[1] if len(parts) > 1 else "",
            tf=parts[2] if len(parts) > 2 else "",
            bull_count=int(parts[3]) if len(parts) > 3 else 0,
            bear_count=int(parts[4]) if len(parts) > 4 else 0,
            changes=parts[5] if len(parts) > 5 else "",
            state=parts[6] if len(parts) > 6 else "UNKNOWN"
        )
        
    except Exception as e:
        logger.error(f"[PULSE_PARSE] Error parsing: {e}")
        return TrendPulseAlert()


def parse_v6_from_dict(data: Dict[str, Any]) -> ZepixV6Alert:
    """
    Create ZepixV6Alert from dictionary.
    
    Args:
        data: Dictionary with alert fields
    
    Returns:
        ZepixV6Alert instance
    """
    return ZepixV6Alert(
        type=data.get("type", data.get("alert_type", "UNKNOWN")),
        ticker=data.get("ticker", data.get("symbol", "UNKNOWN")),
        tf=str(data.get("tf", data.get("timeframe", "15"))),
        price=float(data.get("price", 0.0)),
        direction=data.get("direction", "BUY"),
        conf_level=data.get("conf_level", "MODERATE"),
        conf_score=int(data.get("conf_score", data.get("confidence_score", 50))),
        adx=data.get("adx"),
        adx_strength=data.get("adx_strength", "NONE"),
        sl=data.get("sl", data.get("sl_price")),
        tp1=data.get("tp1", data.get("tp1_price")),
        tp2=data.get("tp2", data.get("tp2_price")),
        tp3=data.get("tp3", data.get("tp3_price")),
        alignment=data.get("alignment", "0/0"),
        tl_status=data.get("tl_status", "TL_OK"),
        momentum_state=data.get("momentum_state", "NEUTRAL"),
        spread_pips=data.get("spread_pips")
    )


def validate_v6_alert(alert: ZepixV6Alert, timeframe: str = None) -> Dict[str, Any]:
    """
    Validate V6 alert for trading.
    
    Args:
        alert: ZepixV6Alert to validate
        timeframe: Expected timeframe (optional)
    
    Returns:
        Dict with validation result and issues
    """
    issues = []
    
    if alert.type == "UNKNOWN":
        issues.append("Unknown alert type")
    
    if alert.ticker == "UNKNOWN":
        issues.append("Unknown ticker/symbol")
    
    if alert.price <= 0:
        issues.append("Invalid price")
    
    if timeframe and alert.tf != timeframe:
        issues.append(f"Timeframe mismatch: expected {timeframe}, got {alert.tf}")
    
    if alert.is_entry and alert.sl is None:
        issues.append("Entry signal missing stop loss")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "alert_type": alert.type,
        "timeframe": alert.tf
    }


class V6AlertFactory:
    """Factory for creating V6 alerts from various sources"""
    
    @staticmethod
    def from_payload(payload: str) -> ZepixV6Alert:
        """Create from pipe-delimited payload"""
        return parse_v6_payload(payload)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> ZepixV6Alert:
        """Create from dictionary"""
        return parse_v6_from_dict(data)
    
    @staticmethod
    def from_json(json_str: str) -> ZepixV6Alert:
        """Create from JSON string"""
        import json
        data = json.loads(json_str)
        return parse_v6_from_dict(data)
    
    @staticmethod
    def create_entry(
        ticker: str,
        tf: str,
        direction: str,
        price: float,
        adx: float = None,
        conf_score: int = 70,
        sl: float = None,
        tp1: float = None
    ) -> ZepixV6Alert:
        """Create entry alert programmatically"""
        alert_type = "BULLISH_ENTRY" if direction.upper() == "BUY" else "BEARISH_ENTRY"
        return ZepixV6Alert(
            type=alert_type,
            ticker=ticker,
            tf=tf,
            price=price,
            direction=direction,
            adx=adx,
            conf_score=conf_score,
            sl=sl,
            tp1=tp1
        )
    
    @staticmethod
    def create_exit(
        ticker: str,
        tf: str,
        direction: str,
        price: float
    ) -> ZepixV6Alert:
        """Create exit alert programmatically"""
        alert_type = "EXIT_BULLISH" if direction.upper() == "BUY" else "EXIT_BEARISH"
        return ZepixV6Alert(
            type=alert_type,
            ticker=ticker,
            tf=tf,
            price=price,
            direction=direction
        )
