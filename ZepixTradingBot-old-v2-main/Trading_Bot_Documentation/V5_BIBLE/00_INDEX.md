# V5 BIBLE - MASTER INDEX

## The Single Source of Truth for Zepix V5 Bot

This documentation consolidates all knowledge from:
- `DOCUMENTATION/` (14 files) - Original bot documentation
- `06_DOCUMENTATION_BIBLE/` (21 files) - V5 architecture documentation

## Quick Navigation

### DEEP DIVE SPECIFICATIONS (New)
| Document | Description |
|----------|-------------|
| [V3_LOGIC_DEEP_DIVE.md](V3_LOGIC_DEEP_DIVE.md) | Complete V3 Combined Logic analysis - 12 signals, dual orders, re-entry |
| [V6_LOGIC_DEEP_DIVE.md](V6_LOGIC_DEEP_DIVE.md) | Complete V6 Price Action analysis - 4 timeframe plugins |
| [ARCHITECTURE_DEEP_DIVE.md](ARCHITECTURE_DEEP_DIVE.md) | System architecture - TradingEngine, ServiceAPI, Plugins |
| [BOT_WORKFLOW_CHAIN.md](BOT_WORKFLOW_CHAIN.md) | Complete execution flow - Startup -> Data -> Alert -> Plugin -> Trade |

### 01 - SYSTEM ARCHITECTURE
| Document | Description | Source |
|----------|-------------|--------|
| [01_CORE_TRADING_ENGINE.md](01_CORE_TRADING_ENGINE.md) | Trading engine orchestration | 06_DOCUMENTATION_BIBLE |
| [02_PLUGIN_SYSTEM.md](02_PLUGIN_SYSTEM.md) | Plugin architecture and registry | 06_DOCUMENTATION_BIBLE |
| [03_SERVICE_API.md](03_SERVICE_API.md) | ServiceAPI unified facade | 06_DOCUMENTATION_BIBLE |
| [04_SHADOW_MODE.md](04_SHADOW_MODE.md) | Shadow mode paper trading | 06_DOCUMENTATION_BIBLE |
| [05_CONFIG_MANAGER.md](05_CONFIG_MANAGER.md) | Configuration management | 06_DOCUMENTATION_BIBLE |
| [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md) | Technical architecture overview | DOCUMENTATION |

### 10 - TRADING LOGIC
| Document | Description | Source |
|----------|-------------|--------|
| [10_V3_COMBINED_PLUGIN.md](10_V3_COMBINED_PLUGIN.md) | V3 Combined Logic plugin | 06_DOCUMENTATION_BIBLE |
| [11_V6_PRICE_ACTION_PLUGINS.md](11_V6_PRICE_ACTION_PLUGINS.md) | V6 Price Action plugins | 06_DOCUMENTATION_BIBLE |
| [12_PLUGIN_INTERFACES.md](12_PLUGIN_INTERFACES.md) | Plugin interface definitions | 06_DOCUMENTATION_BIBLE |
| [FEATURES_SPECIFICATION.md](FEATURES_SPECIFICATION.md) | Feature specifications | DOCUMENTATION |
| [BOT_WORKING_SCENARIOS.md](BOT_WORKING_SCENARIOS.md) | Bot working scenarios | DOCUMENTATION |

### 20 - TRADING SYSTEMS
| Document | Description | Source |
|----------|-------------|--------|
| [20_DUAL_ORDER_SYSTEM.md](20_DUAL_ORDER_SYSTEM.md) | Dual order system (Order A/B) | 06_DOCUMENTATION_BIBLE |
| [21_REENTRY_SYSTEM.md](21_REENTRY_SYSTEM.md) | Re-entry system (SL Hunt, TP Continuation) | 06_DOCUMENTATION_BIBLE |
| [22_PROFIT_BOOKING_SYSTEM.md](22_PROFIT_BOOKING_SYSTEM.md) | Profit booking chains | 06_DOCUMENTATION_BIBLE |
| [23_AUTONOMOUS_SYSTEM.md](23_AUTONOMOUS_SYSTEM.md) | Autonomous safety system | 06_DOCUMENTATION_BIBLE |
| [40_RISK_MANAGEMENT.md](40_RISK_MANAGEMENT.md) | Risk management | 06_DOCUMENTATION_BIBLE |

### 30 - TELEGRAM & NOTIFICATIONS
| Document | Description | Source |
|----------|-------------|--------|
| [30_TELEGRAM_3BOT_SYSTEM.md](30_TELEGRAM_3BOT_SYSTEM.md) | 3-Bot Telegram cluster | 06_DOCUMENTATION_BIBLE |
| [31_SESSION_MANAGER.md](31_SESSION_MANAGER.md) | Session management | 06_DOCUMENTATION_BIBLE |
| [32_VOICE_ALERT_SYSTEM.md](32_VOICE_ALERT_SYSTEM.md) | Voice alert system | 06_DOCUMENTATION_BIBLE |
| [33_REAL_CLOCK_SYSTEM.md](33_REAL_CLOCK_SYSTEM.md) | Real clock system | 06_DOCUMENTATION_BIBLE |
| [VOICE_NOTIFICATION_SYSTEM_V3.md](VOICE_NOTIFICATION_SYSTEM_V3.md) | Voice notification V3 | DOCUMENTATION |
| [VOICE_ALERT_CONFIGURATION.md](VOICE_ALERT_CONFIGURATION.md) | Voice alert config | DOCUMENTATION |

### 03_TELEGRAM - TELEGRAM AUDIT (Phase 13)
| Document | Description | Source |
|----------|-------------|--------|
| [03_TELEGRAM/COMMAND_INTEGRITY_REPORT.md](03_TELEGRAM/COMMAND_INTEGRITY_REPORT.md) | Command parity audit - 91/91 FOUND | Phase 13 Audit |
| [03_TELEGRAM/COMPLETE_TELEGRAM_MANUAL.md](03_TELEGRAM/COMPLETE_TELEGRAM_MANUAL.md) | Complete user manual for all 91 commands | Phase 13 Audit |
| [03_TELEGRAM/NOTIFICATION_INTEGRITY_REPORT.md](03_TELEGRAM/NOTIFICATION_INTEGRITY_REPORT.md) | Notification parity audit - 46 types, FULL COVERAGE | Phase 13-B Audit |
| [03_TELEGRAM/COMPLETE_NOTIFICATION_MANUAL.md](03_TELEGRAM/COMPLETE_NOTIFICATION_MANUAL.md) | Complete notification system guide | Phase 13-B Audit |

### 40 - CONFIGURATION & SETUP
| Document | Description | Source |
|----------|-------------|--------|
| [CONFIGURATION_SETUP.md](CONFIGURATION_SETUP.md) | Configuration setup guide | DOCUMENTATION |
| [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) | Project overview | DOCUMENTATION |
| [API_INTEGRATION.md](API_INTEGRATION.md) | API integration guide | DOCUMENTATION |

### 50 - OPERATIONS & MAINTENANCE
| Document | Description | Source |
|----------|-------------|--------|
| [50_INTEGRATION_POINTS.md](50_INTEGRATION_POINTS.md) | Integration points | 06_DOCUMENTATION_BIBLE |
| [DEPLOYMENT_MAINTENANCE.md](DEPLOYMENT_MAINTENANCE.md) | Deployment & maintenance | DOCUMENTATION |
| [ERROR_HANDLING_TROUBLESHOOTING.md](ERROR_HANDLING_TROUBLESHOOTING.md) | Error handling | DOCUMENTATION |
| [LOGGING_SYSTEM.md](LOGGING_SYSTEM.md) | Logging system | DOCUMENTATION |
| [WORKFLOW_PROCESSES.md](WORKFLOW_PROCESSES.md) | Workflow processes | DOCUMENTATION |

### 60 - USER GUIDES
| Document | Description | Source |
|----------|-------------|--------|
| [SESSION_MANAGER_GUIDE.md](SESSION_MANAGER_GUIDE.md) | Session manager guide | DOCUMENTATION |
| [UI_NAVIGATION_GUIDE.md](UI_NAVIGATION_GUIDE.md) | UI navigation guide | DOCUMENTATION |

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  TELEGRAM CLUSTER                        │
│  ┌─────────────┬─────────────┬─────────────────────┐    │
│  │ Controller  │  Notifier   │     Analytics       │    │
│  └──────┬──────┴──────┬──────┴──────────┬──────────┘    │
└─────────┼─────────────┼─────────────────┼───────────────┘
          │             │                 │
┌─────────▼─────────────▼─────────────────▼───────────────┐
│                   TRADING ENGINE                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │              delegate_to_plugin()               │    │
│  └─────────────────────┬───────────────────────────┘    │
└────────────────────────┼────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                     SERVICE API                          │
│  ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐     │
│  │Order│Risk │Trend│Market│Reent│Dual │Profit│Auto │     │
│  │Exec │Mgmt │Mgmt │Data │ry   │Order│Book │nomous│     │
│  └──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┘     │
└─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼────────┘
      │     │     │     │     │     │     │     │
┌─────▼─────▼─────▼─────▼─────▼─────▼─────▼─────▼────────┐
│                   PLUGIN REGISTRY                        │
│  ┌─────────────────────────────────────────────────┐    │
│  │  V3 Combined  │  V6 1M  │  V6 5M  │  V6 15M/1H │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                     MT5 CLIENT                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │              MetaTrader 5 Terminal              │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## Key Concepts

### V3 Combined Logic
- 12 signal types (7 entry, 2 exit, 2 info, 1 bonus)
- Dual order system (Order A: TP_TRAIL, Order B: PROFIT_TRAIL)
- Re-entry system (SL Hunt, TP Continuation)
- Profit booking chains with pyramid levels

### V6 Price Action
- 4 timeframe plugins (1M, 5M, 15M, 1H)
- ADX and confidence filtering
- Multi-timeframe alignment
- Shadow mode support

### ServiceAPI
- Unified facade for all services
- Service registration and discovery
- Health checks and metrics
- Plugin isolation

### 3-Bot Telegram System
- Controller Bot: Commands and configuration
- Notifier Bot: Trade alerts and notifications
- Analytics Bot: Reports and performance

## Document Consolidation

This V5_BIBLE consolidates documentation from two sources:

### From DOCUMENTATION/ (14 files)
Original bot documentation covering:
- API integration
- Bot working scenarios
- Configuration setup
- Deployment and maintenance
- Error handling
- Features specification
- Logging system
- Project overview
- Session manager guide
- Technical architecture
- UI navigation guide
- Voice alert configuration
- Voice notification system V3
- Workflow processes

### From 06_DOCUMENTATION_BIBLE/ (21 files)
V5 architecture documentation covering:
- Core trading engine
- Plugin system
- Service API
- Shadow mode
- Config manager
- V3 combined plugin
- V6 price action plugins
- Plugin interfaces
- Dual order system
- Re-entry system
- Profit booking system
- Autonomous system
- Telegram 3-bot system
- Session manager
- Voice alert system
- Real clock system
- Risk management
- Integration points

## Version
- Created: 2026-01-16
- Last Updated: 2026-01-16
- Source: Deep scan of src/ directory
