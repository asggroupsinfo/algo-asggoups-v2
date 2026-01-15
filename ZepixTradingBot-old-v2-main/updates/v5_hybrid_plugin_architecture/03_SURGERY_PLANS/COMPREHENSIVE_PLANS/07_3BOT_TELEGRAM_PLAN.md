# PLAN 07: 3-BOT TELEGRAM MIGRATION

**Date:** 2026-01-15
**Priority:** P1 (High)
**Estimated Time:** 4-5 days
**Dependencies:** Plan 06 (Autonomous System)

---

## 1. OBJECTIVE

Migrate from monolithic Telegram bot to 3-Bot architecture. Currently all 95+ commands and 50+ notifications go through a single bot. After this plan:

1. **Controller Bot** - System commands (72 commands)
2. **Notification Bot** - Trade alerts (42 notifications)
3. **Analytics Bot** - Stats and reports (8 commands, 6 notifications)

**Current Problem (from Study Report 04, GAP-3):**
- 3 bot classes exist but ALL notifications still go through legacy bot
- Command routing not implemented
- Notification routing not implemented
- Analytics routing not implemented

**Target State:**
- Controller Bot handles all system commands
- Notification Bot handles all trade alerts
- Analytics Bot handles all stats/reports
- Legacy bot preserved as fallback

---

## 2. SCOPE

### In-Scope:
- Route commands to Controller Bot
- Route notifications to Notification Bot
- Route analytics to Analytics Bot
- Implement message routing logic
- Preserve legacy bot as fallback
- Migrate 95+ commands
- Migrate 50+ notifications

### Out-of-Scope:
- Creating new Telegram bots (already exist)
- Voice alert system (already integrated)
- Rate limiting (already implemented in Plan 05)

---

## 3. CURRENT STATE ANALYSIS

### File: `src/telegram/telegram_bot_fixed.py` (5126 lines)

**Current Structure (from Study Report 03):**
- Monolithic bot handling everything
- 95+ commands across 13 categories
- 50+ notification types across 8 categories
- All notifications go through single `send_notification()` method

### File: `src/telegram/controller_bot.py`

**Current Structure:**
- Bot class exists
- Command handlers defined
- **PROBLEM:** Not actually receiving commands

### File: `src/telegram/notification_bot.py`

**Current Structure:**
- Bot class exists
- Notification methods defined
- **PROBLEM:** Not actually receiving notifications

### File: `src/telegram/analytics_bot.py`

**Current Structure:**
- Bot class exists
- Analytics methods defined
- **PROBLEM:** Not actually receiving analytics

### File: `src/telegram/message_router.py`

**Current Structure:**
- Router class exists
- Routing logic defined
- **PROBLEM:** Not integrated with core

---

## 4. GAPS ADDRESSED

| Gap | Description | How Addressed |
|-----|-------------|---------------|
| GAP-3 | 3-Bot Telegram Integration | Route commands/notifications to correct bot |
| REQ-5.6 | 3-Bot Integration with Core | Wire router to core |
| REQ-5.7 | Command Routing to Controller | Implement command routing |
| REQ-5.8 | Notification Routing | Implement notification routing |
| REQ-5.9 | Analytics Routing | Implement analytics routing |

---

## 5. IMPLEMENTATION STEPS

### Step 1: Define Bot Responsibilities

**Command Distribution (from Study Report 03):**

**Controller Bot (72 commands):**
```
Category 1: Trading Control (7)
- /start, /stop, /pause, /resume, /status, /restart, /shutdown

Category 3: Strategy Control (8)
- /logic1_on, /logic1_off, /logic2_on, /logic2_off, /logic3_on, /logic3_off, /strategy, /symbols

Category 4: Re-entry System (14)
- /reentry_on, /reentry_off, /reentry_status, /chains, /chain_info, /sl_hunt_on, /sl_hunt_off, 
  /tp_cont_on, /tp_cont_off, /exit_cont_on, /exit_cont_off, /recovery_status, /recovery_windows, /autonomous_status

Category 5: Trend Management (5)
- /trends, /set_trend, /auto_trend, /trend_check, /trend_history

Category 6: Risk & Lot Management (11)
- /risk, /set_lot, /daily_limit, /set_daily_limit, /lifetime_limit, /reset_daily, /tier, 
  /balance, /margin, /equity, /risk_stats

Category 7: SL System Control (8)
- /sl_system, /sl1_on, /sl1_off, /sl2_on, /sl2_off, /sl_pips, /set_sl_pips, /sl_reduction

Category 8: Dual Orders (2)
- /dual_on, /dual_off

Category 9: Profit Booking (16)
- /profit_on, /profit_off, /profit_status, /profit_chains, /profit_chain_info, /profit_target,
  /set_profit_target, /profit_levels, /profit_multipliers, /profit_strict_on, /profit_strict_off,
  /profit_sl_hunt_on, /profit_sl_hunt_off, /profit_stats, /profit_history, /book_profit

Category 10: Timeframe Logic (4)
- /timeframe, /tf_multipliers, /set_tf_multiplier, /logic_alignment

Category 11: Fine-Tune Settings (4)
- /finetune, /set_recovery_window, /set_profit_protection, /set_concurrent_limit

Category 12: Session Management (5)
- /sessions, /session_on, /session_off, /overlap_on, /overlap_off

Category 13: Diagnostics & Health (15)
- /health, /mt5_status, /mt5_reconnect, /positions, /orders, /close_all, /close, /panic_close,
  /logs, /errors, /config, /reload_config, /version, /help, /debug
```

**Analytics Bot (8 commands):**
```
Category 2: Performance & Analytics (8)
- /daily, /weekly, /monthly, /pnl, /winrate, /performance, /stats, /history
```

**Notification Distribution:**

**Notification Bot (42 notifications):**
```
- Entry notifications (8): New trade, Order A opened, Order B opened, etc.
- Exit notifications (6): Trade closed, SL hit, TP hit, Manual close, etc.
- Re-entry notifications (8): Recovery started, Recovery success, Recovery failed, etc.
- Profit booking notifications (6): Profit booked, Chain advanced, Chain completed, etc.
- Risk notifications (6): Daily limit warning, Lot adjusted, Tier changed, etc.
- Trend notifications (4): Trend changed, Trend aligned, Trend conflict, etc.
```

**Controller Bot (8 system notifications):**
```
- System started, System stopped, Config reloaded, Error alert, etc.
```

**Analytics Bot (6 analytics notifications):**
```
- Daily summary, Weekly summary, Monthly summary, Performance alert, etc.
```

---

### Step 2: Update Message Router

**File:** `src/telegram/message_router.py`

**Changes:**
```python
"""
Message Router for 3-Bot Telegram System
Routes commands and notifications to appropriate bots
"""
from typing import Dict, Any, Optional, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class BotType(Enum):
    """Bot types in 3-bot system"""
    CONTROLLER = "controller"
    NOTIFICATION = "notification"
    ANALYTICS = "analytics"
    LEGACY = "legacy"  # Fallback

class MessageRouter:
    """Routes messages to appropriate Telegram bots"""
    
    # Command routing map
    CONTROLLER_COMMANDS = {
        # Trading Control
        'start', 'stop', 'pause', 'resume', 'status', 'restart', 'shutdown',
        # Strategy Control
        'logic1_on', 'logic1_off', 'logic2_on', 'logic2_off', 'logic3_on', 'logic3_off', 'strategy', 'symbols',
        # Re-entry System
        'reentry_on', 'reentry_off', 'reentry_status', 'chains', 'chain_info', 'sl_hunt_on', 'sl_hunt_off',
        'tp_cont_on', 'tp_cont_off', 'exit_cont_on', 'exit_cont_off', 'recovery_status', 'recovery_windows', 'autonomous_status',
        # Trend Management
        'trends', 'set_trend', 'auto_trend', 'trend_check', 'trend_history',
        # Risk & Lot Management
        'risk', 'set_lot', 'daily_limit', 'set_daily_limit', 'lifetime_limit', 'reset_daily', 'tier',
        'balance', 'margin', 'equity', 'risk_stats',
        # SL System Control
        'sl_system', 'sl1_on', 'sl1_off', 'sl2_on', 'sl2_off', 'sl_pips', 'set_sl_pips', 'sl_reduction',
        # Dual Orders
        'dual_on', 'dual_off',
        # Profit Booking
        'profit_on', 'profit_off', 'profit_status', 'profit_chains', 'profit_chain_info', 'profit_target',
        'set_profit_target', 'profit_levels', 'profit_multipliers', 'profit_strict_on', 'profit_strict_off',
        'profit_sl_hunt_on', 'profit_sl_hunt_off', 'profit_stats', 'profit_history', 'book_profit',
        # Timeframe Logic
        'timeframe', 'tf_multipliers', 'set_tf_multiplier', 'logic_alignment',
        # Fine-Tune Settings
        'finetune', 'set_recovery_window', 'set_profit_protection', 'set_concurrent_limit',
        # Session Management
        'sessions', 'session_on', 'session_off', 'overlap_on', 'overlap_off',
        # Diagnostics & Health
        'health', 'mt5_status', 'mt5_reconnect', 'positions', 'orders', 'close_all', 'close', 'panic_close',
        'logs', 'errors', 'config', 'reload_config', 'version', 'help', 'debug'
    }
    
    ANALYTICS_COMMANDS = {
        'daily', 'weekly', 'monthly', 'pnl', 'winrate', 'performance', 'stats', 'history'
    }
    
    # Notification routing map
    NOTIFICATION_TYPES = {
        # Entry notifications -> Notification Bot
        'trade_opened', 'order_a_opened', 'order_b_opened', 'signal_received',
        'dual_order_created', 'position_opened', 'entry_executed', 'pending_order_placed',
        # Exit notifications -> Notification Bot
        'trade_closed', 'sl_hit', 'tp_hit', 'manual_close', 'reversal_close', 'position_closed',
        # Re-entry notifications -> Notification Bot
        'recovery_started', 'recovery_success', 'recovery_failed', 'recovery_timeout',
        'sl_hunt_started', 'sl_hunt_success', 'tp_continuation_started', 'exit_continuation_started',
        # Profit booking notifications -> Notification Bot
        'profit_booked', 'chain_advanced', 'chain_completed', 'chain_sl_hit',
        'profit_target_hit', 'pyramid_level_up',
        # Risk notifications -> Notification Bot
        'daily_limit_warning', 'daily_limit_reached', 'lot_adjusted', 'tier_changed',
        'lifetime_limit_warning', 'margin_warning',
        # Trend notifications -> Notification Bot
        'trend_changed', 'trend_aligned', 'trend_conflict', 'trend_pulse_update'
    }
    
    SYSTEM_NOTIFICATIONS = {
        # System notifications -> Controller Bot
        'system_started', 'system_stopped', 'config_reloaded', 'error_alert',
        'mt5_connected', 'mt5_disconnected', 'plugin_enabled', 'plugin_disabled'
    }
    
    ANALYTICS_NOTIFICATIONS = {
        # Analytics notifications -> Analytics Bot
        'daily_summary', 'weekly_summary', 'monthly_summary',
        'performance_alert', 'drawdown_alert', 'profit_milestone'
    }
    
    def __init__(self, controller_bot, notification_bot, analytics_bot, legacy_bot=None):
        self.controller_bot = controller_bot
        self.notification_bot = notification_bot
        self.analytics_bot = analytics_bot
        self.legacy_bot = legacy_bot
        
        self._use_legacy_fallback = legacy_bot is not None
        self._routing_stats = {
            'commands_routed': 0,
            'notifications_routed': 0,
            'fallback_used': 0
        }
    
    def get_bot_for_command(self, command: str) -> BotType:
        """Determine which bot should handle a command"""
        command = command.lower().strip('/')
        
        if command in self.CONTROLLER_COMMANDS:
            return BotType.CONTROLLER
        elif command in self.ANALYTICS_COMMANDS:
            return BotType.ANALYTICS
        else:
            logger.warning(f"Unknown command: {command}, using legacy")
            return BotType.LEGACY
    
    def get_bot_for_notification(self, notification_type: str) -> BotType:
        """Determine which bot should handle a notification"""
        notification_type = notification_type.lower()
        
        if notification_type in self.NOTIFICATION_TYPES:
            return BotType.NOTIFICATION
        elif notification_type in self.SYSTEM_NOTIFICATIONS:
            return BotType.CONTROLLER
        elif notification_type in self.ANALYTICS_NOTIFICATIONS:
            return BotType.ANALYTICS
        else:
            logger.warning(f"Unknown notification type: {notification_type}, using notification bot")
            return BotType.NOTIFICATION
    
    async def route_command(self, command: str, *args, **kwargs):
        """Route a command to the appropriate bot"""
        bot_type = self.get_bot_for_command(command)
        self._routing_stats['commands_routed'] += 1
        
        try:
            if bot_type == BotType.CONTROLLER:
                return await self.controller_bot.handle_command(command, *args, **kwargs)
            elif bot_type == BotType.ANALYTICS:
                return await self.analytics_bot.handle_command(command, *args, **kwargs)
            elif bot_type == BotType.LEGACY and self.legacy_bot:
                self._routing_stats['fallback_used'] += 1
                return await self.legacy_bot.handle_command(command, *args, **kwargs)
        except Exception as e:
            logger.error(f"Command routing failed: {e}")
            if self._use_legacy_fallback and self.legacy_bot:
                self._routing_stats['fallback_used'] += 1
                return await self.legacy_bot.handle_command(command, *args, **kwargs)
            raise
    
    async def route_notification(self, notification_type: str, message: str, **kwargs):
        """Route a notification to the appropriate bot"""
        bot_type = self.get_bot_for_notification(notification_type)
        self._routing_stats['notifications_routed'] += 1
        
        try:
            if bot_type == BotType.NOTIFICATION:
                return await self.notification_bot.send_notification(notification_type, message, **kwargs)
            elif bot_type == BotType.CONTROLLER:
                return await self.controller_bot.send_system_notification(notification_type, message, **kwargs)
            elif bot_type == BotType.ANALYTICS:
                return await self.analytics_bot.send_analytics_notification(notification_type, message, **kwargs)
        except Exception as e:
            logger.error(f"Notification routing failed: {e}")
            if self._use_legacy_fallback and self.legacy_bot:
                self._routing_stats['fallback_used'] += 1
                return await self.legacy_bot.send_notification(message)
            raise
    
    def get_routing_stats(self) -> Dict[str, int]:
        """Get routing statistics"""
        return self._routing_stats.copy()
```

**Reason:** Centralizes routing logic for all commands and notifications.

---

### Step 3: Update Multi-Telegram Manager

**File:** `src/telegram/multi_telegram_manager.py`

**Changes:**
```python
"""
Multi-Telegram Manager
Manages all 3 Telegram bots and provides unified interface
"""
from typing import Dict, Any, Optional
import logging
from src.telegram.controller_bot import ControllerBot
from src.telegram.notification_bot import NotificationBot
from src.telegram.analytics_bot import AnalyticsBot
from src.telegram.message_router import MessageRouter
from src.telegram.telegram_bot_fixed import TelegramBotFixed  # Legacy

logger = logging.getLogger(__name__)

class MultiTelegramManager:
    """Manages the 3-bot Telegram system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize bots
        self.controller_bot = ControllerBot(config.get('controller_bot', {}))
        self.notification_bot = NotificationBot(config.get('notification_bot', {}))
        self.analytics_bot = AnalyticsBot(config.get('analytics_bot', {}))
        
        # Legacy bot for fallback
        self.legacy_bot = TelegramBotFixed(config.get('legacy_bot', {})) if config.get('enable_legacy_fallback', True) else None
        
        # Initialize router
        self.router = MessageRouter(
            self.controller_bot,
            self.notification_bot,
            self.analytics_bot,
            self.legacy_bot
        )
        
        self._initialized = False
    
    async def initialize(self):
        """Initialize all bots"""
        logger.info("Initializing 3-bot Telegram system...")
        
        await self.controller_bot.initialize()
        await self.notification_bot.initialize()
        await self.analytics_bot.initialize()
        
        if self.legacy_bot:
            await self.legacy_bot.initialize()
        
        self._initialized = True
        logger.info("3-bot Telegram system initialized")
    
    async def shutdown(self):
        """Shutdown all bots"""
        logger.info("Shutting down 3-bot Telegram system...")
        
        await self.controller_bot.shutdown()
        await self.notification_bot.shutdown()
        await self.analytics_bot.shutdown()
        
        if self.legacy_bot:
            await self.legacy_bot.shutdown()
        
        self._initialized = False
    
    # ==================== Unified Interface ====================
    
    async def send_notification(self, notification_type: str, message: str, **kwargs):
        """Send notification through router"""
        if not self._initialized:
            logger.warning("Telegram system not initialized")
            return
        
        await self.router.route_notification(notification_type, message, **kwargs)
    
    async def handle_command(self, command: str, *args, **kwargs):
        """Handle command through router"""
        if not self._initialized:
            logger.warning("Telegram system not initialized")
            return
        
        return await self.router.route_command(command, *args, **kwargs)
    
    # ==================== Convenience Methods ====================
    
    async def send_trade_notification(self, trade_data: Dict[str, Any]):
        """Send trade notification"""
        notification_type = trade_data.get('type', 'trade_opened')
        message = self._format_trade_message(trade_data)
        await self.send_notification(notification_type, message, trade_data=trade_data)
    
    async def send_system_alert(self, alert_type: str, message: str):
        """Send system alert"""
        await self.send_notification(alert_type, message)
    
    async def send_daily_summary(self, summary_data: Dict[str, Any]):
        """Send daily summary"""
        message = self._format_summary_message(summary_data)
        await self.send_notification('daily_summary', message, summary_data=summary_data)
    
    def _format_trade_message(self, trade_data: Dict[str, Any]) -> str:
        """Format trade notification message"""
        symbol = trade_data.get('symbol', 'UNKNOWN')
        direction = trade_data.get('direction', 'UNKNOWN')
        price = trade_data.get('price', 0)
        
        return f"Trade: {direction} {symbol} @ {price}"
    
    def _format_summary_message(self, summary_data: Dict[str, Any]) -> str:
        """Format summary message"""
        profit = summary_data.get('profit', 0)
        trades = summary_data.get('trades', 0)
        winrate = summary_data.get('winrate', 0)
        
        return f"Daily Summary: ${profit:.2f} | {trades} trades | {winrate:.1f}% winrate"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Telegram system statistics"""
        return {
            'initialized': self._initialized,
            'routing_stats': self.router.get_routing_stats(),
            'controller_bot_active': self.controller_bot.is_active() if hasattr(self.controller_bot, 'is_active') else True,
            'notification_bot_active': self.notification_bot.is_active() if hasattr(self.notification_bot, 'is_active') else True,
            'analytics_bot_active': self.analytics_bot.is_active() if hasattr(self.analytics_bot, 'is_active') else True
        }
```

**Reason:** Provides unified interface for the 3-bot system.

---

### Step 4: Wire Core to Use Multi-Telegram Manager

**File:** `src/core/trading_engine.py`

**Changes:**
```python
# ADD import
from src.telegram.multi_telegram_manager import MultiTelegramManager

# UPDATE TradingEngine class
class TradingEngine:
    def __init__(self, config: Dict[str, Any]):
        # ... existing init ...
        
        # Initialize Telegram system
        self.telegram_manager = MultiTelegramManager(config.get('telegram', {}))
    
    async def initialize(self):
        # ... existing init ...
        
        # Initialize Telegram
        await self.telegram_manager.initialize()
    
    async def send_notification(self, notification_type: str, message: str, **kwargs):
        """Send notification through Telegram system"""
        await self.telegram_manager.send_notification(notification_type, message, **kwargs)
    
    async def on_trade_opened(self, trade_data: Dict[str, Any]):
        """Called when a trade is opened"""
        await self.telegram_manager.send_trade_notification({
            'type': 'trade_opened',
            **trade_data
        })
    
    async def on_trade_closed(self, trade_data: Dict[str, Any]):
        """Called when a trade is closed"""
        await self.telegram_manager.send_trade_notification({
            'type': 'trade_closed',
            **trade_data
        })
```

**Reason:** Wires core to use the new 3-bot system.

---

### Step 5: Update Plugins to Use Telegram Notifications

**File:** `src/logic_plugins/combined_v3/plugin.py`

**Changes:**
```python
# ADD notification methods

async def _send_notification(self, notification_type: str, message: str, **kwargs):
    """Send notification through ServiceAPI"""
    if hasattr(self, '_service_api') and self._service_api:
        await self._service_api.send_notification(notification_type, message, **kwargs)

async def on_trade_opened(self, order_id: str, order_type: str, details: Dict[str, Any]):
    """Notify when trade is opened"""
    notification_type = 'order_a_opened' if order_type == 'order_a' else 'order_b_opened'
    message = f"{order_type.upper()} opened: {details.get('symbol')} {details.get('direction')}"
    await self._send_notification(notification_type, message, order_id=order_id, **details)

async def on_trade_closed(self, order_id: str, reason: str, details: Dict[str, Any]):
    """Notify when trade is closed"""
    notification_type = 'sl_hit' if reason == 'SL_HIT' else 'tp_hit' if reason == 'TP_HIT' else 'trade_closed'
    message = f"Trade closed ({reason}): {details.get('symbol')} P/L: ${details.get('profit', 0):.2f}"
    await self._send_notification(notification_type, message, order_id=order_id, reason=reason, **details)

async def on_recovery_started(self, trade_id: str, recovery_type: str, details: Dict[str, Any]):
    """Notify when recovery starts"""
    notification_type = f'{recovery_type}_started'
    message = f"Recovery started: {recovery_type} for {details.get('symbol')}"
    await self._send_notification(notification_type, message, trade_id=trade_id, **details)
```

**Reason:** Plugins send notifications through the new system.

---

### Step 6: Create 3-Bot Integration Tests

**File:** `tests/test_3bot_telegram.py` (NEW)

**Code:**
```python
"""
Tests for 3-Bot Telegram System
Verifies commands and notifications are routed correctly
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.telegram.message_router import MessageRouter, BotType
from src.telegram.multi_telegram_manager import MultiTelegramManager

class TestMessageRouter:
    """Test message routing"""
    
    @pytest.fixture
    def router(self):
        """Create router with mocks"""
        controller = MagicMock()
        controller.handle_command = AsyncMock()
        controller.send_system_notification = AsyncMock()
        
        notification = MagicMock()
        notification.send_notification = AsyncMock()
        
        analytics = MagicMock()
        analytics.handle_command = AsyncMock()
        analytics.send_analytics_notification = AsyncMock()
        
        return MessageRouter(controller, notification, analytics)
    
    def test_controller_command_routing(self, router):
        """Test controller commands are routed correctly"""
        controller_commands = ['start', 'stop', 'status', 'health', 'panic_close']
        
        for cmd in controller_commands:
            bot_type = router.get_bot_for_command(cmd)
            assert bot_type == BotType.CONTROLLER, f"Command {cmd} should route to CONTROLLER"
    
    def test_analytics_command_routing(self, router):
        """Test analytics commands are routed correctly"""
        analytics_commands = ['daily', 'weekly', 'monthly', 'pnl', 'stats']
        
        for cmd in analytics_commands:
            bot_type = router.get_bot_for_command(cmd)
            assert bot_type == BotType.ANALYTICS, f"Command {cmd} should route to ANALYTICS"
    
    def test_notification_routing(self, router):
        """Test notifications are routed correctly"""
        trade_notifications = ['trade_opened', 'sl_hit', 'tp_hit', 'recovery_started']
        
        for notif in trade_notifications:
            bot_type = router.get_bot_for_notification(notif)
            assert bot_type == BotType.NOTIFICATION, f"Notification {notif} should route to NOTIFICATION"
    
    def test_system_notification_routing(self, router):
        """Test system notifications route to controller"""
        system_notifications = ['system_started', 'system_stopped', 'error_alert']
        
        for notif in system_notifications:
            bot_type = router.get_bot_for_notification(notif)
            assert bot_type == BotType.CONTROLLER, f"Notification {notif} should route to CONTROLLER"
    
    def test_analytics_notification_routing(self, router):
        """Test analytics notifications route to analytics bot"""
        analytics_notifications = ['daily_summary', 'weekly_summary', 'performance_alert']
        
        for notif in analytics_notifications:
            bot_type = router.get_bot_for_notification(notif)
            assert bot_type == BotType.ANALYTICS, f"Notification {notif} should route to ANALYTICS"
    
    @pytest.mark.asyncio
    async def test_route_command_to_controller(self, router):
        """Test command routing execution"""
        await router.route_command('status')
        
        router.controller_bot.handle_command.assert_called_once_with('status')
    
    @pytest.mark.asyncio
    async def test_route_notification_to_notification_bot(self, router):
        """Test notification routing execution"""
        await router.route_notification('trade_opened', 'Test message')
        
        router.notification_bot.send_notification.assert_called_once()

class TestMultiTelegramManager:
    """Test multi-telegram manager"""
    
    @pytest.fixture
    def manager(self):
        """Create manager with mock config"""
        config = {
            'controller_bot': {'token': 'test_token_1'},
            'notification_bot': {'token': 'test_token_2'},
            'analytics_bot': {'token': 'test_token_3'},
            'enable_legacy_fallback': False
        }
        return MultiTelegramManager(config)
    
    def test_manager_initialization(self, manager):
        """Test manager creates all bots"""
        assert manager.controller_bot is not None
        assert manager.notification_bot is not None
        assert manager.analytics_bot is not None
        assert manager.router is not None
    
    def test_stats_before_init(self, manager):
        """Test stats before initialization"""
        stats = manager.get_stats()
        
        assert stats['initialized'] == False
```

**Reason:** Verifies 3-bot routing works correctly.

---

## 6. DEPENDENCIES

### Prerequisites:
- Plan 06 (Autonomous System) - Safety status commands

### Blocks:
- Plan 08 (Service API) - Needs Telegram integration

---

## 7. FILES AFFECTED

| File | Action | Description |
|------|--------|-------------|
| `src/telegram/message_router.py` | MODIFY | Add routing logic |
| `src/telegram/multi_telegram_manager.py` | MODIFY | Add unified interface |
| `src/core/trading_engine.py` | MODIFY | Wire to Telegram |
| `src/logic_plugins/combined_v3/plugin.py` | MODIFY | Add notifications |
| `tests/test_3bot_telegram.py` | CREATE | Tests |

---

## 8. SUCCESS CRITERIA

1. ✅ MessageRouter routes commands correctly
2. ✅ MessageRouter routes notifications correctly
3. ✅ Controller Bot receives 72 commands
4. ✅ Notification Bot receives 42 notifications
5. ✅ Analytics Bot receives 8 commands + 6 notifications
6. ✅ Legacy fallback works
7. ✅ Plugins send notifications through new system
8. ✅ All tests pass

---

## 11. REFERENCES

- **Study Report 03:** Complete Telegram audit (95+ commands, 50+ notifications)
- **Study Report 04:** GAP-3, REQ-5.6-5.9
- **Code Evidence:** `src/telegram/` directory

---

**END OF PLAN 07**
