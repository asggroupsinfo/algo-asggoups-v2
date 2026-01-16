# V3 PLUGIN MASTER REPAIR - FINAL IMPLEMENTATION PLAN

**Document ID:** 07_FINAL_IMPLEMENTATION_PLAN  
**Date:** 2026-01-16  
**Author:** Devin AI  
**Status:** EXECUTION READY

---

## EXECUTIVE SUMMARY

This document details the exact fixes required to make the V5 Hybrid Plugin Architecture 100% compliant with the V3 Pine Script specifications. Three critical bugs have been identified and will be fixed.

---

## CRITICAL BUGS IDENTIFIED

### BUG #1: MTF String Count Mismatch

**Source Evidence (Pine Script Line 1702):**
```pine
mtfString = str.tostring(htfTrend5) + "," + str.tostring(htfTrend4) + "," + str.tostring(htfTrend3) + ","  + str.tostring(htfTrend2) + "," + str.tostring(htfTrend1)
```

**Pine Output:** `"1,1,-1,1,1"` (5 VALUES: 1D,4H,1H,15m,5m in REVERSE order)

**Bot Expectation (v3_alert_models.py Line 82-83):**
```python
if len(parts) != 6:
    raise ValueError(f"MTF trends must have 6 values (1m,5m,15m,1H,4H,1D), got {len(parts)}")
```

**IMPACT:** All entry signals will FAIL validation because Pine sends 5 values, bot expects 6.

---

### BUG #2: MTF String Order Mismatch

**Pine Script Order:** `htfTrend5,htfTrend4,htfTrend3,htfTrend2,htfTrend1` = `1D,4H,1H,15m,5m` (REVERSE)

**Bot Assumption (v3_alert_models.py Line 109-114):**
```python
return {
    "15m": trends[2],  # Index 2 - Bot thinks this is 15m
    "1h": trends[3],   # Index 3 - Bot thinks this is 1H
    "4h": trends[4],   # Index 4 - Bot thinks this is 4H
    "1d": trends[5]    # Index 5 - Bot thinks this is 1D
}
```

**IMPACT:** Even if count was fixed, bot extracts WRONG timeframes:
- Bot Index 2 = Pine's 1H (not 15m)
- Bot Index 3 = Pine's 15m (not 1H)
- Bot Index 4 = Pine's 5m (not 4H)
- Bot Index 5 = DOESN'T EXIST (only 5 values)

---

### BUG #3: Consensus Score Not Filtered

**Pine Script Sends:** `consensus_score` field (0-9 scale)

**Bot Current Behavior:** Accepts all scores without filtering

**Required Behavior:** Reject signals with `consensus_score < min_consensus_score` (default 5)

---

## FIX #1: MTF String Parsing (v3_alert_models.py)

### Current Code (Lines 77-94):
```python
@validator('mtf_trends')
def validate_mtf_trends(cls, v):
    if v is not None:
        parts = v.split(',')
        if len(parts) != 6:
            raise ValueError(f"MTF trends must have 6 values (1m,5m,15m,1H,4H,1D), got {len(parts)}")
        # ... validation
    return v
```

### Fixed Code:
```python
@validator('mtf_trends')
def validate_mtf_trends(cls, v):
    """
    Validate MTF trends string format.
    
    Pine Script sends TWO different formats:
    - Entry signals (mtfString): 5 values in REVERSE order (1D,4H,1H,15m,5m)
    - Trend Pulse (currentTrendString): 6 values in FORWARD order (1m,5m,15m,1H,4H,1D)
    
    We accept BOTH formats and normalize during pillar extraction.
    """
    if v is not None:
        parts = v.split(',')
        if len(parts) not in [5, 6]:
            raise ValueError(f"MTF trends must have 5 or 6 values, got {len(parts)}")
        
        # Validate each value is 1, -1, or 0
        for part in parts:
            try:
                val = int(part.strip())
                if val not in [-1, 0, 1]:
                    raise ValueError(f"MTF trend values must be -1, 0, or 1, got {val}")
            except ValueError:
                raise ValueError(f"Invalid MTF trend value: {part}")
    
    return v
```

---

## FIX #2: MTF Pillar Extraction (v3_alert_models.py)

### Current Code (Lines 96-114):
```python
def get_mtf_pillars(self) -> dict:
    if not self.mtf_trends:
        return {}
    
    trends = [int(t.strip()) for t in self.mtf_trends.split(',')]
    
    # Extract ONLY indices [2,3,4,5] - ignore [0,1] (1m, 5m noise)
    return {
        "15m": trends[2],
        "1h": trends[3],
        "4h": trends[4],
        "1d": trends[5]
    }
```

### Fixed Code:
```python
def get_mtf_pillars(self) -> dict:
    """
    Extract ONLY the 4 stable pillars from MTF trends string.
    
    Handles TWO Pine Script formats:
    
    FORMAT A (5 values, REVERSE order) - Entry Signals:
    - Pine: mtfString = htfTrend5,htfTrend4,htfTrend3,htfTrend2,htfTrend1
    - Meaning: 1D,4H,1H,15m,5m
    - Index mapping: [0]=1D, [1]=4H, [2]=1H, [3]=15m, [4]=5m
    - Extract: [0]=1D, [1]=4H, [2]=1H, [3]=15m (ignore [4]=5m noise)
    
    FORMAT B (6 values, FORWARD order) - Trend Pulse:
    - Pine: currentTrendString = htfTrend0,htfTrend1,htfTrend2,htfTrend3,htfTrend4,htfTrend5
    - Meaning: 1m,5m,15m,1H,4H,1D
    - Index mapping: [0]=1m, [1]=5m, [2]=15m, [3]=1H, [4]=4H, [5]=1D
    - Extract: [2]=15m, [3]=1H, [4]=4H, [5]=1D (ignore [0]=1m, [1]=5m noise)
    
    Returns:
        dict: {"15m": 1, "1h": 1, "4h": -1, "1d": 1}
    """
    if not self.mtf_trends:
        return {}
    
    trends = [int(t.strip()) for t in self.mtf_trends.split(',')]
    
    if len(trends) == 5:
        # FORMAT A: 5 values in REVERSE order (1D,4H,1H,15m,5m)
        # Indices: [0]=1D, [1]=4H, [2]=1H, [3]=15m, [4]=5m
        return {
            "15m": trends[3],  # Index 3 = 15m
            "1h": trends[2],   # Index 2 = 1H
            "4h": trends[1],   # Index 1 = 4H
            "1d": trends[0]    # Index 0 = 1D
        }
    elif len(trends) == 6:
        # FORMAT B: 6 values in FORWARD order (1m,5m,15m,1H,4H,1D)
        # Indices: [0]=1m, [1]=5m, [2]=15m, [3]=1H, [4]=4H, [5]=1D
        return {
            "15m": trends[2],  # Index 2 = 15m
            "1h": trends[3],   # Index 3 = 1H
            "4h": trends[4],   # Index 4 = 4H
            "1d": trends[5]    # Index 5 = 1D
        }
    else:
        return {}
```

---

## FIX #3: Add Extra Fields for Pine Data (v3_alert_models.py)

### New Fields to Add:
```python
# Additional Pine Script fields (for future use)
fib_level: Optional[float] = None  # Golden Pocket Flip signal
adx_value: Optional[float] = None  # Sideways Breakout signal
confidence: Optional[str] = None   # Signal confidence level
full_alignment: Optional[bool] = None  # Screener signals
reason: Optional[str] = None       # Exit signal reason
message: Optional[str] = None      # Info signal message
trend_labels: Optional[str] = None # Trend Pulse labels
```

---

## FIX #4: Logic Routing Table (v3_combined/plugin.py)

### Signal Type + Timeframe -> Logic Handler Matrix:

| Signal Type | Timeframe | Logic Handler | Reason |
|-------------|-----------|---------------|--------|
| Screener_Full_Bullish | ANY | LOGIC3 | High conviction swing |
| Screener_Full_Bearish | ANY | LOGIC3 | High conviction swing |
| Golden_Pocket_Flip | 60, 240 | LOGIC3 | Higher TF fib reversal |
| Golden_Pocket_Flip | 5, 15 | LOGIC1/2 | Lower TF fib reversal |
| ANY Entry | 5 | LOGIC1 | Scalping timeframe |
| ANY Entry | 15 | LOGIC2 | Intraday timeframe |
| ANY Entry | 60, 240 | LOGIC3 | Swing timeframe |
| ANY Entry | OTHER | LOGIC2 | Default fallback |

### Implementation:
```python
def _route_logic_type(self, signal: Dict[str, Any]) -> str:
    """
    Route signal to appropriate Logic handler.
    
    PRIORITY 1: Signal type overrides (high conviction signals)
    PRIORITY 2: Timeframe-based routing
    """
    signal_type = signal.get('signal_type', '')
    tf = signal.get('tf', '15')
    
    # PRIORITY 1: Signal type overrides
    if signal_type in ["Screener_Full_Bullish", "Screener_Full_Bearish"]:
        return "LOGIC3"  # Always swing for full alignment
    
    if signal_type == "Golden_Pocket_Flip" and tf in ["60", "240"]:
        return "LOGIC3"  # Higher TF golden pocket
    
    # PRIORITY 2: Timeframe routing
    if tf == "5":
        return "LOGIC1"  # Scalping
    elif tf == "15":
        return "LOGIC2"  # Intraday
    elif tf in ["60", "240", "D", "W"]:
        return "LOGIC3"  # Swing
    
    return "LOGIC2"  # Default
```

---

## FIX #5: Consensus Score Filtering (v3_combined/plugin.py)

### Implementation:
```python
def _validate_score_thresholds(self, signal: Dict[str, Any]) -> bool:
    """
    Validate consensus score meets minimum threshold.
    
    Pine Script consensus_score range: 0-9
    - 0-4: Low confidence (REJECT)
    - 5-6: Medium confidence (ACCEPT)
    - 7-9: High confidence (ACCEPT with priority)
    
    Returns:
        bool: True if score meets threshold, False to reject
    """
    score = signal.get('consensus_score', 0)
    min_score = self.plugin_config.get('min_consensus_score', 5)
    
    if score < min_score:
        self.logger.warning(
            f"Signal REJECTED: consensus_score {score} < min {min_score}"
        )
        return False
    
    return True
```

---

## FIX #6: Alert SL Enforcement (v3_combined/plugin.py)

### Implementation:
```python
def _extract_alert_data(self, signal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and validate all alert data from Pine Script signal.
    
    CRITICAL: alert.sl_price MUST override internal calculation for Order A.
    Order B uses fixed $10 risk SL regardless of alert.sl_price.
    """
    return {
        'symbol': signal.get('symbol', ''),
        'direction': signal.get('direction', ''),
        'price': signal.get('price', 0.0),
        'signal_type': signal.get('signal_type', ''),
        'tf': signal.get('tf', '15'),
        'consensus_score': signal.get('consensus_score', 0),
        'position_multiplier': signal.get('position_multiplier', 1.0),
        
        # CRITICAL: SL/TP from Pine Script
        'sl_price': signal.get('sl_price'),  # Order A uses this
        'tp1_price': signal.get('tp1_price'),  # Order B target
        'tp2_price': signal.get('tp2_price'),  # Order A target
        
        # MTF trends
        'mtf_trends': signal.get('mtf_trends', ''),
        'market_trend': signal.get('market_trend', 0),
        
        # Extra fields
        'fib_level': signal.get('fib_level'),
        'adx_value': signal.get('adx_value'),
        'confidence': signal.get('confidence'),
        'volume_delta_ratio': signal.get('volume_delta_ratio'),
        'price_in_ob': signal.get('price_in_ob'),
    }
```

---

## FIX #7: Trend Bypass for V3 Entries (v3_combined/plugin.py)

### Implementation:
```python
async def process_entry_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process V3 entry signal with trend bypass.
    
    V3 entries BYPASS trend check because Pine Script has already
    performed 5-layer pre-validation. Re-entries and autonomous
    actions still REQUIRE trend check.
    """
    # Step 1: Validate consensus score
    if not self._validate_score_thresholds(signal):
        return {'status': 'rejected', 'reason': 'low_consensus_score'}
    
    # Step 2: Extract alert data
    alert_data = self._extract_alert_data(signal)
    
    # Step 3: Route to logic
    logic_type = self._route_logic_type(signal)
    
    # Step 4: BYPASS trend check for fresh V3 entries
    # (Pine Script already validated trend alignment)
    
    # Step 5: Execute entry with hybrid dual orders
    result = await self._execute_v3_entry(alert_data, logic_type)
    
    return result
```

---

## FILES TO MODIFY

| File | Changes |
|------|---------|
| `Trading_Bot/src/v3_alert_models.py` | Fix MTF validator, Fix get_mtf_pillars(), Add extra fields |
| `Trading_Bot/src/logic_plugins/v3_combined/plugin.py` | Add _extract_alert_data(), _route_logic_type(), _validate_score_thresholds() |
| `Trading_Bot_Documentation/V5_BIBLE/10_V3_COMBINED_PLUGIN.md` | Update with actual implementation |
| `Trading_Bot/tests/v5_integrity_check.py` | Create test suite |

---

## TEST CASES (v5_integrity_check.py)

### Test 1: MTF Parsing (5-value reverse order)
```python
def test_mtf_parsing_5_values():
    """Input: "1,1,-1,1,1" -> Output: {15m: 1, 1h: -1, 4h: 1, 1d: 1}"""
    alert = ZepixV3Alert(
        type="entry_v3",
        signal_type="Institutional_Launchpad",
        symbol="EURUSD",
        direction="buy",
        tf="15",
        price=1.0850,
        consensus_score=7,
        mtf_trends="1,1,-1,1,1"  # 5 values: 1D,4H,1H,15m,5m
    )
    pillars = alert.get_mtf_pillars()
    assert pillars == {"15m": 1, "1h": -1, "4h": 1, "1d": 1}
```

### Test 2: Score Filtering
```python
def test_score_filtering():
    """Input: Score 3 (Launchpad Buy) -> REJECTED"""
    # Score 3 < min_score 5 -> Should be rejected
```

### Test 3: Alert SL Enforcement
```python
def test_alert_sl_enforcement():
    """Input: SL: 2000.50 -> Order A SL IS 2000.50"""
    # Order A must use alert.sl_price, not internal calculation
```

### Test 4: Logic Routing
```python
def test_logic_routing():
    """Input: TF: 5m -> Logic 1. Input: TF: 60m -> Logic 3"""
    # Verify routing matrix
```

---

## EXECUTION ORDER

1. **Phase 2A:** Fix `v3_alert_models.py` (MTF parsing + extra fields)
2. **Phase 2B:** Fix `v3_combined/plugin.py` (routing + validation + extraction)
3. **Phase 3:** Update `10_V3_COMBINED_PLUGIN.md` documentation
4. **Phase 4:** Create and run `v5_integrity_check.py`
5. **Phase 5:** Commit and push to GitLab

---

## ACKNOWLEDGMENT

I have analyzed the Pine Script source code (ZEPIX_ULTIMATE_BOT_v3.0_FINAL.pine) and identified the exact discrepancies between what Pine sends and what the bot expects. This plan addresses all critical bugs with precise code fixes.

**Ready for Phase 2 execution.**
