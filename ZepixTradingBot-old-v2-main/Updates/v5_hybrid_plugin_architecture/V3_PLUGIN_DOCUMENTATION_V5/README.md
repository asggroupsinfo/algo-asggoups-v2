# V3 Combined Logic Plugin Documentation (V5 Architecture)

**Version**: 1.0.0  
**Last Updated**: 2026-01-18  
**Architecture**: V5 Hybrid Plugin Architecture

---

## Overview

This folder contains comprehensive V5-aligned documentation for the V3 Combined Logic Plugin, which implements the complete ZEPIX ULTIMATE BOT v3.0 trading system.

---

## Documentation Files

| File | Description |
|------|-------------|
| `00_V3_PLUGIN_OVERVIEW.md` | Executive summary, architecture overview, signal types |
| `01_V3_PINE_LOGIC_BREAKDOWN.md` | Complete Pine Script analysis (1934 lines) |
| `02_V3_BOT_FEATURES_39.md` | All 39 features with implementation mapping |
| `03_V3_PLUGIN_IMPLEMENTATION_PLAN.md` | Step-by-step implementation guide |
| `04_V3_ALERT_PROCESSING.md` | Alert flow from TradingView to execution |
| `05_V3_TESTING_STRATEGY.md` | Testing approach with 98 test cases |
| `06_V3_CONFLICT_RESOLUTION.md` | Conflict handling and V3/V6 isolation |
| `07_V3_DEPLOYMENT_GUIDE.md` | Production deployment instructions |
| `08_V3_CROSS_VERIFICATION_REPORT.md` | Pine Script to Bot verification (100% match) |

---

## Quick Reference

### Signal Types (12)

**Entry Signals (7)**:
1. Institutional Launchpad
2. Liquidity Trap Reversal
3. Momentum Breakout
4. Mitigation Test Entry
5. Golden Pocket Flip
6. Screener Full Bullish
7. Screener Full Bearish

**Exit Signals (2)**:
8. Bullish Exit
9. Bearish Exit

**Info Signals (2)**:
10. Volatility Squeeze
11. Trend Pulse

**Bonus Signal (1)**:
12. Sideways Breakout

### 5-Layer Architecture

| Layer | Weight | Purpose |
|-------|--------|---------|
| SMC | 40% | Order Blocks, FVG, Liquidity |
| Consensus | 25% | 9-Indicator Voting |
| Breakout | 20% | Trend Line Breaks |
| Risk | 10% | Position Sizing |
| Conflict | 5% | Signal Priority |

### Signal Routing

| Timeframe | Logic | Risk Multiplier |
|-----------|-------|-----------------|
| 5m | LOGIC1 | 0.5x |
| 15m | LOGIC2 | 1.0x |
| 1H/4H | LOGIC3 | 1.5x |

**Overrides**:
- Screener Full → Always LOGIC3
- Golden Pocket (1H/4H) → Always LOGIC3

---

## Source Files

| Type | Path |
|------|------|
| Pine Script | `Important_Doc_Trading_Bot/05_Unsorted/TRADINGVIEW_PINE_SCRIPT/ZEPIX_ULTIMATE_BOT_v3.0_FINAL.pine` |
| Plugin | `Trading_Bot/src/logic_plugins/v3_combined/plugin.py` |
| Signal Handlers | `Trading_Bot/src/logic_plugins/v3_combined/signal_handlers.py` |
| Order Manager | `Trading_Bot/src/logic_plugins/v3_combined/order_manager.py` |

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Pine Script Lines | 1934 |
| Plugin Lines | 2034 |
| Signal Types | 12 |
| Features | 39 |
| Test Cases | 98 |
| Verification | 100% |

---

## Related Documentation

- [V6 Plugin Documentation](../V6_PLUGIN_DOCUMENTATION_V5/)
- [Dual Plugin Flow Summary](../DUAL_PLUGIN_FLOW_SUMMARY.md)
- [V5 Architecture Overview](../V5_BIBLE/)

---

## Document Status

| Document | Status |
|----------|--------|
| 00_V3_PLUGIN_OVERVIEW.md | COMPLETE |
| 01_V3_PINE_LOGIC_BREAKDOWN.md | COMPLETE |
| 02_V3_BOT_FEATURES_39.md | COMPLETE |
| 03_V3_PLUGIN_IMPLEMENTATION_PLAN.md | COMPLETE |
| 04_V3_ALERT_PROCESSING.md | COMPLETE |
| 05_V3_TESTING_STRATEGY.md | COMPLETE |
| 06_V3_CONFLICT_RESOLUTION.md | COMPLETE |
| 07_V3_DEPLOYMENT_GUIDE.md | COMPLETE |
| 08_V3_CROSS_VERIFICATION_REPORT.md | COMPLETE |

**Overall Status**: COMPLETE (9/9 files)

---

**V5 Architecture Compliance**: VERIFIED  
**Pine Script Accuracy**: 100%  
**Feature Coverage**: 39/39
