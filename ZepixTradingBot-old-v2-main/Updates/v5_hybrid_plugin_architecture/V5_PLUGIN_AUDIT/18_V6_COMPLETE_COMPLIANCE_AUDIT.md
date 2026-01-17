# MANDATE 18: V6 COMPLETE COMPLIANCE AUDIT

**Date:** 2026-01-17
**Auditor:** Devin AI
**Status:** CRITICAL DISCREPANCIES FOUND

---

## EXECUTIVE SUMMARY

This forensic audit compares three sources:
1. **Pine Script:** `Signals_and_Overlays_V6_Enhanced_Build.pine` (1683 lines)
2. **Documentation:** `V5_BIBLE/11_V6_PRICE_ACTION_PLUGINS.md` and `V6_LOGIC_DEEP_DIVE.md`
3. **Actual Code:** `src/logic_plugins/v6_price_action_*` (4 plugins)

**VERDICT: MULTIPLE CRITICAL DISCREPANCIES FOUND**

The documentation contains conflicting information, and the actual code implementation differs significantly from both the Pine Script logic and the documentation.

---

## COMPLIANCE MATRIX

### 1. V6 1-MINUTE SCALPING PLUGIN

| Parameter | Pine Script | Doc (11_V6) | Doc (DEEP_DIVE) | Actual Code | STATUS |
|-----------|-------------|-------------|-----------------|-------------|--------|
| Timeframe | "1" | 1 minute | 1 minute | "1" | PASS |
| Order Routing | N/A (Pine doesn't specify) | SINGLE ORDER | N/A | ORDER_B_ONLY | PASS |
| Risk Multiplier | N/A | 0.5x | 0.5x | 0.5x | PASS |
| ADX Threshold | >= 25 (STRONG) | >= 20 | >= 30 | >= 20 | MISMATCH |
| Confidence Threshold | N/A | >= 80 | >= 80 | >= 80 | PASS |
| Alignment Required | 6 TFs (minTFAlignment=4) | 5M alignment | 5M alignment | IGNORED | MISMATCH |
| Spread Check | N/A | Required | Required | MAX_SPREAD_PIPS=2.0 | PASS |
| TP Target | TP1 | N/A | N/A | TP1 | PASS |

**1M DISCREPANCIES:**
1. ADX Threshold: Pine says >= 25 for STRONG, Doc (DEEP_DIVE) says >= 30, Code says >= 20
2. Alignment: Docs say 5M alignment required, Code IGNORES Trend Pulse entirely for 1M

---

### 2. V6 5-MINUTE MOMENTUM PLUGIN

| Parameter | Pine Script | Doc (11_V6) | Doc (DEEP_DIVE) | Actual Code | STATUS |
|-----------|-------------|-------------|-----------------|-------------|--------|
| Timeframe | "5" | 5 minutes | 5 minutes | "5" | PASS |
| Order Routing | N/A | DUAL ORDERS | DUAL ORDERS | DUAL_ORDERS | PASS |
| Risk Multiplier | N/A | 1.0x | 1.0x | 1.0x | PASS |
| ADX Threshold | >= 25 (STRONG) | >= 25 | >= 25 | >= 25 | PASS |
| Confidence Threshold | N/A | >= 70 | >= 70 | >= 70 | PASS |
| Alignment Required | 6 TFs (minTFAlignment=4) | 15M alignment | 15M alignment | 15M (check_pulse_alignment) | PASS |
| Order A Target | TP2/TP3 | TP2 | TP2 | TP2 | PASS |
| Order B Target | TP1 | TP1 | TP1 | TP1 | PASS |
| Lot Split | N/A | 50/50 | 50/50 | 50/50 | PASS |

**5M STATUS: COMPLIANT** - All parameters match across sources.

---

### 3. V6 15-MINUTE INTRADAY PLUGIN

| Parameter | Pine Script | Doc (11_V6) | Doc (DEEP_DIVE) | Actual Code | STATUS |
|-----------|-------------|-------------|-----------------|-------------|--------|
| Timeframe | "15" | 15 minutes | 15 minutes | "15" | PASS |
| Order Routing | N/A | DUAL ORDERS | N/A | ORDER_A_ONLY | MISMATCH |
| Risk Multiplier | N/A | 1.5x | 1.2x | 1.0x | MISMATCH |
| ADX Threshold | >= 25 (STRONG) | >= 25 | >= 20 | NOT CHECKED | MISMATCH |
| Confidence Threshold | N/A | >= 65 | >= 65 | >= 60 | MISMATCH |
| Alignment Required | 6 TFs (minTFAlignment=4) | 1H alignment | 1H alignment | Pulse alignment | PARTIAL |
| Market State Check | N/A | N/A | N/A | AVOID CHOPPY/SIDEWAYS | EXTRA |
| TP Target | N/A | N/A | N/A | TP2 | N/A |

**15M DISCREPANCIES:**
1. Order Routing: Doc says DUAL_ORDERS, Code says ORDER_A_ONLY
2. Risk Multiplier: Doc (11_V6) says 1.5x, Doc (DEEP_DIVE) says 1.2x, Code says 1.0x
3. ADX Threshold: Docs say >= 20-25, Code has NO ADX check at all
4. Confidence Threshold: Docs say >= 65, Code says >= 60
5. Alignment: Docs say 1H alignment, Code uses generic Pulse alignment (different method)

---

### 4. V6 1-HOUR SWING PLUGIN

| Parameter | Pine Script | Doc (11_V6) | Doc (DEEP_DIVE) | Actual Code | STATUS |
|-----------|-------------|-------------|-----------------|-------------|--------|
| Timeframe | "60" | 1 hour | 1 hour | "60" | PASS |
| Order Routing | N/A | DUAL ORDERS | N/A | ORDER_A_ONLY | MISMATCH |
| Risk Multiplier | N/A | 2.0x | 1.5x | 0.6x | CRITICAL MISMATCH |
| ADX Threshold | >= 25 (STRONG) | >= 30 | >= 15 | NOT CHECKED | MISMATCH |
| Confidence Threshold | N/A | >= 60 | >= 60 | >= 60 | PASS |
| Alignment Required | 6 TFs (minTFAlignment=4) | 4H alignment | 4H alignment | 4H (check_timeframe_alignment) | PASS |
| Daily Check | N/A | Required | Required | NOT IMPLEMENTED | MISMATCH |
| TP Target | N/A | N/A | N/A | TP3 (fallback TP2) | N/A |

**1H DISCREPANCIES:**
1. Order Routing: Doc says DUAL_ORDERS, Code says ORDER_A_ONLY
2. Risk Multiplier: Doc (11_V6) says 2.0x, Doc (DEEP_DIVE) says 1.5x, Code says 0.6x - CRITICAL!
3. ADX Threshold: Docs say >= 15-30, Code has NO ADX check at all
4. Daily Check: Docs say required, Code does NOT implement daily trend check

---

## PINE SCRIPT LOGIC ANALYSIS

### Confidence Scoring System (Lines 513-547)

The Pine Script calculates confidence as follows:
```
Base signal:           20 points (always)
Trendline confirmation: 25 points (if trendline break or slope)
ADX momentum:          10-20 points (10 moderate, 20 strong)
Multi-TF alignment:    25 points (if >= minTFAlignment TFs aligned)
Volume confirmation:   10 points (if volume supports direction)
MAXIMUM:              100 points
```

**CODE COMPLIANCE:** The plugins receive `conf_score` from the alert and use it directly. They do NOT recalculate confidence. This is CORRECT behavior - the Pine Script calculates and sends the score.

### ADX Strength Classification (Pine Script)

```
STRONG:   ADX >= 25
MODERATE: ADX >= 20
WEAK:     ADX >= 15
NONE:     ADX < 15
```

**CODE COMPLIANCE:** `zepix_v6_alert.py` (lines 125-135) implements the SAME classification. PASS.

### Entry Signal Conditions (Pine Script Lines 582-584)

```pine
bool enhancedBullishEntry = ta.crossover(trend, 0) and showSO
bool enhancedBearishEntry = ta.crossunder(trend, 0) and showSO
```

**CODE COMPLIANCE:** The plugins receive entry signals from TradingView alerts. They don't need to implement the crossover logic. PASS.

### Risk Management (Pine Script Lines 556-579)

```pine
calculateRiskLevels(bool isLong) =>
    float atrVal = ta.atr(atrLength)
    float sl = isLong ? close - (atrVal * slMultiplier) : close + (atrVal * slMultiplier)
    float tp1 = isLong ? close + (atrVal * tp1Multiplier) : close - (atrVal * tp1Multiplier)
    float tp2 = isLong ? close + (atrVal * tp2Multiplier) : close - (atrVal * tp2Multiplier)
    float tp3 = isLong ? close + (atrVal * tp3Multiplier) : close - (atrVal * tp3Multiplier)
```

**CODE COMPLIANCE:** The plugins receive SL/TP values from the alert. They use these values directly. PASS.

### Alert Format (Pine Script Lines 732-777)

```
TYPE|SYMBOL|TF|PRICE|DIRECTION|CONF_LEVEL|CONF_SCORE|ADX|ADX_STRENGTH|SL|TP1|TP2|TP3|ALIGNMENT|TL_STATUS
```

**CODE COMPLIANCE:** `zepix_v6_alert.py` (lines 288-369) parses this exact format. PASS.

---

## DOCUMENTATION INCONSISTENCIES

The two documentation files contain CONFLICTING information:

| Parameter | 11_V6_PRICE_ACTION_PLUGINS.md | V6_LOGIC_DEEP_DIVE.md |
|-----------|-------------------------------|----------------------|
| 1M ADX Threshold | >= 20 | >= 30 |
| 15M Risk Multiplier | 1.5x | 1.2x |
| 15M ADX Threshold | >= 25 | >= 20 |
| 1H Risk Multiplier | 2.0x | 1.5x |
| 1H ADX Threshold | >= 30 | >= 15 |

**RECOMMENDATION:** Consolidate documentation into a single source of truth.

---

## CRITICAL FINDINGS SUMMARY

### CRITICAL (Must Fix)

1. **1H Risk Multiplier:** Docs say 1.5x-2.0x, Code says 0.6x. This is a 3x difference that significantly impacts position sizing.

2. **15M/1H Order Routing:** Docs say DUAL_ORDERS, Code says ORDER_A_ONLY. This changes the entire trade management strategy.

3. **15M/1H ADX Check:** Docs say ADX threshold required, Code has NO ADX check. This removes a key filter.

### HIGH (Should Fix)

4. **1M Alignment:** Docs say 5M alignment required, Code ignores Trend Pulse entirely.

5. **15M Risk Multiplier:** Docs say 1.2x-1.5x, Code says 1.0x.

6. **15M Confidence Threshold:** Docs say >= 65, Code says >= 60.

### MEDIUM (Documentation Issue)

7. **Documentation Conflict:** Two V5_BIBLE files have different values for the same parameters.

---

## RECOMMENDATIONS

### Immediate Actions

1. **Decide on authoritative source:** Is the Pine Script, Documentation, or Code the source of truth?

2. **Fix 1H Risk Multiplier:** Either update code to 1.5x-2.0x OR update docs to 0.6x.

3. **Fix Order Routing:** Either implement DUAL_ORDERS for 15M/1H OR update docs to ORDER_A_ONLY.

4. **Add ADX Checks:** Either add ADX threshold checks to 15M/1H plugins OR remove from docs.

### Documentation Cleanup

5. **Consolidate V6 docs:** Merge `11_V6_PRICE_ACTION_PLUGINS.md` and `V6_LOGIC_DEEP_DIVE.md` into one authoritative document.

6. **Add Pine Script reference:** Documentation should reference specific Pine Script line numbers.

---

## COMPLIANCE SCORE

| Plugin | Compliance Score | Status |
|--------|------------------|--------|
| V6 1M | 70% | PARTIAL |
| V6 5M | 100% | COMPLIANT |
| V6 15M | 40% | NON-COMPLIANT |
| V6 1H | 30% | NON-COMPLIANT |

**OVERALL: 60% COMPLIANT**

---

## FILES AUDITED

### Pine Script
- `Updates/v5_hybrid_plugin_architecture/Signals_and_Overlays_V6_Enhanced_Build.pine` (1683 lines)

### Documentation
- `Trading_Bot_Documentation/V5_BIBLE/11_V6_PRICE_ACTION_PLUGINS.md` (455 lines)
- `Trading_Bot_Documentation/V5_BIBLE/V6_LOGIC_DEEP_DIVE.md` (363 lines)

### Code
- `Trading_Bot/src/logic_plugins/v6_price_action_1m/plugin.py` (509 lines)
- `Trading_Bot/src/logic_plugins/v6_price_action_5m/plugin.py` (524 lines)
- `Trading_Bot/src/logic_plugins/v6_price_action_15m/plugin.py` (506 lines)
- `Trading_Bot/src/logic_plugins/v6_price_action_1h/plugin.py` (497 lines)
- `Trading_Bot/src/core/zepix_v6_alert.py` (538 lines)

---

## AUDIT COMPLETE

**Auditor:** Devin AI
**Date:** 2026-01-17
**Session:** https://app.devin.ai/sessions/4b58f5ede2b9495d874258f2c0f230e5
