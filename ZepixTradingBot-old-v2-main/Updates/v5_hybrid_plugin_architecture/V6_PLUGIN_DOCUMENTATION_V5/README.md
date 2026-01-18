# V6 Price Action Plugin Documentation (V5 Architecture)

**Document Version**: 1.0.0  
**Last Updated**: 2026-01-18  
**Pine Script Source**: `Signals_and_Overlays_V6_Enhanced_Build.pine` (1683 lines)

---

## Overview

This folder contains comprehensive documentation for the V6 Price Action Plugin system within the V5 Hybrid Plugin Architecture. Unlike V3's single combined plugin, V6 uses three timeframe-specific plugins for optimized signal processing.

---

## Documentation Files

| File | Description | Status |
|------|-------------|--------|
| [00_V6_PLUGIN_OVERVIEW.md](./00_V6_PLUGIN_OVERVIEW.md) | Executive summary and architecture overview | COMPLETE |
| [01_V6_PINE_LOGIC_BREAKDOWN.md](./01_V6_PINE_LOGIC_BREAKDOWN.md) | Section-by-section Pine Script analysis | COMPLETE |
| [02_V6_BOT_FEATURES_39.md](./02_V6_BOT_FEATURES_39.md) | Complete 39-feature mapping | COMPLETE |
| [03_V6_PLUGIN_IMPLEMENTATION_PLAN.md](./03_V6_PLUGIN_IMPLEMENTATION_PLAN.md) | Step-by-step implementation guide | COMPLETE |
| [04_V6_ALERT_PROCESSING.md](./04_V6_ALERT_PROCESSING.md) | Alert flow from TradingView to execution | COMPLETE |
| [05_V6_TESTING_STRATEGY.md](./05_V6_TESTING_STRATEGY.md) | Testing approach with 120 test cases | COMPLETE |
| [06_V6_CONFLICT_RESOLUTION.md](./06_V6_CONFLICT_RESOLUTION.md) | Conflict handling and V3/V6 isolation | COMPLETE |
| [07_V6_DEPLOYMENT_GUIDE.md](./07_V6_DEPLOYMENT_GUIDE.md) | Production deployment instructions | COMPLETE |
| [08_V6_CROSS_VERIFICATION_REPORT.md](./08_V6_CROSS_VERIFICATION_REPORT.md) | Pine Script to Bot verification | COMPLETE |
| [README.md](./README.md) | This file - index and navigation | COMPLETE |

---

## Quick Reference

### V6 Plugin System

| Plugin | Timeframe | Risk Multiplier | Base Lot |
|--------|-----------|-----------------|----------|
| v6_price_action_5m | 5m | 0.5x | 0.05 |
| v6_price_action_15m | 15m | 1.0x | 0.10 |
| v6_price_action_1h | 1H/4H | 1.5x | 0.15 |

### Alert Types (14)

**Entry Alerts (6)**:
- Breakout Entry Bull/Bear
- Momentum Entry Bull/Bear
- Screener Full Bullish/Bearish

**Exit Alerts (2)**:
- Bullish Exit
- Bearish Exit

**Trend Pulse Alerts (4)**:
- Trend Pulse Bull
- Trend Pulse Bear
- Trend Pulse Mixed
- Trend Pulse Neutral

**Momentum Alerts (2)**:
- Momentum Surge
- Momentum Fade

### Key Features

| Feature | Description |
|---------|-------------|
| Trendline Integration | Pivot-based trendline detection and breakout |
| MTF Analysis | 6-timeframe trend tracking (1m, 5m, 15m, 1H, 4H, 1D) |
| Confidence Scoring | 0-100 score with HIGH/MEDIUM/LOW classification |
| ADX Momentum Filter | Minimum ADX threshold for entries |
| Dual Order System | Order A (trailing) + Order B (profit booking) |
| Pine Supremacy | Bot never overrides Pine Script calculations |

### Alert Payload Format

**Entry Alert**:
```json
{
  "type": "entry_v6",
  "signal_type": "Breakout_Entry",
  "symbol": "EURUSD",
  "direction": "buy",
  "tf": "15",
  "price": 1.08500,
  "confidence": "HIGH",
  "adx_value": 32.5,
  "trendline_break": true,
  "mtf_trends": "1,1,1,1,1,1",
  "aligned_count": 6,
  "sl_price": 1.08200,
  "tp1_price": 1.08800,
  "tp2_price": 1.09100,
  "volume_confirmed": true
}
```

**Trend Pulse Alert**:
```json
{
  "type": "trend_pulse_v6",
  "signal_type": "Trend_Pulse_Bull",
  "symbol": "EURUSD",
  "tf": "15",
  "price": 1.08500,
  "current_trends": "1,1,1,1,1,1",
  "previous_trends": "1,1,1,-1,-1,-1",
  "changed_timeframes": "1H,4H,1D",
  "change_details": "1H: BEAR→BULL, 4H: BEAR→BULL, 1D: BEAR→BULL",
  "aligned_count": 6,
  "confidence": "HIGH"
}
```

---

## Source Files

| File | Location | Lines |
|------|----------|-------|
| Pine Script | `Important_Doc_Trading_Bot/05_Unsorted/TRADINGVIEW_PINE_SCRIPT/Signals_and_Overlays_V6_Enhanced_Build.pine` | 1683 |
| 5m Plugin | `src/logic_plugins/v6_price_action_5m/plugin.py` | ~200 |
| 15m Plugin | `src/logic_plugins/v6_price_action_15m/plugin.py` | ~200 |
| 1H Plugin | `src/logic_plugins/v6_price_action_1h/plugin.py` | ~200 |

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Total Features | 39 |
| Alert Types | 14 |
| Timeframes Supported | 6 |
| Test Cases | 120 |
| Pine Script Lines | 1683 |
| Documentation Files | 10 |
| Verification Status | 100% MATCH |

---

## Related Documentation

| Document | Location |
|----------|----------|
| V3 Plugin Documentation | `../V3_PLUGIN_DOCUMENTATION_V5/` |
| Dual Plugin Flow Summary | `../DUAL_PLUGIN_FLOW_SUMMARY.md` |
| V5 Architecture Bible | `../V5_BIBLE/` |

---

## Document Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| 00_V6_PLUGIN_OVERVIEW.md | COMPLETE | 2026-01-18 |
| 01_V6_PINE_LOGIC_BREAKDOWN.md | COMPLETE | 2026-01-18 |
| 02_V6_BOT_FEATURES_39.md | COMPLETE | 2026-01-18 |
| 03_V6_PLUGIN_IMPLEMENTATION_PLAN.md | COMPLETE | 2026-01-18 |
| 04_V6_ALERT_PROCESSING.md | COMPLETE | 2026-01-18 |
| 05_V6_TESTING_STRATEGY.md | COMPLETE | 2026-01-18 |
| 06_V6_CONFLICT_RESOLUTION.md | COMPLETE | 2026-01-18 |
| 07_V6_DEPLOYMENT_GUIDE.md | COMPLETE | 2026-01-18 |
| 08_V6_CROSS_VERIFICATION_REPORT.md | COMPLETE | 2026-01-18 |
| README.md | COMPLETE | 2026-01-18 |

---

**Total Documentation Files**: 10  
**Feature Coverage**: 100%  
**V5 Architecture Compliance**: VERIFIED
