# COMPLETE TELEGRAM MANUAL

**Version:** V5 Hybrid Plugin Architecture  
**Total Commands:** 91 Commands across 12 Categories  
**Last Updated:** 2026-01-16

---

## TABLE OF CONTENTS

1. [Quick Start](#quick-start)
2. [Trading Control](#1-trading-control-6-commands)
3. [Performance & Analytics](#2-performance--analytics-6-commands)
4. [Strategy Control](#3-strategy-control-7-commands)
5. [Re-entry System](#4-re-entry-system-12-commands)
6. [Trend Management](#5-trend-management-5-commands)
7. [Risk & Lot Management](#6-risk--lot-management-11-commands)
8. [SL System Control](#7-sl-system-control-8-commands)
9. [Dual Orders](#8-dual-orders-2-commands)
10. [Profit Booking](#9-profit-booking-15-commands)
11. [Diagnostics & Health](#10-diagnostics--health-15-commands)
12. [Fine-Tune & Shield](#11-fine-tune--shield-7-commands)
13. [Timeframe Logic](#12-timeframe-logic-3-commands)
14. [3-Bot Architecture](#3-bot-telegram-architecture)
15. [Notification Types](#notification-types)

---

## QUICK START

### Main Menu Access
Send `/start` to open the main menu with quick action buttons:

```
+----------------------------------+
|        ZEPIX TRADING BOT         |
+----------------------------------+
| [Dashboard]  [Plugin Control]    |
| [Status]     [Settings]          |
| [Help]                           |
+----------------------------------+
```

### Essential Commands
| Command | Description |
|---------|-------------|
| `/start` | Open main menu |
| `/status` | Show bot status |
| `/pause` | Pause all trading |
| `/resume` | Resume trading |
| `/trades` | View open positions |
| `/performance` | View P&L summary |

---

## 1. TRADING CONTROL (6 Commands)

### `/pause` - Pause Trading
Immediately stops all new trade entries. Existing positions remain open.

**Usage:** `/pause`  
**Confirmation:** Required  
**Result:** "Trading PAUSED"

### `/resume` - Resume Trading
Re-enables trade entries after pause.

**Usage:** `/resume`  
**Result:** "Trading RESUMED"

### `/status` - Bot Status
Shows comprehensive bot status including:
- Active/Paused state
- Uptime
- Active plugins (V3/V6)
- Open trades count
- Daily P&L

**Usage:** `/status`

### `/trades` - View Open Trades
Lists all currently open positions with:
- Symbol
- Direction (BUY/SELL)
- Entry price
- Current P&L
- SL/TP levels

**Usage:** `/trades`

### `/signal_status` - Current Signals
Shows signal status for all symbols across timeframes (5m, 15m, 1h, 1d).

**Usage:** `/signal_status`

### `/simulation_mode` - Toggle Simulation
Enable/disable paper trading mode.

**Usage:** 
- `/simulation_mode status` - Check current mode
- `/simulation_mode on` - Enable simulation
- `/simulation_mode off` - Disable simulation

---

## 2. PERFORMANCE & ANALYTICS (6 Commands)

### `/performance` - Performance Summary
Shows win rate, total P&L, daily/lifetime statistics.

**Usage:** `/performance`

### `/stats` - Risk Statistics
Shows current risk tier, loss limits, lot size configuration.

**Usage:** `/stats`

### `/performance_report` - 30-Day Report
Generates detailed 30-day performance analytics.

**Usage:** `/performance_report`

### `/pair_report` - Symbol Performance
Shows per-symbol trading statistics.

**Usage:** `/pair_report`

### `/strategy_report` - Strategy Analytics
Shows per-logic (V3/V6) performance breakdown.

**Usage:** `/strategy_report`

### `/chains` - Re-entry Chains Status
Lists all active re-entry chains with current levels.

**Usage:** `/chains`

---

## 3. STRATEGY CONTROL (7 Commands)

### `/logic_status` - All Logics Status
Shows enabled/disabled status for LOGIC1, LOGIC2, LOGIC3.

**Usage:** `/logic_status`

### Logic Toggle Commands
| Command | Description |
|---------|-------------|
| `/logic1_on` | Enable LOGIC 1 (5-minute) |
| `/logic1_off` | Disable LOGIC 1 |
| `/logic2_on` | Enable LOGIC 2 (15-minute) |
| `/logic2_off` | Disable LOGIC 2 |
| `/logic3_on` | Enable LOGIC 3 (1-hour) |
| `/logic3_off` | Disable LOGIC 3 |

**Result:** Confirmation message with new status

---

## 4. RE-ENTRY SYSTEM (12 Commands)

### `/tp_system` - TP Re-entry Control
Control Take Profit re-entry system.

**Usage:**
- `/tp_system status` - Check status
- `/tp_system on` - Enable
- `/tp_system off` - Disable

### `/sl_hunt` - SL Hunt Re-entry
Control SL Hunt re-entry system (re-enters after stop loss hit).

**Usage:**
- `/sl_hunt status`
- `/sl_hunt on`
- `/sl_hunt off`

### `/exit_continuation` - Exit Continuation
Control exit signal continuation system.

**Usage:**
- `/exit_continuation status`
- `/exit_continuation on`
- `/exit_continuation off`

### `/tp_report` - TP Re-entry Report
Shows TP re-entry statistics and history.

**Usage:** `/tp_report`

### `/reentry_config` - View Configuration
Shows all re-entry system settings.

**Usage:** `/reentry_config`

### Configuration Commands
| Command | Description | Range |
|---------|-------------|-------|
| `/set_monitor_interval` | Price check interval | 30-600 seconds |
| `/set_sl_offset` | SL hunt offset | 1-5 pips |
| `/set_cooldown` | Cooldown between re-entries | 30-600 seconds |
| `/set_recovery_time` | Recovery window | 1-15 minutes |
| `/set_max_levels` | Max chain levels | 1-5 |
| `/set_sl_reduction` | SL reduction per level | 0.3-0.7 (30-70%) |

### `/reset_reentry_config` - Reset to Defaults
Resets all re-entry settings to factory defaults.

**Usage:** `/reset_reentry_config`  
**Confirmation:** Required

---

## 5. TREND MANAGEMENT (5 Commands)

### `/show_trends` - Show Current Trends
Displays current trend for all symbols.

**Usage:** `/show_trends`

### `/trend_matrix` - Complete Matrix
Shows full trend matrix with logic alignments across all timeframes.

**Usage:** `/trend_matrix`

### `/set_trend` - Manually Set Trend
Override automatic trend detection for a symbol.

**Usage:** Interactive menu
1. Select Symbol (XAUUSD, EURUSD, etc.)
2. Select Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
3. Select Trend (BULLISH, BEARISH, NEUTRAL)

### `/set_auto` - Enable Auto Mode
Return to automatic trend detection for a symbol.

**Usage:** Interactive menu
1. Select Symbol
2. Select Timeframe

### `/trend_mode` - Check Trend Mode
Check if a symbol is in MANUAL or AUTO trend mode.

**Usage:** Interactive menu

---

## 6. RISK & LOT MANAGEMENT (11 Commands)

### `/view_risk_caps` - View Risk Limits
Shows daily and lifetime loss caps for all tiers.

**Usage:** `/view_risk_caps`

### `/view_risk_status` - Complete Risk Status
Shows all tier configurations with active tier highlighted.

**Usage:** `/view_risk_status`

### `/switch_tier` - Switch Active Risk Tier
Change active risk tier.

**Tiers Available:**
- $5,000 - Daily $100, Lifetime $500, Lot 0.01
- $10,000 - Daily $200, Lifetime $1,000, Lot 0.05
- $25,000 - Daily $500, Lifetime $2,500, Lot 0.1
- $50,000 - Daily $1,000, Lifetime $5,000, Lot 0.2
- $100,000 - Daily $2,000, Lifetime $10,000, Lot 0.5

### Configuration Commands
| Command | Description |
|---------|-------------|
| `/set_daily_cap` | Set daily loss limit ($10-$5000) |
| `/set_lifetime_cap` | Set lifetime loss limit |
| `/set_risk_tier` | Configure custom tier |
| `/set_lot_size` | Override lot size for tier |

### Reset Commands
| Command | Description |
|---------|-------------|
| `/clear_loss_data` | Clear lifetime loss counter |
| `/clear_daily_loss` | Clear daily loss counter |
| `/lot_size_status` | View current lot sizes |
| `/reset_risk_settings` | Reset all to defaults |

---

## 7. SL SYSTEM CONTROL (8 Commands)

### `/sl_status` - SL System Status
Shows active SL system, enabled status, and reductions.

**Usage:** `/sl_status`

### `/sl_system_change` - Switch SL System
Switch between SL systems:
- **SL-1:** Conservative (Wider SLs)
- **SL-2:** Aggressive (Tighter SLs)

### `/sl_system_on` - Enable SL System
Enable a specific SL system.

### `/complete_sl_system_off` - Disable All SL
Disable all SL systems (DANGEROUS).

**Confirmation:** Required

### `/view_sl_config` - View SL Configuration
Shows all symbol SL values.

### Symbol SL Commands
| Command | Description |
|---------|-------------|
| `/set_symbol_sl` | Reduce SL for specific symbol (5-50%) |
| `/reset_symbol_sl` | Reset one symbol to default |
| `/reset_all_sl` | Reset all symbols to default |

---

## 8. DUAL ORDERS (2 Commands)

### `/dual_order_status` - Dual Order Status
Shows dual order system status.

**Dual Order System:**
- **Order A:** TP_TRAIL - Trails to take profit
- **Order B:** PROFIT_TRAIL - Fixed $10 risk, profit booking

### `/toggle_dual_orders` - Toggle Dual Orders
Enable/disable dual order placement.

**Confirmation:** Required

---

## 9. PROFIT BOOKING (15 Commands)

### Status Commands
| Command | Description |
|---------|-------------|
| `/profit_status` | System status, max level, targets |
| `/profit_stats` | Chain stats, profits, averages |
| `/profit_chains` | View active profit chains |
| `/profit_config` | All profit booking settings |

### Control Commands
| Command | Description |
|---------|-------------|
| `/toggle_profit_booking` | Enable/disable system |
| `/set_profit_targets` | Set profit targets per level |
| `/set_chain_multipliers` | Set lot multipliers (e.g., 1 2 4 8 16) |
| `/stop_profit_chain` | Stop specific chain |
| `/stop_all_profit_chains` | Stop all chains |

### Profit SL Commands
| Command | Description |
|---------|-------------|
| `/profit_sl_status` | Current SL mode and settings |
| `/profit_sl_mode` | Switch SL mode (SL-1.1 or SL-2.1) |
| `/enable_profit_sl` | Enable profit SL |
| `/disable_profit_sl` | Disable profit SL |
| `/set_profit_sl` | Set custom profit SL value |
| `/reset_profit_sl` | Reset to defaults |

**SL Modes:**
- **SL-1.1:** Logic-Specific ($20/$40/$50 per logic)
- **SL-2.1:** Universal Fixed ($10)

---

## 10. DIAGNOSTICS & HEALTH (15 Commands)

### Health Commands
| Command | Description |
|---------|-------------|
| `/health_status` | Full system health report |
| `/error_stats` | Error counts and types |
| `/system_resources` | CPU, RAM, disk usage |

### Logging Commands
| Command | Description |
|---------|-------------|
| `/set_log_level` | Set level (DEBUG/INFO/WARNING/ERROR) |
| `/get_log_level` | Current logging level |
| `/reset_log_level` | Reset to default |
| `/trading_debug_mode` | Toggle trading debug |

### Export Commands
| Command | Description |
|---------|-------------|
| `/export_logs` | Export recent logs (100/500/1000 lines) |
| `/export_current_session` | Export current session log |
| `/export_by_date` | Export specific date log |
| `/export_date_range` | Export date range logs |
| `/log_file_size` | Check log file size |

### Reset Commands
| Command | Description |
|---------|-------------|
| `/reset_errors` | Reset error counters |
| `/reset_health` | Reset health stats |
| `/clear_old_logs` | Clear logs older than 30 days |

---

## 11. FINE-TUNE & SHIELD (7 Commands)

### `/shield` - Reverse Shield Control
Control the Reverse Shield v3.0 system.

**Usage:**
- `/shield status` - Check status
- `/shield on` - Enable
- `/shield off` - Disable

### `/fine_tune` - Fine-Tune Menu
Opens interactive fine-tune menu for advanced settings.

### `/dashboard` - Interactive Dashboard
Real-time P&L dashboard with controls.

### Configuration Commands
| Command | Description |
|---------|-------------|
| `/profit_protection` | Configure profit protection |
| `/sl_reduction` | Configure SL reduction |
| `/recovery_windows` | View recovery windows |
| `/autonomous_status` | View autonomous dashboard |

---

## 12. TIMEFRAME LOGIC (3 Commands)

### `/toggle_timeframe` - Toggle Timeframe Logic
Enable/disable timeframe-specific logic processing.

### `/view_logic_settings` - View Logic Config
Shows current logic configuration for all timeframes.

### `/reset_timeframe_default` - Reset to Default
Reset timeframe logic settings to defaults.

---

## 3-BOT TELEGRAM ARCHITECTURE

The V5 Hybrid Plugin Architecture uses a 3-bot Telegram cluster:

```
+------------------+     +------------------+     +------------------+
|  CONTROLLER BOT  |     |   NOTIFIER BOT   |     |  ANALYTICS BOT   |
+------------------+     +------------------+     +------------------+
| - All /commands  |     | - Trade alerts   |     | - Daily reports  |
| - Configuration  |     | - Entry/Exit     |     | - Performance    |
| - Plugin control |     | - SL/TP hits     |     | - Statistics     |
| - Emergency stop |     | - Re-entry       |     | - Charts         |
+------------------+     +------------------+     +------------------+
        |                        |                        |
        +------------------------+------------------------+
                                 |
                    +------------------------+
                    | UNIFIED NOTIFICATION   |
                    |       ROUTER           |
                    +------------------------+
```

### Bot Responsibilities

**Controller Bot:**
- Handles all slash commands
- System configuration
- Plugin enable/disable
- Emergency controls

**Notifier Bot:**
- Trade entry notifications
- Trade exit notifications
- SL/TP hit alerts
- Re-entry triggers
- Profit booking alerts

**Analytics Bot:**
- Daily summary reports
- Weekly/monthly reports
- Performance analytics
- Chart generation

---

## NOTIFICATION TYPES

### Trade Notifications
| Type | Bot | Description |
|------|-----|-------------|
| ENTRY | Notifier | New trade opened |
| EXIT | Notifier | Trade closed |
| SL_HIT | Notifier | Stop loss triggered |
| TP_HIT | Notifier | Take profit triggered |
| PARTIAL_CLOSE | Notifier | Partial position closed |

### System Notifications
| Type | Bot | Description |
|------|-----|-------------|
| REENTRY_TRIGGER | Notifier | Re-entry activated |
| PROFIT_BOOKING | Notifier | Profit level reached |
| ERROR | Controller | System error |
| WARNING | Controller | System warning |

### Report Notifications
| Type | Bot | Description |
|------|-----|-------------|
| DAILY_SUMMARY | Analytics | End of day report |
| WEEKLY_SUMMARY | Analytics | Weekly performance |
| MONTHLY_SUMMARY | Analytics | Monthly performance |

### Voice Alerts
Voice alerts are triggered for critical events:
- Trade entries
- Trade exits
- SL/TP hits
- Error conditions

Control with `/mute` and `/unmute` commands.

---

## COMMAND QUICK REFERENCE

### Most Used Commands
```
/start          - Main menu
/status         - Bot status
/pause          - Pause trading
/resume         - Resume trading
/trades         - Open positions
/performance    - P&L summary
/chains         - Re-entry chains
/dashboard      - Live dashboard
```

### Emergency Commands
```
/pause          - Stop all trading
/closeall       - Close all positions (DANGEROUS)
/shutdown       - Shutdown bot (ADMIN)
```

### Plugin Commands
```
/plugin         - Plugin control menu
/plugins        - List all plugins
/enable         - Enable plugin
/disable        - Disable plugin
/shadow         - Shadow mode testing
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-16  
**Source:** V5 Hybrid Plugin Architecture  
**Verified Against:** `src/clients/telegram_bot_fixed.py` (5126 lines)
