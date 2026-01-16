# DOCUMENTATION MERGE MANDATE

## Mission
Consolidate all documentation from `DOCUMENTATION/` and `06_DOCUMENTATION_BIBLE/` into a single, authoritative source: `docs/V5_BIBLE/`.

## Source Directories
1. **DOCUMENTATION/** (14 files, ~280KB) - Original bot documentation
2. **06_DOCUMENTATION_BIBLE/** (21 files, ~288KB) - V5 architecture documentation

## Target Directory
`docs/V5_BIBLE/` - The single source of truth for Zepix V5 Bot

## Merge Strategy

### Phase 1: Deep Scan (COMPLETED)
- Read all src/ files to trace V3/V6 logic chains
- Identify actual implementations vs documentation claims
- Map signal flows, order execution, and plugin delegation

### Phase 2: DEEP_DIVE Files (IN PROGRESS)
Create authoritative documentation based on actual code:

1. **V3_DEEP_DIVE.md** - Complete V3 Combined Logic analysis
   - 12 signal types (7 entry, 2 exit, 2 info, 1 bonus)
   - Signal handlers and routing
   - Dual order system (Order A: TP_TRAIL, Order B: PROFIT_TRAIL)
   - Re-entry system (SL Hunt, TP Continuation)
   - Profit booking chains

2. **V6_DEEP_DIVE.md** - Complete V6 Price Action analysis
   - 4 timeframe plugins (1m, 5m, 15m, 1h)
   - Entry filters (ADX, Confidence, Alignment)
   - Risk multipliers per timeframe
   - Shadow mode support

3. **ARCHITECTURE_DEEP_DIVE.md** - System architecture
   - Trading Engine orchestration
   - Plugin delegation system
   - ServiceAPI facade
   - 3-bot Telegram cluster
   - Shadow mode manager

### Phase 3: Consolidation
Merge existing documentation into organized structure:
- 00_INDEX.md - Master table of contents
- 01_ARCHITECTURE/ - System design
- 02_TRADING_LOGIC/ - V3 and V6 strategies
- 03_TELEGRAM/ - Bot commands and menus
- 04_CONFIGURATION/ - Config reference
- 05_DEVELOPER/ - Plugin development guide

## Key Findings from Deep Scan

### V3 Combined Logic Plugin (src/logic_plugins/v3_combined/plugin.py)
- **Lines:** 1836
- **Interfaces:** ISignalProcessor, IOrderExecutor, IReentryCapable, IDualOrderCapable, IProfitBookingCapable, IAutonomousCapable, IDatabaseCapable
- **Signal Types:** 12 total
  - Entry (7): Institutional_Launchpad, Liquidity_Trap, Momentum_Breakout, Mitigation_Test, Golden_Pocket_Flip, Screener_Full_Bullish, Screener_Full_Bearish
  - Exit (2): Bullish_Exit, Bearish_Exit
  - Info (2): Volatility_Squeeze, Trend_Pulse
  - Bonus (1): Sideways_Breakout

### V6 Price Action Plugins (src/logic_plugins/v6_price_action_*/plugin.py)
- **5M Plugin:** ADX >= 25, Confidence >= 70, 15M Alignment, Risk 1.0x
- **15M Plugin:** ADX >= 20, Confidence >= 65, 1H Alignment, Risk 1.2x
- **1H Plugin:** ADX >= 15, Confidence >= 60, 4H Alignment, Risk 1.5x
- **1M Plugin:** Spread filter, High confidence, Risk 0.5x

### Trading Engine (src/core/trading_engine.py)
- **Lines:** 2382
- **Key Methods:**
  - delegate_to_plugin() - Routes signals to appropriate plugin
  - execute_v3_entry() - V3 entry execution
  - handle_v3_exit() - V3 exit handling
  - handle_v3_reversal() - V3 reversal handling

### ServiceAPI (src/core/plugin_system/service_api.py)
- **Lines:** 1312
- **Version:** 3.0.0
- **Services:** OrderExecution, RiskManagement, TrendManagement, MarketData, Reentry, DualOrder, ProfitBooking, Autonomous, Telegram

## Execution Status
- [x] Create 12_DOCUMENTATION_MERGE directory
- [x] Create docs/V5_BIBLE directory
- [ ] Create V3_DEEP_DIVE.md
- [ ] Create V6_DEEP_DIVE.md
- [ ] Create ARCHITECTURE_DEEP_DIVE.md
- [ ] Consolidate existing documentation
- [ ] Create master index

## Date
2026-01-16
