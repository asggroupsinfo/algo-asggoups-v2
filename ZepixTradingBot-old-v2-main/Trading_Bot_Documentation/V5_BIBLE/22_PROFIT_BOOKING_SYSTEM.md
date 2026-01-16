# PROFIT BOOKING SYSTEM

**File:** `src/managers/profit_booking_manager.py`  
**Lines:** 1087  
**Purpose:** Manages profit booking chains for pyramid compounding system

---

## OVERVIEW

The Profit Booking System implements a pyramid compounding strategy for Order B trades. When a profit target is hit, the system books profit and opens multiple new orders at the next level.

### Pyramid Structure

```
Level 0: 1 order  -> $7 profit target
Level 1: 2 orders -> $7 profit target each
Level 2: 4 orders -> $7 profit target each
Level 3: 8 orders -> $7 profit target each
Level 4: 16 orders -> $7 profit target each (MAX)
```

---

## KEY CONCEPTS

### Minimum Profit Target

The system uses a **$7 minimum profit target** per order. This ensures:
- Consistent profit booking across all levels
- Predictable compounding growth
- Risk-controlled position sizing

### Level Progression

| Level | Orders | Profit Target | Total Potential |
|-------|--------|---------------|-----------------|
| 0 | 1 | $7 | $7 |
| 1 | 2 | $7 each | $14 |
| 2 | 4 | $7 each | $28 |
| 3 | 8 | $7 each | $56 |
| 4 | 16 | $7 each | $112 |

---

## CLASS STRUCTURE

### Definition (Lines 14-22)

```python
class ProfitBookingManager:
    """
    Manages profit booking chains for pyramid compounding system
    - Level 0: 1 order → $10 profit target → Level 1
    - Level 1: 2 orders → $20 profit target → Level 2
    - Level 2: 4 orders → $40 profit target → Level 3
    - Level 3: 8 orders → $80 profit target → Level 4
    - Level 4: 16 orders → $160 profit target → Max level
    """
```

### Initialization (Lines 24-60)

```python
def __init__(self, config: Config, mt5_client: MT5Client, 
             pip_calculator: PipCalculator, db: TradeDatabase = None):
    self.config = config
    self.mt5_client = mt5_client
    self.pip_calculator = pip_calculator
    self.db = db
    self.logger = logging.getLogger(__name__)
    
    # Active profit chains
    self.active_chains: Dict[str, ProfitBookingChain] = {}
    
    # Load persisted chains from database
    self._load_persisted_chains()
    
    # Pyramid configuration
    self.pyramid_config = {
        "min_profit_target": 7.0,  # $7 minimum
        "max_level": 4,
        "orders_per_level": [1, 2, 4, 8, 16],
        "sl_type": "fixed_risk",
        "risk_per_order": 10.0  # $10 fixed risk
    }
```

---

## CHAIN MANAGEMENT

### Create Profit Chain (Lines 62-140)

```python
def create_profit_chain(self, order_b_id: int, symbol: str, 
                       direction: str, entry_price: float,
                       lot_size: float, strategy: str) -> Optional[ProfitBookingChain]:
    """
    Create a new profit booking chain for Order B.
    
    Args:
        order_b_id: MT5 ticket for Order B
        symbol: Trading symbol
        direction: Trade direction
        entry_price: Entry price
        lot_size: Position size
        strategy: Strategy name
        
    Returns:
        ProfitBookingChain: New chain or None if creation failed
    """
    chain_id = f"PB_{symbol}_{uuid.uuid4().hex[:8]}"
    
    # Calculate profit target price
    profit_target = self._calculate_profit_target(
        symbol, direction, entry_price, lot_size, level=0
    )
    
    chain = ProfitBookingChain(
        chain_id=chain_id,
        symbol=symbol,
        direction=direction,
        current_level=0,
        max_level=self.pyramid_config["max_level"],
        orders=[{
            "order_id": order_b_id,
            "entry_price": entry_price,
            "lot_size": lot_size,
            "profit_target": profit_target,
            "status": "active"
        }],
        total_profit=0.0,
        created_at=datetime.now().isoformat(),
        last_update=datetime.now().isoformat(),
        metadata={
            "strategy": strategy,
            "initial_lot_size": lot_size,
            "initial_entry": entry_price
        }
    )
    
    self.active_chains[chain_id] = chain
    
    # Persist to database
    if self.db:
        self._persist_chain(chain)
    
    self.logger.info(f"Profit chain created: {chain_id} for Order B #{order_b_id}")
    
    return chain
```

### Calculate Profit Target (Lines 142-200)

```python
def _calculate_profit_target(self, symbol: str, direction: str,
                            entry_price: float, lot_size: float,
                            level: int) -> float:
    """
    Calculate the profit target price for a given level.
    
    Uses $7 minimum profit target per order.
    
    Args:
        symbol: Trading symbol
        direction: Trade direction
        entry_price: Entry price
        lot_size: Position size
        level: Current pyramid level
        
    Returns:
        float: Target price for profit booking
    """
    # Get pip value
    symbol_config = self.config["symbol_config"].get(symbol, {})
    pip_value_std = symbol_config.get("pip_value_per_std_lot", 10.0)
    pip_size = symbol_config.get("pip_size", 0.0001)
    
    # Calculate pip value for this lot size
    pip_value = pip_value_std * lot_size
    
    # Minimum profit target: $7
    min_profit = self.pyramid_config["min_profit_target"]
    
    # Calculate pips needed for $7 profit
    pips_needed = min_profit / pip_value
    
    # Calculate target price
    if direction.lower() in ["buy", "bull"]:
        target_price = entry_price + (pips_needed * pip_size)
    else:
        target_price = entry_price - (pips_needed * pip_size)
    
    return target_price
```

---

## PROFIT TARGET MONITORING

### Check Profit Targets (Lines 202-280)

```python
def check_profit_targets(self, current_prices: Dict[str, float]) -> List[Dict]:
    """
    Check all active chains for profit target hits.
    
    Called by autonomous system manager in the main loop.
    
    Args:
        current_prices: Dict of symbol -> current price
        
    Returns:
        list: List of chains that hit profit targets
    """
    hits = []
    
    for chain_id, chain in list(self.active_chains.items()):
        if chain.status != "active":
            continue
        
        symbol = chain.symbol
        current_price = current_prices.get(symbol)
        
        if not current_price:
            continue
        
        # Check each active order in the chain
        for order in chain.orders:
            if order["status"] != "active":
                continue
            
            target = order["profit_target"]
            
            # Check if target hit
            target_hit = False
            if chain.direction.lower() in ["buy", "bull"]:
                target_hit = current_price >= target
            else:
                target_hit = current_price <= target
            
            if target_hit:
                hits.append({
                    "chain_id": chain_id,
                    "order_id": order["order_id"],
                    "target_price": target,
                    "current_price": current_price,
                    "level": chain.current_level
                })
                
                # Mark order as hit
                order["status"] = "target_hit"
                order["hit_price"] = current_price
                order["hit_time"] = datetime.now().isoformat()
    
    return hits
```

### Handle Profit Target Hit (Lines 282-400)

```python
async def handle_profit_target_hit(self, chain_id: str, order_id: int,
                                  hit_price: float) -> Dict[str, Any]:
    """
    Handle profit target hit - book profit and advance level.
    
    Args:
        chain_id: Chain identifier
        order_id: Order that hit target
        hit_price: Price at which target was hit
        
    Returns:
        dict: Result with new orders placed
    """
    result = {
        "success": False,
        "profit_booked": 0.0,
        "new_orders": [],
        "new_level": 0,
        "chain_complete": False
    }
    
    chain = self.active_chains.get(chain_id)
    if not chain:
        result["error"] = "Chain not found"
        return result
    
    # Find the order
    order = None
    for o in chain.orders:
        if o["order_id"] == order_id:
            order = o
            break
    
    if not order:
        result["error"] = "Order not found in chain"
        return result
    
    # Calculate profit
    entry = order["entry_price"]
    lot_size = order["lot_size"]
    symbol_config = self.config["symbol_config"].get(chain.symbol, {})
    pip_value_std = symbol_config.get("pip_value_per_std_lot", 10.0)
    pip_size = symbol_config.get("pip_size", 0.0001)
    
    pips_gained = abs(hit_price - entry) / pip_size
    profit = pips_gained * pip_value_std * lot_size
    
    result["profit_booked"] = profit
    chain.total_profit += profit
    
    # Close the order
    close_result = await self._close_order(order_id)
    if not close_result["success"]:
        result["error"] = f"Failed to close order: {close_result.get('error')}"
        return result
    
    # Check if all orders at current level are complete
    active_orders = [o for o in chain.orders if o["status"] == "active"]
    
    if len(active_orders) == 0:
        # All orders complete - advance to next level
        if chain.current_level < chain.max_level:
            new_level = chain.current_level + 1
            chain.current_level = new_level
            result["new_level"] = new_level
            
            # Create new orders for next level
            num_orders = self.pyramid_config["orders_per_level"][new_level]
            
            for i in range(num_orders):
                new_order = await self._create_level_order(
                    chain, hit_price, i
                )
                if new_order:
                    chain.orders.append(new_order)
                    result["new_orders"].append(new_order["order_id"])
            
            self.logger.info(f"Chain {chain_id} advanced to Level {new_level} with {num_orders} orders")
        else:
            # Max level reached - chain complete
            chain.status = "completed"
            result["chain_complete"] = True
            self.logger.info(f"Chain {chain_id} COMPLETED! Total profit: ${chain.total_profit:.2f}")
    
    # Update chain
    chain.last_update = datetime.now().isoformat()
    
    # Persist
    if self.db:
        self._persist_chain(chain)
    
    result["success"] = True
    return result
```

---

## LEVEL ORDER CREATION

### Create Level Order (Lines 402-480)

```python
async def _create_level_order(self, chain: ProfitBookingChain,
                             entry_price: float, order_index: int) -> Optional[Dict]:
    """
    Create a new order for the current pyramid level.
    
    Args:
        chain: The profit booking chain
        entry_price: Entry price for new order
        order_index: Index of this order in the level
        
    Returns:
        dict: Order info or None if creation failed
    """
    # Calculate lot size (same as initial)
    lot_size = chain.metadata.get("initial_lot_size", 0.01)
    
    # Calculate SL (fixed $10 risk)
    sl_price = self._calculate_fixed_risk_sl(
        chain.symbol, chain.direction, entry_price, lot_size
    )
    
    # Calculate profit target
    profit_target = self._calculate_profit_target(
        chain.symbol, chain.direction, entry_price, lot_size, chain.current_level
    )
    
    # Place order
    try:
        if self.config.get("simulate_orders", False):
            order_id = random.randint(100000, 999999)
        else:
            order_id = self.mt5_client.place_order(
                symbol=chain.symbol,
                order_type=chain.direction,
                lot_size=lot_size,
                price=entry_price,
                sl=sl_price,
                tp=None,  # No TP - uses profit booking
                comment=f"PB_L{chain.current_level}_{order_index}"
            )
        
        if order_id:
            return {
                "order_id": order_id,
                "entry_price": entry_price,
                "lot_size": lot_size,
                "sl_price": sl_price,
                "profit_target": profit_target,
                "level": chain.current_level,
                "status": "active",
                "created_at": datetime.now().isoformat()
            }
    except Exception as e:
        self.logger.error(f"Failed to create level order: {e}")
    
    return None
```

### Calculate Fixed Risk SL (Lines 482-520)

```python
def _calculate_fixed_risk_sl(self, symbol: str, direction: str,
                            entry_price: float, lot_size: float) -> float:
    """
    Calculate SL price for fixed $10 risk.
    
    Args:
        symbol: Trading symbol
        direction: Trade direction
        entry_price: Entry price
        lot_size: Position size
        
    Returns:
        float: SL price
    """
    # Get pip value
    symbol_config = self.config["symbol_config"].get(symbol, {})
    pip_value_std = symbol_config.get("pip_value_per_std_lot", 10.0)
    pip_size = symbol_config.get("pip_size", 0.0001)
    
    # Calculate pip value for this lot size
    pip_value = pip_value_std * lot_size
    
    # Fixed risk: $10
    risk_amount = self.pyramid_config["risk_per_order"]
    
    # Calculate SL distance in pips
    sl_pips = risk_amount / pip_value
    
    # Calculate SL price
    if direction.lower() in ["buy", "bull"]:
        sl_price = entry_price - (sl_pips * pip_size)
    else:
        sl_price = entry_price + (sl_pips * pip_size)
    
    return sl_price
```

---

## PROFIT BOOKING SL HUNT

### Handle Chain SL Hit (Lines 600-700)

```python
async def handle_chain_sl_hit(self, chain_id: str, order_id: int,
                             sl_price: float) -> Dict[str, Any]:
    """
    Handle SL hit on a profit booking chain order.
    
    Triggers Profit Booking SL Hunt recovery if enabled.
    
    Args:
        chain_id: Chain identifier
        order_id: Order that hit SL
        sl_price: SL price
        
    Returns:
        dict: Result with recovery status
    """
    result = {
        "success": False,
        "recovery_started": False,
        "chain_stopped": False
    }
    
    chain = self.active_chains.get(chain_id)
    if not chain:
        result["error"] = "Chain not found"
        return result
    
    # Find and update the order
    for order in chain.orders:
        if order["order_id"] == order_id:
            order["status"] = "sl_hit"
            order["sl_hit_time"] = datetime.now().isoformat()
            break
    
    # Check if recovery is allowed
    pb_sl_hunt_config = self.config.get("profit_booking_config", {}).get("sl_hunt", {})
    
    if pb_sl_hunt_config.get("enabled", False):
        # Check recovery limits
        if chain.metadata.get("recovery_attempts", 0) < pb_sl_hunt_config.get("max_recoveries", 1):
            chain.status = "recovery_mode"
            chain.metadata["recovery_attempts"] = chain.metadata.get("recovery_attempts", 0) + 1
            chain.metadata["recovery_sl_price"] = sl_price
            chain.metadata["recovery_started_at"] = datetime.now().isoformat()
            
            result["recovery_started"] = True
            self.logger.info(f"Profit Booking SL Hunt started for chain {chain_id}")
        else:
            # Max recoveries exceeded - stop chain
            chain.status = "stopped"
            chain.metadata["stop_reason"] = "Max recovery attempts exceeded"
            result["chain_stopped"] = True
            self.logger.info(f"Chain {chain_id} stopped - max recoveries exceeded")
    else:
        # SL Hunt disabled - stop chain
        chain.status = "stopped"
        chain.metadata["stop_reason"] = "SL hit (recovery disabled)"
        result["chain_stopped"] = True
    
    # Persist
    if self.db:
        self._persist_chain(chain)
    
    result["success"] = True
    return result
```

---

## PERSISTENCE

### Load Persisted Chains (Lines 800-850)

```python
def _load_persisted_chains(self):
    """Load profit chains from database on startup"""
    if not self.db:
        return
    
    try:
        chains_data = self.db.load_profit_chains()
        
        for chain_data in chains_data:
            chain = ProfitBookingChain(**chain_data)
            
            # Only load active chains
            if chain.status in ["active", "recovery_mode"]:
                self.active_chains[chain.chain_id] = chain
                self.logger.info(f"Loaded persisted chain: {chain.chain_id}")
    except Exception as e:
        self.logger.error(f"Failed to load persisted chains: {e}")

def _persist_chain(self, chain: ProfitBookingChain):
    """Persist chain to database"""
    if not self.db:
        return
    
    try:
        self.db.save_profit_chain(chain.to_dict())
    except Exception as e:
        self.logger.error(f"Failed to persist chain {chain.chain_id}: {e}")
```

---

## CONFIGURATION

### Profit Booking Config

```python
{
    "profit_booking_config": {
        "enabled": true,
        "pyramid": {
            "min_profit_target": 7.0,
            "max_level": 4,
            "orders_per_level": [1, 2, 4, 8, 16]
        },
        "risk": {
            "fixed_risk_per_order": 10.0,
            "sl_type": "fixed_risk"
        },
        "sl_hunt": {
            "enabled": true,
            "max_recoveries": 1,
            "recovery_threshold_percent": 70,
            "recovery_window_minutes": 20
        }
    }
}
```

---

## PROFIT BOOKING FLOW

```
Order B Placed
      |
      v
+------------------+
| create_profit_   |
| chain()          |
+------------------+
      |
      v
+------------------+
| Autonomous Loop  |
| check_profit_    |
| targets()        |
+------------------+
      |
      +---> Target Hit?
      |         |
      |         v
      |    +------------------+
      |    | handle_profit_   |
      |    | target_hit()     |
      |    +------------------+
      |         |
      |         +---> Book Profit
      |         |
      |         +---> Close Order
      |         |
      |         +---> Advance Level?
      |         |         |
      |         |         v
      |         |    +------------------+
      |         |    | Create New       |
      |         |    | Level Orders     |
      |         |    +------------------+
      |         |
      |         +---> Max Level?
      |                   |
      |                   v
      |              Chain Complete!
      |
      +---> SL Hit?
                |
                v
           +------------------+
           | handle_chain_    |
           | sl_hit()         |
           +------------------+
                |
                +---> Recovery Mode
                      or Chain Stop
```

---

## RELATED FILES

- `src/core/trading_engine.py` - Uses ProfitBookingManager
- `src/managers/autonomous_system_manager.py` - Monitors profit targets
- `src/managers/profit_booking_reentry_manager.py` - SL Hunt recovery
- `src/database.py` - Chain persistence
