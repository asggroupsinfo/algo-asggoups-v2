# V6 TREND_PULSE Implementation Report

**Date:** 2026-01-18
**Author:** Devin AI
**Status:** COMPLETE

---

## Executive Summary

This report documents the complete implementation of V6 TREND_PULSE alert processing as specified in the V6_TREND_PULSE_IMPLEMENTATION_GUIDE.md. All 4 implementation steps have been completed successfully, enabling the bot to process V6 Trend Pulse alerts and validate entries against higher timeframe trends from the database.

---

## Implementation Overview

### Problem Statement

V6 TREND_PULSE alerts were being sent by Pine Script but NOT processed by the Bot. The alerts were arriving at the webhook but being ignored because there was no handler for the "TREND_PULSE" alert type (only "trend_pulse_v3" for V3 was handled).

### Solution Implemented

A 4-step implementation was completed:

1. **Step 1:** Added V6 TREND_PULSE handler in trading_engine.py
2. **Step 2:** Initialized TrendPulseManager in trading_engine.__init__()
3. **Step 3:** Added check_higher_tf_trend() method in service_api.py
4. **Step 4:** Updated V6 plugin validation logic (5m, 15m, 1h)

---

## Detailed Implementation

### Step 1: V6 TREND_PULSE Handler

**File:** `Trading_Bot/src/core/trading_engine.py`
**Location:** Lines 576-622 (after trend_pulse_v3 handler)

**Code Added:**
```python
# V6 TREND_PULSE: Update market_trends table (SQL database)
elif alert_type == "TREND_PULSE":
    """
    V6 Trend Pulse Alert Handler
    Updates market_trends table with current bull/bear counts per timeframe
    This is SEPARATE from V3 trend_pulse_v3 which uses JSON file
    """
    try:
        from src.core.zepix_v6_alert import TrendPulseAlert
        
        # Parse V6 Trend Pulse alert
        pulse_alert = TrendPulseAlert(
            type=data.get('type', 'TREND_PULSE'),
            symbol=data.get('symbol', data.get('ticker', '')),
            tf=str(data.get('tf', data.get('timeframe', ''))),
            bull_count=int(data.get('bull_count', 0)),
            bear_count=int(data.get('bear_count', 0)),
            changes=data.get('changes', ''),
            state=data.get('state', data.get('market_state', 'UNKNOWN'))
        )
        
        # Update V6 database via TrendPulseManager
        if hasattr(self, 'trend_pulse_manager') and self.trend_pulse_manager:
            await self.trend_pulse_manager.update_pulse(
                symbol=pulse_alert.symbol,
                timeframe=pulse_alert.tf,
                bull_count=pulse_alert.bull_count,
                bear_count=pulse_alert.bear_count,
                market_state=pulse_alert.state,
                changes=pulse_alert.changes
            )
            
            logger.info(
                f"[V6_TREND_PULSE] {pulse_alert.symbol} {pulse_alert.tf}m: "
                f"Bull={pulse_alert.bull_count}, Bear={pulse_alert.bear_count}, "
                f"State={pulse_alert.state}, Changes={pulse_alert.changes}"
            )
        else:
            logger.warning("[V6_TREND_PULSE] TrendPulseManager not initialized!")
        
        return True
        
    except Exception as e:
        logger.error(f"[V6_TREND_PULSE] Error processing alert: {e}")
        import traceback
        traceback.print_exc()
        return False
```

**Purpose:** Handles incoming V6 TREND_PULSE alerts and updates the market_trends table in the database.

---

### Step 2: TrendPulseManager Initialization

**File:** `Trading_Bot/src/core/trading_engine.py`
**Location:** Lines 64-67 (after trend_manager initialization)

**Code Added:**
```python
# V6 Trend Pulse Manager (separate from V3 TimeframeTrendManager)
# Uses SQL database (market_trends table) instead of JSON file
from src.core.trend_pulse_manager import TrendPulseManager
self.trend_pulse_manager = TrendPulseManager(database=self.db)
```

**Purpose:** Initializes the TrendPulseManager with the database connection so it can store and retrieve trend data.

---

### Step 3: check_higher_tf_trend() Method

**File:** `Trading_Bot/src/core/plugin_system/service_api.py`
**Location:** Lines 1501-1602 (after get_pulse_data method)

**Code Added:**
```python
async def check_higher_tf_trend(
    self,
    symbol: str,
    signal_tf: str,
    direction: str
) -> Dict[str, Any]:
    """
    Check if signal aligns with higher timeframe trend from database.
    
    V6 Timeframe Hierarchy:
    - 1M entry -> Check 5M trend
    - 5M entry -> Check 15M trend
    - 15M entry -> Check 1H (60M) trend
    - 1H entry -> Check 4H (240M) trend
    - 4H entry -> No higher TF (approved by default)
    """
    HIGHER_TF_MAP = {
        "1": "5",
        "5": "15",
        "15": "60",
        "60": "240",
        "240": None
    }
    
    higher_tf = HIGHER_TF_MAP.get(signal_tf)
    
    if higher_tf is None:
        return {
            "aligned": True,
            "higher_tf": None,
            "bull_count": 0,
            "bear_count": 0,
            "reason": f"{signal_tf}m is highest TF - no higher TF check needed"
        }
    
    # Query database for higher TF trend data
    if hasattr(self._engine, 'trend_pulse_manager') and self._engine.trend_pulse_manager:
        pulse_data = await self._engine.trend_pulse_manager.get_pulse(symbol, higher_tf)
        
        if pulse_data is None:
            return {
                "aligned": True,
                "higher_tf": higher_tf,
                "bull_count": 0,
                "bear_count": 0,
                "reason": f"No {higher_tf}m trend data available - proceeding with caution"
            }
        
        bull_count = pulse_data.bull_count
        bear_count = pulse_data.bear_count
        
        if direction.upper() == "BUY":
            is_aligned = bull_count > bear_count
        else:
            is_aligned = bear_count > bull_count
        
        return {
            "aligned": is_aligned,
            "higher_tf": higher_tf,
            "bull_count": bull_count,
            "bear_count": bear_count,
            "reason": f"{higher_tf}m trend: Bull={bull_count}, Bear={bear_count}"
        }
```

**Purpose:** Provides a method for V6 plugins to check if their signal aligns with the higher timeframe trend from the database.

---

### Step 4: V6 Plugin Validation Updates

**Files Updated:**
- `Trading_Bot/src/logic_plugins/v6_price_action_5m/plugin.py` (Lines 273-291)
- `Trading_Bot/src/logic_plugins/v6_price_action_15m/plugin.py` (Lines 284-302)
- `Trading_Bot/src/logic_plugins/v6_price_action_1h/plugin.py` (Lines 274-292)

**Before (Payload-based check):**
```python
if self.REQUIRE_15M_ALIGNMENT:
    bull_count, bear_count = alert.get_pulse_counts()
    
    if alert.alignment == "0/0" or (bull_count == 0 and bear_count == 0):
        self.logger.warning(f"[5M] No MTF alignment data in payload, proceeding with caution")
    else:
        if alert.direction.upper() == "BUY":
            is_aligned = bull_count >= 3
        else:
            is_aligned = bear_count >= 3
        
        if not is_aligned:
            return {"valid": False, "reason": "alignment_weak"}
```

**After (Database-based check):**
```python
if self.REQUIRE_15M_ALIGNMENT:
    try:
        higher_tf_result = await self.service_api.check_higher_tf_trend(
            symbol=alert.ticker,
            signal_tf=self.TIMEFRAME,
            direction=alert.direction
        )
        
        if not higher_tf_result.get("aligned", True):
            self.logger.info(
                f"[5M Skip] Higher TF ({higher_tf_result.get('higher_tf', '15')}m) misaligned: "
                f"{higher_tf_result.get('reason', 'Unknown')}"
            )
            return {"valid": False, "reason": "higher_tf_misaligned"}
        
        self.logger.debug(
            f"[5M] Higher TF check passed: {higher_tf_result.get('reason', 'Aligned')}"
        )
    except Exception as e:
        self.logger.warning(f"[5M] Higher TF check failed, proceeding with caution: {e}")
```

**Purpose:** Changes V6 plugins from checking the alert payload for alignment to querying the database for the actual higher timeframe trend data.

---

## V3 Isolation Verification

The implementation maintains complete V3 isolation:

| Aspect | V3 System | V6 System |
|--------|-----------|-----------|
| Alert Type | `trend_pulse_v3` | `TREND_PULSE` |
| Storage | `timeframe_trends.json` | `market_trends` table (SQL) |
| Manager | `TimeframeTrendManager` | `TrendPulseManager` |
| Entry Flow | Bypasses trend check | Requires higher TF alignment |

**V3 Code Unchanged:**
- Lines 571-574 in trading_engine.py remain untouched
- TimeframeTrendManager initialization unchanged
- V3 plugin validation logic unchanged

---

## Timeframe Hierarchy

The implementation follows this hierarchy for higher TF validation:

| Signal TF | Checks Higher TF | Example |
|-----------|------------------|---------|
| 1M | 5M | 1M BUY -> Check 5M Bull > Bear |
| 5M | 15M | 5M SELL -> Check 15M Bear > Bull |
| 15M | 1H (60M) | 15M BUY -> Check 1H Bull > Bear |
| 1H (60M) | 4H (240M) | 1H SELL -> Check 4H Bear > Bull |
| 4H (240M) | None | Approved by default |

---

## Testing Checklist

### Phase 1: TREND_PULSE Alert Processing

| Test | Description | Expected Result |
|------|-------------|-----------------|
| 1.1 | Send TREND_PULSE alert via webhook | Alert processed, log shows [V6_TREND_PULSE] |
| 1.2 | Verify database update | market_trends table updated |
| 1.3 | Verify cache update | TrendPulseManager cache contains data |
| 1.4 | Multiple timeframe updates | Each TF stored separately |

### Phase 2: Higher TF Trend Validation

| Test | Description | Expected Result |
|------|-------------|-----------------|
| 2.1 | 5M BUY with aligned 15M trend | Entry APPROVED |
| 2.2 | 5M BUY with misaligned 15M trend | Entry REJECTED |
| 2.3 | 15M entry checking 1H trend | Correct TF checked |
| 2.4 | 1H entry checking 4H trend | Correct TF checked |

### Phase 3: V3 System Isolation

| Test | Description | Expected Result |
|------|-------------|-----------------|
| 3.1 | Send V3 entry_v3 alert | Bypasses trend check |
| 3.2 | Send V3 trend_pulse_v3 alert | Updates JSON, not SQL |
| 3.3 | Concurrent V3 and V6 alerts | Both processed correctly |
| 3.4 | V3 database unchanged | timeframe_trends.json unchanged |

### Phase 4: Edge Cases

| Test | Description | Expected Result |
|------|-------------|-----------------|
| 4.1 | Missing higher TF data | Proceeds with caution |
| 4.2 | TrendPulseManager not initialized | Warning logged, proceeds |
| 4.3 | 4H entry (no higher TF) | Approved by default |

---

## Files Modified

| File | Lines Changed | Description |
|------|---------------|-------------|
| `trading_engine.py` | +52 lines | V6 TREND_PULSE handler + TrendPulseManager init |
| `service_api.py` | +103 lines | check_higher_tf_trend() method |
| `v6_price_action_5m/plugin.py` | ~20 lines | Database-based validation |
| `v6_price_action_15m/plugin.py` | ~20 lines | Database-based validation |
| `v6_price_action_1h/plugin.py` | ~20 lines | Database-based validation |

---

## Conclusion

The V6 TREND_PULSE implementation is complete. The bot can now:

1. Process V6 TREND_PULSE alerts and store them in the database
2. Validate V6 entries against higher timeframe trends from the database
3. Maintain complete V3 isolation (no V3 code modified)
4. Follow the correct timeframe hierarchy for validation

The implementation follows all guidelines from the V6_TREND_PULSE_IMPLEMENTATION_GUIDE.md and maintains backward compatibility with the existing V3 system.
