# STUDY REPORT 01: ORIGINAL BOT FEATURES
## Comprehensive Feature Catalog

**Date:** 2026-01-15
**Author:** Devin (Deep Study Phase)
**Purpose:** Document ALL features in the existing bot before V5 surgery
**Total Features Identified:** 47 Features across 12 Categories

---

## EXECUTIVE SUMMARY

This report catalogs every feature in the existing Zepix Trading Bot V2. The purpose is to ensure that the V5 Hybrid Plugin Architecture surgery does NOT break or omit any existing functionality. Each feature is documented with its file location, dependencies, and configuration requirements.

---

## CATEGORY 1: TRADING LOGIC SYSTEM (8 Features)

### Feature 1.1: V3 Integration System
**Description:** Multi-timeframe pillar analysis with consensus scoring for trade signals
**File Location:** `src/core/trading_engine.py` (lines 200-400)
**Dependencies:** TimeframeTrendManager, AlertProcessor
**Configuration:** `config.json` → `v3_config`

**Sub-components:**
- Consensus Scoring (0-9 pillars)
- Signal Classification (5 types: bias, trend, entry, reversal, exit)
- Dynamic Signal Routing
- Trend Check Bypass (for specific conditions)

### Feature 1.2: Multi-Timeframe Logic (LOGIC1, LOGIC2, LOGIC3)
**Description:** Three distinct trading strategies based on entry timeframe
**File Location:** `src/managers/timeframe_trend_manager.py` (lines 194-338)
**Dependencies:** TimeframeTrendManager
**Configuration:** `config.json` → `timeframe_specific_config`

| Logic | Entry TF | Trend Requirements | Use Case |
|-------|----------|-------------------|----------|
| LOGIC1 (combinedlogic-1) | 5m | 1H + 15M aligned | Scalping |
| LOGIC2 (combinedlogic-2) | 15m | 1H + 15M aligned | Intraday |
| LOGIC3 (combinedlogic-3) | 1h | 1D + 1H aligned | Swing |

### Feature 1.3: Trend Alignment Check
**Description:** Validates entry signals against higher timeframe trends
**File Location:** `src/managers/timeframe_trend_manager.py` → `check_logic_alignment()`
**Dependencies:** Trend state persistence (`config/timeframe_trends.json`)
**Configuration:** Per-logic trend requirements

### Feature 1.4: Signal Type Processing
**Description:** Routes different alert types to appropriate handlers
**File Location:** `src/processors/alert_processor.py`
**Dependencies:** TradingEngine, TimeframeTrendManager
**Signal Types:**
- `bias` → Updates trend state
- `trend` → Updates trend state
- `entry` → Triggers trade execution
- `reversal` → Closes opposing trades
- `exit` → Closes trades and registers continuation

### Feature 1.5: Duplicate Alert Detection
**Description:** Prevents duplicate trade execution within 5-minute window
**File Location:** `src/processors/alert_processor.py` (line 40)
**Dependencies:** In-memory cache
**Configuration:** 5-minute deduplication window

### Feature 1.6: Strategy Detection from TradingView
**Description:** Maps TradingView strategy names to internal logic identifiers
**File Location:** `src/managers/timeframe_trend_manager.py` → `detect_logic_from_strategy_or_timeframe()`
**Dependencies:** None
**Mapping:** "ZepixPremium" → combinedlogic-1/2/3 based on timeframe

### Feature 1.7: Logic Enable/Disable Control
**Description:** Toggle individual logics on/off via Telegram
**File Location:** `src/clients/telegram_bot_fixed.py`
**Dependencies:** Config persistence
**Commands:** `/logic1_on`, `/logic1_off`, `/logic2_on`, `/logic2_off`, `/logic3_on`, `/logic3_off`

### Feature 1.8: Simulation Mode
**Description:** Test trades without real execution
**File Location:** `src/core/trading_engine.py`
**Dependencies:** Config flag
**Configuration:** `config.json` → `simulate_orders: true/false`

---

## CATEGORY 2: DUAL ORDER SYSTEM (5 Features)

### Feature 2.1: Dual Order Manager
**Description:** Places two orders per entry signal with different SL strategies
**File Location:** `src/managers/dual_order_manager.py` (346 lines)
**Dependencies:** RiskManager, MT5Client, PipCalculator, ProfitSLCalculator
**Configuration:** `config.json` → `dual_order_config`

### Feature 2.2: Order A (TP Trail)
**Description:** First order with V3 Smart SL system
**File Location:** `src/managers/dual_order_manager.py` → `create_dual_orders()`
**SL System:** Dynamic SL based on account tier and symbol
**TP System:** RR ratio-based TP
**Re-entry:** Eligible for TP Continuation chain

### Feature 2.3: Order B (Profit Trail)
**Description:** Second order with fixed $10 risk SL
**File Location:** `src/managers/dual_order_manager.py` → `create_dual_orders()`
**SL System:** Fixed $10 risk SL (via ProfitSLCalculator)
**TP System:** RR ratio-based TP
**Re-entry:** Eligible for Profit Booking chain

### Feature 2.4: Smart Lot Adjustment
**Description:** Auto-reduces lot size when daily loss limit is near
**File Location:** `src/managers/dual_order_manager.py` → `validate_dual_order_risk()` (lines 70-116)
**Dependencies:** RiskManager
**Logic:** Calculates max safe lot to fit remaining daily risk allowance

### Feature 2.5: Independent Order Execution
**Description:** Orders A and B execute independently (no rollback if one fails)
**File Location:** `src/managers/dual_order_manager.py` → `create_dual_orders()` (lines 271-298)
**Dependencies:** MT5Client
**Behavior:** If Order A fails, Order B still attempts; no atomic transaction

---

## CATEGORY 3: RE-ENTRY SYSTEM (7 Features)

### Feature 3.1: Re-Entry Manager
**Description:** Central manager for all re-entry chains
**File Location:** `src/managers/reentry_manager.py` (562 lines)
**Dependencies:** TrendAnalyzer, Config
**Configuration:** `config.json` → `re_entry_config`

### Feature 3.2: SL Hunt Recovery
**Description:** Autonomous recovery after SL hit with 70% price recovery threshold
**File Location:** `src/managers/reentry_manager.py` → `check_sl_hunt_recovery()` (lines 344-470)
**Dependencies:** RecoveryWindowMonitor, AutonomousSystemManager
**Configuration:** `re_entry_config.autonomous_config.sl_hunt_recovery`

**Recovery Logic:**
1. SL hit detected → Chain enters `recovery_mode`
2. Monitor price for recovery (symbol-specific window: 10-50 minutes)
3. If price recovers 70% of SL distance → Place recovery trade
4. Recovery trade uses 50% tighter SL
5. Max 1 recovery attempt per chain

### Feature 3.3: TP Continuation
**Description:** Autonomous continuation after TP hit
**File Location:** `src/managers/reentry_manager.py` → `check_autonomous_tp_continuation()` (lines 472-561)
**Dependencies:** AutonomousSystemManager
**Configuration:** `re_entry_config.autonomous_config.tp_continuation`

**Continuation Logic:**
1. TP hit detected → Record in `completed_tps`
2. Check if within continuation window
3. Check trend alignment
4. If eligible → Place continuation trade with reduced SL
5. Progressive SL reduction per level

### Feature 3.4: Exit Continuation
**Description:** Re-entry after manual/reversal exit when price reverts
**File Location:** `src/managers/exit_continuation_monitor.py` (523 lines)
**Dependencies:** AutonomousSystemManager, TrendAnalyzer
**Configuration:** `re_entry_config.autonomous_config.exit_continuation`

**Continuation Logic:**
1. Trade closed (manual/reversal) → Start monitoring
2. Monitor window: 60 seconds (configurable)
3. Check every 5 seconds for price reversion
4. If price reverts + trend aligns → Place re-entry

### Feature 3.5: Recovery Window Monitor
**Description:** Real-time price monitoring for SL Hunt recovery
**File Location:** `src/managers/recovery_window_monitor.py` (626 lines)
**Dependencies:** AutonomousSystemManager, MT5Client
**Configuration:** Symbol-specific recovery windows

**Symbol-Specific Windows:**
| Symbol | Window | Rationale |
|--------|--------|-----------|
| XAUUSD | 15 min | High volatility |
| GBPJPY | 20 min | Very volatile |
| EURUSD | 30 min | Moderate |
| USDCHF | 35 min | Low volatility |

### Feature 3.6: Chain Level Tracking
**Description:** Tracks re-entry chain levels and progression
**File Location:** `src/managers/reentry_manager.py` → `update_chain_level()` (lines 313-342)
**Dependencies:** Database persistence
**Configuration:** `re_entry_config.max_chain_levels` (default: 5)

### Feature 3.7: Progressive SL Reduction
**Description:** Reduces SL distance with each chain level
**File Location:** `src/managers/reentry_manager.py` → `_check_tp_continuation()` (lines 161-162)
**Dependencies:** Config
**Configuration:** `re_entry_config.sl_reduction_per_level` (e.g., 0.3 = 30%)

---

## CATEGORY 4: PROFIT BOOKING SYSTEM (6 Features)

### Feature 4.1: Profit Booking Manager
**Description:** Manages profit booking chains for pyramid compounding
**File Location:** `src/managers/profit_booking_manager.py` (1087 lines)
**Dependencies:** MT5Client, RiskManager, Database
**Configuration:** `config.json` → `profit_booking_config`

### Feature 4.2: 5-Level Pyramid Chain
**Description:** Progressive order multiplication system
**File Location:** `src/managers/profit_booking_manager.py` → `__init__()` (lines 40-42)
**Dependencies:** Config
**Configuration:** `profit_booking_config.multipliers`

| Level | Orders | Profit Target | Total Orders |
|-------|--------|---------------|--------------|
| 0 | 1 | $7 | 1 |
| 1 | 2 | $7 each | 3 |
| 2 | 4 | $7 each | 7 |
| 3 | 8 | $7 each | 15 |
| 4 | 16 | $7 each | 31 |

### Feature 4.3: Individual Order Booking
**Description:** Books orders individually when they reach $7 profit
**File Location:** `src/managers/profit_booking_manager.py` → `book_individual_order()` (lines 312-355)
**Dependencies:** TradingEngine
**Configuration:** `profit_booking_config.min_profit` (default: $7)

### Feature 4.4: Chain Progression
**Description:** Progresses to next level when all orders in current level are closed
**File Location:** `src/managers/profit_booking_manager.py` → `check_and_progress_chain()` (lines 357-579)
**Dependencies:** RiskManager, MT5Client
**Logic:** All orders closed → Place new orders for next level

### Feature 4.5: Strict Mode (Loss Handling)
**Description:** Stops chain if loss occurs in strict mode (unless recovered)
**File Location:** `src/managers/profit_booking_manager.py` → `check_and_progress_chain()` (lines 393-424)
**Dependencies:** Config
**Configuration:** `profit_booking_config.allow_partial_progression`

### Feature 4.6: Profit Booking SL Hunt
**Description:** Recovery for profit booking orders that hit SL
**File Location:** `src/managers/profit_booking_reentry_manager.py`
**Dependencies:** AutonomousSystemManager, RecoveryWindowMonitor
**Configuration:** `re_entry_config.autonomous_config.profit_sl_hunt`

---

## CATEGORY 5: RISK MANAGEMENT (6 Features)

### Feature 5.1: Risk Manager
**Description:** Central risk management for lot sizing and loss limits
**File Location:** `src/managers/risk_manager.py`
**Dependencies:** Config, MT5Client
**Configuration:** `config.json` → `risk_tiers`

### Feature 5.2: Account Tier System
**Description:** Risk parameters based on account balance
**File Location:** `src/managers/risk_manager.py` → `get_risk_tier()`
**Dependencies:** MT5Client (for balance)
**Configuration:** `config.json` → `risk_by_account_tier`

| Tier | Balance Range | Daily Loss Limit | Lifetime Limit |
|------|---------------|------------------|----------------|
| $5,000 | < $7,500 | $100 | $500 |
| $10,000 | $7,500 - $17,500 | $200 | $1,000 |
| $25,000 | $17,500 - $37,500 | $500 | $2,500 |
| $50,000 | $37,500 - $75,000 | $1,000 | $5,000 |
| $100,000 | > $75,000 | $2,000 | $10,000 |

### Feature 5.3: Daily Loss Limit
**Description:** Pauses trading when daily loss limit is reached
**File Location:** `src/managers/risk_manager.py`
**Dependencies:** Stats persistence (`data/stats.json`)
**Configuration:** Per-tier daily loss limits

### Feature 5.4: Lifetime Loss Limit
**Description:** Stops trading when lifetime loss limit is reached
**File Location:** `src/managers/risk_manager.py`
**Dependencies:** Stats persistence
**Configuration:** Per-tier lifetime loss limits

### Feature 5.5: Fixed Lot Sizing
**Description:** Fixed lot size per account tier
**File Location:** `src/managers/risk_manager.py` → `get_fixed_lot_size()`
**Dependencies:** Config
**Configuration:** `config.json` → `fixed_lot_sizes`

### Feature 5.6: Logic-Based Lot Sizing
**Description:** Different lot sizes per trading logic
**File Location:** `src/managers/risk_manager.py` → `get_lot_size_for_logic()`
**Dependencies:** Config
**Configuration:** `config.json` → `timeframe_specific_config.{logic}.lot_multiplier`

---

## CATEGORY 6: SL SYSTEM (4 Features)

### Feature 6.1: Dual SL System
**Description:** Two SL systems with different risk profiles
**File Location:** `src/utils/pip_calculator.py`
**Dependencies:** Config
**Configuration:** `config.json` → `sl_systems`

| System | Description | Use Case |
|--------|-------------|----------|
| SL-1 | Dynamic SL based on symbol/tier | Order A (TP Trail) |
| SL-2 | Fixed $10 risk SL | Order B (Profit Trail) |

### Feature 6.2: Symbol-Specific SL Pips
**Description:** Different SL pips per symbol and account tier
**File Location:** `src/utils/pip_calculator.py` → `_get_sl_from_dual_system()`
**Dependencies:** Config
**Configuration:** `sl_systems.sl-1.symbols.{symbol}.{tier}.sl_pips`

### Feature 6.3: SL Reduction Optimizer
**Description:** Optimizes SL reduction for re-entry chains
**File Location:** `src/managers/sl_reduction_optimizer.py`
**Dependencies:** Config
**Configuration:** `re_entry_config.sl_reduction_per_level`

### Feature 6.4: Profit SL Calculator
**Description:** Calculates fixed $10 risk SL for Order B
**File Location:** `src/utils/profit_sl_calculator.py`
**Dependencies:** Config, Symbol config
**Configuration:** `config.json` → `profit_booking_config`

---

## CATEGORY 7: AUTONOMOUS SYSTEM (5 Features)

### Feature 7.1: Autonomous System Manager
**Description:** Central coordinator for all autonomous trading operations
**File Location:** `src/managers/autonomous_system_manager.py` (1190 lines)
**Dependencies:** ReentryManager, ProfitBookingManager, RecoveryWindowMonitor, ReverseShieldManager
**Configuration:** `re_entry_config.autonomous_config`

### Feature 7.2: Daily Recovery Limits
**Description:** Limits daily recovery attempts to prevent over-trading
**File Location:** `src/managers/autonomous_system_manager.py` → `check_daily_limits()` (lines 80-112)
**Dependencies:** Daily stats tracking
**Configuration:** `autonomous_config.safety_limits.daily_recovery_attempts` (default: 10)

### Feature 7.3: Concurrent Recovery Limit
**Description:** Limits simultaneous recovery attempts
**File Location:** `src/managers/autonomous_system_manager.py` → `check_concurrent_recovery_limit()` (lines 114-125)
**Dependencies:** Active recovery tracking
**Configuration:** `autonomous_config.safety_limits.max_concurrent_recoveries` (default: 3)

### Feature 7.4: Profit Protection
**Description:** Skips recovery if existing profit is too valuable
**File Location:** `src/managers/autonomous_system_manager.py` → `should_skip_recovery_for_profit_protection()` (lines 127-153)
**Dependencies:** Chain profit tracking
**Configuration:** `autonomous_config.safety_limits.profit_protection_multiplier` (default: 5)

### Feature 7.5: Reverse Shield System (v3.0)
**Description:** Advanced protection during SL recovery with hedge orders
**File Location:** `src/managers/reverse_shield_manager.py`
**Dependencies:** MT5Client, ProfitBookingManager, RiskManager
**Configuration:** `re_entry_config.autonomous_config.reverse_shield`

**Shield Logic:**
1. SL hit → Activate shield (place hedge orders)
2. Monitor for 70% recovery level
3. If 70% reached → Kill switch (close shields, restore original trade)
4. If timeout → Close shields with profit/loss

---

## CATEGORY 8: TELEGRAM SYSTEM (6 Features)

### Feature 8.1: Telegram Bot (Main)
**Description:** Primary Telegram interface with 95+ commands
**File Location:** `src/clients/telegram_bot_fixed.py` (5126 lines)
**Dependencies:** All managers, TradingEngine
**Configuration:** `config.json` → `telegram_token`, `telegram_chat_id`

### Feature 8.2: Interactive Menu System
**Description:** Zero-typing interface with inline keyboards
**File Location:** `src/menu/` directory (multiple handlers)
**Dependencies:** Telegram Bot API
**Categories:** 13 menu categories

### Feature 8.3: Persistent Reply Keyboard
**Description:** Always-visible quick access buttons
**File Location:** `src/clients/telegram_bot_fixed.py`
**Dependencies:** Telegram Bot API
**Layout:** Dashboard, Pause/Resume, Trades, Risk, Re-entry, SL System, Trends, Profit, Help, PANIC CLOSE

### Feature 8.4: Voice Alert System
**Description:** Audio notifications via Telegram voice messages
**File Location:** `src/utils/voice_alert_system.py` (429 lines)
**Dependencies:** gTTS, Telegram Bot API
**Configuration:** `config.json` → `voice_alerts_enabled`

### Feature 8.5: Real-time Notifications
**Description:** 50+ notification types for all trading events
**File Location:** Various managers (send via telegram_bot)
**Dependencies:** Telegram Bot
**Types:** Entry, Exit, TP, SL, Recovery, Chain, Error, Daily Summary

### Feature 8.6: Command Categories
**Description:** 95+ commands organized in 13 categories
**File Location:** `docs/developer_notes/TELEGRAM_COMMAND_STRUCTURE.md`
**Categories:**
1. Trading Control (7 commands)
2. Performance & Analytics (8 commands)
3. Strategy Control (8 commands)
4. Re-entry System (14 commands)
5. Trend Management (5 commands)
6. Risk & Lot Management (11 commands)
7. SL System Control (8 commands)
8. Dual Orders (2 commands)
9. Profit Booking (16 commands)
10. Timeframe Logic (4 commands)
11. Fine-Tune Settings (4 commands)
12. Session Management (5 commands)
13. Diagnostics & Health (15 commands)

---

## CATEGORY 9: DATABASE SYSTEM (4 Features)

### Feature 9.1: Trade Database
**Description:** SQLite database for trade history and chains
**File Location:** `src/database.py`
**Dependencies:** SQLite3
**Tables:** trades, reentry_chains, profit_booking_chains, sl_events, trading_sessions

### Feature 9.2: Trade History Persistence
**Description:** Complete trade record storage
**File Location:** `src/database.py` → `save_trade()`
**Dependencies:** SQLite
**Fields:** Entry/exit prices, SL/TP, PnL, commission, swap, chain associations, logic type

### Feature 9.3: Chain Tracking
**Description:** Re-entry and profit chain persistence
**File Location:** `src/database.py` → `save_reentry_chain()`, `save_profit_chain()`
**Dependencies:** SQLite
**Tracked:** Chain levels, status, total profit, trade associations

### Feature 9.4: Stats Persistence
**Description:** Risk statistics persistence
**File Location:** `data/stats.json`
**Dependencies:** File system
**Fields:** daily_loss, lifetime_loss, daily_profit, total_trades, winning_trades, last_reset_date

---

## CATEGORY 10: CONFIGURATION SYSTEM (4 Features)

### Feature 10.1: Main Configuration
**Description:** Central configuration file
**File Location:** `config/config.json`
**Dependencies:** File system
**Sections:** Telegram, MT5, symbols, risk, SL systems, re-entry, profit booking

### Feature 10.2: Environment Variable Override
**Description:** Sensitive data via environment variables
**File Location:** `.env`
**Dependencies:** python-dotenv
**Variables:** TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, MT5_LOGIN, MT5_PASSWORD, MT5_SERVER

### Feature 10.3: Trend State Persistence
**Description:** Trend state persistence across restarts
**File Location:** `config/timeframe_trends.json`
**Dependencies:** TimeframeTrendManager
**Fields:** Per-symbol, per-timeframe trend and mode

### Feature 10.4: Symbol Mapping
**Description:** TradingView to broker symbol translation
**File Location:** `config/config.json` → `symbol_mapping`
**Dependencies:** Config
**Example:** "XAUUSD" → "GOLD"

---

## CATEGORY 11: MONITORING & HEALTH (3 Features)

### Feature 11.1: Health Check Endpoint
**Description:** API endpoint for monitoring
**File Location:** `src/main.py` → `/health`
**Dependencies:** FastAPI
**Response:** status, mt5_connected, telegram_active, uptime

### Feature 11.2: Statistics Endpoint
**Description:** Trading statistics API
**File Location:** `src/main.py` → `/stats`
**Dependencies:** FastAPI, RiskManager
**Response:** total_trades, winning_trades, win_rate, total_pnl, daily_pnl

### Feature 11.3: Connection Health Monitoring
**Description:** MT5 connection reliability
**File Location:** `src/clients/mt5_client.py`
**Dependencies:** MT5 API
**Features:** Periodic health checks, auto-reconnect, error tracking

---

## CATEGORY 12: SAFETY FEATURES (4 Features)

### Feature 12.1: Panic Close
**Description:** Emergency position closure
**File Location:** `src/clients/telegram_bot_fixed.py` → `/panic_close`
**Dependencies:** MT5Client, TradingEngine
**Actions:** Close all positions, stop all chains, pause trading

### Feature 12.2: Daily Reset
**Description:** Automatic daily stats reset
**File Location:** `src/managers/risk_manager.py`
**Dependencies:** Stats persistence
**Reset Time:** 03:35 UTC (configurable)

### Feature 12.3: Rotating File Logs
**Description:** Automatic log rotation
**File Location:** `src/utils/optimized_logger.py`
**Dependencies:** logging module
**Configuration:** Max 2MB per file, 50 backup files

### Feature 12.4: Forex Session System
**Description:** Session-based trade filtering
**File Location:** `src/managers/session_manager.py`
**Dependencies:** Config
**Sessions:** Asian, London, NY with overlap handling

---

## SUMMARY

**Total Features Documented:** 47 Features
**Categories:** 12 Categories
**Critical for V5 Surgery:** ALL features must be preserved or properly migrated

**Key Dependencies to Preserve:**
1. ReentryManager ↔ AutonomousSystemManager ↔ RecoveryWindowMonitor
2. DualOrderManager ↔ RiskManager ↔ PipCalculator
3. ProfitBookingManager ↔ AutonomousSystemManager ↔ TradingEngine
4. TimeframeTrendManager ↔ TradingEngine ↔ AlertProcessor
5. TelegramBot ↔ All Managers

**Configuration Files to Preserve:**
1. `config/config.json` - Main configuration
2. `config/timeframe_trends.json` - Trend state
3. `data/stats.json` - Risk statistics
4. `.env` - Sensitive credentials

---

**Next Step:** Create STUDY_REPORT_02_V5_PLANNING_REQUIREMENTS.md
