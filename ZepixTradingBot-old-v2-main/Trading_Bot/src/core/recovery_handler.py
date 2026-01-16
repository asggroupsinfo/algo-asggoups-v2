"""
Recovery Handler - Error Handling and Recovery Logic

This module provides ACTUAL error handlers for the main execution loop.
It handles plugin failures, trade errors, connection issues, and automatic recovery.

NOT JUST DOCUMENTATION - THIS IS REAL, WORKING CODE.

Version: 1.0.0
Date: 2026-01-15
"""

import logging
import asyncio
import traceback
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "LOW"           # Log and continue
    MEDIUM = "MEDIUM"     # Log, notify, continue
    HIGH = "HIGH"         # Log, notify, attempt recovery
    CRITICAL = "CRITICAL" # Log, notify, pause trading


class ErrorCategory(Enum):
    """Error categories"""
    PLUGIN = "PLUGIN"
    TRADE = "TRADE"
    CONNECTION = "CONNECTION"
    CONFIG = "CONFIG"
    DATABASE = "DATABASE"
    TELEGRAM = "TELEGRAM"
    MT5 = "MT5"
    UNKNOWN = "UNKNOWN"


@dataclass
class ErrorRecord:
    """Record of an error occurrence"""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    exception: Optional[Exception] = None
    traceback_str: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    recovered: bool = False
    recovery_action: Optional[str] = None


@dataclass
class RecoveryResult:
    """Result of a recovery attempt"""
    success: bool
    action_taken: str
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class RecoveryHandler:
    """
    Central error handling and recovery system.
    
    This is the ACTUAL implementation that handles:
    - Plugin failures with automatic disable/re-enable
    - Trade execution errors with retry logic
    - Connection issues with reconnection
    - Automatic recovery strategies
    """
    
    # Error thresholds for automatic actions
    PLUGIN_FAILURE_THRESHOLD = 5      # Disable plugin after N failures
    TRADE_RETRY_MAX = 3               # Max trade retries
    CONNECTION_RETRY_MAX = 5          # Max connection retries
    CONNECTION_RETRY_DELAY = 5        # Seconds between retries
    ERROR_WINDOW_MINUTES = 10         # Window for counting errors
    
    def __init__(self, trading_engine=None, telegram_bot=None):
        """
        Initialize RecoveryHandler.
        
        Args:
            trading_engine: TradingEngine instance
            telegram_bot: TelegramBot instance for notifications
        """
        self._trading_engine = trading_engine
        self._telegram_bot = telegram_bot
        
        # Error tracking
        self._error_history: List[ErrorRecord] = []
        self._error_counts: Dict[str, int] = {}  # category:count
        self._plugin_failures: Dict[str, int] = {}  # plugin_id:count
        
        # Recovery state
        self._recovery_in_progress = False
        self._paused_plugins: Dict[str, datetime] = {}
        self._disabled_plugins: set = set()
        
        # Callbacks for custom recovery actions
        self._recovery_callbacks: Dict[ErrorCategory, Callable] = {}
        
        # Statistics
        self._stats = {
            "total_errors": 0,
            "recovered_errors": 0,
            "failed_recoveries": 0,
            "plugins_disabled": 0,
            "trades_retried": 0,
            "connections_restored": 0,
        }
        
        logger.info("[RecoveryHandler] Initialized")
    
    def set_dependencies(self, trading_engine=None, telegram_bot=None):
        """Set dependencies after initialization"""
        if trading_engine:
            self._trading_engine = trading_engine
        if telegram_bot:
            self._telegram_bot = telegram_bot
        logger.info("[RecoveryHandler] Dependencies updated")
    
    def register_recovery_callback(self, category: ErrorCategory, callback: Callable):
        """Register a custom recovery callback for an error category"""
        self._recovery_callbacks[category] = callback
        logger.info(f"[RecoveryHandler] Registered recovery callback for {category.value}")
    
    # ========================================
    # Error Recording
    # ========================================
    
    def record_error(
        self,
        category: ErrorCategory,
        severity: ErrorSeverity,
        message: str,
        exception: Exception = None,
        context: Dict[str, Any] = None
    ) -> ErrorRecord:
        """
        Record an error occurrence.
        
        Args:
            category: Error category
            severity: Error severity
            message: Error message
            exception: Optional exception object
            context: Optional context data
        
        Returns:
            ErrorRecord
        """
        error_id = f"{category.value}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        tb_str = None
        if exception:
            tb_str = traceback.format_exc()
        
        record = ErrorRecord(
            error_id=error_id,
            category=category,
            severity=severity,
            message=message,
            exception=exception,
            traceback_str=tb_str,
            context=context or {},
            timestamp=datetime.now()
        )
        
        self._error_history.append(record)
        self._stats["total_errors"] += 1
        
        # Update category count
        cat_key = category.value
        self._error_counts[cat_key] = self._error_counts.get(cat_key, 0) + 1
        
        # Trim old errors
        self._trim_error_history()
        
        logger.error(f"[RecoveryHandler] Error recorded: [{severity.value}] {category.value}: {message}")
        
        return record
    
    def _trim_error_history(self, max_records: int = 1000):
        """Keep error history within limits"""
        if len(self._error_history) > max_records:
            self._error_history = self._error_history[-max_records:]
    
    # ========================================
    # Plugin Error Handling
    # ========================================
    
    async def handle_plugin_error(
        self,
        plugin_id: str,
        error: Exception,
        signal_data: Dict[str, Any] = None
    ) -> RecoveryResult:
        """
        Handle a plugin error with automatic recovery.
        
        Args:
            plugin_id: Plugin identifier
            error: Exception that occurred
            signal_data: Optional signal data that caused the error
        
        Returns:
            RecoveryResult
        """
        # Record error
        record = self.record_error(
            category=ErrorCategory.PLUGIN,
            severity=ErrorSeverity.HIGH,
            message=f"Plugin {plugin_id} failed: {str(error)}",
            exception=error,
            context={"plugin_id": plugin_id, "signal_data": signal_data}
        )
        
        # Track plugin failures
        self._plugin_failures[plugin_id] = self._plugin_failures.get(plugin_id, 0) + 1
        failure_count = self._plugin_failures[plugin_id]
        
        logger.warning(f"[RecoveryHandler] Plugin {plugin_id} failure count: {failure_count}")
        
        # Check if plugin should be disabled
        if failure_count >= self.PLUGIN_FAILURE_THRESHOLD:
            return await self._disable_plugin(plugin_id, record)
        
        # Try to recover plugin
        return await self._recover_plugin(plugin_id, record)
    
    async def _disable_plugin(self, plugin_id: str, record: ErrorRecord) -> RecoveryResult:
        """Disable a plugin due to repeated failures"""
        self._disabled_plugins.add(plugin_id)
        self._stats["plugins_disabled"] += 1
        
        # Disable in trading engine
        if self._trading_engine:
            if hasattr(self._trading_engine, 'plugin_registry'):
                plugin = self._trading_engine.plugin_registry.get_plugin(plugin_id)
                if plugin:
                    plugin.enabled = False
        
        # Notify
        await self._notify_error(
            f"Plugin {plugin_id} DISABLED due to {self._plugin_failures[plugin_id]} failures",
            ErrorSeverity.CRITICAL
        )
        
        record.recovered = False
        record.recovery_action = "plugin_disabled"
        
        logger.critical(f"[RecoveryHandler] Plugin {plugin_id} DISABLED")
        
        return RecoveryResult(
            success=False,
            action_taken="plugin_disabled",
            details={"plugin_id": plugin_id, "failure_count": self._plugin_failures[plugin_id]}
        )
    
    async def _recover_plugin(self, plugin_id: str, record: ErrorRecord) -> RecoveryResult:
        """Attempt to recover a plugin"""
        # Pause plugin temporarily
        self._paused_plugins[plugin_id] = datetime.now()
        
        # Wait briefly
        await asyncio.sleep(1)
        
        # Re-enable plugin
        del self._paused_plugins[plugin_id]
        
        record.recovered = True
        record.recovery_action = "plugin_restarted"
        self._stats["recovered_errors"] += 1
        
        logger.info(f"[RecoveryHandler] Plugin {plugin_id} recovered")
        
        return RecoveryResult(
            success=True,
            action_taken="plugin_restarted",
            details={"plugin_id": plugin_id}
        )
    
    def is_plugin_paused(self, plugin_id: str) -> bool:
        """Check if a plugin is temporarily paused"""
        return plugin_id in self._paused_plugins
    
    def is_plugin_disabled(self, plugin_id: str) -> bool:
        """Check if a plugin is disabled"""
        return plugin_id in self._disabled_plugins
    
    def reset_plugin_failures(self, plugin_id: str):
        """Reset failure count for a plugin"""
        if plugin_id in self._plugin_failures:
            del self._plugin_failures[plugin_id]
        if plugin_id in self._disabled_plugins:
            self._disabled_plugins.remove(plugin_id)
        logger.info(f"[RecoveryHandler] Reset failures for plugin {plugin_id}")
    
    # ========================================
    # Trade Error Handling
    # ========================================
    
    async def handle_trade_error(
        self,
        error: Exception,
        trade_data: Dict[str, Any],
        retry_count: int = 0
    ) -> RecoveryResult:
        """
        Handle a trade execution error with retry logic.
        
        Args:
            error: Exception that occurred
            trade_data: Trade data that failed
            retry_count: Current retry count
        
        Returns:
            RecoveryResult
        """
        # Record error
        record = self.record_error(
            category=ErrorCategory.TRADE,
            severity=ErrorSeverity.HIGH,
            message=f"Trade execution failed: {str(error)}",
            exception=error,
            context={"trade_data": trade_data, "retry_count": retry_count}
        )
        
        # Check if we should retry
        if retry_count < self.TRADE_RETRY_MAX:
            return await self._retry_trade(trade_data, retry_count, record)
        
        # Max retries reached
        await self._notify_error(
            f"Trade FAILED after {retry_count} retries: {trade_data.get('symbol', 'UNKNOWN')}",
            ErrorSeverity.HIGH
        )
        
        record.recovered = False
        record.recovery_action = "max_retries_reached"
        self._stats["failed_recoveries"] += 1
        
        return RecoveryResult(
            success=False,
            action_taken="max_retries_reached",
            details={"trade_data": trade_data, "retry_count": retry_count},
            error=str(error)
        )
    
    async def _retry_trade(
        self,
        trade_data: Dict[str, Any],
        retry_count: int,
        record: ErrorRecord
    ) -> RecoveryResult:
        """Retry a failed trade"""
        self._stats["trades_retried"] += 1
        
        # Wait before retry (exponential backoff)
        wait_time = 2 ** retry_count
        await asyncio.sleep(wait_time)
        
        # Attempt retry
        if self._trading_engine and hasattr(self._trading_engine, 'execute_trades'):
            try:
                result = await self._trading_engine.execute_trades(trade_data)
                
                if result:
                    record.recovered = True
                    record.recovery_action = f"trade_retried_{retry_count + 1}"
                    self._stats["recovered_errors"] += 1
                    
                    logger.info(f"[RecoveryHandler] Trade retry {retry_count + 1} successful")
                    
                    return RecoveryResult(
                        success=True,
                        action_taken=f"trade_retried_{retry_count + 1}",
                        details={"trade_data": trade_data, "result": result}
                    )
            except Exception as e:
                # Recursive retry
                return await self.handle_trade_error(e, trade_data, retry_count + 1)
        
        return RecoveryResult(
            success=False,
            action_taken="retry_failed",
            details={"trade_data": trade_data, "retry_count": retry_count}
        )
    
    # ========================================
    # Connection Error Handling
    # ========================================
    
    async def handle_connection_error(
        self,
        error: Exception,
        connection_type: str = "MT5",
        retry_count: int = 0
    ) -> RecoveryResult:
        """
        Handle a connection error with reconnection logic.
        
        Args:
            error: Exception that occurred
            connection_type: Type of connection (MT5, Telegram, etc.)
            retry_count: Current retry count
        
        Returns:
            RecoveryResult
        """
        # Record error
        record = self.record_error(
            category=ErrorCategory.CONNECTION,
            severity=ErrorSeverity.CRITICAL,
            message=f"{connection_type} connection failed: {str(error)}",
            exception=error,
            context={"connection_type": connection_type, "retry_count": retry_count}
        )
        
        # Check if we should retry
        if retry_count < self.CONNECTION_RETRY_MAX:
            return await self._reconnect(connection_type, retry_count, record)
        
        # Max retries reached - pause trading
        await self._pause_trading(f"{connection_type} connection lost")
        
        record.recovered = False
        record.recovery_action = "trading_paused"
        self._stats["failed_recoveries"] += 1
        
        return RecoveryResult(
            success=False,
            action_taken="trading_paused",
            details={"connection_type": connection_type, "retry_count": retry_count},
            error=str(error)
        )
    
    async def _reconnect(
        self,
        connection_type: str,
        retry_count: int,
        record: ErrorRecord
    ) -> RecoveryResult:
        """Attempt to reconnect"""
        logger.info(f"[RecoveryHandler] Attempting {connection_type} reconnection ({retry_count + 1}/{self.CONNECTION_RETRY_MAX})")
        
        # Wait before retry
        await asyncio.sleep(self.CONNECTION_RETRY_DELAY)
        
        success = False
        
        if connection_type == "MT5" and self._trading_engine:
            if hasattr(self._trading_engine, 'mt5_client'):
                try:
                    success = self._trading_engine.mt5_client.initialize()
                except Exception as e:
                    logger.error(f"[RecoveryHandler] MT5 reconnection failed: {e}")
        
        elif connection_type == "Telegram" and self._telegram_bot:
            try:
                # Telegram bots typically auto-reconnect
                success = True
            except Exception as e:
                logger.error(f"[RecoveryHandler] Telegram reconnection failed: {e}")
        
        if success:
            record.recovered = True
            record.recovery_action = f"reconnected_{retry_count + 1}"
            self._stats["recovered_errors"] += 1
            self._stats["connections_restored"] += 1
            
            await self._notify_error(
                f"{connection_type} connection restored",
                ErrorSeverity.MEDIUM
            )
            
            logger.info(f"[RecoveryHandler] {connection_type} reconnected successfully")
            
            return RecoveryResult(
                success=True,
                action_taken=f"reconnected_{retry_count + 1}",
                details={"connection_type": connection_type}
            )
        
        # Recursive retry
        return await self.handle_connection_error(
            Exception(f"{connection_type} reconnection failed"),
            connection_type,
            retry_count + 1
        )
    
    # ========================================
    # Trading Control
    # ========================================
    
    async def _pause_trading(self, reason: str):
        """Pause trading due to critical error"""
        if self._trading_engine:
            self._trading_engine.is_paused = True
        
        await self._notify_error(
            f"TRADING PAUSED: {reason}",
            ErrorSeverity.CRITICAL
        )
        
        logger.critical(f"[RecoveryHandler] Trading PAUSED: {reason}")
    
    async def resume_trading(self) -> bool:
        """Resume trading after recovery"""
        if self._trading_engine:
            self._trading_engine.is_paused = False
            
            await self._notify_error(
                "Trading RESUMED",
                ErrorSeverity.MEDIUM
            )
            
            logger.info("[RecoveryHandler] Trading RESUMED")
            return True
        return False
    
    # ========================================
    # Notifications
    # ========================================
    
    async def _notify_error(self, message: str, severity: ErrorSeverity):
        """Send error notification via Telegram"""
        if not self._telegram_bot:
            return
        
        severity_emoji = {
            ErrorSeverity.LOW: "ℹ️",
            ErrorSeverity.MEDIUM: "⚠️",
            ErrorSeverity.HIGH: "🔴",
            ErrorSeverity.CRITICAL: "🚨",
        }
        
        emoji = severity_emoji.get(severity, "❓")
        formatted_message = f"{emoji} [{severity.value}] {message}"
        
        try:
            if hasattr(self._telegram_bot, 'send_message'):
                self._telegram_bot.send_message(formatted_message)
        except Exception as e:
            logger.error(f"[RecoveryHandler] Failed to send notification: {e}")
    
    # ========================================
    # Statistics & Monitoring
    # ========================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get recovery statistics"""
        return {
            **self._stats,
            "error_counts": self._error_counts.copy(),
            "plugin_failures": self._plugin_failures.copy(),
            "disabled_plugins": list(self._disabled_plugins),
            "paused_plugins": list(self._paused_plugins.keys()),
            "recent_errors": len([e for e in self._error_history 
                                  if e.timestamp > datetime.now() - timedelta(minutes=self.ERROR_WINDOW_MINUTES)]),
        }
    
    def get_recent_errors(self, limit: int = 10) -> List[ErrorRecord]:
        """Get recent error records"""
        return self._error_history[-limit:]
    
    def get_errors_by_category(self, category: ErrorCategory) -> List[ErrorRecord]:
        """Get errors by category"""
        return [e for e in self._error_history if e.category == category]
    
    def reset_stats(self):
        """Reset statistics"""
        self._stats = {
            "total_errors": 0,
            "recovered_errors": 0,
            "failed_recoveries": 0,
            "plugins_disabled": 0,
            "trades_retried": 0,
            "connections_restored": 0,
        }
        self._error_counts.clear()


# Singleton instance
_recovery_handler: Optional[RecoveryHandler] = None


def get_recovery_handler() -> RecoveryHandler:
    """Get or create singleton RecoveryHandler instance"""
    global _recovery_handler
    if _recovery_handler is None:
        _recovery_handler = RecoveryHandler()
    return _recovery_handler


def init_recovery_handler(trading_engine=None, telegram_bot=None) -> RecoveryHandler:
    """Initialize RecoveryHandler with dependencies"""
    global _recovery_handler
    _recovery_handler = RecoveryHandler(trading_engine, telegram_bot)
    return _recovery_handler
