# INTEGRATION POINTS

**Purpose:** Document all integration points between components

---

## OVERVIEW

This document maps all integration points in the V5 Hybrid Plugin Architecture, showing how components communicate and depend on each other.

---

## SIGNAL FLOW

```
TradingView Alert (Webhook)
         |
         v
+------------------+
| FastAPI Webhook  |
| Handler          |
+------------------+
         |
         v
+------------------+
| AlertProcessor   |
| (Parse & Validate)|
+------------------+
         |
         v
+------------------+
| TradingEngine    |
| process_alert()  |
+------------------+
         |
         +---> Check Execution Mode
         |
         v
+------------------+
| delegate_to_     |
| plugin()         |
+------------------+
         |
         v
+------------------+
| PluginRegistry   |
| get_plugin_for_  |
| signal()         |
+------------------+
         |
         v
+------------------+
| Logic Plugin     |
| (V3 or V6)       |
+------------------+
         |
         v
+------------------+
| ServiceAPI       |
| (Order Execution)|
+------------------+
         |
         v
+------------------+
| MT5Client        |
| place_order()    |
+------------------+
         |
         v
+------------------+
| MultiTelegram    |
| Manager          |
| (Notification)   |
+------------------+
```

---

## COMPONENT DEPENDENCIES

### TradingEngine Dependencies

| Component | Purpose | Interface |
|-----------|---------|-----------|
| MT5Client | Order execution | `place_order()`, `close_position()` |
| PluginRegistry | Plugin management | `get_plugin_for_signal()` |
| ServiceAPI | Service layer | Injected into plugins |
| ShadowModeManager | Shadow testing | `get_execution_mode()` |
| MultiTelegramManager | Notifications | `send_notification_async()` |
| RiskManager | Risk validation | `validate_trade()` |
| ReEntryManager | Re-entry chains | `create_chain()` |
| DualOrderManager | Dual orders | `create_dual_orders()` |
| ProfitBookingManager | Profit chains | `create_profit_chain()` |
| AutonomousSystemManager | Autonomous ops | `run_autonomous_checks()` |
| ConfigManager | Configuration | `get()`, `reload_config()` |
| TradeDatabase | Persistence | `save_trade()`, `load_trades()` |

### Plugin Dependencies

| Component | Purpose | Access Via |
|-----------|---------|------------|
| ServiceAPI | All operations | `self.service_api` |
| Config | Plugin settings | `self.config` |
| Logger | Logging | `self.logger` |

### ServiceAPI Dependencies

| Component | Purpose | Internal |
|-----------|---------|----------|
| OrderExecutionService | Order ops | `self.order_service` |
| RiskManagementService | Risk ops | `self.risk_service` |
| TrendManagementService | Trend analysis | `self.trend_service` |
| MarketDataService | Market data | `self.market_service` |
| ReentryService | Re-entry ops | `self.reentry_service` |
| DualOrderService | Dual order ops | `self.dual_order_service` |
| ProfitBookingService | Profit booking | `self.profit_booking_service` |
| AutonomousService | Autonomous ops | `self.autonomous_service` |

---

## API ENDPOINTS

### Webhook Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/webhook/tradingview` | POST | TradingView alerts |
| `/webhook/custom` | POST | Custom alerts |
| `/api/health` | GET | Health check |
| `/api/status` | GET | System status |

### Internal APIs

| API | Purpose | Consumers |
|-----|---------|-----------|
| PluginRegistry API | Plugin management | TradingEngine |
| ServiceAPI | Plugin operations | All plugins |
| ConfigManager API | Configuration | All components |

---

## EVENT FLOW

### Trade Opened Event

```
1. Plugin calls ServiceAPI.create_dual_orders()
2. ServiceAPI places Order A via MT5Client
3. ServiceAPI places Order B via MT5Client
4. ServiceAPI creates profit chain for Order B
5. TradingEngine creates re-entry chain for Order A
6. MultiTelegramManager sends notification
7. TradeDatabase saves trade
```

### SL Hit Event

```
1. MT5Client detects SL hit
2. TradingEngine._handle_sl_hit() called
3. ReEntryManager.record_sl_hit() called
4. Chain set to "recovery_mode"
5. AutonomousSystemManager monitors for recovery
6. MultiTelegramManager sends notification
```

### TP Hit Event

```
1. MT5Client detects TP hit
2. TradingEngine._handle_tp_hit() called
3. ReEntryManager.record_tp_hit() called
4. AutonomousSystemManager registers continuation
5. MultiTelegramManager sends notification
```

### Profit Target Hit Event

```
1. AutonomousSystemManager detects target hit
2. ProfitBookingManager.handle_profit_target_hit() called
3. Order closed via MT5Client
4. Profit booked
5. If not max level: new orders created
6. Chain advanced to next level
7. MultiTelegramManager sends notification
```

---

## DATA FLOW

### Configuration Data

```
config.json
    |
    v
ConfigManager
    |
    +---> TradingEngine.config
    |
    +---> PluginRegistry.config
    |
    +---> ServiceAPI.config
    |
    +---> All Managers.config
```

### Trade Data

```
Trade Created
    |
    v
TradingEngine.open_trades
    |
    +---> TradeDatabase.save_trade()
    |
    +---> ReEntryManager.active_chains
    |
    +---> ProfitBookingManager.active_chains
```

### Market Data

```
MT5Client
    |
    v
MarketDataService
    |
    +---> ServiceAPI.get_current_price()
    |
    +---> ServiceAPI.get_spread()
    |
    +---> ServiceAPI.get_atr()
```

---

## TELEGRAM INTEGRATION

### Command Flow

```
User sends /command
    |
    v
ControllerBot receives
    |
    v
Command handler called
    |
    v
TradingEngine method called
    |
    v
Response sent to user
```

### Notification Flow

```
Event occurs
    |
    v
TradingEngine.send_notification()
    |
    v
MultiTelegramManager._get_target_bot()
    |
    +---> Trade event -> NotificationBot
    |
    +---> Report event -> AnalyticsBot
    |
    +---> Admin event -> ControllerBot
    |
    v
Bot.send_message()
```

---

## DATABASE INTEGRATION

### Tables

| Table | Purpose | Access |
|-------|---------|--------|
| trades | Trade history | TradeDatabase |
| reentry_chains | Re-entry chains | ReEntryManager |
| profit_chains | Profit booking chains | ProfitBookingManager |
| config_history | Config changes | ConfigManager |

### Persistence Points

| Event | Persisted Data |
|-------|----------------|
| Trade opened | Trade record |
| Trade closed | Updated trade record |
| Chain created | Chain record |
| Chain updated | Updated chain record |
| Config changed | Config history |

---

## RELATED FILES

- `src/core/trading_engine.py` - Central hub
- `src/core/plugin_system/service_api.py` - Service layer
- `src/telegram/multi_telegram_manager.py` - Telegram integration
- `src/database.py` - Database operations
