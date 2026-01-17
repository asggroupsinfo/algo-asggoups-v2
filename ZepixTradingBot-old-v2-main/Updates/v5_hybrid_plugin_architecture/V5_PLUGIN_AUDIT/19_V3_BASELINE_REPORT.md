# V3 BASELINE REPORT - MANDATE 19

**Date:** 2026-01-17
**Purpose:** Capture V3 state BEFORE any V6 fixes
**Status:** BASELINE CAPTURED

---

## V3 PLUGIN FILE CHECKSUMS (MD5)

These checksums MUST match after V6 fixes to prove V3 was not modified:

```
37290b352bbf94dbde2984ab84a30618  Trading_Bot/src/logic_plugins/v3_combined/__init__.py
ceedc93f6f68c446c7b7b8597a4d7330  Trading_Bot/src/logic_plugins/v3_combined/order_events.py
e5982e2a80bd7d71770d27eacef026f2  Trading_Bot/src/logic_plugins/v3_combined/order_manager.py
04f767fedfd62f8ad60b15eea1d1ca5a  Trading_Bot/src/logic_plugins/v3_combined/plugin.py
792c71ff4cbd831f9c212e5fd41352e7  Trading_Bot/src/logic_plugins/v3_combined/signal_handlers.py
0564fe78d8319d2caf54fd4cc79ceda7  Trading_Bot/src/logic_plugins/v3_combined/trend_validator.py
```

## V3 PLUGIN FILE SIZES

```
   17 lines  Trading_Bot/src/logic_plugins/v3_combined/__init__.py
  243 lines  Trading_Bot/src/logic_plugins/v3_combined/order_events.py
  834 lines  Trading_Bot/src/logic_plugins/v3_combined/order_manager.py
 2033 lines  Trading_Bot/src/logic_plugins/v3_combined/plugin.py
  528 lines  Trading_Bot/src/logic_plugins/v3_combined/signal_handlers.py
  367 lines  Trading_Bot/src/logic_plugins/v3_combined/trend_validator.py
-----------------------------------------
 4022 lines  TOTAL
```

## V3 CRITICAL CONFIGURATION VALUES

### From plugin.py (V3CombinedPlugin):

| Parameter | Value | Location |
|-----------|-------|----------|
| Signal Types (Entry) | 7 | Lines 84-87 |
| Signal Types (Exit) | 2 | Line 88 |
| Signal Types (Info) | 2 | Line 89 |
| Shadow Mode Default | False | Line 81 |
| Interfaces Implemented | 8 | Line 46 |

### From order_manager.py (V3OrderManager):

| Parameter | Value | Location |
|-----------|-------|----------|
| Split Ratio | 0.5 (50/50) | Line 56 |
| Fixed SL Dollars | $10.0 | Line 57 |
| Order A SL Source | V3_SMART (Pine Script) | Line 243 |
| Order B SL Source | FIXED_PYRAMID ($10) | Line 303 |
| Order A TP | TP2 (Extended) | Line 218 |
| Order B TP | TP1 (Closer) | Line 275 |

### V3 Consensus Score Mapping (Lines 166-190):

| Score Range | Multiplier |
|-------------|------------|
| 0 | 0.2 |
| 1-3 | 0.2 + (score * 0.1) |
| 4-6 | 0.5 + ((score-3) * 0.1) |
| 7-8 | 0.8 + ((score-6) * 0.05) |
| 9 | 1.0 |

## V3 SERVICEAPI METHODS USED

The V3 plugin uses these ServiceAPI methods (must remain backward compatible):

1. `calculate_lot_size(symbol)` - Get base lot from account tier
2. `calculate_sl_price(plugin_id, price, direction, lot_size)` - Fallback SL calculation
3. `place_order_async(symbol, direction, lot_size, entry_price, sl_price, tp_price, comment, metadata)` - Order placement

## V3 INTERFACES IMPLEMENTED

```python
class V3CombinedPlugin(
    BaseLogicPlugin,
    ISignalProcessor,
    IOrderExecutor,
    IReentryCapable,
    IDualOrderCapable,
    IProfitBookingCapable,
    IAutonomousCapable,
    IDatabaseCapable
)
```

## VERIFICATION COMMAND

Run this command after V6 fixes to verify V3 unchanged:

```bash
cd /home/ubuntu/repos/algo-asggoups-v1/ZepixTradingBot-old-v2-main
md5sum Trading_Bot/src/logic_plugins/v3_combined/*.py
```

Expected output must match the checksums above EXACTLY.

---

## BASELINE CAPTURED AT

- **Git Commit:** 5035e3c
- **Branch:** devin/1768654888-mandate19-v6-fix-v3-protection
- **Timestamp:** 2026-01-17 13:00 UTC

---

**CRITICAL:** If ANY V3 checksum changes after V6 fixes, REVERT IMMEDIATELY.
