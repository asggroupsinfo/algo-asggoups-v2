# BOT WORKFLOW CHAIN - DEEP DIVE

## Visual Chain: Startup -> Data -> Alert -> Plugin -> Trade

This document traces the complete execution flow from bot startup to trade execution, showing how data flows through the V5 Hybrid Plugin Architecture.

## System Startup Chain

```
┌─────────────────────────────────────────────────────────────────────┐
│                        BOT STARTUP SEQUENCE                          │
└─────────────────────────────────────────────────────────────────────┘

1. main.py
   │
   ├── Load config.json
   │   └── Parse: telegram, mt5, risk_tiers, plugin_system, shadow_mode
   │
   ├── Initialize Core Components
   │   ├── Config()
   │   ├── RiskManager()
   │   ├── MT5Client()
   │   └── TelegramBot()
   │
   ├── Create TradingEngine
   │   ├── Initialize ServiceAPI
   │   ├── Initialize PluginRegistry
   │   ├── Initialize ShadowModeManager
   │   ├── Initialize MultiTelegramManager (3-Bot)
   │   └── Initialize VoiceAlertSystem
   │
   ├── TradingEngine.initialize()
   │   ├── MT5Client.initialize() → Connect to MetaTrader 5
   │   ├── PluginRegistry.discover_plugins() → Scan src/logic_plugins/
   │   ├── PluginRegistry.load_all_plugins() → Load V3, V6 plugins
   │   ├── PriceMonitorService.start() → Background price monitoring
   │   └── ProfitBookingManager.recover_chains_from_database()
   │
   └── Start Webhook Server
       └── Listen for TradingView alerts on /webhook endpoint
```

## Alert Processing Chain

```
┌─────────────────────────────────────────────────────────────────────┐
│                     ALERT PROCESSING CHAIN                           │
└─────────────────────────────────────────────────────────────────────┘

TradingView Alert (JSON)
   │
   ▼
┌─────────────────────────────────────────────────────────────────────┐
│ WEBHOOK HANDLER (src/api/webhook_handler.py)                        │
│                                                                      │
│ 1. Receive POST /webhook                                            │
│ 2. Parse JSON payload                                               │
│ 3. Validate required fields (symbol, signal, strategy)              │
│ 4. Forward to AlertProcessor                                        │
└─────────────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────────────┐
│ ALERT PROCESSOR (src/processors/alert_processor.py)                 │
│                                                                      │
│ 1. Determine alert type (V3 or V6)                                  │
│ 2. Parse to appropriate model:                                      │
│    - V3: ZepixV3Alert (12 signal types)                            │
│    - V6: ZepixV6Alert (entry/exit/reversal)                        │
│ 3. Update TimeframeTrendManager                                     │
│ 4. Forward to TradingEngine.process_alert()                        │
└─────────────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────────────┐
│ TRADING ENGINE (src/core/trading_engine.py)                         │
│                                                                      │
│ 1. Validate signal data                                             │
│ 2. Check if trading is paused                                       │
│ 3. Check session manager (trading hours)                            │
│ 4. Call delegate_to_plugin(signal_data)                            │
└─────────────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PLUGIN DELEGATION (TradingEngine.delegate_to_plugin)                │
│                                                                      │
│ 1. PluginRegistry.get_plugin_for_signal(signal_data)               │
│    - Match strategy: "V3_COMBINED" → V3CombinedPlugin              │
│    - Match strategy: "V6_PRICE_ACTION" → V6PriceAction*Plugin      │
│                                                                      │
│ 2. Route to handler based on alert type:                           │
│    - "entry" → plugin.process_entry_signal()                       │
│    - "exit" → plugin.process_exit_signal()                         │
│    - "reversal" → plugin.process_reversal_signal()                 │
│                                                                      │
│ 3. Track execution metrics                                          │
│ 4. Handle plugin failures (disable after 5 failures)               │
└─────────────────────────────────────────────────────────────────────┘
```

## V3 Entry Signal Chain

```
┌─────────────────────────────────────────────────────────────────────┐
│                    V3 ENTRY SIGNAL CHAIN                             │
└─────────────────────────────────────────────────────────────────────┘

V3CombinedPlugin.process_entry_signal(alert)
   │
   ├── 1. VALIDATE ENTRY
   │   ├── Check plugin enabled
   │   ├── Check shadow mode
   │   ├── Validate alert fields
   │   └── Check signal type (one of 12 types)
   │
   ├── 2. ROUTE TO LOGIC
   │   ├── Signal Override Check (aggressive signals → LOGIC3)
   │   └── Timeframe Routing:
   │       ├── 1m/5m → LOGIC1 (Scalping)
   │       ├── 15m/30m → LOGIC2 (Swing)
   │       └── 1h+ → LOGIC3 (Position)
   │
   ├── 3. SAFETY CHECKS (via ServiceAPI)
   │   ├── AutonomousService.check_recovery_allowed()
   │   ├── RiskService.check_daily_limit()
   │   └── RiskService.check_lifetime_limit()
   │
   ├── 4. CALCULATE LOT SIZE
   │   ├── ServiceAPI.calculate_lot_size_async()
   │   ├── Apply logic multiplier (LOGIC1=1.0, LOGIC2=1.2, LOGIC3=1.5)
   │   └── Cap at max_lot_size
   │
   ├── 5. CREATE DUAL ORDERS
   │   │
   │   ├── ORDER A (TP_TRAIL)
   │   │   ├── SL: V3 Smart SL (progressive trailing)
   │   │   ├── TP: 2:1 RR
   │   │   ├── Trailing: Start at 50% SL, step 25%
   │   │   └── ServiceAPI.place_single_order_a()
   │   │
   │   └── ORDER B (PROFIT_TRAIL)
   │       ├── SL: Fixed $10 risk
   │       ├── TP: None (uses profit booking)
   │       ├── Create profit chain
   │       └── ServiceAPI.place_single_order_b()
   │
   ├── 6. CREATE PROFIT CHAIN (for Order B)
   │   ├── ProfitBookingService.create_chain()
   │   └── Initialize pyramid levels ($7 per level)
   │
   └── 7. SEND NOTIFICATIONS
       ├── TelegramService.send_notification("trade_opened")
       └── VoiceAlertSystem.send_voice_alert()
```

## V6 Entry Signal Chain

```
┌─────────────────────────────────────────────────────────────────────┐
│                    V6 ENTRY SIGNAL CHAIN                             │
└─────────────────────────────────────────────────────────────────────┘

V6PriceAction*Plugin.process_entry_signal(alert)
   │
   ├── 1. PARSE ALERT
   │   └── Convert to ZepixV6Alert dataclass
   │
   ├── 2. VALIDATE TIMEFRAME
   │   └── Check alert.tf matches plugin timeframe (1/5/15/60)
   │
   ├── 3. APPLY ENTRY FILTERS
   │   │
   │   ├── ADX CHECK
   │   │   ├── 1M: ADX >= 30
   │   │   ├── 5M: ADX >= 25
   │   │   ├── 15M: ADX >= 20
   │   │   └── 1H: ADX >= 15
   │   │
   │   ├── CONFIDENCE CHECK
   │   │   ├── 1M: Confidence >= 80
   │   │   ├── 5M: Confidence >= 70
   │   │   ├── 15M: Confidence >= 65
   │   │   └── 1H: Confidence >= 60
   │   │
   │   └── ALIGNMENT CHECK
   │       ├── 1M: Requires 5M alignment
   │       ├── 5M: Requires 15M alignment
   │       ├── 15M: Requires 1H alignment
   │       └── 1H: Requires 4H alignment
   │
   ├── 4. CALCULATE LOT SIZE
   │   ├── ServiceAPI.calculate_lot_size_async()
   │   ├── Apply risk multiplier (1M=0.5x, 5M=1.0x, 15M=1.2x, 1H=1.5x)
   │   └── Cap at max_lot_size
   │
   ├── 5. PLACE DUAL ORDERS
   │   ├── Order A: 50% lot, targets TP2
   │   └── Order B: 50% lot, targets TP1
   │
   └── 6. SEND NOTIFICATIONS
       └── TelegramService.send_notification("trade_opened")
```

## Order Execution Chain

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ORDER EXECUTION CHAIN                             │
└─────────────────────────────────────────────────────────────────────┘

ServiceAPI.place_order() / place_single_order_a() / place_single_order_b()
   │
   ├── 1. RISK VALIDATION
   │   ├── RiskManagementService.validate_trade_risk()
   │   ├── Check daily loss limit
   │   ├── Check lifetime loss limit
   │   └── DualOrderManager.validate_dual_order_risk()
   │       └── Smart auto-adjustment if near limit
   │
   ├── 2. SHADOW MODE CHECK
   │   ├── If plugin in shadow mode:
   │   │   └── Record virtual order, skip MT5
   │   └── If live mode:
   │       └── Continue to MT5
   │
   ├── 3. MT5 ORDER PLACEMENT
   │   ├── MT5Client.place_order()
   │   │   ├── symbol
   │   │   ├── order_type (buy/sell)
   │   │   ├── lot_size
   │   │   ├── price
   │   │   ├── sl
   │   │   ├── tp
   │   │   └── comment (plugin_id + order_type)
   │   │
   │   └── Return trade_id or None
   │
   ├── 4. DATABASE RECORD
   │   ├── TradeDatabase.record_trade()
   │   └── Plugin-isolated database (data/zepix_{plugin_id}.db)
   │
   └── 5. RETURN RESULT
       └── {"success": bool, "trade_id": int, "error": str}
```

## Trade Management Chain

```
┌─────────────────────────────────────────────────────────────────────┐
│                   TRADE MANAGEMENT CHAIN                             │
└─────────────────────────────────────────────────────────────────────┘

PriceMonitorService (Background Loop)
   │
   ├── Every 30 seconds:
   │   │
   │   ├── 1. CHECK OPEN TRADES
   │   │   └── MT5Client.get_open_positions()
   │   │
   │   ├── 2. CHECK SL/TP HITS
   │   │   │
   │   │   ├── If SL Hit (Order A):
   │   │   │   ├── ReentryService.start_sl_hunt_recovery()
   │   │   │   ├── Activate Reverse Shield
   │   │   │   └── Create recovery chain
   │   │   │
   │   │   ├── If TP Hit (Order A):
   │   │   │   └── ReentryService.start_tp_continuation()
   │   │   │
   │   │   └── If SL Hit (Order B):
   │   │       └── ProfitBookingService.on_chain_sl_hit()
   │   │
   │   ├── 3. CHECK PROFIT TARGETS (Order B)
   │   │   ├── ProfitBookingService.check_profit_targets()
   │   │   └── If $7 profit reached:
   │   │       ├── Close partial position
   │   │       └── Advance to next pyramid level
   │   │
   │   └── 4. UPDATE TRAILING STOPS
   │       └── DualOrderManager.update_trailing_stops()
   │
   └── Send notifications for all events
```

## Exit Signal Chain

```
┌─────────────────────────────────────────────────────────────────────┐
│                     EXIT SIGNAL CHAIN                                │
└─────────────────────────────────────────────────────────────────────┘

Plugin.process_exit_signal(alert)
   │
   ├── 1. DETERMINE CLOSE DIRECTION
   │   ├── Bullish_Exit → Close BUY positions
   │   └── Bearish_Exit → Close SELL positions
   │
   ├── 2. GET POSITIONS TO CLOSE
   │   └── ServiceAPI.get_plugin_orders(plugin_id, direction)
   │
   ├── 3. CLOSE EACH POSITION
   │   ├── ServiceAPI.close_position(order_id)
   │   ├── MT5Client.close_position()
   │   └── Calculate P/L
   │
   ├── 4. UPDATE DATABASE
   │   └── TradeDatabase.record_close()
   │
   └── 5. SEND NOTIFICATIONS
       ├── TelegramService.send_notification("trade_closed")
       └── VoiceAlertSystem.send_voice_alert()
```

## Reversal Signal Chain

```
┌─────────────────────────────────────────────────────────────────────┐
│                    REVERSAL SIGNAL CHAIN                             │
└─────────────────────────────────────────────────────────────────────┘

Plugin.process_reversal_signal(alert)
   │
   ├── 1. EXIT EXISTING POSITIONS
   │   └── process_exit_signal(alert) → Close opposite direction
   │
   ├── 2. ENTER NEW POSITION
   │   └── process_entry_signal(alert) → Open new direction
   │
   └── 3. RETURN COMBINED RESULT
       └── {"exit_result": {...}, "entry_result": {...}}
```

## Notification Chain

```
┌─────────────────────────────────────────────────────────────────────┐
│                    NOTIFICATION CHAIN                                │
└─────────────────────────────────────────────────────────────────────┘

TradingEngine.send_notification(type, message)
   │
   ├── If MultiTelegramManager available:
   │   │
   │   ├── Route by notification type:
   │   │   │
   │   │   ├── Trade Events (trade_opened, trade_closed, sl_hit, tp_hit)
   │   │   │   └── NotifierBot.send_message()
   │   │   │
   │   │   ├── Analytics (daily_summary, performance)
   │   │   │   └── AnalyticsBot.send_message()
   │   │   │
   │   │   └── Commands/Errors
   │   │       └── ControllerBot.send_message()
   │   │
   │   └── Apply rate limiting (30 msg/sec)
   │
   └── Fallback to legacy TelegramBot.send_message()

VoiceAlertSystem.send_voice_alert(message, priority)
   │
   ├── Convert text to speech
   ├── Apply priority (HIGH, MEDIUM, LOW)
   └── Send voice message to Telegram
```

## Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    COMPLETE DATA FLOW                                │
└─────────────────────────────────────────────────────────────────────┘

TradingView Pine Script
        │
        ▼
   [JSON Alert]
        │
        ▼
┌───────────────┐
│ Webhook       │ ──────────────────────────────────────────────────┐
│ Handler       │                                                    │
└───────┬───────┘                                                    │
        │                                                            │
        ▼                                                            │
┌───────────────┐                                                    │
│ Alert         │                                                    │
│ Processor     │                                                    │
└───────┬───────┘                                                    │
        │                                                            │
        ▼                                                            │
┌───────────────┐     ┌───────────────┐     ┌───────────────┐       │
│ Trading       │────▶│ Plugin        │────▶│ V3 Combined   │       │
│ Engine        │     │ Registry      │     │ Plugin        │       │
└───────┬───────┘     └───────────────┘     └───────┬───────┘       │
        │                     │                     │               │
        │                     ▼                     │               │
        │             ┌───────────────┐             │               │
        │             │ V6 Price      │             │               │
        │             │ Action Plugins│             │               │
        │             └───────┬───────┘             │               │
        │                     │                     │               │
        ▼                     ▼                     ▼               │
┌───────────────────────────────────────────────────────────────┐   │
│                        SERVICE API                             │   │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────┬───────┐  │   │
│  │ Order   │ Risk    │ Reentry │ Dual    │ Profit  │ Tele  │  │   │
│  │ Exec    │ Mgmt    │ Service │ Order   │ Booking │ gram  │  │   │
│  └────┬────┴────┬────┴────┬────┴────┬────┴────┬────┴───┬───┘  │   │
└───────┼─────────┼─────────┼─────────┼─────────┼────────┼──────┘   │
        │         │         │         │         │        │          │
        ▼         │         │         │         │        ▼          │
┌───────────────┐ │         │         │         │ ┌───────────────┐ │
│ MT5 Client    │ │         │         │         │ │ 3-Bot Telegram│ │
└───────┬───────┘ │         │         │         │ │ Cluster       │ │
        │         │         │         │         │ └───────┬───────┘ │
        ▼         │         │         │         │         │         │
┌───────────────┐ │         │         │         │         ▼         │
│ MetaTrader 5  │ │         │         │         │ ┌───────────────┐ │
│ Terminal      │ │         │         │         │ │ User Phone    │◀┘
└───────────────┘ │         │         │         │ └───────────────┘
        │         │         │         │         │
        ▼         ▼         ▼         ▼         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE LAYER                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ zepix_v3.db     │  │ zepix_v6_5m.db  │  │ zepix_core.db   │  │
│  │ (V3 trades)     │  │ (V6 5M trades)  │  │ (shared data)   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Integration Points

| Component | Integrates With | Purpose |
|-----------|-----------------|---------|
| WebhookHandler | AlertProcessor | Parse incoming alerts |
| AlertProcessor | TradingEngine | Route alerts to engine |
| TradingEngine | PluginRegistry | Find appropriate plugin |
| Plugin | ServiceAPI | Access all services |
| ServiceAPI | MT5Client | Execute orders |
| ServiceAPI | TelegramService | Send notifications |
| PriceMonitor | ReentryService | Handle SL/TP events |
| PriceMonitor | ProfitBookingService | Check profit targets |

## Version History
- v1.0.0 (2026-01-16): Initial workflow chain documentation
- Based on deep scan of src/ directory
- Traces complete execution flow from startup to trade
