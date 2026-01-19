# 📋 COMPLETE TELEGRAM COMMAND INVENTORY

**Generated:** January 19, 2026  
**Bot Version:** V5 Hybrid Plugin Architecture  
**Total Commands Found:** 95+  
**Implementation Status:** 72 Working (76%) | 15 Partial (16%) | 8 Missing (8%)

---

## 📊 COMMAND SUMMARY BY CATEGORY

| Category | Commands | Working | Partial | Missing |
|----------|----------|---------|---------|---------|
| 💰 Trading Control | 8 | 8 | 0 | 0 |
| ⚡ Performance & Analytics | 12 | 7 | 3 | 2 |
| ⚙️ Strategy/Logic Control | 10 | 10 | 0 | 0 |
| 🔄 Re-entry System | 15 | 12 | 3 | 0 |
| 📍 Trend Management | 6 | 6 | 0 | 0 |
| 🛡️ Risk Management | 12 | 10 | 2 | 0 |
| ⚙️ SL System | 10 | 8 | 2 | 0 |
| 💎 Dual Orders | 3 | 2 | 1 | 0 |
| 📈 Profit Booking | 18 | 15 | 2 | 1 |
| 🔧 System Settings | 4 | 3 | 0 | 1 |
| 🎯 V6 Price Action | 8 | 0 | 1 | 7 |

---

## 💰 CATEGORY 1: TRADING CONTROL (8 Commands)

### Existing Commands (All Working ✅)

| Command | Description | Parameters | Status | Handler |
|---------|-------------|------------|--------|---------|
| `/start` | Show main menu & persistent keyboard | None | ✅ Working | `handle_start()` |
| `/status` | Show bot status, MT5, balances | None | ✅ Working | `handle_status()` |
| `/pause` | Pause trading (no new trades) | None | ✅ Working | `handle_pause()` |
| `/resume` | Resume trading | None | ✅ Working | `handle_resume()` |
| `/trades` | Show open trades list | None | ✅ Working | `handle_trades()` |
| `/dashboard` | Interactive dashboard with live PnL | None | ✅ Working | `handle_dashboard()` |
| `/panic` | Emergency close all positions | Confirmation | ✅ Working | `handle_panic_close()` |
| `/simulation_mode` | Toggle simulation on/off/status | `on/off/status` | ✅ Working | `handle_simulation_mode()` |

### V5 Upgrade Requirements:

```
NONE - All working correctly with V5 plugin system
```

### Wiring Status:
```
✅ All handlers registered in self.command_handlers dict
✅ All connected to trading_engine
✅ Menu callbacks working
```

---

## ⚡ CATEGORY 2: PERFORMANCE & ANALYTICS (12 Commands)

### Existing Commands

| Command | Description | Parameters | Status | Handler |
|---------|-------------|------------|--------|---------|
| `/performance` | Trading performance stats | None | ✅ Working | `handle_performance()` |
| `/stats` | Risk management stats | None | ✅ Working | `handle_stats()` |
| `/pair_report` | Performance by symbol | None | ✅ Working | `handle_pair_report()` |
| `/strategy_report` | Performance by strategy | None | ✅ Working | `handle_strategy_report()` |
| `/tp_report` | TP re-entry statistics | None | ✅ Working | `handle_tp_report()` |
| `/profit_stats` | Profit booking statistics | None | ✅ Working | `handle_profit_stats()` |
| `/chains` | Show active re-entry chains | None | ✅ Working | `handle_chains_status()` |
| `/daily` | Daily performance report | Date (optional) | ⚠️ Partial | NOT IMPLEMENTED |
| `/weekly` | Weekly performance report | Date range | ⚠️ Partial | NOT IMPLEMENTED |
| `/monthly` | Monthly performance report | Month | ⚠️ Partial | NOT IMPLEMENTED |
| `/compare` | V3 vs V6 comparison | None | ❌ Missing | NOT IMPLEMENTED |
| `/export` | Export analytics to CSV | Type, range | ❌ Missing | NOT IMPLEMENTED |

### V5 Upgrade Requirements:

```python
# NEW COMMANDS TO IMPLEMENT:

# 1. /daily handler
async def handle_daily(self, message):
    """Generate daily performance report"""
    date = message.get('date', datetime.now().strftime('%Y-%m-%d'))
    report = self.analytics_engine.get_daily_report(date)
    # Format and send
    
# 2. /weekly handler
async def handle_weekly(self, message):
    """Generate weekly performance report"""
    
# 3. /monthly handler  
async def handle_monthly(self, message):
    """Generate monthly performance report"""
    
# 4. /compare handler (V3 vs V6)
async def handle_compare(self, message):
    """Compare V3 Combined vs V6 Price Action performance"""
    v3_stats = self.db.get_plugin_performance('v3_combined')
    v6_stats = self.db.get_plugin_performance('v6_price_action')
    # Format comparison
```

### Wiring Instructions:

```python
# Add to telegram_bot.py __init__ self.command_handlers:

self.command_handlers.update({
    "/daily": self.handle_daily,
    "/weekly": self.handle_weekly,
    "/monthly": self.handle_monthly,
    "/compare": self.handle_compare,
    "/export": self.handle_export,
})

# Required: Create analytics_menu_handler.py with interactive menu
# Required: Add date picker for date range selection
```

---

## ⚙️ CATEGORY 3: STRATEGY/LOGIC CONTROL (10 Commands)

### Existing Commands (All Working ✅)

| Command | Description | Parameters | Status | Handler |
|---------|-------------|------------|--------|---------|
| `/logic1_on` | Enable combinedlogic-1 | None | ✅ Working | `handle_combinedlogic1_on()` |
| `/logic1_off` | Disable combinedlogic-1 | None | ✅ Working | `handle_combinedlogic1_off()` |
| `/logic2_on` | Enable combinedlogic-2 | None | ✅ Working | `handle_combinedlogic2_on()` |
| `/logic2_off` | Disable combinedlogic-2 | None | ✅ Working | `handle_combinedlogic2_off()` |
| `/logic3_on` | Enable combinedlogic-3 | None | ✅ Working | `handle_combinedlogic3_on()` |
| `/logic3_off` | Disable combinedlogic-3 | None | ✅ Working | `handle_combinedlogic3_off()` |
| `/logic_control` | Show logic control menu | None | ✅ Working | `handle_logic_control()` |
| `/logic_status` | Show all logic statuses | None | ✅ Working | `handle_logic_status()` |
| `/view_logic_settings` | View logic configuration | None | ✅ Working | `handle_view_logic_settings()` |
| `/reset_timeframe_default` | Reset timeframe defaults | None | ✅ Working | `handle_reset_timeframe_default()` |

### V5 Upgrade Requirements:

```
# UPGRADE NEEDED: Add V6 Price Action timeframe controls

NEW COMMANDS REQUIRED:
- /tf15m_on, /tf15m_off - Control V6 15M plugin
- /tf30m_on, /tf30m_off - Control V6 30M plugin  
- /tf1h_on, /tf1h_off - Control V6 1H plugin
- /tf4h_on, /tf4h_off - Control V6 4H plugin
- /v6_status - Show all V6 timeframe statuses
- /v6_control - V6 timeframe control menu
```

### Wiring Instructions:

```python
# File: src/menu/v6_timeframe_menu_handler.py (NEW FILE)

class V6TimeframeMenuHandler:
    def __init__(self, telegram_bot):
        self.bot = telegram_bot
        
    def show_v6_timeframe_menu(self, user_id, message_id=None):
        """Show V6 timeframe control menu"""
        text = "🎯 V6 PRICE ACTION TIMEFRAME CONTROL\n\n"
        
        # Get plugin statuses
        plugins = {
            '15M': self.bot.trading_engine.get_plugin_status('v6_price_action_15m'),
            '30M': self.bot.trading_engine.get_plugin_status('v6_price_action_30m'),
            '1H': self.bot.trading_engine.get_plugin_status('v6_price_action_1h'),
            '4H': self.bot.trading_engine.get_plugin_status('v6_price_action_4h'),
        }
        
        for tf, enabled in plugins.items():
            status = "✅ ON" if enabled else "❌ OFF"
            text += f"• {tf}: {status}\n"
        
        keyboard = [
            [{"text": "⏱️ 15M", "callback_data": "v6_toggle_15m"},
             {"text": "⏱️ 30M", "callback_data": "v6_toggle_30m"}],
            [{"text": "⏱️ 1H", "callback_data": "v6_toggle_1h"},
             {"text": "⏱️ 4H", "callback_data": "v6_toggle_4h"}],
            [{"text": "✅ Enable All", "callback_data": "v6_enable_all"},
             {"text": "❌ Disable All", "callback_data": "v6_disable_all"}],
            [{"text": "🔙 Back", "callback_data": "menu_main"}]
        ]
        
        # Send/edit message
        
# Wire in telegram_bot.py:
from src.menu.v6_timeframe_menu_handler import V6TimeframeMenuHandler
self.v6_timeframe_handler = V6TimeframeMenuHandler(self)

# Add commands:
self.command_handlers.update({
    "/tf15m_on": lambda m: self.toggle_v6_timeframe('15m', True),
    "/tf15m_off": lambda m: self.toggle_v6_timeframe('15m', False),
    # ... etc
})

# Add callback handler in handle_callback_query():
if callback_data.startswith("v6_"):
    self.v6_timeframe_handler.handle_callback(callback_query)
```

---

## 🔄 CATEGORY 4: RE-ENTRY SYSTEM (15 Commands)

### Existing Commands

| Command | Description | Parameters | Status | Handler |
|---------|-------------|------------|--------|---------|
| `/tp_system` | TP continuation on/off/status | `on/off/status` | ✅ Working | `handle_tp_system()` |
| `/sl_hunt` | SL hunt recovery on/off/status | `on/off/status` | ✅ Working | `handle_sl_hunt()` |
| `/exit_continuation` | Exit continuation on/off | `on/off/status` | ✅ Working | `handle_exit_continuation()` |
| `/reentry_config` | Show all re-entry config | None | ✅ Working | `handle_reentry_config()` |
| `/set_monitor_interval` | Set price monitor interval | `30-300` seconds | ✅ Working | `handle_set_monitor_interval()` |
| `/set_sl_offset` | Set SL hunt offset pips | `1-5` pips | ✅ Working | `handle_set_sl_offset()` |
| `/set_cooldown` | Set SL hunt cooldown | `30-300` seconds | ✅ Working | `handle_set_cooldown()` |
| `/set_recovery_time` | Set recovery window | `1-10` minutes | ✅ Working | `handle_set_recovery_time()` |
| `/set_max_levels` | Set max chain levels | `1-5` | ✅ Working | `handle_set_max_levels()` |
| `/set_sl_reduction` | Set SL reduction % | `0.3-0.7` | ✅ Working | `handle_set_sl_reduction()` |
| `/reset_reentry_config` | Reset to defaults | None | ✅ Working | `handle_reset_reentry_config()` |
| `/autonomous_status` | Show autonomous dashboard | None | ✅ Working | `handle_autonomous_status()` |
| `/autonomous_config` | Configure autonomous | Plugin-specific | ⚠️ Partial | Needs V6 support |
| `/reentry_v3` | V3-specific re-entry config | None | ⚠️ Partial | NOT IMPLEMENTED |
| `/reentry_v6` | V6-specific re-entry config | None | ⚠️ Partial | NOT IMPLEMENTED |

### V5 Upgrade Requirements:

```python
# CRITICAL: Add per-plugin re-entry configuration

# Config structure change needed:
"re_entry_config": {
    "global": {
        "tp_reentry_enabled": true,
        "sl_hunt_reentry_enabled": true
    },
    "per_plugin": {
        "v3_combined": {
            "tp_reentry_enabled": true,
            "sl_hunt_reentry_enabled": true,
            "max_chain_levels": 3
        },
        "v6_price_action": {
            "tp_reentry_enabled": false,
            "sl_hunt_reentry_enabled": true,
            "max_chain_levels": 2
        }
    }
}

# New handlers needed:
async def handle_reentry_v3(self, message):
    """Show V3-specific re-entry config menu"""
    
async def handle_reentry_v6(self, message):
    """Show V6-specific re-entry config menu"""
```

### Wiring Instructions:

```python
# Update reentry_menu_handler.py to support per-plugin config:

class ReentryMenuHandler:
    def show_reentry_menu(self, user_id, message_id=None):
        """Show main re-entry menu with plugin selection"""
        keyboard = [
            [{"text": "🌐 Global Settings", "callback_data": "reentry_global"}],
            [{"text": "🔷 V3 Combined", "callback_data": "reentry_v3"},
             {"text": "🔶 V6 Price Action", "callback_data": "reentry_v6"}],
            [{"text": "📊 Statistics", "callback_data": "reentry_stats"}],
            [{"text": "🔙 Back", "callback_data": "menu_main"}]
        ]
        
    def show_plugin_reentry_config(self, user_id, plugin_id, message_id):
        """Show re-entry config for specific plugin"""
        config = self.bot.config.get('re_entry_config', {}).get('per_plugin', {}).get(plugin_id, {})
        # Build menu with plugin-specific toggles
```

---

## 📍 CATEGORY 5: TREND MANAGEMENT (6 Commands)

### Existing Commands (All Working ✅)

| Command | Description | Parameters | Status | Handler |
|---------|-------------|------------|--------|---------|
| `/set_trend` | Manually set trend (MANUAL mode) | `SYMBOL TF TREND` | ✅ Working | `handle_set_trend()` |
| `/set_auto` | Set trend back to AUTO mode | `SYMBOL TF` | ✅ Working | `handle_set_auto()` |
| `/show_trends` | Show all current trends | None | ✅ Working | `handle_show_trends()` |
| `/trend_matrix` | Complete trend matrix | None | ✅ Working | `handle_trend_matrix()` |
| `/trend_mode` | Check trend mode (AUTO/MANUAL) | `SYMBOL TF` | ✅ Working | `handle_trend_mode()` |
| `/signal_status` | Show signal status | None | ✅ Working | `handle_signal_status()` |

### V5 Upgrade Requirements:

```
NONE - All working correctly
```

---

## 🛡️ CATEGORY 6: RISK MANAGEMENT (12 Commands)

### Existing Commands

| Command | Description | Parameters | Status | Handler |
|---------|-------------|------------|--------|---------|
| `/view_risk_caps` | View all risk caps | None | ✅ Working | `handle_view_risk_caps()` |
| `/set_daily_cap` | Set daily loss limit | `TIER AMOUNT` | ✅ Working | `handle_set_daily_cap()` |
| `/set_lifetime_cap` | Set lifetime loss limit | `TIER AMOUNT` | ✅ Working | `handle_set_lifetime_cap()` |
| `/set_risk_tier` | Set complete tier config | `TIER DAILY LIFETIME` | ✅ Working | `handle_set_risk_tier()` |
| `/switch_tier` | Switch active tier | `TIER` | ✅ Working | `handle_switch_tier()` |
| `/view_risk_status` | View complete risk status | None | ✅ Working | `handle_view_risk_status()` |
| `/reset_risk_settings` | Reset to defaults | None | ✅ Working | `handle_reset_risk_settings()` |
| `/clear_daily_loss` | Clear daily loss data | None | ✅ Working | `handle_clear_daily_loss()` |
| `/clear_loss_data` | Clear lifetime loss data | None | ✅ Working | `handle_clear_loss_data()` |
| `/lot_size_status` | Show lot size config | None | ✅ Working | `handle_lot_size_status()` |
| `/set_lot_size` | Set lot size for tier | `TIER LOT` | ✅ Working | `handle_set_lot_size()` |
| `/risk_by_plugin` | Risk per plugin | `v3/v6` | ⚠️ Partial | NOT IMPLEMENTED |

### V5 Upgrade Requirements:

```python
# Add per-plugin risk tracking

async def handle_risk_by_plugin(self, message):
    """Show risk metrics per plugin"""
    v3_risk = self.db.get_plugin_risk_metrics('v3_combined')
    v6_risk = self.db.get_plugin_risk_metrics('v6_price_action')
    
    msg = "🛡️ RISK BY PLUGIN\n\n"
    msg += "🔷 V3 COMBINED:\n"
    msg += f"  Daily Loss: ${v3_risk['daily_loss']:.2f}\n"
    msg += f"  Open Risk: ${v3_risk['open_risk']:.2f}\n\n"
    msg += "🔶 V6 PRICE ACTION:\n"
    msg += f"  Daily Loss: ${v6_risk['daily_loss']:.2f}\n"
    msg += f"  Open Risk: ${v6_risk['open_risk']:.2f}"
```

---

## ⚙️ CATEGORY 7: SL SYSTEM (10 Commands)

### Existing Commands

| Command | Description | Parameters | Status | Handler |
|---------|-------------|------------|--------|---------|
| `/view_sl_config` | View all SL configs | None | ✅ Working | `handle_view_sl_config()` |
| `/sl_status` | Show active SL system | None | ✅ Working | `handle_sl_status()` |
| `/sl_system_change` | Switch SL system | `sl-1/sl-2` | ✅ Working | `handle_sl_system_change()` |
| `/sl_system_on` | Enable specific SL system | `sl-1/sl-2` | ✅ Working | `handle_sl_system_on()` |
| `/set_symbol_sl` | Reduce symbol SL by % | `SYMBOL PERCENT` | ✅ Working | `handle_set_symbol_sl()` |
| `/reset_symbol_sl` | Reset symbol to original | `SYMBOL` | ✅ Working | `handle_reset_symbol_sl()` |
| `/reset_all_sl` | Reset all symbol SLs | None | ✅ Working | `handle_reset_all_sl()` |
| `/complete_sl_system_off` | Disable all SL systems | None | ✅ Working | `handle_complete_sl_system_off()` |
| `/sl_by_timeframe` | SL config per timeframe | `TF` | ⚠️ Partial | NOT IMPLEMENTED |
| `/sl_by_plugin` | SL config per plugin | `v3/v6` | ⚠️ Partial | NOT IMPLEMENTED |

---

## 💎 CATEGORY 8: DUAL ORDERS (3 Commands)

### Existing Commands

| Command | Description | Parameters | Status | Handler |
|---------|-------------|------------|--------|---------|
| `/dual_order_status` | Show dual order status | None | ✅ Working | `handle_dual_order_status()` |
| `/toggle_dual_orders` | Toggle dual orders | None | ✅ Working | `handle_toggle_dual_orders()` |
| `/dual_order_config` | Configure dual orders | Various | ⚠️ Partial | Menu incomplete |

---

## 📈 CATEGORY 9: PROFIT BOOKING (18 Commands)

### Existing Commands

| Command | Description | Parameters | Status | Handler |
|---------|-------------|------------|--------|---------|
| `/profit_status` | Profit booking status | None | ✅ Working | `handle_profit_status()` |
| `/profit_stats` | Profit statistics | None | ✅ Working | `handle_profit_stats()` |
| `/toggle_profit_booking` | Toggle system | None | ✅ Working | `handle_toggle_profit_booking()` |
| `/set_profit_targets` | Set targets | `T1 T2 T3...` | ✅ Working | `handle_set_profit_targets()` |
| `/profit_chains` | Show active chains | None | ✅ Working | `handle_profit_chains()` |
| `/stop_profit_chain` | Stop specific chain | `CHAIN_ID` | ✅ Working | `handle_stop_profit_chain()` |
| `/stop_all_profit_chains` | Stop all chains | None | ✅ Working | `handle_stop_all_profit_chains()` |
| `/set_chain_multipliers` | Set multipliers | `M1 M2 M3...` | ✅ Working | `handle_set_chain_multipliers()` |
| `/set_sl_reductions` | Set SL reductions | `R1 R2 R3...` | ✅ Working | `handle_set_sl_reductions()` |
| `/profit_config` | Show full config | None | ✅ Working | `handle_profit_config()` |
| `/profit_sl_status` | Profit SL status | None | ✅ Working | `handle_profit_sl_status()` |
| `/profit_sl_mode` | Switch SL mode | `SL-1.1/SL-2.1` | ✅ Working | `handle_profit_sl_mode()` |
| `/enable_profit_sl` | Enable profit SL | None | ✅ Working | `handle_enable_profit_sl()` |
| `/disable_profit_sl` | Disable profit SL | None | ✅ Working | `handle_disable_profit_sl()` |
| `/set_profit_sl` | Set profit SL value | `[LOGIC] VALUE` | ✅ Working | `handle_set_profit_sl()` |
| `/reset_profit_sl` | Reset to defaults | None | ✅ Working | `handle_reset_profit_sl()` |
| `/shield` | Reverse Shield control | Various | ✅ Working | `handle_shield_command()` |
| `/profit_by_plugin` | Profit per plugin | `v3/v6` | ❌ Missing | NOT IMPLEMENTED |

---

## 🎯 CATEGORY 10: V6 PRICE ACTION (8 Commands) - MOSTLY MISSING ❌

### Required New Commands

| Command | Description | Parameters | Status | Handler |
|---------|-------------|------------|--------|---------|
| `/v6_status` | V6 plugin status (all TFs) | None | ❌ Missing | NOT IMPLEMENTED |
| `/v6_control` | V6 timeframe control menu | None | ❌ Missing | NOT IMPLEMENTED |
| `/tf15m` | Toggle 15M plugin | `on/off` | ❌ Missing | NOT IMPLEMENTED |
| `/tf30m` | Toggle 30M plugin | `on/off` | ❌ Missing | NOT IMPLEMENTED |
| `/tf1h` | Toggle 1H plugin | `on/off` | ❌ Missing | NOT IMPLEMENTED |
| `/tf4h` | Toggle 4H plugin | `on/off` | ❌ Missing | NOT IMPLEMENTED |
| `/v6_performance` | V6 performance by TF | `TF` (optional) | ❌ Missing | NOT IMPLEMENTED |
| `/v6_settings` | V6 settings menu | None | ⚠️ Partial | Callback broken |

### Complete Implementation Required:

```python
# File: src/menu/v6_control_handler.py (NEW FILE - 400 lines)

class V6ControlHandler:
    """Handler for V6 Price Action plugin control via Telegram"""
    
    def __init__(self, telegram_bot):
        self.bot = telegram_bot
        self.trading_engine = telegram_bot.trading_engine
        
    async def handle_v6_status(self, message):
        """Show V6 plugin status for all timeframes"""
        plugins = self.trading_engine.plugin_manager.get_v6_plugins()
        
        msg = "🎯 V6 PRICE ACTION STATUS\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for plugin_id, plugin in plugins.items():
            tf = plugin_id.split('_')[-1].upper()  # Extract timeframe
            status = "✅ ENABLED" if plugin.enabled else "❌ DISABLED"
            trades = plugin.get_trade_count()
            pnl = plugin.get_total_pnl()
            
            msg += f"⏱️ {tf}:\n"
            msg += f"  Status: {status}\n"
            msg += f"  Trades: {trades}\n"
            msg += f"  PnL: ${pnl:.2f}\n\n"
        
        keyboard = [
            [{"text": "⚙️ Control Panel", "callback_data": "v6_control"}],
            [{"text": "📊 Performance", "callback_data": "v6_performance"}],
            [{"text": "🔙 Back", "callback_data": "menu_main"}]
        ]
        
        self.bot.send_message_with_keyboard(msg, {"inline_keyboard": keyboard})
    
    async def handle_v6_control(self, message):
        """Show V6 control panel with timeframe toggles"""
        # Implementation...
        
    async def toggle_timeframe(self, timeframe: str, enabled: bool):
        """Toggle specific V6 timeframe plugin"""
        plugin_id = f"v6_price_action_{timeframe}"
        
        if enabled:
            success = await self.trading_engine.plugin_manager.enable_plugin(plugin_id)
        else:
            success = await self.trading_engine.plugin_manager.disable_plugin(plugin_id)
        
        return success

# Wire in telegram_bot.py:
from src.menu.v6_control_handler import V6ControlHandler

# In __init__ or set_dependencies:
self.v6_handler = V6ControlHandler(self)

# Add to command_handlers:
self.command_handlers.update({
    "/v6_status": self.v6_handler.handle_v6_status,
    "/v6_control": self.v6_handler.handle_v6_control,
    "/tf15m": lambda m: self.v6_handler.toggle_timeframe('15m', 'on' in m.get('text', '')),
    "/tf30m": lambda m: self.v6_handler.toggle_timeframe('30m', 'on' in m.get('text', '')),
    "/tf1h": lambda m: self.v6_handler.toggle_timeframe('1h', 'on' in m.get('text', '')),
    "/tf4h": lambda m: self.v6_handler.toggle_timeframe('4h', 'on' in m.get('text', '')),
    "/v6_performance": self.v6_handler.handle_v6_performance,
})

# Add callback handling:
if callback_data.startswith("v6_"):
    await self.v6_handler.handle_callback(callback_query)
```

---

## 🔧 CATEGORY 11: SYSTEM SETTINGS (4 Commands)

### Existing Commands

| Command | Description | Parameters | Status | Handler |
|---------|-------------|------------|--------|---------|
| `/fine_tune` | Fine-tune menu | None | ✅ Working | `handle_fine_tune()` |
| `/autonomous_dashboard` | Autonomous status | None | ✅ Working | `handle_autonomous_dashboard()` |
| `/profit_protection` | Profit protection menu | None | ✅ Working | `handle_profit_protection()` |
| `/recovery_windows` | Recovery windows info | None | ✅ Working | `handle_recovery_windows()` |

---

## 📊 COMMAND OPTIMIZATION FOR V5

### Current State: 95+ Commands (Too Many!)
### Target State: 20 Visible + Menu Access

**Problem:** 95+ commands are overwhelming for users.

**Solution:** Reduce visible commands to 20 essential ones, rest accessible via menus.

### Recommended 20 Core Commands:

```
ESSENTIAL (Always Visible):
1. /start - Main menu
2. /status - Bot status
3. /dashboard - Live dashboard
4. /pause - Pause trading
5. /resume - Resume trading
6. /trades - Open trades
7. /performance - Performance stats
8. /panic - Emergency close

PLUGIN CONTROL:
9. /logic_control - V3 logic menu
10. /v6_control - V6 timeframe menu

RE-ENTRY/PROFIT:
11. /chains - Active chains
12. /reentry_config - Re-entry menu
13. /profit_config - Profit menu

RISK:
14. /stats - Risk stats
15. /view_risk_caps - Risk caps

TRENDS:
16. /trend_matrix - Trend overview

ANALYTICS:
17. /daily - Daily report
18. /compare - V3 vs V6

SYSTEM:
19. /fine_tune - Fine-tune menu
20. /help - Help & all commands
```

### Implementation:

```python
# In handle_start(), set BotCommand list:

async def set_visible_commands(self):
    """Set visible commands in Telegram (20 only)"""
    commands = [
        BotCommand("start", "Main menu & controls"),
        BotCommand("status", "Bot status"),
        BotCommand("dashboard", "Live dashboard"),
        BotCommand("pause", "Pause trading"),
        BotCommand("resume", "Resume trading"),
        BotCommand("trades", "Open trades"),
        BotCommand("performance", "Performance stats"),
        BotCommand("panic", "Emergency close all"),
        BotCommand("logic_control", "V3 logic control"),
        BotCommand("v6_control", "V6 timeframe control"),
        BotCommand("chains", "Active chains"),
        BotCommand("reentry_config", "Re-entry settings"),
        BotCommand("profit_config", "Profit booking"),
        BotCommand("stats", "Risk stats"),
        BotCommand("view_risk_caps", "Risk caps"),
        BotCommand("trend_matrix", "Trend overview"),
        BotCommand("daily", "Daily report"),
        BotCommand("compare", "V3 vs V6 comparison"),
        BotCommand("fine_tune", "Fine-tune settings"),
        BotCommand("help", "All commands & help"),
    ]
    
    await self.bot.set_my_commands(commands)
```

---

## 🔗 COMPLETE WIRING CHECKLIST

### Files to Create:
- [ ] `src/menu/v6_control_handler.py` - V6 timeframe control
- [ ] `src/menu/analytics_menu_handler.py` - Analytics commands
- [ ] `src/services/plugin_comparison_service.py` - V3 vs V6 stats

### Files to Modify:
- [ ] `src/clients/telegram_bot.py` - Add 8 new V6 commands
- [ ] `src/menu/menu_manager.py` - Wire new handlers
- [ ] `src/menu/callback_query_handler.py` - Add V6 callbacks
- [ ] `src/menu/reentry_menu_handler.py` - Add per-plugin config
- [ ] `config/config.json` - Add per-plugin re-entry structure

### Database Changes:
- [ ] Add `plugin_id` column to trades table (if not exists)
- [ ] Add plugin performance views/queries

---

## ✅ IMPLEMENTATION PRIORITY

### Phase 1 (Critical - Week 1):
1. V6 timeframe control commands (8 commands)
2. V6 control menu handler
3. Fix V6 settings callback

### Phase 2 (High - Week 2):
1. Analytics commands (/daily, /weekly, /monthly)
2. V3 vs V6 comparison (/compare)
3. Analytics menu handler

### Phase 3 (Medium - Week 3):
1. Per-plugin re-entry configuration
2. Per-plugin risk tracking
3. Command optimization (95 → 20)

---

**END OF COMMAND INVENTORY**

---

## ⚠️ DEVELOPER NOTE - IMPORTANT

**Bot Source Code Location:**  
`C:\Users\Ansh Shivaay Gupta\Downloads\ZepixTradingBot-New-v1\ZepixTradingBot-old-v2-main\Trading_Bot`

### Implementation Guidelines:

> ⚠️ **This is a Planning & Research Document - DO NOT Apply Blindly!**

**Implementation Process:**

1. **First, Complete Scan of the Bot**
   - Analyze the complete bot code
   - Understand the current architecture
   - Review existing implementations

2. **Map Ideas According to the Bot**
   - Check how the ideas given here will be implemented in the bot
   - Identify dependencies
   - Look for conflicts

3. **Create New Plan According to the Bot**
   - Create a new implementation plan according to the bot's current state
   - Adapt ideas that don't directly fit

4. **Make Improvements (Full Freedom)**
   - You have full freedom to improve the ideas
   - Use a better approach if available
   - Optimize according to the bot's architecture

5. **Then Implement**
   - Implement only after planning is complete

### Critical Rules:

| Rule | Description |
|------|-------------|
| ✅ **Idea Must Be Fully Implemented** | The core idea/concept must be fully implemented |
| ✅ **Improvements Allowed** | You can improve the implementation |
| ❌ **Idea Should Not Change** | The core concept of the idea must remain the same |
| ❌ **Do Not Apply Blindly** | First scan, plan, then implement |

**Remember:** This document provides ideas & possibilities - the final implementation will depend on the bot's actual architecture.

---

**END OF DOCUMENT**