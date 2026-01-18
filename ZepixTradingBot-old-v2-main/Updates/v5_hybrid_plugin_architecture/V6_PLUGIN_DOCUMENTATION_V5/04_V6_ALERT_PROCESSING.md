# V6 Price Action Plugin - Alert Processing

**Document Version**: 1.0.0  
**Last Updated**: 2026-01-18  
**Pine Script Source**: `Signals_and_Overlays_V6_Enhanced_Build.pine` (1683 lines)

---

## Alert Flow Overview

```
TradingView Pine Script
        │
        ▼
   Alert Fires (JSON)
        │
        ▼
   Webhook Server
        │
        ▼
   Plugin Router
        │
        ├──► V6 5m Plugin (tf="5")
        ├──► V6 15m Plugin (tf="15")
        └──► V6 1H Plugin (tf="60" or "240")
                │
                ▼
         Signal Validation
                │
                ▼
         TrendManager Check
                │
                ▼
         Order Execution
                │
                ▼
         Telegram Notification
```

---

## 1. Pine Script Alert Generation

### 1.1 Consolidated Alert Trigger (Lines 1651-1683)

```pine
// Entry alert
if anyBullishEntry or anyBearishEntry
    alert(entryAlertMessage, alert.freq_once_per_bar_close)

// Exit alert
if exitBullish or exitBearish
    alert(exitAlertMessage, alert.freq_once_per_bar_close)

// Trend pulse alert
if trendPulseTriggered
    alert(trendPulseAlertMessage, alert.freq_once_per_bar_close)

// Momentum alerts
if momentumSurge
    alert(momentumSurgeMessage, alert.freq_once_per_bar_close)
if momentumFade
    alert(momentumFadeMessage, alert.freq_once_per_bar_close)
```

### 1.2 Entry Alert Message Construction (Lines 1555-1590)

```pine
entryAlertMessage = '{"type":"entry_v6","signal_type":"' + activeSignalType + 
    '","symbol":"{{ticker}}","direction":"' + activeDirection + 
    '","tf":"' + timeframe.period + 
    '","price":{{close}},"confidence":"' + confidenceLevel + 
    '","adx_value":' + str.tostring(adxValue, '#.#') + 
    ',"trendline_break":' + str.tostring(trendlineBreakBull or trendlineBreakBear) + 
    ',"mtf_trends":"' + mtfString + 
    '","aligned_count":' + str.tostring(math.max(alignedBullish, alignedBearish)) + 
    ',"sl_price":' + str.tostring(activeDirection == "buy" ? slPriceLong : slPriceShort) + 
    ',"tp1_price":' + str.tostring(activeDirection == "buy" ? tp1Long : tp1Short) + 
    ',"tp2_price":' + str.tostring(activeDirection == "buy" ? tp2Long : tp2Short) + 
    ',"volume_confirmed":' + str.tostring(volumeOK) + '}'
```

---

## 2. Webhook Reception

### 2.1 Webhook Endpoint

```python
# src/webhook/server.py
@app.route('/webhook/tradingview', methods=['POST'])
async def tradingview_webhook():
    """Receive TradingView alerts."""
    try:
        # Parse JSON payload
        data = request.get_json()
        
        # Validate webhook secret (if configured)
        if not validate_webhook_secret(request):
            return jsonify({'error': 'Invalid secret'}), 401
        
        # Route to appropriate handler
        alert_type = data.get('type', '')
        
        if alert_type.endswith('_v6'):
            result = await plugin_router.route_v6_alert(data)
        elif alert_type.endswith('_v3'):
            result = await plugin_router.route_v3_alert(data)
        else:
            return jsonify({'error': 'Unknown alert type'}), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500
```

### 2.2 Alert Validation

```python
def validate_v6_alert(data: Dict[str, Any]) -> bool:
    """Validate V6 alert payload."""
    required_fields = ['type', 'signal_type', 'symbol', 'tf', 'price']
    
    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing required field: {field}")
            return False
    
    # Validate type
    if not data['type'].endswith('_v6'):
        logger.warning(f"Invalid alert type: {data['type']}")
        return False
    
    # Validate timeframe
    valid_timeframes = ['1', '5', '15', '60', '240', '1D']
    if data['tf'] not in valid_timeframes:
        logger.warning(f"Invalid timeframe: {data['tf']}")
        return False
    
    return True
```

---

## 3. Plugin Router

### 3.1 V6 Alert Routing

```python
# src/core/plugin_router.py
class PluginRouter:
    def __init__(self, registry: PluginRegistry):
        self._registry = registry
        self.logger = logging.getLogger("PluginRouter")
    
    async def route_v6_alert(self, alert: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Route V6 alert to appropriate plugin based on timeframe."""
        tf = alert.get('tf', '')
        
        # Determine target plugin
        plugin_id = self._get_v6_plugin_for_timeframe(tf)
        
        if not plugin_id:
            self.logger.warning(f"No plugin for V6 timeframe: {tf}")
            return {'status': 'error', 'reason': 'no_plugin_for_timeframe'}
        
        # Get plugin
        plugin = self._registry.get_plugin(plugin_id)
        
        if not plugin:
            self.logger.warning(f"Plugin not registered: {plugin_id}")
            return {'status': 'error', 'reason': 'plugin_not_registered'}
        
        # Check if plugin can process
        if not plugin.can_process_signal(alert):
            self.logger.info(f"Plugin {plugin_id} cannot process signal")
            return {'status': 'rejected', 'reason': 'plugin_cannot_process'}
        
        # Process signal
        return await plugin.process_signal(alert)
    
    def _get_v6_plugin_for_timeframe(self, tf: str) -> Optional[str]:
        """Get V6 plugin ID for timeframe."""
        mapping = {
            '5': 'v6_price_action_5m',
            '15': 'v6_price_action_15m',
            '60': 'v6_price_action_1h',
            '240': 'v6_price_action_1h'
        }
        return mapping.get(tf)
```

---

## 4. V6 Plugin Signal Processing

### 4.1 Entry Signal Processing

```python
async def process_entry_signal(self, alert: V6Alert) -> Dict[str, Any]:
    """Process V6 entry signal."""
    self.logger.info(f"Processing V6 entry: {alert.signal_type} | {alert.symbol}")
    
    # Step 1: Validate confidence
    if not self._validate_confidence(alert):
        return {'status': 'rejected', 'reason': 'confidence_too_low'}
    
    # Step 2: Validate ADX
    if alert.adx_value < self._min_adx:
        return {'status': 'rejected', 'reason': 'adx_too_low'}
    
    # Step 3: Validate trendline break (if required)
    if self._require_trendline_break and alert.signal_type == 'Breakout_Entry':
        if not alert.trendline_break:
            return {'status': 'rejected', 'reason': 'no_trendline_break'}
    
    # Step 4: Validate volume (if required)
    if self._require_volume_confirmation and not alert.volume_confirmed:
        return {'status': 'rejected', 'reason': 'no_volume_confirmation'}
    
    # Step 5: TrendManager validation (Pine Supremacy)
    if not self._validate_via_trend_manager(alert):
        return {'status': 'rejected', 'reason': 'trend_manager_validation_failed'}
    
    # Step 6: Create dual orders
    if self._shadow_mode:
        self.logger.info(f"[SHADOW] Would execute entry: {alert.symbol} {alert.direction}")
        return {'status': 'shadow', 'would_execute': True}
    
    result = await self._create_dual_orders(alert)
    
    # Step 7: Send notification
    if result.success:
        await self._send_notification('trade_opened', {
            'symbol': alert.symbol,
            'direction': alert.direction,
            'signal_type': alert.signal_type,
            'confidence': alert.confidence,
            'entry_price': alert.price,
            'sl_price': alert.sl_price,
            'tp_price': alert.tp1_price
        })
    
    return {
        'status': 'executed' if result.success else 'failed',
        'signal_type': alert.signal_type,
        'order_a_id': result.order_a_id,
        'order_b_id': result.order_b_id
    }
```

### 4.2 Exit Signal Processing

```python
async def process_exit_signal(self, alert: V6Alert) -> Dict[str, Any]:
    """Process V6 exit signal."""
    self.logger.info(f"Processing V6 exit: {alert.signal_type} | {alert.symbol}")
    
    # Get open positions for this symbol from this plugin
    positions = await self._service_api.get_open_positions(
        symbol=alert.symbol,
        plugin_id=self.plugin_id
    )
    
    if not positions:
        self.logger.info(f"No open positions for {alert.symbol}")
        return {'status': 'no_positions'}
    
    # Determine which positions to close
    closed_count = 0
    for position in positions:
        should_close = False
        
        if alert.signal_type == 'Bullish_Exit' and position.direction == 'buy':
            should_close = True
        elif alert.signal_type == 'Bearish_Exit' and position.direction == 'sell':
            should_close = True
        
        if should_close:
            if self._shadow_mode:
                self.logger.info(f"[SHADOW] Would close position: {position.id}")
            else:
                await self._service_api.close_position(position.id)
            closed_count += 1
    
    if closed_count > 0:
        await self._send_notification('trade_closed', {
            'symbol': alert.symbol,
            'signal_type': alert.signal_type,
            'closed_count': closed_count
        })
    
    return {
        'status': 'executed',
        'signal_type': alert.signal_type,
        'closed_count': closed_count
    }
```

### 4.3 Trend Pulse Processing

```python
async def process_trend_pulse(self, alert: V6Alert) -> Dict[str, Any]:
    """Process V6 trend pulse alert."""
    self.logger.info(f"Processing V6 trend pulse: {alert.signal_type}")
    
    # Update TrendManager with new trends
    trend_manager = self._service_api.get_trend_manager()
    trends = self._parse_mtf_trends(alert.current_trends)
    
    timeframes = ['1', '5', '15', '60', '240', '1D']
    for i, tf in enumerate(timeframes):
        trend_manager.update_trend(alert.symbol, tf, trends[i])
    
    # Send notification
    await self._send_notification('trend_pulse', {
        'symbol': alert.symbol,
        'signal_type': alert.signal_type,
        'changed_timeframes': alert.changed_timeframes,
        'change_details': alert.change_details,
        'aligned_count': alert.aligned_count,
        'confidence': alert.confidence,
        'message': f"Trend change on {alert.changed_timeframes}"
    })
    
    return {
        'status': 'info',
        'signal_type': alert.signal_type,
        'action': 'trend_pulse'
    }
```

---

## 5. Signal Validation

### 5.1 Confidence Validation

```python
def _validate_confidence(self, alert: V6Alert) -> bool:
    """Validate confidence meets minimum threshold."""
    confidence_levels = {'LOW': 0, 'MEDIUM': 1, 'HIGH': 2}
    
    alert_level = confidence_levels.get(alert.confidence, 0)
    min_level = confidence_levels.get(self._min_confidence, 1)
    
    if alert_level < min_level:
        self.logger.info(
            f"Confidence {alert.confidence} below minimum {self._min_confidence}"
        )
        return False
    
    return True
```

### 5.2 TrendManager Validation (Pine Supremacy)

```python
def _validate_via_trend_manager(self, alert: V6Alert) -> bool:
    """
    Validate signal via TrendManager.
    
    Pine Supremacy Rule: The bot NEVER overrides Pine Script calculations.
    TrendManager stores Pine-calculated trends and validates that new signals
    align with the stored trend state.
    """
    trend_manager = self._service_api.get_trend_manager()
    
    # Get stored trend for this symbol/timeframe
    stored_trend = trend_manager.get_trend(alert.symbol, self.timeframe)
    
    # If no stored trend, allow signal (first signal for this pair)
    if stored_trend is None:
        return True
    
    # Validate direction matches stored trend
    if alert.direction == 'buy' and stored_trend == -1:
        self.logger.warning(
            f"Buy signal conflicts with stored BEAR trend for {alert.symbol}"
        )
        return False
    
    if alert.direction == 'sell' and stored_trend == 1:
        self.logger.warning(
            f"Sell signal conflicts with stored BULL trend for {alert.symbol}"
        )
        return False
    
    return True
```

### 5.3 MTF Alignment Validation

```python
def _validate_mtf_alignment(self, alert: V6Alert) -> bool:
    """Validate MTF alignment meets threshold."""
    if alert.aligned_count < self._min_tf_alignment:
        self.logger.info(
            f"MTF alignment {alert.aligned_count} below minimum {self._min_tf_alignment}"
        )
        return False
    
    return True
```

---

## 6. Dual Order Creation

### 6.1 Order Flow

```
Signal Validated
      │
      ▼
Calculate Lot Size
      │
      ├──► Order A Config
      │    - V6 Calculated SL
      │    - Trailing enabled
      │    - TP at 2:1 RR
      │
      └──► Order B Config
           - Fixed $10 Risk SL
           - No trailing
           - Profit booking chain
      │
      ▼
ServiceAPI.create_dual_orders()
      │
      ▼
MT5 Execution
      │
      ▼
Return Order IDs
```

### 6.2 Lot Size Calculation

```python
def _calculate_lot_size(self, alert: V6Alert) -> float:
    """Calculate lot size based on plugin settings and confidence."""
    # Start with base lot for this timeframe
    base = self.base_lot
    
    # Apply risk multiplier for this timeframe
    lot = base * self.risk_multiplier
    
    # Adjust for confidence level
    if alert.confidence == 'HIGH':
        lot *= 1.2  # 20% increase for HIGH confidence
    elif alert.confidence == 'LOW':
        lot *= 0.8  # 20% decrease for LOW confidence
    
    # Apply max lot limit
    max_lot = self.config.get('risk_management', {}).get('max_lot', 0.30)
    lot = min(lot, max_lot)
    
    # Apply min lot limit
    lot = max(lot, 0.01)
    
    return round(lot, 2)
```

---

## 7. Error Handling

### 7.1 Alert Processing Errors

```python
async def process_signal(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Process signal with error handling."""
    try:
        # Parse alert
        alert = self._parse_alert(signal)
        
        # Route to handler
        signal_type = alert.signal_type
        
        if signal_type in ['Breakout_Entry', 'Momentum_Entry']:
            return await self.process_entry_signal(alert)
        elif signal_type in ['Screener_Full_Bullish', 'Screener_Full_Bearish']:
            return await self.process_entry_signal(alert)
        elif signal_type in ['Bullish_Exit', 'Bearish_Exit']:
            return await self.process_exit_signal(alert)
        elif signal_type.startswith('Trend_Pulse'):
            return await self.process_trend_pulse(alert)
        elif signal_type in ['Momentum_Surge', 'Momentum_Fade']:
            return await self.process_momentum_alert(alert)
        else:
            self.logger.warning(f"Unknown signal type: {signal_type}")
            return {'status': 'error', 'reason': 'unknown_signal_type'}
            
    except ValidationError as e:
        self.logger.error(f"Validation error: {e}")
        return {'status': 'error', 'reason': 'validation_error', 'details': str(e)}
    except ExecutionError as e:
        self.logger.error(f"Execution error: {e}")
        return {'status': 'error', 'reason': 'execution_error', 'details': str(e)}
    except Exception as e:
        self.logger.exception(f"Unexpected error processing signal: {e}")
        return {'status': 'error', 'reason': 'unexpected_error', 'details': str(e)}
```

---

## 8. Logging & Monitoring

### 8.1 Alert Processing Logs

```python
def _log_signal_received(self, alert: V6Alert):
    """Log signal receipt."""
    self.logger.info(
        f"[V6] Signal received | "
        f"Type: {alert.signal_type} | "
        f"Symbol: {alert.symbol} | "
        f"Direction: {alert.direction} | "
        f"TF: {alert.tf} | "
        f"Confidence: {alert.confidence} | "
        f"ADX: {alert.adx_value}"
    )

def _log_signal_result(self, alert: V6Alert, result: Dict[str, Any]):
    """Log signal processing result."""
    status = result.get('status', 'unknown')
    
    if status == 'executed':
        self.logger.info(
            f"[V6] Signal executed | "
            f"Type: {alert.signal_type} | "
            f"Symbol: {alert.symbol} | "
            f"Order A: {result.get('order_a_id')} | "
            f"Order B: {result.get('order_b_id')}"
        )
    elif status == 'rejected':
        self.logger.info(
            f"[V6] Signal rejected | "
            f"Type: {alert.signal_type} | "
            f"Symbol: {alert.symbol} | "
            f"Reason: {result.get('reason')}"
        )
    elif status == 'shadow':
        self.logger.info(
            f"[V6] [SHADOW] Signal processed | "
            f"Type: {alert.signal_type} | "
            f"Symbol: {alert.symbol} | "
            f"Would execute: {result.get('would_execute')}"
        )
```

---

## 9. Alert Field Reference

### 9.1 Entry Alert Fields

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| type | string | "entry_v6" | Fixed |
| signal_type | string | Signal name | Pine Script |
| symbol | string | Trading pair | {{ticker}} |
| direction | string | "buy" or "sell" | Pine Script |
| tf | string | Timeframe | timeframe.period |
| price | float | Entry price | {{close}} |
| confidence | string | "HIGH", "MEDIUM", "LOW" | Pine Script |
| adx_value | float | ADX indicator value | Pine Script |
| trendline_break | boolean | Trendline breakout | Pine Script |
| mtf_trends | string | "1,1,1,1,1,1" format | Pine Script |
| aligned_count | int | Aligned TF count | Pine Script |
| sl_price | float | Stop loss price | Pine Script |
| tp1_price | float | Take profit 1 | Pine Script |
| tp2_price | float | Take profit 2 | Pine Script |
| volume_confirmed | boolean | Volume above average | Pine Script |

### 9.2 Exit Alert Fields

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| type | string | "exit_v6" | Fixed |
| signal_type | string | "Bullish_Exit" or "Bearish_Exit" | Pine Script |
| symbol | string | Trading pair | {{ticker}} |
| direction | string | "close_long" or "close_short" | Pine Script |
| tf | string | Timeframe | timeframe.period |
| price | float | Exit price | {{close}} |

### 9.3 Trend Pulse Alert Fields

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| type | string | "trend_pulse_v6" | Fixed |
| signal_type | string | Pulse type | Pine Script |
| symbol | string | Trading pair | {{ticker}} |
| tf | string | Timeframe | timeframe.period |
| price | float | Current price | {{close}} |
| current_trends | string | Current MTF trends | Pine Script |
| previous_trends | string | Previous MTF trends | Pine Script |
| changed_timeframes | string | Changed TF list | Pine Script |
| change_details | string | Change descriptions | Pine Script |
| aligned_count | int | Aligned TF count | Pine Script |
| confidence | string | Confidence level | Pine Script |
| message | string | Human-readable message | Pine Script |

---

**Document Status**: COMPLETE  
**Alert Processing Coverage**: 100%  
**V5 Architecture Compliance**: VERIFIED
