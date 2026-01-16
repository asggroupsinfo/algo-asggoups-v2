# TESTING STRATEGY PLAN - Brutal Verification

**Objective:** Test EVERYTHING brutally with evidence. No assumptions. Every test must have proof.

**Estimated Effort:** 4-6 hours

---

## PART 1: TESTING PHILOSOPHY

### 1.1 Zero Tolerance Policy

- **NO assumptions** - Every claim must have evidence
- **NO shortcuts** - Every test must be executed
- **NO partial tests** - Complete end-to-end verification
- **NO silent failures** - All errors must be logged and reported

### 1.2 Evidence Requirements

Every test must produce:
1. **Input:** What was sent
2. **Output:** What was received
3. **Logs:** Console/file logs showing execution
4. **Database:** Records created/modified
5. **Screenshots:** Visual proof (for Telegram)

---

## PART 2: UNIT TESTS

### 2.1 Plugin System Unit Tests

**File:** `tests/test_plugin_system.py`

| Test ID | Test Name | Description | Expected Result |
|---------|-----------|-------------|-----------------|
| PS-001 | test_plugin_registry_init | PluginRegistry initializes correctly | Registry created with empty plugins dict |
| PS-002 | test_plugin_discovery | discover_plugins() finds all plugins | Returns list of plugin folders |
| PS-003 | test_plugin_loading | load_all_plugins() loads plugins | All plugins in registry |
| PS-004 | test_get_plugin | get_plugin() returns correct plugin | Plugin instance or None |
| PS-005 | test_route_alert_to_plugin | route_alert_to_plugin() calls plugin | Plugin method called |
| PS-006 | test_plugin_not_found | route_alert_to_plugin() with invalid ID | Returns error dict |
| PS-007 | test_plugin_disabled | route_alert_to_plugin() with disabled plugin | Returns skipped dict |
| PS-008 | test_fallback_plugin | Fallback when primary not found | Uses fallback plugin |

### 2.2 V3 Plugin Unit Tests

**File:** `tests/test_v3_plugin.py`

| Test ID | Test Name | Description | Expected Result |
|---------|-----------|-------------|-----------------|
| V3-001 | test_v3_plugin_init | V3 plugin initializes | Plugin created with config |
| V3-002 | test_process_entry_signal | Entry signal processing | Returns success dict |
| V3-003 | test_process_exit_signal | Exit signal processing | Closes positions |
| V3-004 | test_process_reversal_signal | Reversal signal processing | Closes + opens opposite |
| V3-005 | test_route_to_logic | Timeframe routing | Correct logic selected |
| V3-006 | test_get_logic_multiplier | Multiplier calculation | Correct multiplier |
| V3-007 | test_dual_order_placement | V3 dual orders | Two orders placed |
| V3-008 | test_mtf_trend_validation | MTF trend check | Validation result |

### 2.3 V6 Plugin Unit Tests

**File:** `tests/test_v6_plugin.py`

| Test ID | Test Name | Description | Expected Result |
|---------|-----------|-------------|-----------------|
| V6-001 | test_v6_plugin_init | V6 plugin initializes | Plugin created with config |
| V6-002 | test_process_entry_signal | Entry signal processing | Returns success dict |
| V6-003 | test_trend_pulse_alignment | Trend Pulse check | Alignment result |
| V6-004 | test_adx_filter | ADX filter check | Filter result |
| V6-005 | test_spread_filter | Spread filter check | Filter result |
| V6-006 | test_order_a_placement | Order A only | Single order placed |
| V6-007 | test_order_b_placement | Order B only | Single order placed |
| V6-008 | test_dual_order_placement | V6 dual orders | Two orders placed |

### 2.4 Core Routing Unit Tests

**File:** `tests/test_core_routing.py`

| Test ID | Test Name | Description | Expected Result |
|---------|-----------|-------------|-----------------|
| CR-001 | test_process_alert_v3_entry | V3 entry routes to plugin | Plugin called |
| CR-002 | test_process_alert_v3_exit | V3 exit routes to plugin | Plugin called |
| CR-003 | test_process_alert_v6_entry | V6 entry routes to plugin | Plugin called |
| CR-004 | test_process_alert_v6_exit | V6 exit routes to plugin | Plugin called |
| CR-005 | test_timeframe_to_plugin_v3 | V3 timeframe mapping | Correct plugin ID |
| CR-006 | test_timeframe_to_plugin_v6 | V6 timeframe mapping | Correct plugin ID |
| CR-007 | test_no_hardcoded_logic | Core has no trading logic | No direct order calls |

---

## PART 3: INTEGRATION TESTS

### 3.1 V3 Signal End-to-End Test

**Test ID:** INT-V3-001  
**Description:** Complete V3 entry signal flow

**Test Steps:**
1. Create mock V3 entry alert
2. Send to process_alert()
3. Verify plugin is called
4. Verify ServiceAPI methods called
5. Verify order placed (mock MT5)
6. Verify database record created
7. Verify Telegram notification sent

**Input:**
```json
{
  "type": "entry_v3",
  "symbol": "XAUUSD",
  "tf": "15",
  "direction": "buy",
  "signal_type": "Institutional_Launchpad",
  "consensus_score": 7,
  "position_multiplier": 1.5,
  "entry_price": 2650.50,
  "sl_price": 2640.00,
  "tp1_price": 2665.00,
  "tp2_price": 2680.00,
  "mtf_trends": "1,1,1,1,1,1"
}
```

**Expected Output:**
```json
{
  "status": "success",
  "plugin_id": "v3-logic-02-15min",
  "orders": [
    {"ticket": 12345, "type": "ORDER_A"},
    {"ticket": 12346, "type": "ORDER_B"}
  ]
}
```

**Evidence Required:**
- [ ] Log showing "Routing to Plugin"
- [ ] Log showing plugin process_entry_signal called
- [ ] Mock MT5 place_order called twice
- [ ] Database trade record with plugin_id
- [ ] Telegram notification mock called

### 3.2 V6 Signal End-to-End Test

**Test ID:** INT-V6-001  
**Description:** Complete V6 entry signal flow

**Test Steps:**
1. Create mock V6 entry alert
2. Send to process_alert()
3. Verify plugin is called
4. Verify Trend Pulse check
5. Verify ADX filter
6. Verify spread filter
7. Verify order placed
8. Verify database record
9. Verify notification

**Input:**
```json
{
  "type": "entry_v6",
  "symbol": "XAUUSD",
  "tf": "5",
  "direction": "sell",
  "signal_type": "MOMENTUM_ENTRY",
  "order_type": "DUAL",
  "entry_price": 2650.50,
  "sl_price": 2655.00,
  "tp1_price": 2645.00,
  "tp2_price": 2640.00,
  "adx_value": 30,
  "spread_pips": 1.2,
  "trend_pulse": {
    "bull_count": 1,
    "bear_count": 4,
    "market_state": "TRENDING_BEARISH"
  }
}
```

**Expected Output:**
```json
{
  "status": "success",
  "plugin_id": "v6-logic-02-5min",
  "orders": [
    {"ticket": 12347, "type": "ORDER_A"},
    {"ticket": 12348, "type": "ORDER_B"}
  ]
}
```

### 3.3 Plugin Fallback Test

**Test ID:** INT-FALLBACK-001  
**Description:** Verify fallback when plugin not found

**Test Steps:**
1. Send alert with invalid plugin_id
2. Verify fallback plugin used
3. Verify trade still executes

**Expected:** Fallback plugin processes signal

### 3.4 Plugin Disabled Test

**Test ID:** INT-DISABLED-001  
**Description:** Verify disabled plugin is skipped

**Test Steps:**
1. Disable a plugin
2. Send alert for that plugin
3. Verify signal is skipped
4. Verify appropriate response

**Expected:** Returns `{"skipped": true, "reason": "plugin_disabled"}`

---

## PART 4: MANUAL TESTS

### 4.1 Manual Test: Real V3 Alert

**Test ID:** MAN-V3-001  
**Description:** Send real V3 alert via webhook

**Prerequisites:**
- Bot running in shadow mode
- MT5 connected (demo account)
- Telegram bot active

**Test Steps:**
1. Send V3 entry alert to webhook endpoint
2. Observe bot logs
3. Check MT5 for orders
4. Check Telegram for notification
5. Check database for trade record

**Evidence Required:**
- [ ] Screenshot of webhook response
- [ ] Screenshot of bot logs showing plugin routing
- [ ] Screenshot of MT5 orders (or shadow mode log)
- [ ] Screenshot of Telegram notification
- [ ] Database query showing trade with plugin_id

### 4.2 Manual Test: Real V6 Alert

**Test ID:** MAN-V6-001  
**Description:** Send real V6 alert via webhook

**Prerequisites:**
- Bot running in shadow mode
- MT5 connected (demo account)
- Telegram bot active

**Test Steps:**
1. Send V6 entry alert to webhook endpoint
2. Observe bot logs
3. Check MT5 for orders
4. Check Telegram for notification
5. Check database for trade record

**Evidence Required:**
- [ ] Screenshot of webhook response
- [ ] Screenshot of bot logs showing plugin routing
- [ ] Screenshot of MT5 orders (or shadow mode log)
- [ ] Screenshot of Telegram notification
- [ ] Database query showing trade with plugin_id

### 4.3 Manual Test: Plugin Enable/Disable

**Test ID:** MAN-TOGGLE-001  
**Description:** Test plugin enable/disable via Telegram

**Test Steps:**
1. Send /disable v3-logic-02-15min command
2. Verify plugin disabled
3. Send V3 15min alert
4. Verify alert is skipped
5. Send /enable v3-logic-02-15min command
6. Verify plugin enabled
7. Send V3 15min alert
8. Verify alert is processed

**Evidence Required:**
- [ ] Screenshot of disable command response
- [ ] Screenshot of skipped alert log
- [ ] Screenshot of enable command response
- [ ] Screenshot of processed alert log

---

## PART 5: DATABASE VERIFICATION

### 5.1 Plugin ID Tracking Test

**Test ID:** DB-001  
**Description:** Verify trades have correct plugin_id

**SQL Query:**
```sql
SELECT plugin_id, COUNT(*) as count, SUM(pnl) as total_pnl
FROM trades
WHERE status = 'closed'
GROUP BY plugin_id
ORDER BY count DESC;
```

**Expected:** Each plugin_id has separate statistics

### 5.2 Migration Verification Test

**Test ID:** DB-002  
**Description:** Verify existing trades migrated correctly

**SQL Query:**
```sql
SELECT logic_type, plugin_id, COUNT(*) as count
FROM trades
GROUP BY logic_type, plugin_id;
```

**Expected:**
- combinedlogic-1 -> v3-logic-01-5min
- combinedlogic-2 -> v3-logic-02-15min
- combinedlogic-3 -> v3-logic-03-1h

---

## PART 6: TELEGRAM NOTIFICATION VERIFICATION

### 6.1 V3 Notification Format Test

**Test ID:** TG-V3-001  
**Description:** Verify V3 notification format

**Expected Format:**
```
🎯 V3 DUAL ORDER PLACED
Plugin: v3-logic-02-15min
Signal: Institutional_Launchpad
Symbol: XAUUSD
Direction: BUY
Entry: 2650.50
Order A SL: 2640.00 | TP: 2680.00
Order B SL: 2645.00 | TP: 2665.00
```

### 6.2 V6 Notification Format Test

**Test ID:** TG-V6-001  
**Description:** Verify V6 notification format

**Expected Format:**
```
🎯 V6 ORDER PLACED
Plugin: v6-logic-02-5min
Signal: MOMENTUM_ENTRY
Symbol: XAUUSD
Direction: SELL
Order Type: DUAL
Entry: 2650.50
SL: 2655.00
TP1: 2645.00 | TP2: 2640.00
Trend Pulse: 1B/4S (BEARISH)
ADX: 30
```

---

## PART 7: REGRESSION TESTS

### 7.1 Legacy Alert Handling

**Test ID:** REG-001  
**Description:** Verify legacy alerts still work

**Test Steps:**
1. Send legacy 'bias' alert
2. Send legacy 'trend' alert
3. Send legacy 'entry' alert
4. Verify all handled correctly

**Expected:** Legacy alerts processed without errors

### 7.2 Backward Compatibility

**Test ID:** REG-002  
**Description:** Verify old code paths still work

**Test Steps:**
1. Verify ServiceAPI backward compatible methods work
2. Verify database backward compatible queries work
3. Verify Telegram backward compatible commands work

**Expected:** All backward compatible features work

---

## PART 8: TEST EXECUTION ORDER

| Order | Test Category | Tests | Duration |
|-------|---------------|-------|----------|
| 1 | Unit Tests - Plugin System | PS-001 to PS-008 | 30 min |
| 2 | Unit Tests - V3 Plugin | V3-001 to V3-008 | 30 min |
| 3 | Unit Tests - V6 Plugin | V6-001 to V6-008 | 30 min |
| 4 | Unit Tests - Core Routing | CR-001 to CR-007 | 30 min |
| 5 | Integration Tests | INT-V3-001, INT-V6-001, etc. | 1 hour |
| 6 | Database Verification | DB-001, DB-002 | 15 min |
| 7 | Manual Tests | MAN-V3-001, MAN-V6-001, etc. | 1 hour |
| 8 | Telegram Verification | TG-V3-001, TG-V6-001 | 15 min |
| 9 | Regression Tests | REG-001, REG-002 | 30 min |

**Total Estimated Time:** 4-6 hours

---

## PART 9: TEST EVIDENCE TEMPLATE

### 9.1 Test Report Format

```markdown
# Test Report: [TEST_ID]

**Date:** YYYY-MM-DD HH:MM:SS
**Tester:** Devin AI
**Status:** PASS / FAIL

## Input
[Input data or command]

## Expected Output
[What was expected]

## Actual Output
[What actually happened]

## Logs
```
[Relevant log entries]
```

## Database Records
```sql
[SQL query and results]
```

## Screenshots
[Attached screenshots]

## Verdict
[PASS/FAIL with explanation]
```

---

## PART 10: VERIFICATION CHECKLIST

### 10.1 Pre-Implementation Checklist

- [ ] All unit test files created
- [ ] All integration test files created
- [ ] Test data fixtures created
- [ ] Mock objects configured

### 10.2 Post-Implementation Checklist

- [ ] All unit tests pass (100%)
- [ ] All integration tests pass (100%)
- [ ] Manual V3 test completed with evidence
- [ ] Manual V6 test completed with evidence
- [ ] Database migration verified
- [ ] Telegram notifications verified
- [ ] Regression tests pass (100%)

---

## SUCCESS CRITERIA

1. **100% unit test pass rate**
2. **100% integration test pass rate**
3. **Manual tests completed with screenshots**
4. **Database records show correct plugin_id**
5. **Telegram notifications show new format**
6. **No regression in legacy functionality**
7. **All evidence documented and attached**
