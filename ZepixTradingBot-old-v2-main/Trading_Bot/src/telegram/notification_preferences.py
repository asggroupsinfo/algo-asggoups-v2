"""
Notification Preferences - User notification filtering system

Allows users to customize which notifications they receive:
- Per-type notification toggles
- Per-plugin filtering (V3 only / V6 only / Both)
- Quiet hours configuration
- Priority levels (Critical / Important / Info)

Version: 1.0.0
Date: 2026-01-19
Part of Telegram V5 Upgrade - Batch 1
"""

import json
import logging
from datetime import datetime, time
from typing import Dict, Any, Optional, List, Set
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class NotificationCategory(Enum):
    """Notification categories for filtering"""
    TRADE_ENTRY = "trade_entry"
    TRADE_EXIT = "trade_exit"
    TP_HIT = "tp_hit"
    SL_HIT = "sl_hit"
    PROFIT_BOOKING = "profit_booking"
    SL_MODIFIED = "sl_modified"
    BREAKEVEN = "breakeven"
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_SUMMARY = "weekly_summary"
    TREND_PULSE = "trend_pulse"
    PRICE_ACTION = "price_action"
    SHADOW_TRADE = "shadow_trade"
    SYSTEM_ALERT = "system_alert"
    ERROR_ALERT = "error_alert"
    PLUGIN_STATUS = "plugin_status"


class PluginFilter(Enum):
    """Plugin filter options"""
    ALL = "all"           # Receive from all plugins
    V3_ONLY = "v3_only"   # Only V3 Combined notifications
    V6_ONLY = "v6_only"   # Only V6 Price Action notifications
    NONE = "none"         # Mute all


class PriorityLevel(Enum):
    """Priority level filter"""
    ALL = "all"           # Receive all priorities
    CRITICAL_ONLY = "critical_only"  # Only critical alerts
    HIGH_AND_ABOVE = "high_and_above"  # High and critical
    MEDIUM_AND_ABOVE = "medium_and_above"  # Medium, high, critical


class NotificationPreferences:
    """
    Manages user notification preferences.
    
    Features:
    - Per-category enable/disable
    - Plugin filtering (V3/V6/Both)
    - Quiet hours
    - Priority filtering
    - Persistence to JSON file
    """
    
    DEFAULT_PREFERENCES = {
        "enabled": True,
        "categories": {
            "trade_entry": True,
            "trade_exit": True,
            "tp_hit": True,
            "sl_hit": True,
            "profit_booking": True,
            "sl_modified": False,  # Less important by default
            "breakeven": False,    # Less important by default
            "daily_summary": True,
            "weekly_summary": True,
            "trend_pulse": True,
            "price_action": False,  # Can be noisy
            "shadow_trade": True,
            "system_alert": True,
            "error_alert": True,
            "plugin_status": True,
        },
        "plugin_filter": "all",  # all, v3_only, v6_only, none
        "priority_level": "all",  # all, critical_only, high_and_above, medium_and_above
        "quiet_hours": {
            "enabled": False,
            "start": "22:00",
            "end": "06:00",
            "allow_critical": True,  # Allow critical alerts during quiet hours
        },
        "v6_timeframe_filter": {
            "15m": True,
            "30m": True,
            "1h": True,
            "4h": True,
        },
        "sound_enabled": True,
        "voice_alerts_enabled": False,
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize NotificationPreferences.
        
        Args:
            config_path: Path to preferences JSON file
        """
        self._logger = logger
        self._config_path = config_path or self._get_default_config_path()
        self._preferences: Dict[str, Any] = {}
        self._load_preferences()
    
    def _get_default_config_path(self) -> str:
        """Get default config path"""
        base_path = Path(__file__).parent.parent.parent
        config_dir = base_path / "config"
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / "notification_preferences.json")
    
    def _load_preferences(self):
        """Load preferences from file or use defaults"""
        try:
            if Path(self._config_path).exists():
                with open(self._config_path, 'r') as f:
                    self._preferences = json.load(f)
                self._logger.info(f"[NotifPrefs] Loaded preferences from {self._config_path}")
            else:
                self._preferences = self.DEFAULT_PREFERENCES.copy()
                self._save_preferences()
                self._logger.info("[NotifPrefs] Created default preferences")
        except Exception as e:
            self._logger.error(f"[NotifPrefs] Error loading preferences: {e}")
            self._preferences = self.DEFAULT_PREFERENCES.copy()
    
    def _save_preferences(self):
        """Save preferences to file"""
        try:
            with open(self._config_path, 'w') as f:
                json.dump(self._preferences, f, indent=2)
            self._logger.info("[NotifPrefs] Preferences saved")
        except Exception as e:
            self._logger.error(f"[NotifPrefs] Error saving preferences: {e}")
    
    def is_enabled(self) -> bool:
        """Check if notifications are globally enabled"""
        return self._preferences.get("enabled", True)
    
    def set_enabled(self, enabled: bool):
        """Set global notification enabled state"""
        self._preferences["enabled"] = enabled
        self._save_preferences()
    
    def is_category_enabled(self, category: str) -> bool:
        """
        Check if a notification category is enabled.
        
        Args:
            category: Category name (e.g., 'trade_entry', 'tp_hit')
        
        Returns:
            True if enabled, False otherwise
        """
        categories = self._preferences.get("categories", {})
        return categories.get(category, True)
    
    def set_category_enabled(self, category: str, enabled: bool):
        """
        Enable/disable a notification category.
        
        Args:
            category: Category name
            enabled: True to enable, False to disable
        """
        if "categories" not in self._preferences:
            self._preferences["categories"] = {}
        self._preferences["categories"][category] = enabled
        self._save_preferences()
    
    def get_plugin_filter(self) -> str:
        """Get current plugin filter setting"""
        return self._preferences.get("plugin_filter", "all")
    
    def set_plugin_filter(self, filter_type: str):
        """
        Set plugin filter.
        
        Args:
            filter_type: 'all', 'v3_only', 'v6_only', 'none'
        """
        valid_filters = ["all", "v3_only", "v6_only", "none"]
        if filter_type in valid_filters:
            self._preferences["plugin_filter"] = filter_type
            self._save_preferences()
    
    def get_priority_level(self) -> str:
        """Get current priority level filter"""
        return self._preferences.get("priority_level", "all")
    
    def set_priority_level(self, level: str):
        """
        Set priority level filter.
        
        Args:
            level: 'all', 'critical_only', 'high_and_above', 'medium_and_above'
        """
        valid_levels = ["all", "critical_only", "high_and_above", "medium_and_above"]
        if level in valid_levels:
            self._preferences["priority_level"] = level
            self._save_preferences()
    
    def is_quiet_hours_enabled(self) -> bool:
        """Check if quiet hours are enabled"""
        quiet_hours = self._preferences.get("quiet_hours", {})
        return quiet_hours.get("enabled", False)
    
    def set_quiet_hours(self, enabled: bool, start: str = None, end: str = None, allow_critical: bool = True):
        """
        Configure quiet hours.
        
        Args:
            enabled: Enable/disable quiet hours
            start: Start time (HH:MM format)
            end: End time (HH:MM format)
            allow_critical: Allow critical alerts during quiet hours
        """
        if "quiet_hours" not in self._preferences:
            self._preferences["quiet_hours"] = {}
        
        self._preferences["quiet_hours"]["enabled"] = enabled
        if start:
            self._preferences["quiet_hours"]["start"] = start
        if end:
            self._preferences["quiet_hours"]["end"] = end
        self._preferences["quiet_hours"]["allow_critical"] = allow_critical
        self._save_preferences()
    
    def is_in_quiet_hours(self) -> bool:
        """Check if current time is within quiet hours"""
        quiet_hours = self._preferences.get("quiet_hours", {})
        if not quiet_hours.get("enabled", False):
            return False
        
        try:
            now = datetime.now().time()
            start_str = quiet_hours.get("start", "22:00")
            end_str = quiet_hours.get("end", "06:00")
            
            start_time = datetime.strptime(start_str, "%H:%M").time()
            end_time = datetime.strptime(end_str, "%H:%M").time()
            
            # Handle overnight quiet hours (e.g., 22:00 - 06:00)
            if start_time > end_time:
                return now >= start_time or now <= end_time
            else:
                return start_time <= now <= end_time
        except Exception as e:
            self._logger.error(f"[NotifPrefs] Error checking quiet hours: {e}")
            return False
    
    def is_v6_timeframe_enabled(self, timeframe: str) -> bool:
        """
        Check if V6 notifications for a specific timeframe are enabled.
        
        Args:
            timeframe: Timeframe (15m, 30m, 1h, 4h)
        
        Returns:
            True if enabled, False otherwise
        """
        tf_filter = self._preferences.get("v6_timeframe_filter", {})
        return tf_filter.get(timeframe.lower(), True)
    
    def set_v6_timeframe_enabled(self, timeframe: str, enabled: bool):
        """
        Enable/disable V6 notifications for a specific timeframe.
        
        Args:
            timeframe: Timeframe (15m, 30m, 1h, 4h)
            enabled: True to enable, False to disable
        """
        if "v6_timeframe_filter" not in self._preferences:
            self._preferences["v6_timeframe_filter"] = {}
        self._preferences["v6_timeframe_filter"][timeframe.lower()] = enabled
        self._save_preferences()
    
    def should_send_notification(
        self,
        category: str,
        plugin_name: str = None,
        priority: str = "medium",
        timeframe: str = None
    ) -> bool:
        """
        Check if a notification should be sent based on all preferences.
        
        Args:
            category: Notification category
            plugin_name: Plugin name (e.g., 'v3_combined', 'v6_price_action_1h')
            priority: Priority level (critical, high, medium, low, info)
            timeframe: V6 timeframe if applicable
        
        Returns:
            True if notification should be sent, False otherwise
        """
        # Check global enabled
        if not self.is_enabled():
            return False
        
        # Check category enabled
        if not self.is_category_enabled(category):
            return False
        
        # Check plugin filter
        plugin_filter = self.get_plugin_filter()
        if plugin_filter == "none":
            return False
        elif plugin_filter == "v3_only" and plugin_name and "v6" in plugin_name.lower():
            return False
        elif plugin_filter == "v6_only" and plugin_name and "v3" in plugin_name.lower():
            return False
        
        # Check V6 timeframe filter
        if timeframe and not self.is_v6_timeframe_enabled(timeframe):
            return False
        
        # Check priority level
        priority_level = self.get_priority_level()
        priority_map = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}
        current_priority = priority_map.get(priority.lower(), 3)
        
        if priority_level == "critical_only" and current_priority < 5:
            return False
        elif priority_level == "high_and_above" and current_priority < 4:
            return False
        elif priority_level == "medium_and_above" and current_priority < 3:
            return False
        
        # Check quiet hours
        if self.is_in_quiet_hours():
            quiet_hours = self._preferences.get("quiet_hours", {})
            allow_critical = quiet_hours.get("allow_critical", True)
            if not allow_critical or current_priority < 5:
                return False
        
        return True
    
    def get_all_preferences(self) -> Dict[str, Any]:
        """Get all preferences as a dictionary"""
        return self._preferences.copy()
    
    def reset_to_defaults(self):
        """Reset all preferences to defaults"""
        self._preferences = self.DEFAULT_PREFERENCES.copy()
        self._save_preferences()
        self._logger.info("[NotifPrefs] Reset to defaults")
    
    def get_enabled_categories(self) -> List[str]:
        """Get list of enabled categories"""
        categories = self._preferences.get("categories", {})
        return [cat for cat, enabled in categories.items() if enabled]
    
    def get_disabled_categories(self) -> List[str]:
        """Get list of disabled categories"""
        categories = self._preferences.get("categories", {})
        return [cat for cat, enabled in categories.items() if not enabled]
    
    def toggle_category(self, category: str) -> bool:
        """
        Toggle a category on/off.
        
        Args:
            category: Category name
        
        Returns:
            New enabled state
        """
        current = self.is_category_enabled(category)
        self.set_category_enabled(category, not current)
        return not current
    
    def enable_all_categories(self):
        """Enable all notification categories"""
        for category in NotificationCategory:
            self.set_category_enabled(category.value, True)
    
    def disable_all_categories(self):
        """Disable all notification categories (except critical)"""
        for category in NotificationCategory:
            # Keep system and error alerts enabled
            if category in [NotificationCategory.SYSTEM_ALERT, NotificationCategory.ERROR_ALERT]:
                continue
            self.set_category_enabled(category.value, False)
