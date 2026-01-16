"""
Config Wizard - Self-Healing Configuration System

This module provides automatic detection and healing of configuration issues,
particularly for the 3-bot Telegram system.

Features:
- Auto-detection of missing/empty config values
- Fallback mode: Use single telegram_token for all bots if 3-bot tokens empty
- Graceful degradation: System works with 1 bot or 3 bots
- Token validation: Test API call before use
- User notification: Alert about missing config via Telegram

Version: 1.0.0
Date: 2026-01-15
"""

import json
import logging
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ConfigMode(Enum):
    """Configuration mode based on available tokens"""
    NO_BOT = "NO_BOT"           # No tokens configured
    SINGLE_BOT = "SINGLE_BOT"   # Only main token, fallback mode
    MULTI_BOT = "MULTI_BOT"     # All 3 bot tokens configured


class IssueSeverity(Enum):
    """Severity levels for configuration issues"""
    CRITICAL = "CRITICAL"   # System cannot start
    WARNING = "WARNING"     # System can start with degraded functionality
    INFO = "INFO"           # Informational only


@dataclass
class ConfigIssue:
    """Represents a configuration issue"""
    severity: IssueSeverity
    field: str
    message: str
    auto_healable: bool = False


@dataclass
class ConfigDiagnosis:
    """Result of configuration diagnosis"""
    mode: ConfigMode
    issues: List[ConfigIssue] = field(default_factory=list)
    is_healthy: bool = False
    can_start: bool = False


class ConfigWizard:
    """
    Self-healing configuration system for V5 Hybrid Plugin Architecture.
    
    Automatically detects and fixes configuration issues, particularly
    for the 3-bot Telegram system.
    """
    
    def __init__(self, config_path: str = "config/config.json"):
        """
        Initialize ConfigWizard.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.issues: List[ConfigIssue] = []
        self.mode: ConfigMode = ConfigMode.NO_BOT
        self._healed = False
        
        # Load configuration
        self._load_config()
        
        logger.info(f"[ConfigWizard] Initialized with config: {self.config_path}")
    
    def _load_config(self) -> bool:
        """Load configuration from file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                logger.info(f"[ConfigWizard] Loaded config from {self.config_path}")
                return True
            else:
                logger.error(f"[ConfigWizard] Config file not found: {self.config_path}")
                return False
        except json.JSONDecodeError as e:
            logger.error(f"[ConfigWizard] Invalid JSON in config: {e}")
            return False
        except Exception as e:
            logger.error(f"[ConfigWizard] Failed to load config: {e}")
            return False
    
    def diagnose(self) -> ConfigDiagnosis:
        """
        Diagnose configuration issues.
        
        Returns:
            ConfigDiagnosis with mode, issues, and health status
        """
        self.issues = []
        
        # Check main Telegram token
        main_token = self.config.get("telegram_token", "")
        chat_id = self.config.get("telegram_chat_id", "")
        
        # Check 3-bot tokens
        controller_token = self.config.get("telegram_controller_token", "")
        notification_token = self.config.get("telegram_notification_token", "")
        analytics_token = self.config.get("telegram_analytics_token", "")
        
        # Check MT5 credentials
        mt5_login = self.config.get("mt5_login", "")
        mt5_password = self.config.get("mt5_password", "")
        mt5_server = self.config.get("mt5_server", "")
        
        # Diagnose Telegram tokens
        if not main_token:
            self.issues.append(ConfigIssue(
                severity=IssueSeverity.CRITICAL,
                field="telegram_token",
                message="Main Telegram token is missing or empty",
                auto_healable=False
            ))
        
        if not chat_id:
            self.issues.append(ConfigIssue(
                severity=IssueSeverity.CRITICAL,
                field="telegram_chat_id",
                message="Telegram chat ID is missing",
                auto_healable=False
            ))
        
        # Determine mode based on 3-bot tokens
        has_all_3_tokens = all([controller_token, notification_token, analytics_token])
        
        if has_all_3_tokens:
            self.mode = ConfigMode.MULTI_BOT
            logger.info("[ConfigWizard] Mode: MULTI_BOT (all 3 tokens configured)")
        elif main_token:
            self.mode = ConfigMode.SINGLE_BOT
            self.issues.append(ConfigIssue(
                severity=IssueSeverity.WARNING,
                field="3-bot tokens",
                message="3-bot tokens empty. Using fallback single-bot mode.",
                auto_healable=True
            ))
            logger.info("[ConfigWizard] Mode: SINGLE_BOT (fallback mode)")
        else:
            self.mode = ConfigMode.NO_BOT
            logger.error("[ConfigWizard] Mode: NO_BOT (no tokens configured)")
        
        # Check MT5 credentials
        if not mt5_login:
            self.issues.append(ConfigIssue(
                severity=IssueSeverity.WARNING,
                field="mt5_login",
                message="MT5 login not configured",
                auto_healable=False
            ))
        
        if not mt5_password:
            self.issues.append(ConfigIssue(
                severity=IssueSeverity.WARNING,
                field="mt5_password",
                message="MT5 password not configured",
                auto_healable=False
            ))
        
        # Check plugin system
        plugin_enabled = self.config.get("plugin_system", {}).get("enabled", False)
        if not plugin_enabled:
            self.issues.append(ConfigIssue(
                severity=IssueSeverity.INFO,
                field="plugin_system.enabled",
                message="Plugin system is disabled",
                auto_healable=False
            ))
        
        # Determine health status
        critical_issues = [i for i in self.issues if i.severity == IssueSeverity.CRITICAL]
        is_healthy = len(critical_issues) == 0
        can_start = self.mode != ConfigMode.NO_BOT
        
        diagnosis = ConfigDiagnosis(
            mode=self.mode,
            issues=self.issues,
            is_healthy=is_healthy,
            can_start=can_start
        )
        
        logger.info(f"[ConfigWizard] Diagnosis complete: mode={self.mode.value}, issues={len(self.issues)}, can_start={can_start}")
        
        return diagnosis
    
    def heal(self) -> bool:
        """
        Apply self-healing fixes to configuration.
        
        Returns:
            True if healing was successful
        """
        if self._healed:
            logger.info("[ConfigWizard] Already healed")
            return True
        
        if self.mode == ConfigMode.SINGLE_BOT:
            # Use main token for all bots
            main_token = self.config.get("telegram_token", "")
            
            if main_token:
                self.config["telegram_controller_token"] = main_token
                self.config["telegram_notification_token"] = main_token
                self.config["telegram_analytics_token"] = main_token
                
                self._healed = True
                logger.info("[ConfigWizard] Healed: Applied main token to all 3-bot slots")
                return True
        
        elif self.mode == ConfigMode.MULTI_BOT:
            # Already configured correctly
            self._healed = True
            logger.info("[ConfigWizard] No healing needed: MULTI_BOT mode")
            return True
        
        logger.warning("[ConfigWizard] Cannot heal: NO_BOT mode")
        return False
    
    def get_effective_config(self) -> Dict[str, Any]:
        """
        Get effective token configuration after healing.
        
        Returns:
            Dict with controller, notification, analytics tokens and chat_id
        """
        # Apply healing if not done
        if not self._healed:
            self.heal()
        
        return {
            "controller_token": self.config.get("telegram_controller_token") or self.config.get("telegram_token"),
            "notification_token": self.config.get("telegram_notification_token") or self.config.get("telegram_token"),
            "analytics_token": self.config.get("telegram_analytics_token") or self.config.get("telegram_token"),
            "chat_id": self.config.get("telegram_chat_id"),
            "mode": self.mode.value
        }
    
    def validate_token(self, token: str) -> bool:
        """
        Validate a Telegram bot token by making a test API call.
        
        Args:
            token: Telegram bot token to validate
        
        Returns:
            True if token is valid
        """
        if not token:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{token}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    bot_info = data.get("result", {})
                    logger.info(f"[ConfigWizard] Token valid: @{bot_info.get('username', 'unknown')}")
                    return True
            
            logger.warning(f"[ConfigWizard] Token validation failed: {response.status_code}")
            return False
            
        except requests.RequestException as e:
            logger.error(f"[ConfigWizard] Token validation error: {e}")
            return False
    
    def send_startup_notification(self, message: str = None) -> bool:
        """
        Send startup notification to Telegram.
        
        Args:
            message: Optional custom message
        
        Returns:
            True if message was sent successfully
        """
        effective = self.get_effective_config()
        token = effective.get("controller_token")
        chat_id = effective.get("chat_id")
        
        if not token or not chat_id:
            logger.error("[ConfigWizard] Cannot send notification: missing token or chat_id")
            return False
        
        if message is None:
            # Default startup message
            mode_emoji = "🟢" if self.mode == ConfigMode.MULTI_BOT else "🟡"
            issues_count = len(self.issues)
            
            message = (
                f"🤖 <b>ZEPIX BOT STARTUP</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"<b>Config Status:</b>\n"
                f"├─ Mode: {mode_emoji} {self.mode.value}\n"
                f"├─ Issues: {issues_count}\n"
                f"└─ Healed: {'✅' if self._healed else '❌'}\n\n"
            )
            
            if self.issues:
                message += "<b>Issues Detected:</b>\n"
                for issue in self.issues[:5]:  # Show max 5 issues
                    severity_emoji = "🔴" if issue.severity == IssueSeverity.CRITICAL else ("🟡" if issue.severity == IssueSeverity.WARNING else "🔵")
                    message += f"├─ {severity_emoji} {issue.field}: {issue.message}\n"
                
                if len(self.issues) > 5:
                    message += f"└─ ... and {len(self.issues) - 5} more\n"
            
            message += "\n<b>System Ready!</b> 🚀"
        
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("[ConfigWizard] Startup notification sent successfully")
                return True
            else:
                logger.error(f"[ConfigWizard] Failed to send notification: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"[ConfigWizard] Notification error: {e}")
            return False
    
    def format_diagnosis_report(self) -> str:
        """
        Format diagnosis as a readable report.
        
        Returns:
            Formatted diagnosis report string
        """
        report = []
        report.append("=" * 50)
        report.append("CONFIG WIZARD DIAGNOSIS REPORT")
        report.append("=" * 50)
        report.append(f"\nMode: {self.mode.value}")
        report.append(f"Healed: {self._healed}")
        report.append(f"Issues: {len(self.issues)}")
        report.append("")
        
        if self.issues:
            report.append("ISSUES FOUND:")
            report.append("-" * 30)
            for i, issue in enumerate(self.issues, 1):
                report.append(f"{i}. [{issue.severity.value}] {issue.field}")
                report.append(f"   {issue.message}")
                report.append(f"   Auto-healable: {issue.auto_healable}")
            report.append("")
        
        effective = self.get_effective_config()
        report.append("EFFECTIVE CONFIG:")
        report.append("-" * 30)
        report.append(f"Controller Token: {'SET' if effective['controller_token'] else 'MISSING'}")
        report.append(f"Notification Token: {'SET' if effective['notification_token'] else 'MISSING'}")
        report.append(f"Analytics Token: {'SET' if effective['analytics_token'] else 'MISSING'}")
        report.append(f"Chat ID: {effective['chat_id'] or 'MISSING'}")
        
        report.append("")
        report.append("=" * 50)
        
        return "\n".join(report)


# Convenience function for quick diagnosis
def quick_diagnose(config_path: str = "config/config.json") -> ConfigDiagnosis:
    """
    Quick diagnosis of configuration.
    
    Args:
        config_path: Path to configuration file
    
    Returns:
        ConfigDiagnosis result
    """
    wizard = ConfigWizard(config_path)
    return wizard.diagnose()


# Convenience function for quick heal
def quick_heal(config_path: str = "config/config.json") -> Dict[str, Any]:
    """
    Quick heal and get effective configuration.
    
    Args:
        config_path: Path to configuration file
    
    Returns:
        Effective configuration dict
    """
    wizard = ConfigWizard(config_path)
    wizard.diagnose()
    wizard.heal()
    return wizard.get_effective_config()
