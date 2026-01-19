# 🧭 MENU SYSTEMS ARCHITECTURE

**Generated:** January 19, 2026  
**Bot Version:** V5 Hybrid Plugin Architecture  
**Total Menu Handlers:** 12  
**Status:** 9 Working (75%) | 2 Broken (17%) | 1 Missing (8%)

---

## 📊 MENU HANDLERS OVERVIEW

| Handler | File | Lines | Status | Purpose |
|---------|------|-------|--------|---------|
| MenuManager | `menu_manager.py` | 959 | ✅ Working | Central menu orchestration |
| FineTuneMenuHandler | `fine_tune_menu_handler.py` | ~300 | ✅ Working | Fine-tune settings |
| ReentryMenuHandler | `reentry_menu_handler.py` | ~250 | ✅ Working | Re-entry config |
| ProfitBookingMenuHandler | `profit_booking_menu_handler.py` | ~350 | ✅ Working | Profit booking |
| TimeframeMenuHandler | `timeframe_menu_handler.py` | ~200 | ✅ Working | Timeframe settings |
| ContextManager | `context_manager.py` | ~150 | ✅ Working | User context state |
| CommandExecutor | `command_executor.py` | ~200 | ✅ Working | Execute commands |
| CommandMapping | `command_mapping.py` | ~100 | ✅ Working | Map buttons to commands |
| RiskMenuHandler | `risk_menu_handler.py` | ~200 | ✅ Working | Risk settings |
| V6SettingsHandler | `menu_manager.py` | ~50 | ⚠️ Broken | V6 plugin settings |
| AnalyticsMenuHandler | - | 0 | ❌ Missing | Analytics & reports |
| V6ControlMenuHandler | - | 0 | ❌ Missing | V6 timeframe control |

---

## 🏗️ MENU SYSTEM ARCHITECTURE

### Current Architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                     MENU FLOW ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User Interaction                                               │
│       │                                                         │
│       ▼                                                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    telegram_bot.py                        │   │
│  │  handle_callback_query() → route to handlers              │   │
│  └───────────────────────────┬──────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    MenuManager                            │   │
│  │  • show_main_menu()                                       │   │
│  │  • handle_menu_callback()                                 │   │
│  │  • Route to specific handlers                             │   │
│  └───────────────────────────┬──────────────────────────────┘   │
│                              │                                  │
│              ┌───────────────┼───────────────┐                  │
│              │               │               │                  │
│              ▼               ▼               ▼                  │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐      │
│  │ FineTune       │ │ Reentry        │ │ ProfitBooking  │      │
│  │ MenuHandler    │ │ MenuHandler    │ │ MenuHandler    │      │
│  └────────────────┘ └────────────────┘ └────────────────┘      │
│              │               │               │                  │
│              └───────────────┼───────────────┘                  │
│                              ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  CommandExecutor                          │   │
│  │  Execute actual commands via TradingEngine                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Callback Data Flow:

```python
# callback_data pattern: "category_action_params"

Examples:
- "menu_main"           → Show main menu
- "menu_trading"        → Show trading control menu
- "menu_reentry"        → Show re-entry menu
- "menu_profit"         → Show profit booking menu
- "menu_risk"           → Show risk management menu
- "menu_v6"             → Show V6 settings (BROKEN)
- "menu_analytics"      → Show analytics menu (MISSING)

- "toggle_pause"        → Toggle pause/resume
- "toggle_logic1"       → Toggle combinedlogic-1
- "confirm_panic"       → Confirm panic close

- "reentry_tp_on"       → Enable TP re-entry
- "reentry_sl_off"      → Disable SL hunt

- "profit_target_1"     → Set profit target 1
- "profit_chain_stop"   → Stop profit chain
```

---

## 📱 SECTION 1: MAIN MENU STRUCTURE

### Current Main Menu:

```
┌────────────────────────────────────────┐
│        🤖 ZEPIX TRADING BOT            │
│                                        │
│  Status: 🟢 Active                     │
│  PnL Today: +$125.50                   │
│                                        │
├────────────────────────────────────────┤
│                                        │
│  [💰 Trading]    [📊 Performance]      │
│                                        │
│  [⚙️ Logic]      [🔄 Re-entry]         │
│                                        │
│  [📈 Profit]     [🛡️ Risk]             │
│                                        │
│  [📍 Trends]     [🔧 Fine-Tune]        │
│                                        │
│  [📱 Dashboard]  [⚠️ Panic]            │
│                                        │
└────────────────────────────────────────┘
```

### Main Menu Implementation:

```python
# File: src/menu/menu_manager.py

class MenuManager:
    def show_main_menu(self, user_id: int, message_id: int = None):
        """Display main menu with all control categories"""
        
        # Get current status
        status = self.get_bot_status()
        pnl = self.get_daily_pnl()
        
        # Build header
        status_emoji = "🟢" if status == "active" else "🔴"
        text = f"""
🤖 <b>ZEPIX TRADING BOT</b>

Status: {status_emoji} {status.title()}
PnL Today: {"+" if pnl >= 0 else ""}{pnl:.2f}

Select a category:
        """
        
        # Build keyboard
        keyboard = [
            [
                {"text": "💰 Trading", "callback_data": "menu_trading"},
                {"text": "📊 Performance", "callback_data": "menu_performance"}
            ],
            [
                {"text": "⚙️ Logic Control", "callback_data": "menu_logic"},
                {"text": "🔄 Re-entry", "callback_data": "menu_reentry"}
            ],
            [
                {"text": "📈 Profit Booking", "callback_data": "menu_profit"},
                {"text": "🛡️ Risk", "callback_data": "menu_risk"}
            ],
            [
                {"text": "📍 Trends", "callback_data": "menu_trends"},
                {"text": "🔧 Fine-Tune", "callback_data": "menu_finetune"}
            ],
            [
                {"text": "📱 Dashboard", "callback_data": "menu_dashboard"},
                {"text": "⚠️ Panic Close", "callback_data": "menu_panic"}
            ],
            # MISSING: V6 Control & Analytics
        ]
        
        self.send_or_edit_menu(user_id, text, keyboard, message_id)
```

---

## 💰 SECTION 2: TRADING CONTROL MENU

### Current Implementation (Working ✅):

```
┌────────────────────────────────────────┐
│       💰 TRADING CONTROL               │
│                                        │
│  Bot: 🟢 Active                        │
│  Open Trades: 3                        │
│                                        │
├────────────────────────────────────────┤
│                                        │
│  [⏸️ Pause]     [▶️ Resume]            │
│                                        │
│  [📋 Trades]    [📊 Status]            │
│                                        │
│  [🔄 Refresh]   [🔙 Back]              │
│                                        │
└────────────────────────────────────────┘
```

### Handler Code:

```python
def show_trading_menu(self, user_id: int, message_id: int = None):
    """Show trading control menu"""
    
    status = self.trading_engine.get_status()
    open_trades = self.trading_engine.get_open_trades_count()
    
    status_emoji = "🟢" if status.is_active else "🔴"
    
    text = f"""
💰 <b>TRADING CONTROL</b>
━━━━━━━━━━━━━━━━━━━━━━━━

Bot Status: {status_emoji} {status.state}
Open Trades: {open_trades}
"""
    
    # Dynamic buttons based on state
    pause_btn = {"text": "▶️ Resume", "callback_data": "trading_resume"} \
                if status.is_paused else \
                {"text": "⏸️ Pause", "callback_data": "trading_pause"}
    
    keyboard = [
        [pause_btn, {"text": "📊 Status", "callback_data": "trading_status"}],
        [
            {"text": "📋 Trades", "callback_data": "trading_list"},
            {"text": "🔄 Refresh", "callback_data": "menu_trading"}
        ],
        [{"text": "🔙 Back", "callback_data": "menu_main"}]
    ]
    
    self.send_or_edit_menu(user_id, text, keyboard, message_id)
```

---

## ⚙️ SECTION 3: LOGIC CONTROL MENU

### Current Implementation (Working ✅):

```
┌────────────────────────────────────────┐
│       ⚙️ V3 LOGIC CONTROL              │
│                                        │
│  Logic-1: 🟢 ON                        │
│  Logic-2: 🟢 ON                        │
│  Logic-3: 🔴 OFF                       │
│                                        │
├────────────────────────────────────────┤
│                                        │
│  [Logic-1 🟢]  [Logic-2 🟢]            │
│                                        │
│  [Logic-3 🔴]  [Reset All]             │
│                                        │
│  [🔙 Back]                             │
│                                        │
└────────────────────────────────────────┘
```

### V6 Control Menu MISSING ❌:

```
┌────────────────────────────────────────┐
│       🎯 V6 TIMEFRAME CONTROL          │  ← NEEDS TO BE CREATED
│                                        │
│  15M: 🟢 ON    (5 trades, +$45)        │
│  30M: 🟢 ON    (3 trades, +$28)        │
│  1H:  🔴 OFF   (0 trades)              │
│  4H:  🔴 OFF   (0 trades)              │
│                                        │
├────────────────────────────────────────┤
│                                        │
│  [⏱️ 15M 🟢]   [⏱️ 30M 🟢]             │
│                                        │
│  [🕐 1H 🔴]    [🕓 4H 🔴]              │
│                                        │
│  [✅ Enable All] [❌ Disable All]       │
│                                        │
│  [📊 Performance] [🔙 Back]            │
│                                        │
└────────────────────────────────────────┘
```

---

## 🔄 SECTION 4: RE-ENTRY MENU

### Current Implementation (Working ✅):

```python
# File: src/menu/reentry_menu_handler.py

class ReentryMenuHandler:
    def show_reentry_menu(self, user_id: int, message_id: int = None):
        """Show re-entry configuration menu"""
        
        config = self.config.get('re_entry_config', {})
        
        tp_status = "🟢 ON" if config.get('tp_reentry_enabled') else "🔴 OFF"
        sl_status = "🟢 ON" if config.get('sl_hunt_reentry_enabled') else "🔴 OFF"
        exit_status = "🟢 ON" if config.get('exit_continuation_enabled') else "🔴 OFF"
        
        text = f"""
🔄 <b>RE-ENTRY CONFIGURATION</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>Systems:</b>
• TP Re-entry: {tp_status}
• SL Hunt: {sl_status}
• Exit Continuation: {exit_status}

<b>Settings:</b>
• Max Levels: {config.get('max_chain_levels', 3)}
• SL Reduction: {config.get('sl_reduction_percent', 0.5)*100:.0f}%
• Monitor Interval: {config.get('monitor_interval', 60)}s
"""
        
        keyboard = [
            [
                {"text": f"TP: {tp_status}", "callback_data": "reentry_toggle_tp"},
                {"text": f"SL: {sl_status}", "callback_data": "reentry_toggle_sl"}
            ],
            [
                {"text": f"Exit: {exit_status}", "callback_data": "reentry_toggle_exit"},
                {"text": "📊 Stats", "callback_data": "reentry_stats"}
            ],
            [
                {"text": "⚙️ Settings", "callback_data": "reentry_settings"},
                {"text": "🔄 Reset", "callback_data": "reentry_reset"}
            ],
            [{"text": "🔙 Back", "callback_data": "menu_main"}]
        ]
        
        self.send_or_edit_menu(user_id, text, keyboard, message_id)
```

### V5 Upgrade Needed - Per-Plugin Re-entry:

```
┌────────────────────────────────────────┐
│       🔄 RE-ENTRY CONFIGURATION        │
│                                        │
├────────────────────────────────────────┤
│  📌 GLOBAL SETTINGS                    │
│  • TP Re-entry: 🟢 ON                  │
│  • SL Hunt: 🟢 ON                      │
│                                        │
├────────────────────────────────────────┤
│  🔷 V3 COMBINED                        │
│  • TP Re-entry: 🟢 ON                  │
│  • SL Hunt: 🟢 ON                      │
│  • Max Levels: 3                       │
│                                        │
├────────────────────────────────────────┤
│  🔶 V6 PRICE ACTION                    │  ← NEW SECTION
│  • TP Re-entry: 🔴 OFF                 │
│  • SL Hunt: 🟢 ON                      │
│  • Max Levels: 2                       │
│                                        │
├────────────────────────────────────────┤
│                                        │
│  [🌐 Global]  [🔷 V3]  [🔶 V6]         │
│                                        │
│  [📊 Stats]   [🔙 Back]                │
│                                        │
└────────────────────────────────────────┘
```

---

## 📈 SECTION 5: PROFIT BOOKING MENU

### Current Implementation (Working ✅):

```python
# File: src/menu/profit_booking_menu_handler.py

class ProfitBookingMenuHandler:
    def show_profit_menu(self, user_id: int, message_id: int = None):
        """Show profit booking configuration menu"""
        
        config = self.config.get('profit_booking', {})
        enabled = config.get('enabled', False)
        targets = config.get('targets', [])
        
        status = "🟢 ENABLED" if enabled else "🔴 DISABLED"
        
        text = f"""
📈 <b>PROFIT BOOKING SYSTEM</b>
━━━━━━━━━━━━━━━━━━━━━━━━

Status: {status}

<b>Targets:</b>
"""
        for i, target in enumerate(targets, 1):
            text += f"• T{i}: {target}%\n"
        
        keyboard = [
            [{"text": f"System: {status}", "callback_data": "profit_toggle"}],
            [
                {"text": "🎯 Targets", "callback_data": "profit_targets"},
                {"text": "📊 Stats", "callback_data": "profit_stats"}
            ],
            [
                {"text": "🔗 Chains", "callback_data": "profit_chains"},
                {"text": "⚙️ Config", "callback_data": "profit_config"}
            ],
            [{"text": "🔙 Back", "callback_data": "menu_main"}]
        ]
```

---

## 📊 SECTION 6: ANALYTICS MENU (MISSING ❌)

### Required Implementation:

```
┌────────────────────────────────────────┐
│       📊 ANALYTICS & REPORTS           │
│                                        │
│  Today: +$125.50 (8 trades)            │
│  Week:  +$450.00 (32 trades)           │
│  Month: +$1,250.00 (145 trades)        │
│                                        │
├────────────────────────────────────────┤
│                                        │
│  [📅 Daily]     [📆 Weekly]            │
│                                        │
│  [📈 Monthly]   [🔄 Compare]           │
│                                        │
│  [💱 By Pair]   [⚙️ By Logic]          │
│                                        │
│  [📤 Export]    [🔙 Back]              │
│                                        │
└────────────────────────────────────────┘
```

### Implementation Code:

```python
# File: src/menu/analytics_menu_handler.py (NEW FILE)

class AnalyticsMenuHandler:
    """Handler for analytics and reports menu"""
    
    def __init__(self, telegram_bot):
        self.bot = telegram_bot
        self.trading_engine = telegram_bot.trading_engine
        self.db = telegram_bot.db
        
    def show_analytics_menu(self, user_id: int, message_id: int = None):
        """Show analytics main menu"""
        
        # Get stats
        today_pnl = self.db.get_daily_pnl(datetime.now())
        today_trades = self.db.get_daily_trade_count(datetime.now())
        
        week_pnl = self.db.get_weekly_pnl()
        week_trades = self.db.get_weekly_trade_count()
        
        month_pnl = self.db.get_monthly_pnl()
        month_trades = self.db.get_monthly_trade_count()
        
        text = f"""
📊 <b>ANALYTICS & REPORTS</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>Performance Overview:</b>

📅 Today:  {self._format_pnl(today_pnl)} ({today_trades} trades)
📆 Week:   {self._format_pnl(week_pnl)} ({week_trades} trades)
📈 Month:  {self._format_pnl(month_pnl)} ({month_trades} trades)
"""
        
        keyboard = [
            [
                {"text": "📅 Daily Report", "callback_data": "analytics_daily"},
                {"text": "📆 Weekly Report", "callback_data": "analytics_weekly"}
            ],
            [
                {"text": "📈 Monthly Report", "callback_data": "analytics_monthly"},
                {"text": "🔄 V3 vs V6", "callback_data": "analytics_compare"}
            ],
            [
                {"text": "💱 By Pair", "callback_data": "analytics_pair"},
                {"text": "⚙️ By Logic", "callback_data": "analytics_logic"}
            ],
            [
                {"text": "📤 Export CSV", "callback_data": "analytics_export"},
                {"text": "🔙 Back", "callback_data": "menu_main"}
            ]
        ]
        
        self.send_or_edit_menu(user_id, text, keyboard, message_id)
    
    def show_comparison_report(self, user_id: int, message_id: int = None):
        """Show V3 vs V6 comparison"""
        
        v3_stats = self.db.get_plugin_performance('v3_combined')
        v6_stats = self.db.get_plugin_performance('v6_price_action')
        
        text = f"""
🔄 <b>V3 vs V6 COMPARISON</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>🔷 V3 Combined:</b>
• Trades: {v3_stats['trade_count']}
• Win Rate: {v3_stats['win_rate']:.1f}%
• PnL: {self._format_pnl(v3_stats['total_pnl'])}
• Avg Win: ${v3_stats['avg_win']:.2f}
• Avg Loss: ${v3_stats['avg_loss']:.2f}

<b>🔶 V6 Price Action:</b>
• Trades: {v6_stats['trade_count']}
• Win Rate: {v6_stats['win_rate']:.1f}%
• PnL: {self._format_pnl(v6_stats['total_pnl'])}
• Avg Win: ${v6_stats['avg_win']:.2f}
• Avg Loss: ${v6_stats['avg_loss']:.2f}

<b>📊 Winner: {'V3 Combined' if v3_stats['total_pnl'] > v6_stats['total_pnl'] else 'V6 Price Action'}</b>
"""
        
        keyboard = [
            [
                {"text": "🔷 V3 Details", "callback_data": "analytics_v3_detail"},
                {"text": "🔶 V6 Details", "callback_data": "analytics_v6_detail"}
            ],
            [
                {"text": "📊 By Timeframe", "callback_data": "analytics_v6_timeframe"}
            ],
            [{"text": "🔙 Back", "callback_data": "menu_analytics"}]
        ]
        
        self.send_or_edit_menu(user_id, text, keyboard, message_id)
```

---

## 🎯 SECTION 7: V6 CONTROL MENU (MISSING ❌)

### Required Implementation:

```python
# File: src/menu/v6_control_menu_handler.py (NEW FILE)

class V6ControlMenuHandler:
    """Handler for V6 Price Action timeframe control menu"""
    
    def __init__(self, telegram_bot):
        self.bot = telegram_bot
        self.plugin_manager = telegram_bot.trading_engine.plugin_manager
        
    def show_v6_control_menu(self, user_id: int, message_id: int = None):
        """Show V6 timeframe control menu"""
        
        # Get status for each timeframe
        tf_status = {
            '15m': self.plugin_manager.is_plugin_enabled('v6_price_action_15m'),
            '30m': self.plugin_manager.is_plugin_enabled('v6_price_action_30m'),
            '1h': self.plugin_manager.is_plugin_enabled('v6_price_action_1h'),
            '4h': self.plugin_manager.is_plugin_enabled('v6_price_action_4h'),
        }
        
        # Get stats for each
        tf_stats = {}
        for tf in ['15m', '30m', '1h', '4h']:
            plugin_id = f'v6_price_action_{tf}'
            tf_stats[tf] = self.bot.db.get_plugin_quick_stats(plugin_id)
        
        text = f"""
🎯 <b>V6 PRICE ACTION CONTROL</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>Timeframe Status:</b>

⏱️ 15M: {self._status_icon(tf_status['15m'])} | {tf_stats['15m']['trades']} trades | {self._format_pnl(tf_stats['15m']['pnl'])}
⏱️ 30M: {self._status_icon(tf_status['30m'])} | {tf_stats['30m']['trades']} trades | {self._format_pnl(tf_stats['30m']['pnl'])}
🕐 1H:  {self._status_icon(tf_status['1h'])} | {tf_stats['1h']['trades']} trades | {self._format_pnl(tf_stats['1h']['pnl'])}
🕓 4H:  {self._status_icon(tf_status['4h'])} | {tf_stats['4h']['trades']} trades | {self._format_pnl(tf_stats['4h']['pnl'])}

<b>Active Plugins: {sum(tf_status.values())}/4</b>
"""
        
        keyboard = [
            [
                {"text": f"⏱️ 15M {self._status_icon(tf_status['15m'])}", 
                 "callback_data": "v6_toggle_15m"},
                {"text": f"⏱️ 30M {self._status_icon(tf_status['30m'])}", 
                 "callback_data": "v6_toggle_30m"}
            ],
            [
                {"text": f"🕐 1H {self._status_icon(tf_status['1h'])}", 
                 "callback_data": "v6_toggle_1h"},
                {"text": f"🕓 4H {self._status_icon(tf_status['4h'])}", 
                 "callback_data": "v6_toggle_4h"}
            ],
            [
                {"text": "✅ Enable All", "callback_data": "v6_enable_all"},
                {"text": "❌ Disable All", "callback_data": "v6_disable_all"}
            ],
            [
                {"text": "📊 Performance", "callback_data": "v6_performance"},
                {"text": "⚙️ Settings", "callback_data": "v6_settings"}
            ],
            [{"text": "🔙 Back", "callback_data": "menu_main"}]
        ]
        
        self.send_or_edit_menu(user_id, text, keyboard, message_id)
    
    def _status_icon(self, enabled: bool) -> str:
        return "🟢" if enabled else "🔴"
    
    def _format_pnl(self, pnl: float) -> str:
        sign = "+" if pnl >= 0 else ""
        return f"{sign}${pnl:.2f}"
    
    async def handle_toggle(self, callback_query, timeframe: str):
        """Toggle specific V6 timeframe plugin"""
        
        plugin_id = f'v6_price_action_{timeframe}'
        current = self.plugin_manager.is_plugin_enabled(plugin_id)
        
        if current:
            success = await self.plugin_manager.disable_plugin(plugin_id)
            action = "disabled"
        else:
            success = await self.plugin_manager.enable_plugin(plugin_id)
            action = "enabled"
        
        if success:
            await self.bot.answer_callback_query(
                callback_query.id, 
                f"V6 {timeframe.upper()} {action}!"
            )
            # Refresh menu
            self.show_v6_control_menu(callback_query.from_user.id, callback_query.message.message_id)
        else:
            await self.bot.answer_callback_query(
                callback_query.id, 
                f"Failed to {action[:-1]} V6 {timeframe.upper()}", 
                show_alert=True
            )
```

---

## 🔧 SECTION 8: WIRING INSTRUCTIONS

### Step 1: Update Main Menu

```python
# File: src/menu/menu_manager.py

# Add V6 and Analytics to main menu keyboard:
keyboard = [
    # ... existing rows ...
    [
        {"text": "🎯 V6 Control", "callback_data": "menu_v6"},  # ADD
        {"text": "📊 Analytics", "callback_data": "menu_analytics"}  # ADD
    ],
    [
        {"text": "📱 Dashboard", "callback_data": "menu_dashboard"},
        {"text": "⚠️ Panic Close", "callback_data": "menu_panic"}
    ],
]
```

### Step 2: Create New Handler Files

```
Create these new files:
1. src/menu/analytics_menu_handler.py (300 lines)
2. src/menu/v6_control_menu_handler.py (250 lines)
```

### Step 3: Wire Handlers in telegram_bot.py

```python
# File: src/clients/telegram_bot.py

# In __init__ or set_dependencies:
from src.menu.analytics_menu_handler import AnalyticsMenuHandler
from src.menu.v6_control_menu_handler import V6ControlMenuHandler

self.analytics_menu_handler = AnalyticsMenuHandler(self)
self.v6_control_menu_handler = V6ControlMenuHandler(self)

# In handle_callback_query:
async def handle_callback_query(self, callback_query):
    data = callback_query.data
    
    # Menu routing
    if data == "menu_main":
        self.menu_manager.show_main_menu(callback_query.from_user.id, callback_query.message.message_id)
    
    elif data == "menu_analytics":
        self.analytics_menu_handler.show_analytics_menu(callback_query.from_user.id, callback_query.message.message_id)
    
    elif data == "menu_v6":
        self.v6_control_menu_handler.show_v6_control_menu(callback_query.from_user.id, callback_query.message.message_id)
    
    elif data.startswith("analytics_"):
        await self.analytics_menu_handler.handle_callback(callback_query)
    
    elif data.startswith("v6_"):
        await self.v6_control_menu_handler.handle_callback(callback_query)
    
    # ... rest of existing handlers
```

### Step 4: Fix V6 Settings Callback

```python
# File: src/menu/menu_manager.py

# Find broken callback and fix:
# OLD (BROKEN):
elif data == "menu_v6_settings":
    pass  # No implementation

# NEW (FIXED):
elif data == "menu_v6_settings" or data == "menu_v6":
    self.v6_control_menu_handler.show_v6_control_menu(user_id, message_id)
```

---

## 📱 SECTION 9: TELEGRAM VISUAL CAPABILITIES

### Menu Button (≡):

```python
# Add persistent menu button using setMenuButton API

async def set_menu_button(self):
    """Set persistent menu button in chat"""
    
    await self.bot.set_chat_menu_button(
        chat_id=self.chat_id,
        menu_button={
            "type": "commands",  # Shows command list
        }
    )
```

### Persistent Keyboard:

```python
def get_persistent_keyboard(self):
    """Get persistent ReplyKeyboardMarkup for quick access"""
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton("📱 Dashboard"),
                KeyboardButton("📊 Status")
            ],
            [
                KeyboardButton("📋 Trades"),
                KeyboardButton("⏸️ Pause/Resume")
            ],
            [
                KeyboardButton("📈 Performance"),
                KeyboardButton("🔄 Re-entry")
            ]
        ],
        resize_keyboard=True,
        persistent=True
    )
    
    return keyboard
```

### Chat Actions:

```python
async def show_typing_indicator(self, chat_id: int):
    """Show 'typing...' while processing"""
    await self.bot.send_chat_action(chat_id, "typing")
```

---

## ✅ IMPLEMENTATION CHECKLIST

### Critical (Week 1):
- [ ] Create `analytics_menu_handler.py`
- [ ] Create `v6_control_menu_handler.py`
- [ ] Add V6 & Analytics to main menu
- [ ] Wire new handlers in telegram_bot.py
- [ ] Fix V6 settings callback (broken)

### High (Week 2):
- [ ] Add per-plugin re-entry menus
- [ ] Implement comparison reports
- [ ] Add V6 timeframe performance menu
- [ ] Add export functionality

### Medium (Week 3):
- [ ] Add persistent keyboard
- [ ] Add menu button
- [ ] Add chat actions (typing...)
- [ ] Optimize menu navigation

---

## 📁 FILES TO CREATE/MODIFY

| File | Action | Lines | Priority |
|------|--------|-------|----------|
| `src/menu/analytics_menu_handler.py` | CREATE | ~300 | Critical |
| `src/menu/v6_control_menu_handler.py` | CREATE | ~250 | Critical |
| `src/menu/menu_manager.py` | MODIFY | +20 | Critical |
| `src/clients/telegram_bot.py` | MODIFY | +50 | Critical |
| `src/menu/reentry_menu_handler.py` | MODIFY | +80 | High |

---

**END OF MENU SYSTEMS DOCUMENTATION**

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