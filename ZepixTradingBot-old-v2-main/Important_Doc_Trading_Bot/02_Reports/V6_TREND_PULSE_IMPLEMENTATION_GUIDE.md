# V6 TREND_PULSE Implementation Guide

**Created:** January 18, 2026  
**Purpose:** Developer guide for implementing missing V6 TREND_PULSE alert processing  
**Impact:** V3 System - ZERO (Complete Isolation Verified)

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Current vs Required Architecture](#current-vs-required-architecture)
3. [Implementation Guide](#implementation-guide)
4. [Code Examples](#code-examples)
5. [V3 Isolation Verification](#v3-isolation-verification)
6. [Testing Checklist](#testing-checklist)
7. [Technical Reference](#technical-reference)

---

## Problem Statement

### Critical Missing Feature

V6 TREND_PULSE alerts are being sent by Pine Script but **NOT processed** by the Bot, causing:

1. **Database never gets populated** - `market_trends` table remains empty
2. **Plugins use wrong alignment source** - Check alert payload ("5/1") instead of higher TF database trends
3. **Re-entry system can't access trends** - No real-time trend data available for autonomous re-entries
4. **Higher TF validation fails** - 5M can't check 15M trend, 15M can't check 1H trend, etc.

### What Should Happen (Hindi Explanation)

```
Pine Script har bar trend change hone par TREND_PULSE alert bhejta hai:
- 5M trend BEAR→BULL hua? → TREND_PULSE alert
- 1H trend BULL→BEAR hua? → TREND_PULSE alert
- Market SIDEWAYS→TRENDING hua? → TREND_PULSE alert

Bot ko ye alerts receive karke database me save karne chahiye:
- 5M entry aaye → 15M trend database se check kare
- 15M entry aaye → 1H trend database se check kare
- Re-entry system → Real-time trends dekh kar decide kare

CURRENTLY: Alerts aa rahe hain par process NAHI ho rahe!
```

---

## Current vs Required Architecture

### Current Implementation (Wrong)

```
Pine Script → TradingView Webhook → Bot
                                      ↓
                        alert_type == "TREND_PULSE"?
                                      ↓
                                NO HANDLER!
                                      ↓
                               Alert Ignored
```

**Plugin Validation (WRONG):**
```python
# v6_price_action_5m/plugin.py Line 273
bull_count, bear_count = alert.get_pulse_counts()  # Gets "5/1" from alert payload
is_aligned = bull_count >= 3                        # Checks SAME TF, not 15M trend
```

### Required Implementation (Correct)

```
Pine Script → TradingView Webhook → Bot
                                      ↓
                        alert_type == "TREND_PULSE"?
                                      ↓ YES
                        Parse TrendPulseAlert
                                      ↓
                        Store in market_trends table
                                      ↓
                        Update cache
                                      ↓
                   Database now has latest trends
```

**Plugin Validation (CORRECT):**
```python
# Check 15M trend from DATABASE (not alert payload)
higher_tf_check = await self.service_api.check_higher_tf_trend(
    symbol="EURUSD",
    signal_tf="5",      # Current signal timeframe
    direction="BUY"
)

if not higher_tf_check["aligned"]:
    # 15M trend is bearish, reject bullish 5M entry
    return {"valid": False, "reason": "15m_trend_misaligned"}
```

---

## Implementation Guide

### Overview of Changes

| File | Change Type | Lines to Modify | Impact |
|------|-------------|-----------------|--------|
| `trading_engine.py` | Add handler | After Line 575 | Processes V6 TREND_PULSE alerts |
| `trading_engine.py` | Initialize manager | Line ~120 | Creates TrendPulseManager instance |
| `service_api.py` | Add method | After Line 1500 | Provides higher TF trend query |
| `v6_price_action_5m/plugin.py` | Update validation | Lines 272-293 | Queries database for 15M trend |
| `v6_price_action_15m/plugin.py` | Update validation | Lines 272-293 | Queries database for 1H trend |
| `v6_price_action_1h/plugin.py` | Update validation | Lines 273-294 | Queries database for 4H trend |
| `v6_price_action_1m/plugin.py` | No change | - | Too fast for higher TF checks |

### Step-by-Step Implementation

#### Step 1: Add V6 TREND_PULSE Handler

**File:** `Trading_Bot/src/core/trading_engine.py`  
**Location:** After Line 575 (after `trend_pulse_v3` handler)

```python
# ADD THIS CODE:

elif alert_type == "TREND_PULSE":  # V6 Trend Pulse (different from trend_pulse_v3)
    """
    V6 Trend Pulse Alert Handler
    Updates market_trends table with current bull/bear counts per timeframe
    """
    try:
        # Parse V6 Trend Pulse alert
        from src.core.zepix_v6_alert import TrendPulseAlert
        pulse_alert = TrendPulseAlert(**data)
        
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
        return False
```

**Safety Check:**
- V3's `"trend_pulse_v3"` handler at Line 571 remains **UNCHANGED**
- Different alert type name = No conflict
- Different manager instance = No database conflict

---

#### Step 2: Initialize TrendPulseManager

**File:** `Trading_Bot/src/core/trading_engine.py`  
**Location:** In `__init__()` method, around Line 120

```python
# EXISTING CODE (Don't touch):
self.trend_manager = TimeframeTrendManager()  # V3 JSON-based trend manager

# ADD THIS CODE:
# Initialize V6 TrendPulseManager (SQL-based)
from src.core.trend_pulse_manager import create_trend_pulse_manager
try:
    # Get V6 database connection from service_api
    v6_database = self.service_api.get_database_for_plugin('v6_price_action_5m')
    self.trend_pulse_manager = create_trend_pulse_manager(database=v6_database)
    logger.info("TrendPulseManager initialized (V6 SQL database)")
except Exception as e:
    logger.warning(f"Could not initialize TrendPulseManager: {e}")
    self.trend_pulse_manager = None
```

**Notes:**
- `self.trend_manager` = V3 (JSON file)
- `self.trend_pulse_manager` = V6 (SQL database)
- No variable name conflict

---

#### Step 3: Add ServiceAPI Method for Higher TF Trend Check

**File:** `Trading_Bot/src/core/plugin_system/service_api.py`  
**Location:** After Line 1500 (after existing trend methods)

```python
async def check_higher_tf_trend(
    self,
    symbol: str,
    signal_tf: str,
    direction: str
) -> Dict[str, Any]:
    """
    Check if higher timeframe trend aligns with signal direction.
    
    Timeframe Hierarchy:
    - 1M entry → Check 5M trend
    - 5M entry → Check 15M trend
    - 15M entry → Check 1H trend
    - 1H entry → Check 4H trend
    
    Args:
        symbol: Trading pair (e.g., "EURUSD")
        signal_tf: Current signal timeframe ("1", "5", "15", "60")
        direction: Signal direction ("BUY" or "SELL")
    
    Returns:
        {
            "aligned": bool,
            "higher_tf": str,
            "bull_count": int,
            "bear_count": int,
            "reason": str
        }
    """
    # Timeframe hierarchy mapping
    tf_hierarchy = {
        "1": "5",      # 1M → Check 5M
        "5": "15",     # 5M → Check 15M
        "15": "60",    # 15M → Check 1H
        "60": "240"    # 1H → Check 4H
    }
    
    higher_tf = tf_hierarchy.get(signal_tf)
    
    # No higher TF to check (e.g., 4H entry)
    if not higher_tf:
        return {
            "aligned": True,
            "higher_tf": None,
            "bull_count": 0,
            "bear_count": 0,
            "reason": "no_higher_tf"
        }
    
    # Get higher TF trend from database
    try:
        pulse_data = await self._trend_service.get_pulse_data(symbol, higher_tf)
        
        if not pulse_data or higher_tf not in pulse_data:
            return {
                "aligned": False,
                "higher_tf": higher_tf,
                "bull_count": 0,
                "bear_count": 0,
                "reason": f"no_{higher_tf}m_data"
            }
        
        tf_data = pulse_data[higher_tf]
        bull_count = tf_data.get("bull_count", 0)
        bear_count = tf_data.get("bear_count", 0)
        
        # Check alignment based on signal direction
        if direction.upper() == "BUY":
            aligned = bull_count > bear_count
        else:  # SELL
            aligned = bear_count > bull_count
        
        return {
            "aligned": aligned,
            "higher_tf": higher_tf,
            "bull_count": bull_count,
            "bear_count": bear_count,
            "reason": "aligned" if aligned else f"{higher_tf}m_misaligned"
        }
        
    except Exception as e:
        self.logger.error(f"Error checking higher TF trend: {e}")
        return {
            "aligned": False,
            "higher_tf": higher_tf,
            "bull_count": 0,
            "bear_count": 0,
            "reason": f"error_{str(e)}"
        }
```

---

#### Step 4: Update V6 Plugin Validation Logic

**File:** `Trading_Bot/src/logic_plugins/v6_price_action_5m/plugin.py`  
**Location:** Lines 272-293 (in `_validate_entry` method)

**REMOVE THIS:**
```python
# OLD CODE (Wrong - checks alert payload)
if self.REQUIRE_15M_ALIGNMENT:
    bull_count, bear_count = alert.get_pulse_counts()  # Gets "5/1" from payload
    
    if alert.direction.upper() == "BUY":
        is_aligned = bull_count >= 3
    else:
        is_aligned = bear_count >= 3
    
    if not is_aligned:
        # ... rejection logic ...
```

**REPLACE WITH THIS:**
```python
# NEW CODE (Correct - checks database)
if self.REQUIRE_15M_ALIGNMENT:
    # Query database for 15M trend
    higher_tf_check = await self.service_api.check_higher_tf_trend(
        symbol=alert.ticker,
        signal_tf="5",              # Current signal is 5M
        direction=alert.direction
    )
    
    if not higher_tf_check["aligned"]:
        self.logger.info(
            f"[5M_SKIP] 15M trend not aligned: "
            f"Bull={higher_tf_check['bull_count']}, "
            f"Bear={higher_tf_check['bear_count']} "
            f"for {alert.direction} entry"
        )
        return {
            "valid": False,
            "reason": higher_tf_check["reason"],
            "details": f"15M: {higher_tf_check['bull_count']}B/{higher_tf_check['bear_count']}B"
        }
    
    # Alignment confirmed
    self.logger.info(
        f"[5M_OK] 15M alignment confirmed: "
        f"Bull={higher_tf_check['bull_count']}, "
        f"Bear={higher_tf_check['bear_count']}"
    )
```

**Apply Same Logic to Other Plugins:**

- **15M Plugin:** Check 1H trend (`signal_tf="15"`, checks `"60"`)
- **1H Plugin:** Check 4H trend (`signal_tf="60"`, checks `"240"`)
- **1M Plugin:** Check 5M trend (`signal_tf="1"`, checks `"5"`) - OPTIONAL (scalping may skip)

---

## Code Examples

### Example 1: Complete TREND_PULSE Alert Flow

```python
# Pine Script sends:
{
    "type": "TREND_PULSE",
    "symbol": "EURUSD",
    "tf": "5",
    "bull_count": 4,
    "bear_count": 2,
    "state": "TRENDING_BULLISH",
    "changes": "5m:BEAR→BULL,1h:SIDE→BULL"
}

# Bot receives and processes:
# 1. trading_engine.py handles alert
alert_type = data.get('type')  # "TREND_PULSE"

# 2. Parse and store
pulse_alert = TrendPulseAlert(**data)
await self.trend_pulse_manager.update_pulse(...)

# 3. Database updated
# market_trends table:
# | symbol | timeframe | bull_count | bear_count | market_state       |
# |--------|-----------|------------|------------|--------------------|
# | EURUSD | 5         | 4          | 2          | TRENDING_BULLISH   |

# 4. Cache updated (fast access for plugins)
```

### Example 2: Plugin Higher TF Validation

```python
# 5M BUY entry alert arrives
alert = ZepixV6Alert(
    ticker="EURUSD",
    tf="5",
    direction="BUY",
    price=1.0850,
    adx=28,
    conf_score=75
)

# Plugin checks 15M trend from database
higher_tf_check = await self.service_api.check_higher_tf_trend(
    symbol="EURUSD",
    signal_tf="5",
    direction="BUY"
)

# Database returns:
{
    "aligned": True,           # 15M is bullish (4 > 2)
    "higher_tf": "15",
    "bull_count": 4,
    "bear_count": 2,
    "reason": "aligned"
}

# Result: Entry APPROVED
```

### Example 3: Misalignment Rejection

```python
# 5M BUY entry alert arrives
# But 15M trend is BEARISH

higher_tf_check = await self.service_api.check_higher_tf_trend(
    symbol="EURUSD",
    signal_tf="5",
    direction="BUY"  # Wants to buy
)

# Database returns:
{
    "aligned": False,          # 15M is bearish (2 < 5)
    "higher_tf": "15",
    "bull_count": 2,           # Only 2 bullish TFs
    "bear_count": 5,           # 5 bearish TFs
    "reason": "15m_misaligned"
}

# Result: Entry REJECTED
# Log: "[5M_SKIP] 15M trend not aligned: Bull=2, Bear=5 for BUY entry"
```

---

## V3 Isolation Verification

### Complete Separation Proof

| Component | V3 System | V6 System | Conflict? |
|-----------|-----------|-----------|-----------|
| **Alert Type** | `"entry_v3"`, `"trend_pulse_v3"` | `"entry_v6"`, `"TREND_PULSE"` | NO |
| **Alert Model** | `ZepixV3Alert` | `ZepixV6Alert`, `TrendPulseAlert` | NO |
| **Trend Storage** | `config/timeframe_trends.json` | `market_trends` table (SQL) | NO |
| **Trend Manager** | `TimeframeTrendManager` | `TrendPulseManager` | NO |
| **Database** | None (JSON file) | `zepix_price_action.db` | NO |
| **Plugin** | `v3_combined` | `v6_price_action_*` | NO |
| **Validation** | Consensus Score (bypasses trends) | ADX + Conf + Higher TF | NO |
| **Entry Flow** | BYPASS trend check | REQUIRE trend check | NO |

### V3 Flow Remains Unchanged

**BEFORE Implementation:**
```python
# trading_engine.py Line 505
if alert_type == "entry_v3":
    logger.info("V3 Entry Signal - BYPASSING Trend Manager")
    # Execute WITHOUT trend validation
    result = await self.execute_v3_entry(v3_alert)
```

**AFTER Implementation:**
```python
# trading_engine.py Line 505
if alert_type == "entry_v3":
    logger.info("V3 Entry Signal - BYPASSING Trend Manager")  # UNCHANGED
    # Execute WITHOUT trend validation                         # UNCHANGED
    result = await self.execute_v3_entry(v3_alert)            # UNCHANGED

# NEW CODE (Different alert type, different flow):
elif alert_type == "TREND_PULSE":  # V6 only
    await self.trend_pulse_manager.update_pulse(...)  # V6 database
```

### Why Zero Impact?

1. **Different Alert Type Names**
   - V3: `"trend_pulse_v3"` (Line 571)
   - V6: `"TREND_PULSE"` (NEW)
   - Alert routing separates them automatically

2. **Different Storage Mechanisms**
   - V3: `timeframe_trends.json` (TimeframeTrendManager)
   - V6: `market_trends` table (TrendPulseManager)
   - No file/table overlap

3. **Different Manager Instances**
   - V3: `self.trend_manager` (JSON operations)
   - V6: `self.trend_pulse_manager` (SQL operations)
   - No variable conflict

4. **V3 Bypass Logic Untouched**
   - V3 never calls trend validation
   - V3 trusts Pine Script consensus score
   - V6 implementation doesn't modify V3 code path

---

## Testing Checklist

### Phase 1: TREND_PULSE Alert Processing

- [ ] **Test 1.1:** Send TREND_PULSE alert via webhook
  - Expected: Alert received and logged
  - Log: `[V6_TREND_PULSE] EURUSD 5m: Bull=4, Bear=2`

- [ ] **Test 1.2:** Verify database update
  - Query: `SELECT * FROM market_trends WHERE symbol='EURUSD' AND timeframe='5'`
  - Expected: Row exists with bull_count=4, bear_count=2

- [ ] **Test 1.3:** Verify cache update
  - Call: `await trend_pulse_manager.get_pulse("EURUSD", "5")`
  - Expected: Returns cached data (fast response)

- [ ] **Test 1.4:** Multiple timeframe updates
  - Send TREND_PULSE for 1M, 5M, 15M, 1H, 4H
  - Expected: All 5 rows in database

### Phase 2: Higher TF Trend Validation

- [ ] **Test 2.1:** 5M entry with aligned 15M trend
  - Setup: 15M bull_count=4, bear_count=2 (bullish)
  - Send: 5M BUY entry alert
  - Expected: Entry APPROVED

- [ ] **Test 2.2:** 5M entry with misaligned 15M trend
  - Setup: 15M bull_count=2, bear_count=5 (bearish)
  - Send: 5M BUY entry alert
  - Expected: Entry REJECTED, reason="15m_misaligned"

- [ ] **Test 2.3:** 15M entry checking 1H trend
  - Setup: 1H bull_count=5, bear_count=1 (bullish)
  - Send: 15M BUY entry alert
  - Expected: Entry APPROVED

- [ ] **Test 2.4:** 1H entry checking 4H trend
  - Setup: 4H bull_count=3, bear_count=4 (bearish)
  - Send: 1H BUY entry alert
  - Expected: Entry REJECTED

### Phase 3: V3 System Isolation

- [ ] **Test 3.1:** Send V3 entry_v3 alert
  - Expected: Processes normally, BYPASSES trend check
  - Log: `V3 Entry Signal - BYPASSING Trend Manager`

- [ ] **Test 3.2:** Send V3 trend_pulse_v3 alert
  - Expected: Updates timeframe_trends.json (NOT market_trends table)
  - Verify: JSON file modified, SQL table unchanged

- [ ] **Test 3.3:** Concurrent V3 and V6 alerts
  - Send: V3 entry + V6 TREND_PULSE simultaneously
  - Expected: Both process independently, no conflict

- [ ] **Test 3.4:** V3 database unchanged
  - Before: Check timeframe_trends.json content
  - Run: V6 TREND_PULSE processing
  - After: Verify timeframe_trends.json identical

### Phase 4: Re-Entry System Integration

- [ ] **Test 4.1:** Re-entry with trend change
  - Initial: 15M bullish, 5M position opened
  - Change: 15M turns bearish (TREND_PULSE alert)
  - Expected: Re-entry manager rejects new 5M buy entries

- [ ] **Test 4.2:** Re-entry with trend recovery
  - Initial: Position closed due to trend reversal
  - Change: 15M returns to bullish
  - Expected: Re-entry opportunity detected

### Phase 5: Performance & Edge Cases

- [ ] **Test 5.1:** Missing higher TF data
  - Setup: 15M trend data not in database
  - Send: 5M entry alert
  - Expected: Rejected with reason="no_15m_data"

- [ ] **Test 5.2:** TrendPulseManager not initialized
  - Simulate: Manager initialization failure
  - Send: TREND_PULSE alert
  - Expected: Warning logged, alert not processed

- [ ] **Test 5.3:** Rapid TREND_PULSE updates
  - Send: 10 TREND_PULSE alerts within 1 second
  - Expected: All processed, database updated correctly

---

## Technical Reference

### File Paths & Line Numbers

```
Trading_Bot/
├── src/
│   ├── core/
│   │   ├── trading_engine.py
│   │   │   ├── Line 120: __init__() - Add TrendPulseManager initialization
│   │   │   ├── Line 505: V3 entry processing (BYPASS logic)
│   │   │   ├── Line 571: V3 trend_pulse_v3 handler (UNCHANGED)
│   │   │   └── Line 575+: ADD V6 TREND_PULSE handler
│   │   │
│   │   ├── trend_pulse_manager.py
│   │   │   ├── Line 150-230: update_pulse() method
│   │   │   ├── Line 201-229: get_pulse() method
│   │   │   └── Line 409-439: get_timeframe_alignment() method
│   │   │
│   │   ├── zepix_v6_alert.py
│   │   │   ├── Line 145-160: get_pulse_counts() (alert payload parser)
│   │   │   └── Line 244-273: TrendPulseAlert model
│   │   │
│   │   ├── plugin_system/
│   │   │   └── service_api.py
│   │   │       ├── Line 1427: update_trend_pulse() wrapper
│   │   │       ├── Line 1457: get_market_state() method
│   │   │       └── Line 1500+: ADD check_higher_tf_trend() method
│   │   │
│   │   └── services/
│   │       └── trend_management_service.py
│   │           ├── Line 198-246: update_trend_pulse()
│   │           ├── Line 248-280: get_market_state()
│   │           └── Line 335-390: get_pulse_data()
│   │
│   └── logic_plugins/
│       ├── v3_combined/
│       │   ├── plugin.py (UNTOUCHED - V3 logic)
│       │   └── signal_handlers.py
│       │       └── Line 304: handle_trend_pulse() - V3 JSON update
│       │
│       ├── v6_price_action_1m/
│       │   └── plugin.py (OPTIONAL - may skip higher TF check)
│       │
│       ├── v6_price_action_5m/
│       │   └── plugin.py
│       │       └── Line 272-293: UPDATE to check 15M trend from database
│       │
│       ├── v6_price_action_15m/
│       │   └── plugin.py
│       │       └── Line 272-293: UPDATE to check 1H trend from database
│       │
│       └── v6_price_action_1h/
│           └── plugin.py
│               └── Line 273-294: UPDATE to check 4H trend from database
│
├── database/
│   └── schemas/
│       └── price_action_v6_schema.sql
│           └── Line 167-176: market_trends table definition
│
└── config/
    └── timeframe_trends.json (V3 storage - UNTOUCHED)
```

### Database Schema

**V6 Market Trends Table:**
```sql
CREATE TABLE IF NOT EXISTS market_trends (
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    bull_count INTEGER DEFAULT 0,
    bear_count INTEGER DEFAULT 0,
    net_direction TEXT DEFAULT 'NEUTRAL',
    market_state TEXT DEFAULT 'SIDEWAYS',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, timeframe)
);
```

**Example Data:**
```sql
INSERT INTO market_trends VALUES 
('EURUSD', '1', 3, 3, 'NEUTRAL', 'SIDEWAYS', '2026-01-18 10:15:30'),
('EURUSD', '5', 4, 2, 'BULLISH', 'TRENDING_BULLISH', '2026-01-18 10:16:45'),
('EURUSD', '15', 5, 1, 'BULLISH', 'TRENDING_BULLISH', '2026-01-18 10:14:22'),
('EURUSD', '60', 4, 2, 'BULLISH', 'TRENDING_BULLISH', '2026-01-18 10:10:11');
```

### Alert Payload Examples

**V3 Trend Pulse (JSON file update):**
```json
{
    "type": "trend_pulse_v3",
    "symbol": "EURUSD",
    "changed_timeframes": ["15m", "1h"],
    "trend_data": {
        "15m": "BULLISH",
        "1h": "BULLISH"
    }
}
```

**V6 Trend Pulse (SQL database update):**
```json
{
    "type": "TREND_PULSE",
    "symbol": "EURUSD",
    "tf": "5",
    "bull_count": 4,
    "bear_count": 2,
    "state": "TRENDING_BULLISH",
    "changes": "5m:BEAR→BULL,1h:SIDE→BULL",
    "timestamp": "2026-01-18T10:16:45Z"
}
```

### Timeframe Hierarchy

```
1M (60 seconds)
  ↓ checks
5M (300 seconds)
  ↓ checks
15M (900 seconds)
  ↓ checks
1H (3600 seconds)
  ↓ checks
4H (14400 seconds)
```

**Validation Rules:**
- 1M entry → 5M trend must align
- 5M entry → 15M trend must align
- 15M entry → 1H trend must align
- 1H entry → 4H trend must align
- 4H entry → No higher TF (approved by default)

---

## Summary

### What Gets Fixed

- **V6 TREND_PULSE alerts** - Now processed and stored in database  
- **Plugin validation** - Checks real higher TF trends from database  
- **Re-entry system** - Accesses real-time trend data  
- **Higher TF alignment** - Proper TF hierarchy validation (5M→15M→1H→4H)

### What Stays Unchanged

- **V3 entry flow** - Still bypasses trend checks  
- **V3 trend storage** - Still uses JSON file  
- **V3 consensus logic** - Still trusts Pine Script validation  
- **V3 alert processing** - Completely isolated from V6

### Key Guarantees

- **Zero V3 Impact** - Different alert types, storage, managers  
- **Database Isolation** - V3 uses JSON, V6 uses SQL  
- **Manager Isolation** - TimeframeTrendManager vs TrendPulseManager  
- **Alert Type Separation** - "trend_pulse_v3" vs "TREND_PULSE"

---

## Developer Notes

### Hindi Explanation (Quick Reference)

```
PROBLEM:
Pine Script TREND_PULSE alerts bhej raha hai par Bot process nahi kar raha.
Result: Database khali hai, plugins galat data check kar rahe hain.

SOLUTION:
1. trading_engine.py me handler add karo (Line 575 ke baad)
2. TrendPulseManager initialize karo (__init__ me)
3. ServiceAPI me check_higher_tf_trend() method add karo
4. V6 plugins update karo (database se trend check karein)

V3 IMPACT:
BILKUL NAHI! V3 apna JSON file use karta hai, V6 apna SQL database.
Alert type names bhi alag hain: "trend_pulse_v3" vs "TREND_PULSE"

BENEFIT:
- 5M entry → 15M trend dekh kar approve/reject
- Re-entry system → Real-time trends se decide
- Pro Trader Mind → Sahi higher TF alignment check
```

### Common Pitfalls to Avoid

1. **Don't modify V3 code** - Only add new V6 handlers
2. **Don't reuse V3 managers** - Create separate TrendPulseManager instance
3. **Don't mix alert types** - Keep "trend_pulse_v3" and "TREND_PULSE" separate
4. **Don't skip database initialization** - TrendPulseManager must be created in __init__()

### Deployment Checklist

- [ ] Backup `trading_engine.py` before modification
- [ ] Verify `market_trends` table exists in database
- [ ] Test TREND_PULSE handler with sample alert
- [ ] Confirm V3 entries still work (send test entry_v3 alert)
- [ ] Monitor logs for both V3 and V6 alert processing
- [ ] Check database for trend updates after TREND_PULSE alerts
- [ ] Validate higher TF checks reject misaligned entries

---

**Document Version:** 1.0  
**Last Updated:** January 18, 2026  
**Status:** Ready for Implementation  
**Estimated Implementation Time:** 2-3 hours  
**Risk Level:** LOW (V3 isolation verified)
