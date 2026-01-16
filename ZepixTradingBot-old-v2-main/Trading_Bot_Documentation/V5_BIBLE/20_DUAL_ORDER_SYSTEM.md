# DUAL ORDER SYSTEM

**File:** `src/managers/dual_order_manager.py`  
**Lines:** 346  
**Purpose:** Manages Order A (TP Trail) and Order B (Profit Trail) placement

---

## OVERVIEW

The Dual Order System creates TWO orders for every trade signal:

- **Order A (TP_TRAIL):** Uses V3 Smart SL with progressive trailing and TP target
- **Order B (PROFIT_TRAIL):** Uses fixed $10 risk SL with profit booking pyramid

Both orders use the SAME lot size and work independently (no rollback if one fails).

---

## ORDER TYPES

### Order A: TP Trail

| Property | Value |
|----------|-------|
| SL Type | V3 Smart SL (progressive trailing) |
| TP Target | Yes (2:1 RR) |
| Trailing | Starts at 50% of SL in profit |
| Trail Step | 25% of SL |
| On SL Hit | Triggers SL Hunt Recovery |
| On TP Hit | Triggers TP Continuation |

### Order B: Profit Trail

| Property | Value |
|----------|-------|
| SL Type | Fixed $10 risk |
| TP Target | No (uses profit booking) |
| Trailing | No |
| Profit Target | $7 per order |
| On SL Hit | Triggers Profit Booking SL Hunt |
| On Profit Target | Books profit, advances chain level |

---

## CLASS STRUCTURE

### Definition (Lines 10-27)

```python
class DualOrderManager:
    """
    Manages dual order placement system
    - Order A: TP Continuation Trail (existing system)
    - Order B: Profit Booking Trail (new pyramid system)
    - Both orders use SAME lot size (no split)
    - Orders work independently (no rollback if one fails)
    """
    
    def __init__(self, config: Config, risk_manager: RiskManager, 
                 mt5_client: MT5Client, pip_calculator: PipCalculator,
                 profit_sl_calculator=None):
        self.config = config
        self.risk_manager = risk_manager
        self.mt5_client = mt5_client
        self.pip_calculator = pip_calculator
        self.profit_sl_calculator = profit_sl_calculator  # For Order B
        self.logger = logging.getLogger(__name__)
```

---

## CORE METHODS

### Is Enabled (Lines 29-31)

```python
def is_enabled(self) -> bool:
    """Check if dual order system is enabled"""
    return self.config.get("dual_order_config", {}).get("enabled", True)
```

### Validate Dual Order Risk (Lines 33-131)

```python
def validate_dual_order_risk(self, symbol: str, lot_size: float, 
                            account_balance: float) -> Dict[str, Any]:
    """
    Validate if account can handle 2x lot size risk
    Returns: {"valid": bool, "reason": str}
    
    NOTE: Margin validation DISABLED as it was causing false positives.
    MT5 broker handles margin requirements automatically.
    We only check daily/lifetime loss limits here.
    """
    if not self.is_enabled():
        return {"valid": True, "reason": "Dual orders disabled"}
    
    # Calculate risk for 2x lot size
    symbol_config = self.config["symbol_config"][symbol]
    account_tier = self.risk_manager.get_risk_tier(account_balance)
    
    # Get SL pips from dual SL system
    sl_pips = self.pip_calculator._get_sl_from_dual_system(symbol, account_balance)
    
    # Get pip value
    pip_value_std = symbol_config.get("pip_value_per_std_lot", 10.0)
    pip_value = pip_value_std * (lot_size * 2)  # 2x lot size
    
    # Calculate expected loss for 2 orders
    expected_loss = sl_pips * pip_value
    
    # Get risk tier limits
    risk_params = self.config["risk_tiers"][account_tier]
    
    # Check daily loss cap
    daily_loss = self.risk_manager.daily_loss
    risk_gap = daily_loss + expected_loss - risk_params["daily_loss_limit"]
    
    if risk_gap > 0:
        # SMART AUTO-ADJUSTMENT LOGIC
        available_risk = max(0, risk_params["daily_loss_limit"] - daily_loss)
        
        if available_risk < 1.0:
            return {
                "valid": False,
                "reason": f"Daily loss cap reached: ${daily_loss:.2f}"
            }
        
        # Calculate max allowed lot size
        max_allowed_lot = available_risk / (sl_pips * pip_value_std * 2)
        adjusted_lot = math.floor(max_allowed_lot * 100) / 100.0
        
        if adjusted_lot < 0.01:
            return {
                "valid": False,
                "reason": f"Available risk ${available_risk:.2f} too small"
            }
        
        return {
            "valid": True,
            "reason": f"Auto-adjusted lot to {adjusted_lot}",
            "adjusted_lot": adjusted_lot,
            "was_adjusted": True
        }
    
    # Check lifetime loss cap
    lifetime_loss = self.risk_manager.lifetime_loss
    if lifetime_loss + expected_loss > risk_params["max_total_loss"]:
        return {
            "valid": False,
            "reason": f"Lifetime loss cap exceeded"
        }
    
    return {"valid": True, "reason": "Risk validation passed"}
```

### Create Dual Orders (Lines 133-305)

```python
def create_dual_orders(self, alert: Alert, strategy: str, 
                      account_balance: float) -> Dict[str, Any]:
    """
    Create Order A (TP Trail) and Order B (Profit Trail) with same lot size
    Returns: {
        "order_a": Trade object or None,
        "order_b": Trade object or None,
        "order_a_placed": bool,
        "order_b_placed": bool,
        "errors": List[str]
    }
    """
    result = {
        "order_a": None,
        "order_b": None,
        "order_a_placed": False,
        "order_b_placed": False,
        "errors": []
    }
    
    if not self.is_enabled():
        return result
    
    try:
        # Get lot size (same for both orders)
        requested_lot_size = self.risk_manager.get_lot_size_for_logic(
            account_balance, logic=strategy
        )
        
        if requested_lot_size <= 0:
            result["errors"].append("Invalid lot size")
            return result
        
        # Validate risk for 2x lot size
        risk_validation = self.validate_dual_order_risk(
            alert.symbol, requested_lot_size, account_balance
        )
        
        # Check for adjusted lot size
        final_lot_size = requested_lot_size
        if risk_validation.get("was_adjusted"):
            final_lot_size = risk_validation.get("adjusted_lot")
        
        if not risk_validation["valid"]:
            result["errors"].append(f"Risk validation failed: {risk_validation['reason']}")
            return result
        
        lot_size = final_lot_size
        
        # Calculate SL and TP for Order A (TP Trail)
        sl_price_a, sl_distance_a = self.pip_calculator.calculate_sl_price(
            alert.symbol, alert.price, alert.signal, lot_size, account_balance,
            logic=strategy
        )
        
        tp_price_a = self.pip_calculator.calculate_tp_price(
            alert.price, sl_price_a, alert.signal, self.config.get("rr_ratio", 1.0)
        )
        
        # Calculate SL for Order B (Profit Trail) - uses logic-based SL
        if self.profit_sl_calculator:
            sl_price_b, sl_distance_b = self.profit_sl_calculator.calculate_sl_price(
                alert.price, alert.signal, alert.symbol, lot_size, strategy
            )
        else:
            sl_price_b, sl_distance_b = sl_price_a, sl_distance_a
        
        # Calculate TP for Order B
        tp_price_b = self.pip_calculator.calculate_tp_price(
            alert.price, sl_price_b or alert.price * 0.99, alert.signal, 
            self.config.get("rr_ratio", 1.0)
        )
        
        # Create Order A (TP Trail)
        order_a = Trade(
            symbol=alert.symbol,
            entry=alert.price,
            sl=sl_price_a,
            tp=tp_price_a,
            lot_size=lot_size,
            direction=alert.signal,
            strategy=strategy,
            open_time=datetime.now().isoformat(),
            original_entry=alert.price,
            original_sl_distance=sl_distance_a,
            order_type="TP_TRAIL"
        )
        
        # Create Order B (Profit Trail)
        order_b = Trade(
            symbol=alert.symbol,
            entry=alert.price,
            sl=sl_price_b,  # Independent $10 fixed SL
            tp=tp_price_b,
            lot_size=lot_size,  # Same lot size
            direction=alert.signal,
            strategy=strategy,
            open_time=datetime.now().isoformat(),
            original_entry=alert.price,
            original_sl_distance=sl_distance_b or 0.0,
            order_type="PROFIT_TRAIL"
        )
        
        result["order_a"] = order_a
        result["order_b"] = order_b
        
        # Place Order A independently
        order_a_result = self._place_single_order(order_a, strategy, "TP_TRAIL")
        if order_a_result["success"]:
            result["order_a_placed"] = True
            order_a.trade_id = order_a_result["trade_id"]
        else:
            result["errors"].append(f"Order A failed: {order_a_result.get('error')}")
        
        # Place Order B independently (regardless of Order A result)
        order_b_result = self._place_single_order(order_b, strategy, "PROFIT_TRAIL")
        if order_b_result["success"]:
            result["order_b_placed"] = True
            order_b.trade_id = order_b_result["trade_id"]
        else:
            result["errors"].append(f"Order B failed: {order_b_result.get('error')}")
        
        return result
        
    except Exception as e:
        result["errors"].append(f"Dual order creation error: {str(e)}")
        return result
```

### Place Single Order (Lines 307-345)

```python
def _place_single_order(self, trade: Trade, strategy: str, 
                       order_type: str) -> Dict[str, Any]:
    """
    Place a single order in MT5
    Returns: {"success": bool, "trade_id": Optional[int], "error": Optional[str]}
    """
    try:
        if self.config.get("simulate_orders", False):
            # Simulation mode
            trade_id = random.randint(100000, 999999)
            return {"success": True, "trade_id": trade_id, "error": None}
        
        # Live trading mode
        trade_id = self.mt5_client.place_order(
            symbol=trade.symbol,
            order_type=trade.direction,
            lot_size=trade.lot_size,
            price=trade.entry,
            sl=trade.sl,
            tp=trade.tp,
            comment=f"{strategy}_{order_type}"
        )
        
        if trade_id:
            return {"success": True, "trade_id": trade_id, "error": None}
        else:
            return {"success": False, "trade_id": None, "error": "MT5 order placement failed"}
            
    except Exception as e:
        return {"success": False, "trade_id": None, "error": str(e)}
```

---

## ORDER FLOW DIAGRAM

```
Signal Received
      |
      v
+------------------+
| DualOrderManager |
| create_dual_     |
| orders()         |
+------------------+
      |
      +---> Validate Risk (2x lot)
      |
      +---> Calculate Lot Size
      |
      +---> Calculate Order A SL/TP (V3 Smart SL)
      |
      +---> Calculate Order B SL/TP (Fixed $10)
      |
      v
+------------------+     +------------------+
|    Order A       |     |    Order B       |
|   (TP_TRAIL)     |     | (PROFIT_TRAIL)   |
+------------------+     +------------------+
      |                        |
      v                        v
+------------------+     +------------------+
| MT5 Place Order  |     | MT5 Place Order  |
+------------------+     +------------------+
      |                        |
      v                        v
+------------------+     +------------------+
| ReEntryManager   |     | ProfitBooking    |
| (SL Hunt/TP Cont)|     | Manager (Pyramid)|
+------------------+     +------------------+
```

---

## SL CALCULATION

### Order A: V3 Smart SL

```python
# Progressive trailing SL
# Starts at 50% of SL in profit
# Trails in 25% steps

sl_pips = config["sl_systems"]["sl-1"]["symbols"][symbol][tier]["sl_pips"]
trailing_start = sl_pips * 0.5  # Start trailing at 50% of SL
trailing_step = sl_pips * 0.25  # Trail in 25% steps
```

### Order B: Fixed $10 Risk SL

```python
# Calculate SL based on fixed $10 risk
# SL distance = $10 / (pip_value * lot_size)

risk_amount = 10.0  # Fixed $10 risk
pip_value = symbol_config["pip_value_per_std_lot"] * lot_size
sl_pips = risk_amount / pip_value
```

---

## CONFIGURATION

### Dual Order Config

```python
{
    "dual_order_config": {
        "enabled": true,
        "order_a": {
            "sl_type": "V3_SMART_SL",
            "trailing_enabled": true,
            "trailing_start_percent": 50,
            "trailing_step_percent": 25,
            "tp_rr_ratio": 2.0
        },
        "order_b": {
            "sl_type": "FIXED_RISK",
            "risk_amount": 10.0,
            "profit_booking_enabled": true,
            "min_profit_target": 7.0
        }
    }
}
```

---

## SMART AUTO-ADJUSTMENT

When daily loss limit is approaching, the system automatically reduces lot size:

```python
# Example:
# Daily limit: $100
# Current daily loss: $80
# Available risk: $20
# Requested lot: 0.10 (would risk $40)
# Adjusted lot: 0.05 (risks $20)

available_risk = daily_limit - daily_loss  # $20
max_lot = available_risk / (sl_pips * pip_value * 2)  # 0.05
```

---

## INTEGRATION POINTS

### Inbound

| Source | Method | Description |
|--------|--------|-------------|
| TradingEngine | `create_dual_orders()` | New trade signal |
| AlertProcessor | `create_dual_orders()` | Parsed alert |

### Outbound

| Target | Method | Description |
|--------|--------|-------------|
| MT5Client | `place_order()` | Order execution |
| ReEntryManager | `create_chain()` | Order A chain |
| ProfitBookingManager | `create_profit_chain()` | Order B chain |

---

## RELATED FILES

- `src/core/trading_engine.py` - Uses DualOrderManager
- `src/managers/reentry_manager.py` - Order A recovery
- `src/managers/profit_booking_manager.py` - Order B profit chains
- `src/utils/pip_calculator.py` - SL/TP calculations
- `src/utils/profit_sl_calculator.py` - Order B SL calculations
