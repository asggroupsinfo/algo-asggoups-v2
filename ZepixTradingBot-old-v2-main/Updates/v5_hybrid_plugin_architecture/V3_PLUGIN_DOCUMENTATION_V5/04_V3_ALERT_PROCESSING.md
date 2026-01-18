# V3 Alert Processing Flow

**Document Version**: 1.0.0  
**Last Updated**: 2026-01-18  
**Pine Script Source**: `ZEPIX_ULTIMATE_BOT_v3.0_FINAL.pine` (1934 lines)

---

## Alert Flow Overview

```
TradingView Pine Script
        │
        ▼
   JSON Alert Payload
        │
        ▼
   Webhook Endpoint
        │
        ▼
   Alert Processor
        │
        ▼
   Plugin Router
        │
        ▼
   V3 Combined Plugin
        │
        ├──► Entry Signal Handler
        │         │
        │         ▼
        │    Signal Validation
        │         │
        │         ▼
        │    Logic Routing
        │         │
        │         ▼
        │    Dual Order Creation
        │
        ├──► Exit Signal Handler
        │         │
        │         ▼
        │    Position Close
        │
        └──► Info Signal Handler
                  │
                  ▼
             Notification Only
```

---

## 1. Pine Script Alert Generation

### 1.1 Consolidated Alert Trigger (Lines 1820-1836)

```pine
// Single consolidated alert condition - triggers for ANY signal
bool anySignalActive = signal1_InstitutionalLaunchpad or signal1_InstitutionalLaunchpadBear or 
                       signal2_LiquidityTrapBull or signal2_LiquidityTrapBear or 
                       signal3_MomentumBreakoutBull or signal3_MomentumBreakoutBear or 
                       signal4_MitigationTestBull or signal4_MitigationTestBear or 
                       signal5_BullishExit or signal6_BearishExit or 
                       signal7_GoldenPocketFlipBull or signal7_GoldenPocketFlipBear or 
                       signal8_VolatilitySqueeze or 
                       signal9_ScreenerFullBullish or signal10_ScreenerFullBearish or 
                       trendPulseTriggered or
                       signal12_SidewaysBreakoutBull or signal12_SidewaysBreakoutBear

// *** MAIN CONSOLIDATED ALERT - USE THIS ONE! ***
if anySignalActive
    alert(activeMessage, alert.freq_once_per_bar_close)
```

### 1.2 Alert Message Construction (Lines 1505-1800)

Each signal type constructs its own JSON payload with specific fields:

**Entry Signal Payload**:
```json
{
  "type": "entry_v3",
  "signal_type": "Institutional_Launchpad",
  "symbol": "{{ticker}}",
  "direction": "buy",
  "tf": "15",
  "price": {{close}},
  "consensus_score": 7,
  "sl_price": 1.08200,
  "tp1_price": 1.08800,
  "tp2_price": 1.09100,
  "mtf_trends": "1,1,1,1,1,1",
  "market_trend": 1,
  "volume_delta_ratio": 1.25,
  "price_in_ob": true,
  "full_alignment": true,
  "position_multiplier": 0.8
}
```

**Exit Signal Payload**:
```json
{
  "type": "exit_v3",
  "signal_type": "Bullish_Exit",
  "symbol": "{{ticker}}",
  "direction": "close_long",
  "tf": "15",
  "price": {{close}},
  "consensus_score": 3,
  "previous_score": 7
}
```

**Trend Pulse Payload**:
```json
{
  "type": "trend_pulse_v3",
  "signal_type": "Trend_Pulse",
  "symbol": "{{ticker}}",
  "tf": "15",
  "price": {{close}},
  "current_trends": "1,1,1,1,1,1",
  "previous_trends": "1,1,1,-1,-1,-1",
  "changed_timeframes": "1H,4H,1D",
  "change_details": "1H: BEAR→BULL, 4H: BEAR→BULL, 1D: BEAR→BULL",
  "trend_labels": "1m,5m,15m,1H,4H,1D",
  "market_trend": 1,
  "consensus_score": 7,
  "message": "Trend change detected on: 1H,4H,1D"
}
```

---

## 2. Webhook Reception

### 2.1 Webhook Endpoint

```python
# src/webhook/webhook_handler.py
@app.post("/webhook/tradingview")
async def receive_tradingview_alert(request: Request):
    """Receive and process TradingView webhook alerts."""
    try:
        payload = await request.json()
        
        # Validate payload
        if not payload.get('type'):
            return {"status": "error", "message": "Missing type field"}
        
        # Route to alert processor
        result = await alert_processor.process_alert(payload)
        
        return {"status": "success", "result": result}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}
```

### 2.2 Alert Validation

```python
# src/processors/alert_processor.py
def validate_v3_alert(self, payload: Dict[str, Any]) -> bool:
    """Validate V3 alert payload."""
    required_fields = ['type', 'signal_type', 'symbol', 'tf', 'price']
    
    for field in required_fields:
        if field not in payload:
            self.logger.warning(f"Missing required field: {field}")
            return False
    
    # Validate type
    valid_types = ['entry_v3', 'exit_v3', 'trend_pulse_v3']
    if payload['type'] not in valid_types:
        self.logger.warning(f"Invalid type: {payload['type']}")
        return False
    
    return True
```

---

## 3. Plugin Router

### 3.1 Route to V3 Plugin

```python
# src/core/plugin_router.py
async def route_alert(self, alert: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Route alert to appropriate plugin."""
    alert_type = alert.get('type', '')
    
    # V3 alerts
    if alert_type in ['entry_v3', 'exit_v3', 'trend_pulse_v3']:
        plugin = self.registry.get_plugin('v3_combined')
        if plugin and await plugin.can_process_signal(alert):
            return await plugin.process_signal(alert)
    
    # V6 alerts
    elif alert_type in ['entry_v6', 'exit_v6']:
        # Route to appropriate V6 plugin based on timeframe
        tf = alert.get('tf', '')
        plugin_id = self._get_v6_plugin_for_timeframe(tf)
        plugin = self.registry.get_plugin(plugin_id)
        if plugin and await plugin.can_process_signal(alert):
            return await plugin.process_signal(alert)
    
    return None
```

---

## 4. V3 Plugin Signal Processing

### 4.1 Entry Signal Processing

```python
# src/logic_plugins/v3_combined/plugin.py
async def process_entry_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
    """Process V3 entry signal."""
    # Parse alert
    alert = self._extract_alert_data(signal)
    
    # Validate consensus score
    if not self._validate_score_thresholds(alert):
        return {"status": "rejected", "reason": "score_threshold"}
    
    # Check if aggressive reversal signal
    if self._is_aggressive_reversal_signal(alert.signal_type):
        return await self._handle_aggressive_reversal(alert)
    
    # Route to logic
    logic = self._route_to_logic(alert)
    
    # Shadow mode check
    if self.shadow_mode:
        return await self._process_shadow_entry(alert)
    
    # Calculate lot size
    base_lot = self._get_base_lot(logic)
    smart_lot = self.get_smart_lot_size(base_lot)
    
    # Create dual orders
    result = await self.create_dual_orders({
        'symbol': alert.symbol,
        'direction': alert.direction,
        'logic': logic,
        'price': alert.price,
        'sl_price': alert.sl_price,
        'tp1_price': alert.tp1_price,
        'tp2_price': alert.tp2_price,
        'signal_type': alert.signal_type
    })
    
    # Send notification
    await self._send_notification('trade_opened', {
        'symbol': alert.symbol,
        'direction': alert.direction,
        'signal_type': alert.signal_type,
        'order_a_id': result.order_a_id,
        'order_b_id': result.order_b_id
    })
    
    return {
        'status': 'executed',
        'logic': logic,
        'order_a_id': result.order_a_id,
        'order_b_id': result.order_b_id
    }
```

### 4.2 Exit Signal Processing

```python
async def process_exit_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
    """Process V3 exit signal."""
    alert = self._extract_alert_data(signal)
    
    # Shadow mode check
    if self.shadow_mode:
        return await self._process_shadow_exit(alert)
    
    # Determine close direction
    close_direction = "SELL" if "Bullish" in alert.signal_type else "BUY"
    
    # Close positions via service API
    result = await self.service_api.close_positions_by_direction(
        plugin_id=self.plugin_id,
        symbol=alert.symbol,
        direction=close_direction
    )
    
    # Send notification
    await self._send_notification('trade_closed', {
        'symbol': alert.symbol,
        'signal_type': alert.signal_type,
        'closed_positions': result
    })
    
    return {
        'status': 'executed',
        'action': 'exit',
        'closed_positions': result
    }
```

### 4.3 Trend Pulse Processing

```python
async def process_trend_pulse(self, signal: Dict[str, Any]) -> Dict[str, Any]:
    """Process V3 trend pulse signal."""
    alert = self._extract_alert_data(signal)
    
    # Update MTF tracking
    current_trends = alert.current_trends.split(',')
    previous_trends = alert.previous_trends.split(',')
    changed_tfs = alert.changed_timeframes.split(',')
    
    # Log trend changes
    self.logger.info(
        f"[Trend Pulse] {alert.symbol} | "
        f"Changed: {changed_tfs} | "
        f"Details: {alert.change_details}"
    )
    
    # Send notification
    await self._send_notification('trend_pulse', {
        'symbol': alert.symbol,
        'changed_timeframes': changed_tfs,
        'change_details': alert.change_details,
        'current_trends': current_trends
    })
    
    return {
        'status': 'info',
        'action': 'trend_pulse',
        'changed_timeframes': changed_tfs
    }
```

---

## 5. Signal Validation

### 5.1 Consensus Score Validation

```python
def _validate_score_thresholds(self, alert) -> bool:
    """Validate consensus score against thresholds."""
    score = alert.consensus_score
    direction = alert.direction
    
    # Bullish signals need score >= 5
    if direction == 'buy' and score < 5:
        self.logger.info(f"Bullish signal rejected: score {score} < 5")
        return False
    
    # Bearish signals need score <= 4
    if direction == 'sell' and score > 4:
        self.logger.info(f"Bearish signal rejected: score {score} > 4")
        return False
    
    return True
```

### 5.2 MTF Alignment Validation

```python
def _check_v3_trend_alignment(self, alert) -> bool:
    """Check MTF trend alignment for V3 signals."""
    # V3 entries bypass trend check by default
    if alert.type == 'entry_v3':
        if self.plugin_config.get('bypass_trend_check_for_v3_entries', True):
            self.logger.info("V3 entry - bypassing trend check")
            return True
    
    # Parse MTF trends (indices 2-5 only: 15m, 1H, 4H, 1D)
    trends = [int(t) for t in alert.mtf_trends.split(',')]
    if len(trends) >= 6:
        pillars = trends[2:6]  # 15m, 1H, 4H, 1D
        
        # Count aligned timeframes
        expected_trend = 1 if alert.direction == 'buy' else -1
        aligned = sum(1 for t in pillars if t == expected_trend)
        
        if aligned >= 3:
            return True
        else:
            self.logger.info(f"MTF alignment weak: {aligned}/4 aligned")
            return False
    
    return True
```

---

## 6. Signal-to-Logic Routing

### 6.1 Routing Matrix

| Signal Type | 5m | 15m | 1H | 4H |
|-------------|----|----|----|----|
| Institutional Launchpad | LOGIC1 | LOGIC2 | LOGIC3 | LOGIC3 |
| Liquidity Trap | LOGIC1 | LOGIC2 | LOGIC3 | LOGIC3 |
| Momentum Breakout | LOGIC1 | LOGIC2 | LOGIC3 | LOGIC3 |
| Mitigation Test | LOGIC1 | LOGIC2 | LOGIC3 | LOGIC3 |
| Golden Pocket Flip | LOGIC1 | LOGIC2 | **LOGIC3** | **LOGIC3** |
| Screener Full | **LOGIC3** | **LOGIC3** | **LOGIC3** | **LOGIC3** |
| Sideways Breakout | LOGIC1 | LOGIC2 | LOGIC3 | LOGIC3 |

### 6.2 Routing Implementation

```python
def _route_to_logic(self, alert) -> str:
    """Route signal to appropriate logic based on type and timeframe."""
    # PRIORITY 1: Signal type overrides
    if alert.signal_type in ["Screener_Full_Bullish", "Screener_Full_Bearish"]:
        return "LOGIC3"  # Always swing
    
    if alert.signal_type == "Golden_Pocket_Flip" and alert.tf in ["60", "240"]:
        return "LOGIC3"
    
    # PRIORITY 2: Timeframe routing
    if alert.tf == "5":
        return "LOGIC1"  # Scalping
    elif alert.tf == "15":
        return "LOGIC2"  # Intraday (Default)
    elif alert.tf in ["60", "240"]:
        return "LOGIC3"  # Swing
    
    return "LOGIC2"  # DEFAULT
```

---

## 7. Dual Order Creation

### 7.1 Order Flow

```
Signal Validated
      │
      ▼
Calculate Lot Size
      │
      ├──► Base Lot (from Logic)
      │         │
      │         ▼
      │    × V3 Position Multiplier
      │         │
      │         ▼
      │    × Logic Multiplier
      │         │
      │         ▼
      │    = Final Lot Size
      │
      ▼
Split 50/50
      │
      ├──► Order A (50%)
      │         │
      │         ▼
      │    V3 Smart SL
      │    2:1 RR TP
      │    Trailing Enabled
      │
      └──► Order B (50%)
                │
                ▼
           Fixed $10 Risk SL
           No TP (Profit Booking)
           Creates Profit Chain
```

### 7.2 Lot Size Calculation

```python
def get_smart_lot_size(self, base_lot: float) -> float:
    """Calculate smart lot size with V3 multiplier."""
    # Get V3 position multiplier from alert
    v3_multiplier = self.current_alert.position_multiplier
    
    # Get logic multiplier
    logic = self._route_to_logic(self.current_alert)
    logic_multiplier = self._get_logic_multiplier(logic)
    
    # Calculate final lot
    final_lot = base_lot * v3_multiplier * logic_multiplier
    
    # Apply limits
    final_lot = max(0.01, min(final_lot, 1.0))
    
    return round(final_lot, 2)
```

---

## 8. Error Handling

### 8.1 Alert Processing Errors

```python
async def process_signal(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Process signal with error handling."""
    try:
        alert_type = signal.get('type', '')
        
        if alert_type == 'entry_v3':
            return await self.process_entry_signal(signal)
        elif alert_type == 'exit_v3':
            return await self.process_exit_signal(signal)
        elif alert_type == 'trend_pulse_v3':
            return await self.process_trend_pulse(signal)
        
        return None
        
    except ValidationError as e:
        self.logger.warning(f"Validation error: {e}")
        return {"status": "error", "reason": "validation", "message": str(e)}
        
    except OrderExecutionError as e:
        self.logger.error(f"Order execution error: {e}")
        return {"status": "error", "reason": "execution", "message": str(e)}
        
    except Exception as e:
        self.logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "reason": "unknown", "message": str(e)}
```

---

## 9. Logging & Monitoring

### 9.1 Alert Processing Logs

```
[INFO] V3 Alert received: entry_v3 | Institutional_Launchpad | EURUSD | buy
[INFO] Consensus score: 7 (threshold: 5) - PASS
[INFO] MTF alignment: 4/4 pillars aligned - PASS
[INFO] Routing to LOGIC2 (15m timeframe)
[INFO] Lot calculation: Base=0.10 × V3=0.8 × Logic=1.0 = 0.08
[INFO] Creating dual orders: A=0.04, B=0.04
[INFO] Order A created: #12345 | SL=1.08200 | TP=1.08800
[INFO] Order B created: #12346 | SL=1.08150 | Chain=CHAIN_001
[INFO] Trade notification sent to Telegram
```

---

## 10. Alert Field Reference

### 10.1 Entry Alert Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | string | Yes | "entry_v3" |
| signal_type | string | Yes | Signal name |
| symbol | string | Yes | Trading symbol |
| direction | string | Yes | "buy" or "sell" |
| tf | string | Yes | Timeframe |
| price | float | Yes | Entry price |
| consensus_score | int | Yes | 0-9 |
| sl_price | float | Yes | Stop loss price |
| tp1_price | float | Yes | Take profit 1 |
| tp2_price | float | Yes | Take profit 2 |
| mtf_trends | string | Yes | "1,1,1,1,1,1" |
| market_trend | int | Yes | 1, 0, or -1 |
| volume_delta_ratio | float | No | Buy/Sell volume ratio |
| price_in_ob | bool | No | Price in Order Block |
| full_alignment | bool | No | All TFs aligned |
| position_multiplier | float | Yes | 0.2-1.0 |

### 10.2 Exit Alert Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | string | Yes | "exit_v3" |
| signal_type | string | Yes | "Bullish_Exit" or "Bearish_Exit" |
| symbol | string | Yes | Trading symbol |
| direction | string | Yes | "close_long" or "close_short" |
| tf | string | Yes | Timeframe |
| price | float | Yes | Exit price |
| consensus_score | int | Yes | Current score |
| previous_score | int | No | Previous score |

### 10.3 Trend Pulse Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | string | Yes | "trend_pulse_v3" |
| signal_type | string | Yes | "Trend_Pulse" |
| symbol | string | Yes | Trading symbol |
| tf | string | Yes | Timeframe |
| price | float | Yes | Current price |
| current_trends | string | Yes | "1,1,1,1,1,1" |
| previous_trends | string | Yes | "1,1,1,-1,-1,-1" |
| changed_timeframes | string | Yes | "1H,4H,1D" |
| change_details | string | Yes | "1H: BEAR→BULL, ..." |
| trend_labels | string | Yes | "1m,5m,15m,1H,4H,1D" |
| market_trend | int | Yes | 1, 0, or -1 |
| consensus_score | int | Yes | 0-9 |
| message | string | No | Human-readable message |

---

**Document Status**: COMPLETE  
**Alert Flow Coverage**: 100%  
**V5 Architecture Compliance**: VERIFIED
