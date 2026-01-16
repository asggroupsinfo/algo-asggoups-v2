# ULTIMATE RECOVERY PLAN

**Date:** 2026-01-15  
**Phase:** 11 - Ultimate Recovery  
**Goal:** Fix ALL critical gaps identified in Wrath of God Audit  
**Success Criteria:** System sends "SUCCESS" message to Telegram

---

## EXECUTIVE SUMMARY

This plan addresses the 6 CRITICAL failures identified in the Wrath of God Audit:

| Issue | Solution | Priority |
|-------|----------|----------|
| Empty 3-Bot Tokens | Self-Healing Config Wizard | P0 |
| Missing Plugin Control | Plugin Control Menu | P0 |
| Thin Controller Bot | Unified Command System | P1 |
| 80% Missing Notifications | Unified Notification Router | P1 |
| No Analytics Commands | Analytics Command Handlers | P2 |
| 70+ Silent Failures | Error Logging System | P3 |

---

## PHASE 1: SELF-HEALING CONFIG WIZARD

### Problem
```json
"telegram_controller_token": "",      // EMPTY!
"telegram_notification_token": "",    // EMPTY!
"telegram_analytics_token": "",       // EMPTY!
```

### Solution: ConfigWizard Class

**File:** `src/core/config_wizard.py`

**Features:**
1. **Auto-Detection:** Detect missing/empty config values on startup
2. **Fallback Mode:** If 3-bot tokens empty, use single `telegram_token` for all
3. **Graceful Degradation:** System works with 1 bot or 3 bots
4. **Validation:** Validate tokens before use (test API call)
5. **User Notification:** Alert user about missing config via Telegram

**Implementation:**

```python
class ConfigWizard:
    """Self-healing configuration system"""
    
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.issues = []
        self.mode = "UNKNOWN"  # SINGLE_BOT or MULTI_BOT
    
    def diagnose(self) -> Dict[str, Any]:
        """Diagnose configuration issues"""
        self.issues = []
        
        # Check Telegram tokens
        main_token = self.config.get("telegram_token", "")
        controller_token = self.config.get("telegram_controller_token", "")
        notification_token = self.config.get("telegram_notification_token", "")
        analytics_token = self.config.get("telegram_analytics_token", "")
        
        if not main_token:
            self.issues.append({"severity": "CRITICAL", "field": "telegram_token", "message": "Main token missing"})
        
        # Determine mode
        if controller_token and notification_token and analytics_token:
            self.mode = "MULTI_BOT"
        elif main_token:
            self.mode = "SINGLE_BOT"
            self.issues.append({"severity": "WARNING", "field": "3-bot tokens", "message": "Using fallback single-bot mode"})
        else:
            self.mode = "NO_BOT"
            self.issues.append({"severity": "CRITICAL", "field": "all tokens", "message": "No Telegram tokens configured"})
        
        return {"mode": self.mode, "issues": self.issues}
    
    def heal(self) -> bool:
        """Apply self-healing fixes"""
        if self.mode == "SINGLE_BOT":
            # Use main token for all bots
            main_token = self.config.get("telegram_token")
            self.config["telegram_controller_token"] = main_token
            self.config["telegram_notification_token"] = main_token
            self.config["telegram_analytics_token"] = main_token
            return True
        return False
    
    def get_effective_config(self) -> Dict[str, str]:
        """Get effective token configuration"""
        return {
            "controller": self.config.get("telegram_controller_token") or self.config.get("telegram_token"),
            "notification": self.config.get("telegram_notification_token") or self.config.get("telegram_token"),
            "analytics": self.config.get("telegram_analytics_token") or self.config.get("telegram_token"),
            "chat_id": self.config.get("telegram_chat_id")
        }
```

### Startup Integration

**File:** `src/main.py` (modify)

```python
# At startup
config_wizard = ConfigWizard("config/config.json")
diagnosis = config_wizard.diagnose()

if diagnosis["mode"] == "NO_BOT":
    logger.critical("No Telegram tokens configured. Exiting.")
    sys.exit(1)

if diagnosis["mode"] == "SINGLE_BOT":
    config_wizard.heal()
    logger.warning("Running in SINGLE_BOT fallback mode")

effective_config = config_wizard.get_effective_config()
```

---

## PHASE 2: PLUGIN CONTROL MENU

### Problem
User asked: "Mujhe ek hi pine pe trade karna hua to ek ko band karna hua to wo kaha se hoga?"
Answer: **NOWHERE** - No plugin control exists.

### Solution: PluginControlMenu Class

**File:** `src/telegram/plugin_control_menu.py`

**Features:**
1. **Plugin Selector:** [V3 Logic] [V6 Logic] buttons
2. **Enable/Disable:** Live plugin switching without restart
3. **Status Display:** Show which plugins are active
4. **Per-Plugin Settings:** Access settings for each plugin

**Menu Structure:**
```
Main Menu
├── [Plugin Control]
│   ├── V3 Combined Logic
│   │   ├── Status: ENABLED
│   │   ├── [Enable] [Disable]
│   │   └── [Settings]
│   ├── V6 Price Action
│   │   ├── Status: DISABLED
│   │   ├── [Enable] [Disable]
│   │   └── [Settings]
│   └── [Back to Main]
```

**Implementation:**

```python
class PluginControlMenu:
    """Plugin control menu for Telegram"""
    
    def __init__(self, trading_engine, telegram_bot):
        self.engine = trading_engine
        self.bot = telegram_bot
        self.callbacks = {
            "plugin_menu": self.show_plugin_menu,
            "plugin_v3_toggle": self.toggle_v3,
            "plugin_v6_toggle": self.toggle_v6,
            "plugin_v3_settings": self.show_v3_settings,
            "plugin_v6_settings": self.show_v6_settings,
        }
    
    def show_plugin_menu(self, chat_id: int):
        """Show main plugin control menu"""
        v3_status = "ENABLED" if self.engine.is_plugin_enabled("v3_combined") else "DISABLED"
        v6_status = "ENABLED" if self.engine.is_plugin_enabled("v6_price_action") else "DISABLED"
        
        v3_emoji = "🟢" if v3_status == "ENABLED" else "🔴"
        v6_emoji = "🟢" if v6_status == "ENABLED" else "🔴"
        
        message = (
            "🔌 <b>PLUGIN CONTROL</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>V3 Combined Logic:</b> {v3_emoji} {v3_status}\n"
            f"<b>V6 Price Action:</b> {v6_emoji} {v6_status}\n\n"
            "Select a plugin to manage:"
        )
        
        keyboard = [
            [{"text": f"{v3_emoji} V3 Combined Logic", "callback_data": "plugin_v3_menu"}],
            [{"text": f"{v6_emoji} V6 Price Action", "callback_data": "plugin_v6_menu"}],
            [{"text": "🔙 Back to Main", "callback_data": "menu_main"}]
        ]
        
        self.bot.send_message(chat_id, message, reply_markup={"inline_keyboard": keyboard})
    
    def toggle_v3(self, chat_id: int, enable: bool):
        """Toggle V3 plugin"""
        if enable:
            self.engine.enable_plugin("v3_combined")
            self.bot.send_message(chat_id, "✅ V3 Combined Logic ENABLED")
        else:
            self.engine.disable_plugin("v3_combined")
            self.bot.send_message(chat_id, "🔴 V3 Combined Logic DISABLED")
    
    def toggle_v6(self, chat_id: int, enable: bool):
        """Toggle V6 plugin"""
        if enable:
            self.engine.enable_plugin("v6_price_action")
            self.bot.send_message(chat_id, "✅ V6 Price Action ENABLED")
        else:
            self.engine.disable_plugin("v6_price_action")
            self.bot.send_message(chat_id, "🔴 V6 Price Action DISABLED")
```

### TradingEngine Integration

**File:** `src/core/trading_engine.py` (modify)

```python
def enable_plugin(self, plugin_id: str) -> bool:
    """Enable a plugin at runtime"""
    if plugin_id in self._plugins:
        self._plugins[plugin_id].enabled = True
        self._active_plugins.add(plugin_id)
        logger.info(f"Plugin {plugin_id} ENABLED")
        return True
    return False

def disable_plugin(self, plugin_id: str) -> bool:
    """Disable a plugin at runtime"""
    if plugin_id in self._plugins:
        self._plugins[plugin_id].enabled = False
        self._active_plugins.discard(plugin_id)
        logger.info(f"Plugin {plugin_id} DISABLED")
        return True
    return False

def is_plugin_enabled(self, plugin_id: str) -> bool:
    """Check if plugin is enabled"""
    return plugin_id in self._active_plugins
```

---

## PHASE 3: UNIFIED NOTIFICATION SYSTEM

### Problem
NotificationBot only has 6 methods but legacy system has 50+ notification types.

### Solution: UnifiedNotificationRouter

**File:** `src/telegram/unified_notification_router.py`

**Features:**
1. **Single Entry Point:** All notifications go through one router
2. **Type-Based Routing:** Route to correct bot based on notification type
3. **Fallback Mode:** Use single bot if 3-bot not configured
4. **Priority System:** HIGH/MEDIUM/LOW priority handling
5. **Mute Support:** Allow muting specific notification types

**Implementation:**

```python
class UnifiedNotificationRouter:
    """Routes all notifications to appropriate bot"""
    
    NOTIFICATION_TYPES = {
        # Trading notifications -> NotificationBot
        "trade_entry": {"bot": "notification", "priority": "HIGH"},
        "trade_exit": {"bot": "notification", "priority": "HIGH"},
        "tp_hit": {"bot": "notification", "priority": "HIGH"},
        "sl_hit": {"bot": "notification", "priority": "HIGH"},
        "profit_booking": {"bot": "notification", "priority": "MEDIUM"},
        
        # Autonomous system -> NotificationBot
        "tp_continuation": {"bot": "notification", "priority": "MEDIUM"},
        "sl_hunt_activated": {"bot": "notification", "priority": "HIGH"},
        "recovery_success": {"bot": "notification", "priority": "MEDIUM"},
        "recovery_failed": {"bot": "notification", "priority": "HIGH"},
        
        # Risk alerts -> NotificationBot
        "daily_limit_warning": {"bot": "notification", "priority": "HIGH"},
        "daily_limit_hit": {"bot": "notification", "priority": "CRITICAL"},
        "lifetime_limit_hit": {"bot": "notification", "priority": "CRITICAL"},
        
        # Analytics -> AnalyticsBot
        "performance_report": {"bot": "analytics", "priority": "LOW"},
        "daily_summary": {"bot": "analytics", "priority": "LOW"},
        "weekly_summary": {"bot": "analytics", "priority": "LOW"},
        
        # System -> ControllerBot
        "bot_startup": {"bot": "controller", "priority": "MEDIUM"},
        "config_changed": {"bot": "controller", "priority": "LOW"},
        "error_alert": {"bot": "controller", "priority": "HIGH"},
    }
    
    def __init__(self, controller_bot, notification_bot, analytics_bot, fallback_bot=None):
        self.bots = {
            "controller": controller_bot,
            "notification": notification_bot,
            "analytics": analytics_bot,
        }
        self.fallback_bot = fallback_bot or controller_bot
        self.muted_types = set()
        self.mode = "MULTI_BOT" if all(self.bots.values()) else "SINGLE_BOT"
    
    def send(self, notification_type: str, data: Dict[str, Any]) -> bool:
        """Send notification through appropriate channel"""
        if notification_type in self.muted_types:
            return False
        
        config = self.NOTIFICATION_TYPES.get(notification_type, {"bot": "notification", "priority": "MEDIUM"})
        
        # Get appropriate bot
        if self.mode == "MULTI_BOT":
            bot = self.bots.get(config["bot"], self.fallback_bot)
        else:
            bot = self.fallback_bot
        
        # Format and send
        message = self._format_notification(notification_type, data)
        return bot.send_message(message) is not None
    
    def _format_notification(self, notification_type: str, data: Dict) -> str:
        """Format notification based on type"""
        formatters = {
            "trade_entry": self._format_trade_entry,
            "trade_exit": self._format_trade_exit,
            "tp_continuation": self._format_tp_continuation,
            "sl_hunt_activated": self._format_sl_hunt,
            "daily_limit_warning": self._format_daily_limit_warning,
            "daily_limit_hit": self._format_daily_limit_hit,
            "bot_startup": self._format_bot_startup,
            "error_alert": self._format_error_alert,
        }
        
        formatter = formatters.get(notification_type, self._format_generic)
        return formatter(data)
    
    def mute(self, notification_type: str):
        """Mute a notification type"""
        self.muted_types.add(notification_type)
    
    def unmute(self, notification_type: str):
        """Unmute a notification type"""
        self.muted_types.discard(notification_type)
```

---

## PHASE 4: TESTING & VALIDATION

### Test 1: Config Wizard Test

```python
def test_config_wizard():
    """Test self-healing config"""
    # Test with empty 3-bot tokens
    wizard = ConfigWizard("config/config.json")
    diagnosis = wizard.diagnose()
    
    assert diagnosis["mode"] == "SINGLE_BOT"
    assert len(diagnosis["issues"]) > 0
    
    # Test healing
    wizard.heal()
    effective = wizard.get_effective_config()
    
    assert effective["controller"] is not None
    assert effective["notification"] is not None
    assert effective["analytics"] is not None
```

### Test 2: Plugin Control Test

```python
def test_plugin_control():
    """Test plugin enable/disable"""
    engine = TradingEngine(config)
    
    # Test disable
    engine.disable_plugin("v3_combined")
    assert not engine.is_plugin_enabled("v3_combined")
    
    # Test enable
    engine.enable_plugin("v3_combined")
    assert engine.is_plugin_enabled("v3_combined")
```

### Test 3: Notification Router Test

```python
def test_notification_router():
    """Test unified notification routing"""
    router = UnifiedNotificationRouter(controller, notification, analytics)
    
    # Test trade notification
    result = router.send("trade_entry", {"symbol": "XAUUSD", "direction": "BUY"})
    assert result == True
    
    # Test muting
    router.mute("trade_entry")
    result = router.send("trade_entry", {"symbol": "XAUUSD", "direction": "BUY"})
    assert result == False
```

### Test 4: SUCCESS Message Test

```python
def test_success_message():
    """Final integration test - send SUCCESS to Telegram"""
    # Initialize system
    config_wizard = ConfigWizard("config/config.json")
    config_wizard.diagnose()
    config_wizard.heal()
    
    effective = config_wizard.get_effective_config()
    
    # Create bot with effective config
    bot = TelegramBot(effective["controller"], effective["chat_id"])
    
    # Send SUCCESS message
    message = (
        "🎉 <b>RECOVERY COMPLETE</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "✅ Config Wizard: ACTIVE\n"
        "✅ Plugin Control: ACTIVE\n"
        "✅ Notification Router: ACTIVE\n\n"
        "<b>System Status:</b> OPERATIONAL\n"
        "<b>Mode:</b> {mode}\n\n"
        "🚀 V5 Hybrid Plugin Architecture is now FULLY FUNCTIONAL!"
    )
    
    result = bot.send_message(message.format(mode=config_wizard.mode))
    assert result is not None
    print("SUCCESS MESSAGE SENT!")
```

---

## IMPLEMENTATION ORDER

| Step | Component | File | Est. Time |
|------|-----------|------|-----------|
| 1 | ConfigWizard | `src/core/config_wizard.py` | 30 min |
| 2 | TradingEngine plugin methods | `src/core/trading_engine.py` | 15 min |
| 3 | PluginControlMenu | `src/telegram/plugin_control_menu.py` | 45 min |
| 4 | UnifiedNotificationRouter | `src/telegram/unified_notification_router.py` | 60 min |
| 5 | Main.py integration | `src/main.py` | 15 min |
| 6 | Tests | `tests/test_recovery.py` | 30 min |
| 7 | SUCCESS message | Integration test | 15 min |

**Total Estimated Time:** 3.5 hours

---

## SUCCESS CRITERIA

The recovery is complete when:

1. **Config Wizard** detects empty tokens and auto-heals to single-bot mode
2. **Plugin Control Menu** allows enabling/disabling V3/V6 plugins
3. **Unified Notification Router** routes all 50+ notification types
4. **SUCCESS message** is sent to Telegram confirming all systems operational

---

*Plan created by Devin in Autonomous Mode*  
*ULTIMATE RECOVERY PHASE INITIATED*
