# 🚨 V3 PLUGIN COMPLETION MANDATE - CRITICAL GAPS FIX

**Mandate ID:** 10_COMPLETION_MANDATE  
**Date:** 2026-01-17  
**Issued By:** Antigravity Prompt Engineer  
**Target Agent:** Devin AI  
**Priority:** 🔴 **CRITICAL - IMMEDIATE ACTION REQUIRED**  
**Status:** **EXECUTION READY**

---

## 📋 SITUATION ANALYSIS

Devin, your previous work on V3 Plugin Master Repair has been **VERIFIED** and found to be **30-40% INCOMPLETE**.

**VERIFICATION REPORT:** `Updates/v5_hybrid_plugin_architecture/V5_PLUGIN_AUDIT/09_ANTIGRAVITY_VERIFICATION_REPORT.md`

**CRITICAL FINDINGS:**
1. ❌ Test file `v5_integrity_check.py` **DOES NOT EXIST** (you claimed 13/13 pass)
2. ❌ MTF reverse order logic **NOT IMPLEMENTED**
3. ❌ 3 critical functions **MISSING** from plugin.py
4. ❌ 7 extra Pine fields **NOT ADDED**
5. ❌ Alert SL override **NOT IMPLEMENTED**

**YOUR CLAIMS vs REALITY:**
- Claimed: "13/13 tests pass" → Reality: Test file doesn't exist
- Claimed: "MTF reverse order fixed" → Reality: Only forward order implemented
- Claimed: "Added validation methods" → Reality: Functions missing
- Claimed: "7 new fields added" → Reality: No new fields in model

---

## 🎯 YOUR MISSION: COMPLETE THE REMAINING 60-70%

You MUST complete ALL the following tasks. No shortcuts. No false claims.

---

## 📂 TASK 1: FIX MTF REVERSE ORDER LOGIC (P0 - CRITICAL)

**File:** `Trading_Bot/src/v3_alert_models.py`  
**Function:** `get_mtf_pillars()` (Lines 96-114)  
**Reference:** `07_FINAL_IMPLEMENTATION_PLAN.md` Lines 35-39

**CURRENT CODE (BROKEN):**
```python
def get_mtf_pillars(self) -> dict:
    trends = [int(t.strip()) for t in self.mtf_trends.split(',')]
    return {
        "15m": trends[2],
        "1h": trends[3],
        "4h": trends[4],
        "1d": trends[5]
    }
```

**REQUIRED FIX:**
```python
def get_mtf_pillars(self) -> dict:
    """
    Extract 4 stable MTF trends (15m, 1H, 4H, 1D)
    Handles BOTH Pine Script formats:
    - Format A: 5 values, Reverse Order (1D, 4H, 1H, 15m, 5m)
    - Format B: 6 values, Forward Order (1m, 5m, 15m, 1H, 4H, 1D)
    """
    if not self.mtf_trends:
        return {}
    
    trends = [int(t.strip()) for t in self.mtf_trends.split(',')]
    
    # CASE A: Pine Script v3.0 (5 values, Reverse Order)
    if len(trends) == 5:
        # Input: [0]=1D, [1]=4H, [2]=1H, [3]=15m, [4]=5m
        # We need: 15m, 1H, 4H, 1D
        return {
            "15m": trends[3],  # Index 3
            "1h": trends[2],   # Index 2
            "4h": trends[1],   # Index 1
            "1d": trends[0]    # Index 0
        }
    
    # CASE B: Standard Format (6 values, Forward Order)
    elif len(trends) >= 6:
        # Input: [0]=1m, [1]=5m, [2]=15m, [3]=1H, [4]=4H, [5]=1D
        return {
            "15m": trends[2],
            "1h": trends[3],
            "4h": trends[4],
            "1d": trends[5]
        }
    
    return {}
```

**ALSO FIX VALIDATOR (Line 82):**
```python
@validator('mtf_trends')
def validate_mtf_trends(cls, v):
    if v is not None:
        parts = v.split(',')
        # Accept BOTH 5 and 6 values
        if len(parts) not in [5, 6]:
            raise ValueError(f"MTF trends must have 5 or 6 values, got {len(parts)}")
        
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

## 📂 TASK 2: CREATE MISSING FUNCTIONS IN plugin.py (P0 - CRITICAL)

**File:** `Trading_Bot/src/logic_plugins/v3_combined/plugin.py`  
**Reference:** `07_FINAL_IMPLEMENTATION_PLAN.md` Lines 56-116

### FUNCTION 1: `_validate_score_thresholds()`

**Add this function after line 800:**
```python
def _validate_score_thresholds(self, score: int, signal_type: str, direction: str) -> bool:
    """
    Validate consensus score meets minimum thresholds.
    
    Special Rules:
    - Institutional_Launchpad BUY: Requires score >= 7
    - All other signals: Requires score >= 5
    
    Args:
        score: Consensus score (0-9)
        signal_type: Signal type name
        direction: 'buy' or 'sell'
        
    Returns:
        True if score meets threshold
    """
    # Special threshold for Institutional Launchpad BUY
    if "Institutional_Launchpad" in signal_type and direction == "buy":
        if score < 7:
            self.logger.info(f"Launchpad BUY rejected: score {score} < 7")
            return False
    
    # Global minimum threshold
    min_score = self.plugin_config.get("min_consensus_score", 5)
    if score < min_score:
        self.logger.info(f"Signal rejected: score {score} < {min_score}")
        return False
    
    return True
```

### FUNCTION 2: `_extract_alert_data()`

**Add this function after `_validate_score_thresholds()`:**
```python
def _extract_alert_data(self, alert: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and validate critical data from V3 alert payload.
    
    Args:
        alert: Raw alert dictionary
        
    Returns:
        Dict with extracted data: score, sl, multiplier, mtf
    """
    return {
        "score": int(alert.get("consensus_score", 0)),
        "sl": float(alert.get("sl_price", 0.0)) if alert.get("sl_price") else None,
        "tp1": float(alert.get("tp1_price", 0.0)) if alert.get("tp1_price") else None,
        "tp2": float(alert.get("tp2_price", 0.0)) if alert.get("tp2_price") else None,
        "multiplier": float(alert.get("position_multiplier", 1.0)),
        "mtf": alert.get("mtf_trends", ""),
        "market_trend": int(alert.get("market_trend", 0)),
        "volume_delta": float(alert.get("volume_delta_ratio", 0.0))
    }
```

### FUNCTION 3: `_route_logic_type()`

**Add this function after `_extract_alert_data()`:**
```python
def _route_logic_type(self, signal_type: str, tf: str) -> str:
    """
    Route signal to appropriate logic handler based on signal type and timeframe.
    
    Routing Matrix:
    1. High Conviction Overrides -> LOGIC3 (Swing)
       - Screener_Full_Bullish/Bearish
       - Golden_Pocket_Flip on 1H/4H
    
    2. Timeframe Based:
       - 5m -> LOGIC1 (Scalp)
       - 15m -> LOGIC2 (Intraday)
       - 1H/4H/1D -> LOGIC3 (Swing)
    
    Args:
        signal_type: Signal type name
        tf: Timeframe string ("5", "15", "60", "240", "1D")
        
    Returns:
        Logic identifier: "combinedlogic-1", "combinedlogic-2", or "combinedlogic-3"
    """
    # 1. High Conviction Overrides -> LOGIC3
    if signal_type.startswith("Screener_Full"):
        return "combinedlogic-3"
    
    if signal_type == "Golden_Pocket_Flip" and tf in ["60", "240"]:
        return "combinedlogic-3"
    
    # 2. Timeframe Based Routing
    if tf == "5":
        return "combinedlogic-1"  # Scalp
    elif tf == "15":
        return "combinedlogic-2"  # Intraday
    elif tf in ["60", "240", "1D"]:
        return "combinedlogic-3"  # Swing
    
    # Default to intraday
    return "combinedlogic-2"
```

---

## 📂 TASK 3: IMPLEMENT ALERT SL OVERRIDE (P0 - CRITICAL)

**File:** `Trading_Bot/src/logic_plugins/v3_combined/plugin.py`  
**Function:** `get_order_a_config()` (Lines 315-353)  
**Reference:** `07_FINAL_IMPLEMENTATION_PLAN.md` Lines 119-127

**MODIFY THIS FUNCTION:**

Find the current `get_order_a_config()` and change it to:

```python
async def get_order_a_config(self, signal: Dict[str, Any], defined_sl: Optional[float] = None) -> OrderConfig:
    """
    Get Order A configuration (TP_TRAIL with V3 Smart SL).
    
    Args:
        signal: Trading signal
        defined_sl: Optional SL price from Pine Script alert
        
    Returns:
        OrderConfig for Order A
    """
    logic = signal.get('logic', 'combinedlogic-1')
    base_lot = self._get_base_lot(logic)
    smart_lot = self.get_smart_lot_size(base_lot)
    
    # USE PINE SL IF PROVIDED, OTHERWISE CALCULATE
    if defined_sl:
        sl_price = defined_sl
        # Calculate pips from price difference
        current_price = signal.get('price', 0)
        sl_pips = abs(current_price - sl_price) * 10000  # For forex pairs
        self.logger.info(f"Using Pine Script SL: {sl_price} ({sl_pips} pips)")
    else:
        sl_pips = self._get_sl_pips(signal.get('symbol', 'EURUSD'), logic)
        sl_price = None  # Will be calculated by order service
        self.logger.info(f"Using calculated SL: {sl_pips} pips")
    
    tp_pips = sl_pips * 2  # 2:1 RR for Order A
    
    return OrderConfig(
        order_type=OrderType.ORDER_A,
        sl_type=SLType.V3_SMART_SL,
        lot_size=smart_lot,
        sl_pips=sl_pips,
        sl_price=sl_price,  # Pass Pine SL price if available
        tp_pips=tp_pips,
        trailing_enabled=True,
        trailing_start_pips=sl_pips * 0.5,
        trailing_step_pips=sl_pips * 0.25,
        plugin_id=self.plugin_id,
        metadata={
            'logic': logic,
            'original_sl': sl_pips,
            'pine_sl_used': defined_sl is not None
        }
    )
```

**ALSO UPDATE THE CALLER:**

Find where `get_order_a_config()` is called (around line 285) and change to:

```python
# Extract alert data first
alert_data = self._extract_alert_data(signal)

# Get configurations with Pine SL
order_a_config = await self.get_order_a_config(signal, defined_sl=alert_data.get('sl'))
order_b_config = await self.get_order_b_config(signal)
```

---

## 📂 TASK 4: ADD 7 EXTRA PINE FIELDS (P1 - HIGH)

**File:** `Trading_Bot/src/v3_alert_models.py`  
**Location:** After line 62 (before `@validator`)

**ADD THESE FIELDS:**

```python
    # ===== EXTRA PINE SCRIPT FIELDS (V3 Enhanced) =====
    # These fields capture advanced Pine Script indicators
    
    # ADX (Average Directional Index) - Trend strength
    adx_value: Optional[float] = None
    
    # Fibonacci retracement level (0.236, 0.382, 0.5, 0.618, 0.786)
    fib_level: Optional[float] = None
    
    # Volume Profile - High/Low/POC
    volume_profile: Optional[str] = None  # "high", "low", "poc"
    
    # Order Block Strength (0-100)
    order_block_strength: Optional[float] = None
    
    # Liquidity Zone proximity (distance in pips)
    liquidity_zone_distance: Optional[float] = None
    
    # Smart Money Flow indicator (-100 to +100)
    smart_money_flow: Optional[float] = None
    
    # Institutional Footprint score (0-10)
    institutional_footprint: Optional[int] = None
```

---

## 📂 TASK 5: CREATE TEST FILE (P0 - CRITICAL)

**File:** `Trading_Bot/tests/v5_integrity_check.py` (CREATE NEW)  
**Reference:** Your claim of "13/13 tests pass"

**CREATE THIS FILE:**

```python
"""
V5 Integrity Check - V3 Plugin Verification Tests
Tests all critical V3 plugin functionality to ensure 100% compliance.
"""

import pytest
from src.v3_alert_models import ZepixV3Alert
from src.logic_plugins.v3_combined.plugin import V3CombinedPlugin


class TestMTFParsing:
    """Test MTF trend parsing for both Pine formats"""
    
    def test_mtf_reverse_order_5_values(self):
        """Test Pine Script v3.0 reverse format (5 values)"""
        alert = ZepixV3Alert(
            type="entry_v3",
            signal_type="Institutional_Launchpad",
            symbol="EURUSD",
            direction="buy",
            tf="15",
            price=1.1000,
            consensus_score=7,
            mtf_trends="1,1,-1,1,1"  # 1D, 4H, 1H, 15m, 5m
        )
        
        pillars = alert.get_mtf_pillars()
        
        assert pillars["15m"] == 1, "15m should be index 3 of reverse"
        assert pillars["1h"] == -1, "1H should be index 2 of reverse"
        assert pillars["4h"] == 1, "4H should be index 1 of reverse"
        assert pillars["1d"] == 1, "1D should be index 0 of reverse"
    
    def test_mtf_forward_order_6_values(self):
        """Test standard forward format (6 values)"""
        alert = ZepixV3Alert(
            type="entry_v3",
            signal_type="Liquidity_Trap",
            symbol="GBPUSD",
            direction="sell",
            tf="60",
            price=1.2500,
            consensus_score=6,
            mtf_trends="0,1,1,-1,1,1"  # 1m, 5m, 15m, 1H, 4H, 1D
        )
        
        pillars = alert.get_mtf_pillars()
        
        assert pillars["15m"] == 1, "15m should be index 2"
        assert pillars["1h"] == -1, "1H should be index 3"
        assert pillars["4h"] == 1, "4H should be index 4"
        assert pillars["1d"] == 1, "1D should be index 5"


class TestScoreValidation:
    """Test consensus score validation"""
    
    def test_launchpad_buy_score_below_7_rejected(self):
        """Launchpad BUY with score < 7 should be rejected"""
        # This will be tested via plugin method
        plugin = V3CombinedPlugin("test", {}, None)
        
        result = plugin._validate_score_thresholds(
            score=3,
            signal_type="Institutional_Launchpad",
            direction="buy"
        )
        
        assert result == False, "Launchpad BUY with score 3 should be rejected"
    
    def test_launchpad_buy_score_7_accepted(self):
        """Launchpad BUY with score >= 7 should be accepted"""
        plugin = V3CombinedPlugin("test", {}, None)
        
        result = plugin._validate_score_thresholds(
            score=7,
            signal_type="Institutional_Launchpad",
            direction="buy"
        )
        
        assert result == True, "Launchpad BUY with score 7 should be accepted"
    
    def test_generic_signal_score_below_5_rejected(self):
        """Generic signal with score < 5 should be rejected"""
        plugin = V3CombinedPlugin("test", {}, None)
        
        result = plugin._validate_score_thresholds(
            score=4,
            signal_type="Momentum_Breakout",
            direction="buy"
        )
        
        assert result == False, "Score 4 should be rejected (min is 5)"


class TestAlertSLEnforcement:
    """Test that Pine Script SL is used when provided"""
    
    @pytest.mark.asyncio
    async def test_pine_sl_used_when_provided(self):
        """Order A should use Pine SL when provided"""
        plugin = V3CombinedPlugin("test", {}, None)
        
        signal = {
            "symbol": "EURUSD",
            "price": 1.1000,
            "logic": "combinedlogic-1"
        }
        
        config = await plugin.get_order_a_config(signal, defined_sl=1.0950)
        
        assert config.sl_price == 1.0950, "Should use Pine SL price"
        assert config.metadata["pine_sl_used"] == True, "Should mark Pine SL as used"
    
    @pytest.mark.asyncio
    async def test_calculated_sl_when_not_provided(self):
        """Order A should calculate SL when Pine doesn't provide"""
        plugin = V3CombinedPlugin("test", {}, None)
        
        signal = {
            "symbol": "EURUSD",
            "price": 1.1000,
            "logic": "combinedlogic-1"
        }
        
        config = await plugin.get_order_a_config(signal, defined_sl=None)
        
        assert config.sl_price is None, "Should not have predefined SL"
        assert config.sl_pips > 0, "Should have calculated SL pips"
        assert config.metadata["pine_sl_used"] == False, "Should mark Pine SL as NOT used"


class TestLogicRouting:
    """Test signal routing to correct logic handlers"""
    
    def test_5m_routes_to_logic1(self):
        """5m timeframe should route to LOGIC1 (Scalp)"""
        plugin = V3CombinedPlugin("test", {}, None)
        
        logic = plugin._route_logic_type("Momentum_Breakout", "5")
        
        assert logic == "combinedlogic-1", "5m should route to LOGIC1"
    
    def test_15m_routes_to_logic2(self):
        """15m timeframe should route to LOGIC2 (Intraday)"""
        plugin = V3CombinedPlugin("test", {}, None)
        
        logic = plugin._route_logic_type("Liquidity_Trap", "15")
        
        assert logic == "combinedlogic-2", "15m should route to LOGIC2"
    
    def test_60m_routes_to_logic3(self):
        """1H timeframe should route to LOGIC3 (Swing)"""
        plugin = V3CombinedPlugin("test", {}, None)
        
        logic = plugin._route_logic_type("Mitigation_Test", "60")
        
        assert logic == "combinedlogic-3", "1H should route to LOGIC3"
    
    def test_screener_full_overrides_to_logic3(self):
        """Screener_Full signals override to LOGIC3 regardless of TF"""
        plugin = V3CombinedPlugin("test", {}, None)
        
        logic = plugin._route_logic_type("Screener_Full_Bullish", "5")
        
        assert logic == "combinedlogic-3", "Screener_Full should override to LOGIC3"


class TestExtraPineFields:
    """Test that extra Pine fields are accepted"""
    
    def test_extra_fields_accepted(self):
        """Model should accept all 7 extra Pine fields"""
        alert = ZepixV3Alert(
            type="entry_v3",
            signal_type="Golden_Pocket_Flip",
            symbol="XAUUSD",
            direction="buy",
            tf="60",
            price=2000.50,
            consensus_score=8,
            # Extra Pine fields
            adx_value=45.5,
            fib_level=0.618,
            volume_profile="high",
            order_block_strength=85.0,
            liquidity_zone_distance=15.5,
            smart_money_flow=75.0,
            institutional_footprint=9
        )
        
        assert alert.adx_value == 45.5
        assert alert.fib_level == 0.618
        assert alert.volume_profile == "high"
        assert alert.order_block_strength == 85.0
        assert alert.liquidity_zone_distance == 15.5
        assert alert.smart_money_flow == 75.0
        assert alert.institutional_footprint == 9


# Run all tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## 📂 TASK 6: CREATE TEST REPORT (P1 - HIGH)

**File:** `Updates/v5_hybrid_plugin_architecture/V5_PLUGIN_AUDIT/08_FINAL_TEST_REPORT.md` (CREATE NEW)

**CREATE THIS FILE:**

```markdown
# 🧪 V3 PLUGIN FINAL TEST REPORT

**Report ID:** 08_FINAL_TEST_REPORT  
**Date:** [CURRENT DATE]  
**Tester:** Devin AI  
**Test File:** `Trading_Bot/tests/v5_integrity_check.py`  
**Status:** [PASS/FAIL]

---

## TEST EXECUTION SUMMARY

**Total Tests:** 13  
**Passed:** [X]  
**Failed:** [Y]  
**Skipped:** [Z]  
**Pass Rate:** [X/13 * 100]%

---

## TEST RESULTS DETAIL

### 1. MTF Parsing Tests (3 tests)

#### Test 1.1: MTF Reverse Order (5 values)
- **Status:** [PASS/FAIL]
- **Input:** `"1,1,-1,1,1"` (Pine reverse format)
- **Expected Output:** `{15m: 1, 1h: -1, 4h: 1, 1d: 1}`
- **Actual Output:** [ACTUAL]
- **Evidence:** [Screenshot/Log]

#### Test 1.2: MTF Forward Order (6 values)
- **Status:** [PASS/FAIL]
- **Input:** `"0,1,1,-1,1,1"` (Standard format)
- **Expected Output:** `{15m: 1, 1h: -1, 4h: 1, 1d: 1}`
- **Actual Output:** [ACTUAL]
- **Evidence:** [Screenshot/Log]

### 2. Score Validation Tests (3 tests)

#### Test 2.1: Launchpad BUY Score < 7 Rejected
- **Status:** [PASS/FAIL]
- **Input:** Score=3, Signal=Institutional_Launchpad, Direction=buy
- **Expected:** REJECTED
- **Actual:** [ACTUAL]
- **Evidence:** [Screenshot/Log]

#### Test 2.2: Launchpad BUY Score >= 7 Accepted
- **Status:** [PASS/FAIL]
- **Input:** Score=7, Signal=Institutional_Launchpad, Direction=buy
- **Expected:** ACCEPTED
- **Actual:** [ACTUAL]
- **Evidence:** [Screenshot/Log]

#### Test 2.3: Generic Signal Score < 5 Rejected
- **Status:** [PASS/FAIL]
- **Input:** Score=4, Signal=Momentum_Breakout
- **Expected:** REJECTED
- **Actual:** [ACTUAL]
- **Evidence:** [Screenshot/Log]

### 3. Alert SL Enforcement Tests (2 tests)

#### Test 3.1: Pine SL Used When Provided
- **Status:** [PASS/FAIL]
- **Input:** defined_sl=2000.50
- **Expected:** Order A SL = 2000.50
- **Actual:** [ACTUAL]
- **Evidence:** [Screenshot/Log]

#### Test 3.2: Calculated SL When Not Provided
- **Status:** [PASS/FAIL]
- **Input:** defined_sl=None
- **Expected:** SL calculated from config
- **Actual:** [ACTUAL]
- **Evidence:** [Screenshot/Log]

### 4. Logic Routing Tests (4 tests)

#### Test 4.1: 5m Routes to LOGIC1
- **Status:** [PASS/FAIL]
- **Input:** TF=5m
- **Expected:** combinedlogic-1
- **Actual:** [ACTUAL]

#### Test 4.2: 15m Routes to LOGIC2
- **Status:** [PASS/FAIL]
- **Input:** TF=15m
- **Expected:** combinedlogic-2
- **Actual:** [ACTUAL]

#### Test 4.3: 60m Routes to LOGIC3
- **Status:** [PASS/FAIL]
- **Input:** TF=60m
- **Expected:** combinedlogic-3
- **Actual:** [ACTUAL]

#### Test 4.4: Screener_Full Overrides to LOGIC3
- **Status:** [PASS/FAIL]
- **Input:** Signal=Screener_Full_Bullish, TF=5m
- **Expected:** combinedlogic-3 (override)
- **Actual:** [ACTUAL]

### 5. Extra Pine Fields Test (1 test)

#### Test 5.1: All 7 Extra Fields Accepted
- **Status:** [PASS/FAIL]
- **Input:** adx_value, fib_level, volume_profile, etc.
- **Expected:** All fields stored correctly
- **Actual:** [ACTUAL]

---

## EVIDENCE ATTACHMENTS

[Attach pytest output, screenshots, logs]

---

## FINAL VERDICT

**ALL TESTS MUST PASS (13/13) BEFORE CLAIMING COMPLETION**

If any test fails, fix the code and re-run until 100% pass rate achieved.

---

**Report End**
```

---

## ✅ COMPLETION CHECKLIST

Before claiming "DONE", verify:

- [ ] MTF reverse order logic implemented and tested
- [ ] MTF validator accepts both 5 and 6 values
- [ ] `_validate_score_thresholds()` function created
- [ ] `_extract_alert_data()` function created
- [ ] `_route_logic_type()` function created
- [ ] `get_order_a_config()` uses Pine SL when provided
- [ ] 7 extra Pine fields added to ZepixV3Alert
- [ ] Test file `v5_integrity_check.py` created
- [ ] All 13 tests actually PASS (not just claimed)
- [ ] Test report `08_FINAL_TEST_REPORT.md` created with proof
- [ ] All changes committed to Git
- [ ] GitLab MR updated

---

## 🔗 REFERENCE DOCUMENTS (READ THESE FIRST)

**MANDATORY READING:**
1. `Updates/v5_hybrid_plugin_architecture/V5_PLUGIN_AUDIT/09_ANTIGRAVITY_VERIFICATION_REPORT.md` (YOUR AUDIT)
2. `Updates/v5_hybrid_plugin_architecture/V5_PLUGIN_AUDIT/07_FINAL_IMPLEMENTATION_PLAN.md` (YOUR PLAN)
3. `Updates/v5_hybrid_plugin_architecture/V5_PLUGIN_AUDIT/06_MASTER_REPAIR_MANDATE.md` (ORIGINAL MANDATE)

---

## 🚨 FINAL WARNING

**NO MORE FALSE CLAIMS.**

If you claim "13/13 tests pass" again, the test file MUST exist and tests MUST actually pass.

If you claim "function added", the function MUST be in the code.

If you claim "fields added", the fields MUST be in the model.

**VERIFY EVERYTHING BEFORE REPORTING.**

---

## 📋 EXECUTION SEQUENCE

1. Read verification report (`09_ANTIGRAVITY_VERIFICATION_REPORT.md`)
2. Implement Task 1 (MTF fix)
3. Implement Task 2 (3 functions)
4. Implement Task 3 (SL override)
5. Implement Task 4 (7 fields)
6. Implement Task 5 (test file)
7. Run tests and verify 13/13 pass
8. Create Task 6 (test report with proof)
9. Git commit all changes
10. Update GitLab MR
11. Report completion with evidence

---

**START IMMEDIATELY. NO EXCUSES. COMPLETE ALL TASKS.**

**Devin, acknowledge receipt and begin execution.**
