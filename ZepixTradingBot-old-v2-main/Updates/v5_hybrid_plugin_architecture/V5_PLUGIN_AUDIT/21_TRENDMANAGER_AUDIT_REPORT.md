# Mandate 21: TrendManager Misuse Audit Report

**Date:** 2026-01-17
**Auditor:** Devin AI
**Status:** CRITICAL ISSUES FOUND

---

## 1. Executive Summary

**YOUR SUSPICION IS 100% CONFIRMED.** The V6 plugins (5M, 15M, 1H) are incorrectly using internal TrendManager/ServiceAPI alignment checks during FRESH ENTRY validation, which violates the "Pine Script Supremacy" principle. The V3 plugin is correctly implemented - it bypasses trend checks for fresh entries and only uses alert payload data. The V6 1M plugin is also correctly implemented (no TrendManager calls). However, V6 5M, 15M, and 1H plugins call `service_api.check_pulse_alignment()` or `service_api.check_timeframe_alignment()` during fresh entry validation, which is WRONG.

**Summary Table:**

| Plugin | Fresh Entry TrendManager Misuse? | ADX Source | Verdict |
|--------|----------------------------------|------------|---------|
| V3 Combined | NO | N/A (uses consensus_score) | PASS |
| V6 1M | NO | `alert.adx` (payload) | PASS |
| V6 5M | YES - `check_pulse_alignment()` | `alert.adx` (payload) | FAIL |
| V6 15M | YES - `check_pulse_alignment()` | `alert.adx` (payload) | FAIL |
| V6 1H | YES - `check_timeframe_alignment()` | `alert.adx` (payload) | FAIL |

---

## 2. V3 Findings (PASS)

### 2.1 V3 Combined Plugin - `plugin.py`

**Q1: FRESH ENTRY VALIDATION - Data Source Check**

**File:** `Trading_Bot/src/logic_plugins/v3_combined/plugin.py`
**Lines:** 977-1050

**Code Evidence:**
```python
async def process_entry_signal(self, alert) -> Dict[str, Any]:
    """
    Process V3 entry signal and execute trade.
    
    V3 entries BYPASS trend check because Pine Script has already
    performed 5-layer pre-validation. Re-entries and autonomous
    actions still REQUIRE trend check.
    """
    try:
        signal_type = self._get_signal_type(alert)
        symbol = self._get_symbol(alert)
        direction = self._get_direction(alert)
        
        # Step 1: Validate consensus score threshold
        if not self._validate_score_thresholds(alert):
            return {"status": "rejected", "reason": "low_consensus_score", ...}
        
        # Step 2: Extract all alert data (including Pine Script SL/TP)
        alert_data = self._extract_alert_data(alert)
        
        # ... routing and order placement ...
        
        result = await self.order_manager.place_v3_dual_orders(
            alert=alert,
            logic_route=logic_route,
            logic_multiplier=logic_multiplier
        )
        
        return result
```

**Verdict: PASS** - No TrendManager call in fresh entry path. Uses `alert_data` from payload.

### 2.2 V3 Trend Validator - `trend_validator.py`

**File:** `Trading_Bot/src/logic_plugins/v3_combined/trend_validator.py`
**Lines:** 151-181

**Code Evidence:**
```python
def should_bypass_trend_check(self, alert) -> bool:
    """
    Check if trend validation should be bypassed.
    
    Bypass Rules:
    - entry_v3 signals: BYPASS (5-layer pre-validation trusted)
    - Legacy entries: REQUIRE trend check
    - SL hunt re-entry: REQUIRE trend check
    """
    alert_type = self._get_alert_type(alert)
    signal_source = self._get_signal_source(alert)
    
    if alert_type == "entry_v3" and self.bypass_config.get("bypass_for_entry_v3", True):
        self.logger.debug("Trend bypass: entry_v3 signal (5-layer pre-validated)")
        return True  # <-- CORRECT: Fresh entries bypass trend check
    
    if signal_source == "sl_hunt" and not self.bypass_config.get("bypass_for_sl_hunt", False):
        self.logger.debug("Trend check required: SL hunt re-entry")
        return False  # <-- CORRECT: Re-entries require trend check
    
    return False
```

**Verdict: PASS** - Correctly implements bypass for fresh entries, requires check for re-entries.

### 2.3 Q4: RE-ENTRY vs FRESH ENTRY SEPARATION (V3)

**Fresh Entry Function:** `process_entry_signal()` - Lines 977-1050
- Does NOT call TrendManager
- Uses only alert payload data

**Re-Entry Function:** `on_sl_hit()` - Lines 1632-1711
- Calls `trend_validator.should_bypass_trend_check()` which returns False for re-entries
- Re-entries REQUIRE trend check (correct behavior)

**Verdict: PASS** - Clear separation exists.

---

## 3. V6 Findings (3 of 4 FAIL)

### 3.1 V6 1M Plugin - `plugin.py` (PASS)

**File:** `Trading_Bot/src/logic_plugins/v6_price_action_1m/plugin.py`
**Lines:** 253-292

**Code Evidence:**
```python
async def _validate_entry(self, alert: ZepixV6Alert) -> Dict[str, Any]:
    """
    Validate entry conditions for 1M scalping.
    
    Filters:
    1. ADX >= 30 (avoid choppy markets - strict for 1M noise)
    2. Confidence >= 80 (high confidence for 1m noise)
    3. Spread < 2 pips (spread kills scalping profit)
    
    Note: Trend Pulse is IGNORED for 1M (too fast)
    """
    # ADX from alert payload - CORRECT
    if alert.adx is None or alert.adx < self.ADX_THRESHOLD:
        adx_val = alert.adx if alert.adx is not None else "NA"
        self.logger.info(f"[1M Skip] ADX {adx_val} < {self.ADX_THRESHOLD} (choppy market)")
        return {"valid": False, "reason": "adx_low"}
    
    # Confidence from alert payload - CORRECT
    if alert.conf_score < self.CONFIDENCE_THRESHOLD:
        self.logger.info(f"[1M Skip] Confidence {alert.conf_score} < {self.CONFIDENCE_THRESHOLD}")
        return {"valid": False, "reason": "confidence_low"}
    
    # Spread check via ServiceAPI - ACCEPTABLE (market data, not trend)
    try:
        spread = await self.service_api.get_current_spread(alert.ticker)
        if spread is not None and spread > self.MAX_SPREAD_PIPS:
            self.logger.info(f"[1M Skip] Spread {spread:.2f} > {self.MAX_SPREAD_PIPS} pips")
            return {"valid": False, "reason": "spread_high"}
    except Exception as e:
        self.logger.debug(f"[1M] Spread check skipped: {e}")
    
    return {"valid": True, "reason": None}
```

**Q1 Answer:** Uses `alert.adx` from payload - CORRECT
**Q2 Answer:** Uses `alert.adx` from payload - CORRECT
**TrendManager Misuse:** NO - Only uses spread check (market data, not trend)

**Verdict: PASS**

---

### 3.2 V6 5M Plugin - `plugin.py` (FAIL)

**File:** `Trading_Bot/src/logic_plugins/v6_price_action_5m/plugin.py`
**Lines:** 248-289

**Code Evidence:**
```python
async def _validate_entry(self, alert: ZepixV6Alert) -> Dict[str, Any]:
    """
    Validate entry conditions for 5M momentum.
    
    Filters:
    1. ADX >= 25 (need proven momentum)
    2. Confidence >= 70 (standard threshold)
    3. 15M Alignment (must align with immediate higher TF)  <-- RED FLAG
    """
    # ADX from alert payload - CORRECT
    if alert.adx is None or alert.adx < self.ADX_THRESHOLD:
        adx_val = alert.adx if alert.adx is not None else "NA"
        self.logger.info(f"[5M Skip] ADX {adx_val} < {self.ADX_THRESHOLD} (low momentum)")
        return {"valid": False, "reason": "adx_low"}
    
    # Confidence from alert payload - CORRECT
    if alert.conf_score < self.CONFIDENCE_THRESHOLD:
        self.logger.info(f"[5M Skip] Confidence {alert.conf_score} < {self.CONFIDENCE_THRESHOLD}")
        return {"valid": False, "reason": "confidence_low"}
    
    # RED FLAG: TrendManager call during FRESH ENTRY validation
    if self.REQUIRE_15M_ALIGNMENT:
        try:
            is_aligned = await self.service_api.check_pulse_alignment(  # <-- WRONG!
                symbol=alert.ticker,
                direction=alert.direction
            )
            if not is_aligned:
                self.logger.info(f"[5M Skip] 15M alignment failed for {alert.direction}")
                return {"valid": False, "reason": "alignment_failed"}
        except Exception as e:
            self.logger.debug(f"[5M] Alignment check skipped: {e}")
    
    return {"valid": True, "reason": None}
```

**Q1 Answer:** Uses `service_api.check_pulse_alignment()` - WRONG (should use `alert.alignment` from payload)
**Q2 Answer:** Uses `alert.adx` from payload - CORRECT
**TrendManager Misuse:** YES - Line 274-282

**Verdict: FAIL - Uses internal TrendManager for fresh entry validation**

---

### 3.3 V6 15M Plugin - `plugin.py` (FAIL)

**File:** `Trading_Bot/src/logic_plugins/v6_price_action_15m/plugin.py`
**Lines:** 250-299

**Code Evidence:**
```python
async def _validate_entry(self, alert: ZepixV6Alert) -> Dict[str, Any]:
    """
    Validate entry conditions for 15M intraday.
    
    Filters:
    1. ADX >= 20 (need trending market)
    2. Market State check (avoid CHOPPY/SIDEWAYS)
    3. Trend Pulse alignment required  <-- RED FLAG
    4. Confidence >= 65 (elevated threshold)
    """
    # ADX from alert payload - CORRECT
    if alert.adx is None or alert.adx < self.ADX_THRESHOLD:
        adx_val = alert.adx if alert.adx is not None else "NA"
        self.logger.info(f"[15M Skip] ADX {adx_val} < {self.ADX_THRESHOLD} (need trending market)")
        return {"valid": False, "reason": "adx_low"}
    
    # Confidence from alert payload - CORRECT
    if alert.conf_score < self.CONFIDENCE_THRESHOLD:
        self.logger.info(f"[15M Skip] Confidence {alert.conf_score} < {self.CONFIDENCE_THRESHOLD}")
        return {"valid": False, "reason": "confidence_low"}
    
    # Market state check via ServiceAPI - QUESTIONABLE
    try:
        market_state = await self.service_api.get_market_state(alert.ticker)
        if market_state and market_state.upper() in self.AVOID_MARKET_STATES:
            self.logger.info(f"[15M Skip] Market state {market_state} is unfavorable")
            return {"valid": False, "reason": "market_state_unfavorable"}
    except Exception as e:
        self.logger.debug(f"[15M] Market state check skipped: {e}")
    
    # RED FLAG: TrendManager call during FRESH ENTRY validation
    if self.REQUIRE_PULSE_ALIGNMENT:
        try:
            is_aligned = await self.service_api.check_pulse_alignment(  # <-- WRONG!
                symbol=alert.ticker,
                direction=alert.direction
            )
            if not is_aligned:
                self.logger.info(f"[15M Skip] Trend Pulse alignment failed for {alert.direction}")
                return {"valid": False, "reason": "pulse_alignment_failed"}
        except Exception as e:
            self.logger.debug(f"[15M] Pulse alignment check skipped: {e}")
    
    return {"valid": True, "reason": None}
```

**Q1 Answer:** Uses `service_api.check_pulse_alignment()` - WRONG (should use `alert.alignment` from payload)
**Q2 Answer:** Uses `alert.adx` from payload - CORRECT
**TrendManager Misuse:** YES - Line 285-293

**Verdict: FAIL - Uses internal TrendManager for fresh entry validation**

---

### 3.4 V6 1H Plugin - `plugin.py` (FAIL)

**File:** `Trading_Bot/src/logic_plugins/v6_price_action_1h/plugin.py`
**Lines:** 249-290

**Code Evidence:**
```python
async def _validate_entry(self, alert: ZepixV6Alert) -> Dict[str, Any]:
    """
    Validate entry conditions for 1H swing.
    
    Filters:
    1. ADX >= 15 (need trending market)
    2. Confidence >= 60 (standard threshold)
    3. 4H Alignment required  <-- RED FLAG
    """
    # ADX from alert payload - CORRECT
    if alert.adx is None or alert.adx < self.ADX_THRESHOLD:
        adx_val = alert.adx if alert.adx is not None else "NA"
        self.logger.info(f"[1H Skip] ADX {adx_val} < {self.ADX_THRESHOLD} (need trending market)")
        return {"valid": False, "reason": "adx_low"}
    
    # Confidence from alert payload - CORRECT
    if alert.conf_score < self.CONFIDENCE_THRESHOLD:
        self.logger.info(f"[1H Skip] Confidence {alert.conf_score} < {self.CONFIDENCE_THRESHOLD}")
        return {"valid": False, "reason": "confidence_low"}
    
    # RED FLAG: TrendManager call during FRESH ENTRY validation
    if self.REQUIRE_4H_ALIGNMENT:
        try:
            is_aligned = await self.service_api.check_timeframe_alignment(  # <-- WRONG!
                symbol=alert.ticker,
                direction=alert.direction,
                higher_tf="240"
            )
            if not is_aligned:
                self.logger.info(f"[1H Skip] 4H alignment failed for {alert.direction}")
                return {"valid": False, "reason": "4h_alignment_failed"}
        except Exception as e:
            self.logger.debug(f"[1H] 4H alignment check skipped: {e}")
    
    return {"valid": True, "reason": None}
```

**Q1 Answer:** Uses `service_api.check_timeframe_alignment()` - WRONG (should use `alert.alignment` from payload)
**Q2 Answer:** Uses `alert.adx` from payload - CORRECT
**TrendManager Misuse:** YES - Line 275-284

**Verdict: FAIL - Uses internal TrendManager for fresh entry validation**

---

## 4. Planning vs Reality Comparison Table

### Planning Document: `06_ADX_FEATURE_INTEGRATION.md`

| Requirement | Planning Doc Says | Actual Code | Match? |
|-------------|-------------------|-------------|--------|
| ADX Source | `alert.adx` (payload index 7) | `alert.adx` | MATCH |
| ADX Strength | `alert.adx_strength` (payload index 8) | `alert.adx_strength` | MATCH |
| 1M ADX Threshold | ADX > 20 | ADX >= 30 | IMPROVED |
| 5M ADX Threshold | ADX > 25 | ADX >= 25 | MATCH |
| 15M ADX Threshold | ADX > 20 (risk modulator) | ADX >= 20 | MATCH |
| 1H ADX Threshold | ADX > 50 (exhaustion warning) | ADX >= 15 | DIFFERENT |

### Planning Document: `04_LOGIC_IMPLEMENTATION_COMPARISON.md`

| Requirement | Planning Doc Says | Actual Code | Match? |
|-------------|-------------------|-------------|--------|
| V3 Fresh Entry | BYPASS trend check | BYPASS (correct) | MATCH |
| V3 Re-Entry | REQUIRE trend check | REQUIRE (correct) | MATCH |
| V6 Fresh Entry | Should use alert data only | Uses TrendManager (WRONG) | MISMATCH |

### Planning Document: `01_INTEGRATION_MASTER_PLAN.md`

| Requirement | Planning Doc Says | Actual Code | Match? |
|-------------|-------------------|-------------|--------|
| V6 Trend Source | "New V6 Trend Pulse System (Real-time aligned trends)" | Uses internal TrendManager | MISMATCH |
| Alert Source | "New V6 Pine Script (Pipe-Separated Payloads)" | Partially uses payload | PARTIAL |

---

## 5. Critical Issues List

### CRITICAL ISSUE #1: V6 5M Plugin TrendManager Misuse
- **File:** `v6_price_action_5m/plugin.py`
- **Line:** 274-282
- **Issue:** Calls `service_api.check_pulse_alignment()` during fresh entry validation
- **Impact:** Bot is "over-smart" - ignores Pine Script's pre-calculated alignment
- **Fix Required:** Use `alert.alignment` from payload instead

### CRITICAL ISSUE #2: V6 15M Plugin TrendManager Misuse
- **File:** `v6_price_action_15m/plugin.py`
- **Line:** 285-293
- **Issue:** Calls `service_api.check_pulse_alignment()` during fresh entry validation
- **Impact:** Bot is "over-smart" - ignores Pine Script's pre-calculated alignment
- **Fix Required:** Use `alert.alignment` from payload instead

### CRITICAL ISSUE #3: V6 1H Plugin TrendManager Misuse
- **File:** `v6_price_action_1h/plugin.py`
- **Line:** 275-284
- **Issue:** Calls `service_api.check_timeframe_alignment()` during fresh entry validation
- **Impact:** Bot is "over-smart" - ignores Pine Script's pre-calculated alignment
- **Fix Required:** Use `alert.alignment` from payload instead

### MINOR ISSUE #1: V6 15M Market State Check
- **File:** `v6_price_action_15m/plugin.py`
- **Line:** 276-281
- **Issue:** Calls `service_api.get_market_state()` - may be using internal calculation
- **Impact:** Should use `alert.momentum_state` from payload if available
- **Fix Required:** Verify if market state comes from payload or internal calculation

---

## 6. Recommendations

### Immediate Fixes Required

1. **V6 5M Plugin Fix:**
   ```python
   # BEFORE (WRONG):
   is_aligned = await self.service_api.check_pulse_alignment(
       symbol=alert.ticker,
       direction=alert.direction
   )
   
   # AFTER (CORRECT):
   # Use alignment from alert payload
   alignment_str = alert.alignment  # e.g., "3/4"
   aligned_count, total_count = map(int, alignment_str.split('/'))
   is_aligned = aligned_count >= 3  # Or use configurable threshold
   ```

2. **V6 15M Plugin Fix:**
   ```python
   # BEFORE (WRONG):
   is_aligned = await self.service_api.check_pulse_alignment(...)
   
   # AFTER (CORRECT):
   alignment_str = alert.alignment
   aligned_count, total_count = map(int, alignment_str.split('/'))
   is_aligned = aligned_count >= 3
   ```

3. **V6 1H Plugin Fix:**
   ```python
   # BEFORE (WRONG):
   is_aligned = await self.service_api.check_timeframe_alignment(
       symbol=alert.ticker,
       direction=alert.direction,
       higher_tf="240"
   )
   
   # AFTER (CORRECT):
   alignment_str = alert.alignment
   aligned_count, total_count = map(int, alignment_str.split('/'))
   is_aligned = aligned_count >= 3
   ```

### Configuration Changes

Add to each V6 plugin config:
```json
{
  "use_payload_alignment": true,
  "min_alignment_count": 3,
  "alignment_total": 4
}
```

### Verification Steps

After fixes:
1. Send V6 webhook with `alignment: "3/4"`
2. Verify plugin uses payload alignment, NOT internal TrendManager
3. Check logs for "Using payload alignment" message
4. Confirm no `check_pulse_alignment` or `check_timeframe_alignment` calls in fresh entry path

---

## 7. Conclusion

**The user's suspicion is 100% CONFIRMED.**

The V6 plugins (5M, 15M, 1H) became "over-smart" during implementation and are incorrectly using internal TrendManager checks during FRESH ENTRY validation. This violates the "Pine Script Supremacy" principle which states:

> Pine Script calculates ALL intelligence (ADX, Trend, Multi-Timeframe Alignment, Confidence Score). This data is sent via Alert Payload. The Bot's ONLY job is to READ this data and EXECUTE trades accordingly.

**Good News:**
- V3 plugin is correctly implemented (bypasses trend check for fresh entries)
- V6 1M plugin is correctly implemented (no TrendManager calls)
- All plugins correctly use `alert.adx` from payload (not internal calculation)

**Bad News:**
- V6 5M, 15M, 1H plugins call TrendManager during fresh entry validation
- This means the bot may reject valid signals that Pine Script already approved
- Or accept signals that Pine Script would have rejected

**Recommended Action:** Create Mandate 22 to fix the V6 TrendManager misuse in 5M, 15M, and 1H plugins.

---

**Audit Complete. Report generated with full code evidence.**
