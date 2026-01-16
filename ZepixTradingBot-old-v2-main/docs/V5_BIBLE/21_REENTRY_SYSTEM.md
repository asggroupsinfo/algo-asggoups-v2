# RE-ENTRY SYSTEM

**File:** `src/managers/reentry_manager.py`  
**Lines:** 562  
**Purpose:** Manages SL Hunt Recovery, TP Continuation, and Exit Continuation

---

## OVERVIEW

The Re-Entry System provides three recovery mechanisms:

1. **SL Hunt Recovery:** Re-enter after SL hit when price recovers 70%
2. **TP Continuation:** Continue in same direction after TP hit
3. **Exit Continuation:** Re-enter after exit signal when trend resumes

---

## RECOVERY TYPES

### SL Hunt Recovery

| Property | Value |
|----------|-------|
| Trigger | SL hit on Order A |
| Recovery Threshold | 70% of original SL distance |
| Max Recoveries | 1 per chain |
| SL Reduction | Progressive per level |
| Timeout | Symbol-specific (default 30 min) |

### TP Continuation

| Property | Value |
|----------|-------|
| Trigger | TP hit on Order A |
| Continuation Window | 30 minutes |
| Same Direction | Required |
| Max Levels | 3 |
| SL Reduction | 10% per level |

### Exit Continuation

| Property | Value |
|----------|-------|
| Trigger | Exit signal received |
| Re-entry Window | 15 minutes |
| Trend Alignment | Required |
| Max Attempts | 1 |

---

## CLASS STRUCTURE

### Definition (Lines 7-26)

```python
class ReEntryManager:
    """Manage re-entry chains and SL hunting protection"""
    
    def __init__(self, config, mt5_client=None):
        self.config = config
        self.mt5_client = mt5_client
        self.active_chains = {}  # chain_id -> ReEntryChain
        self.recent_sl_hits = {}  # symbol -> list of recent SL hits
        self.completed_tps = {}  # symbol -> recent TP completions
        
        # Initialize TrendAnalyzer if client available
        self.trend_analyzer = None
        if self.mt5_client:
            self.trend_analyzer = TrendAnalyzer(self.mt5_client)
```

---

## CHAIN MANAGEMENT

### Create Chain (Lines 28-93)

```python
def create_chain(self, trade: Trade) -> ReEntryChain:
    """Create a new re-entry chain from initial trade"""
    
    chain_id = f"{trade.symbol}_{uuid.uuid4().hex[:8]}"
    
    # Get active SL system and reduction info
    active_system = self.config.get("active_sl_system", "sl-1")
    symbol_reductions = self.config.get("symbol_sl_reductions", {})
    symbol_reduction = symbol_reductions.get(trade.symbol, 0)
    
    # Get ORIGINAL unreduced SL pips from dual system config
    # Determine account tier based on balance
    balance = self.config.get("account_balance", 10000)
    tier = self._get_tier(balance)
    
    # Fetch original SL pips from the active system config
    original_sl_pips = self.config["sl_systems"][active_system]["symbols"][trade.symbol][tier]["sl_pips"]
    
    # Calculate applied SL pips (what was actually used on the trade)
    applied_sl_pips = original_sl_pips * (1 - symbol_reduction / 100)
    
    chain = ReEntryChain(
        chain_id=chain_id,
        symbol=trade.symbol,
        direction=trade.direction,
        original_entry=trade.entry,
        original_sl_distance=abs(trade.entry - trade.sl),
        current_level=1,
        max_level=self.config["re_entry_config"]["max_chain_levels"],
        trades=[trade.trade_id] if trade.trade_id else [],
        created_at=datetime.now().isoformat(),
        last_update=datetime.now().isoformat(),
        metadata={
            "sl_system_used": active_system,
            "sl_reduction_percent": symbol_reduction,
            "original_sl_pips": original_sl_pips,
            "applied_sl_pips": applied_sl_pips,
            "actual_lot_size": trade.lot_size,
            "logic": trade.strategy
        }
    )
    
    self.active_chains[chain_id] = chain
    trade.chain_id = chain_id
    
    return chain
```

---

## RE-ENTRY OPPORTUNITY DETECTION

### Check Re-Entry Opportunity (Lines 95-127)

```python
def check_reentry_opportunity(self, symbol: str, signal: str, 
                             price: float) -> Dict[str, Any]:
    """Check if new signal qualifies for re-entry"""
    
    result = {
        "is_reentry": False,
        "type": None,  # "tp_continuation" or "sl_recovery"
        "chain_id": None,
        "level": 1,
        "sl_adjustment": 1.0
    }
    
    # Check for TP continuation
    tp_opportunity = self._check_tp_continuation(symbol, signal, price)
    if tp_opportunity["eligible"]:
        result["is_reentry"] = True
        result["type"] = "tp_continuation"
        result["chain_id"] = tp_opportunity["chain_id"]
        result["level"] = tp_opportunity["level"]
        result["sl_adjustment"] = tp_opportunity["sl_adjustment"]
        return result
    
    # Check for SL recovery
    sl_opportunity = self._check_sl_recovery(symbol, signal, price)
    if sl_opportunity["eligible"]:
        result["is_reentry"] = True
        result["type"] = "sl_recovery"
        result["chain_id"] = sl_opportunity["chain_id"]
        result["level"] = sl_opportunity["level"]
        result["sl_adjustment"] = sl_opportunity["sl_adjustment"]
        return result
    
    return result
```

### Check TP Continuation (Lines 129-166)

```python
def _check_tp_continuation(self, symbol: str, signal: str, 
                          price: float) -> Dict[str, Any]:
    """Check if this is a continuation after TP hit"""
    
    result = {"eligible": False}
    
    if symbol not in self.completed_tps:
        return result
    
    recent_tps = self.completed_tps[symbol]
    current_time = datetime.now()
    
    for tp_event in recent_tps:
        time_since_tp = current_time - tp_event["time"]
        
        # Check if within continuation window
        if time_since_tp > timedelta(minutes=self.config["re_entry_config"]["recovery_window_minutes"]):
            continue
        
        # Check if same direction
        signal_direction = "buy" if signal in ["buy", "bull"] else "sell"
        if signal_direction != tp_event["direction"]:
            continue
        
        # Check if we haven't exceeded max levels
        chain = self.active_chains.get(tp_event["chain_id"])
        if chain and chain.current_level < chain.max_level:
            result["eligible"] = True
            result["chain_id"] = chain.chain_id
            result["level"] = chain.current_level + 1
            
            # Calculate SL adjustment
            reduction_per_level = self.config["re_entry_config"]["sl_reduction_per_level"]
            result["sl_adjustment"] = (1 - reduction_per_level) ** (result["level"] - 1)
            
            break
    
    return result
```

### Check SL Recovery (Lines 168-237)

```python
def _check_sl_recovery(self, symbol: str, signal: str, 
                      price: float) -> Dict[str, Any]:
    """Check if this is a recovery after SL hit - continues existing chain"""
    
    result = {"eligible": False}
    
    if symbol not in self.recent_sl_hits:
        return result
    
    recent_sls = self.recent_sl_hits[symbol]
    current_time = datetime.now()
    
    for sl_event in recent_sls:
        time_since_sl = current_time - sl_event["time"]
        
        # Check if within recovery window
        if time_since_sl > timedelta(minutes=self.config["re_entry_config"]["recovery_window_minutes"]):
            continue
        
        # SAFETY CHECK #1: Enforce minimum time between re-entries (cooldown)
        min_time_seconds = self.config["re_entry_config"]["min_time_between_re_entries"]
        if time_since_sl < timedelta(seconds=min_time_seconds):
            print(f"WAIT: Re-entry cooldown active ({time_since_sl.seconds}s / {min_time_seconds}s)")
            continue
        
        # Check if same direction
        signal_direction = "buy" if signal in ["buy", "bull"] else "sell"
        if signal_direction != sl_event["direction"]:
            continue
        
        # Get chain info to continue it (not create new one!)
        chain_id = sl_event.get("chain_id")
        chain = self.active_chains.get(chain_id) if chain_id else None
        
        # Only allow re-entry if chain exists and hasn't hit max level
        if chain and chain.current_level < chain.max_level:
            # SAFETY CHECK #2: Verify price has recovered towards original entry
            price_recovered = False
            if signal_direction == "buy":
                price_recovered = price > sl_event["sl_price"]
            else:
                price_recovered = price < sl_event["sl_price"]
            
            if not price_recovered:
                print(f"ERROR: Re-entry blocked: Price has not recovered from SL level")
                continue
            
            result["eligible"] = True
            result["chain_id"] = chain.chain_id
            result["level"] = chain.current_level + 1
            
            # Calculate SL adjustment (progressive reduction)
            reduction_per_level = self.config["re_entry_config"]["sl_reduction_per_level"]
            result["sl_adjustment"] = (1 - reduction_per_level) ** (result["level"] - 1)
            
            # Reactivate chain
            chain.status = "active"
            
            break
    
    return result
```

---

## EVENT RECORDING

### Record TP Hit (Lines 239-260)

```python
def record_tp_hit(self, trade: Trade, tp_price: float):
    """Record TP hit for continuation tracking"""
    
    if trade.symbol not in self.completed_tps:
        self.completed_tps[trade.symbol] = []
    
    # Keep only recent TPs (last 30 minutes)
    self._clean_old_events(self.completed_tps[trade.symbol])
    
    self.completed_tps[trade.symbol].append({
        "time": datetime.now(),
        "chain_id": trade.chain_id,
        "direction": trade.direction,
        "tp_price": tp_price,
        "original_entry": trade.original_entry or trade.entry
    })
    
    # Update chain status
    if trade.chain_id in self.active_chains:
        chain = self.active_chains[trade.chain_id]
        chain.total_profit += abs(tp_price - trade.entry) * trade.lot_size * 10000
        chain.last_update = datetime.now().isoformat()
```

### Record SL Hit (Lines 262-303)

```python
def record_sl_hit(self, trade: Trade):
    """Record SL hit for recovery tracking"""
    
    if trade.symbol not in self.recent_sl_hits:
        self.recent_sl_hits[trade.symbol] = []
    
    # Keep only recent SLs (last 30 minutes)
    self._clean_old_events(self.recent_sl_hits[trade.symbol])
    
    self.recent_sl_hits[trade.symbol].append({
        "time": datetime.now(),
        "direction": trade.direction,
        "sl_price": trade.sl,
        "original_entry": trade.original_entry or trade.entry,
        "chain_id": trade.chain_id
    })
    
    # Update chain status based on Loss Capping Logic
    if trade.chain_id in self.active_chains:
        chain = self.active_chains[trade.chain_id]
        
        # Count recovery attempts
        if not hasattr(chain, 'recovery_attempts'):
            chain.recovery_attempts = 0
        
        # Allow MAX 1 recovery attempt
        MAX_RECOVERIES = 1
        
        if chain.recovery_attempts < MAX_RECOVERIES:
            chain.status = "recovery_mode"
            chain.recovery_attempts += 1
            
            # Store recovery metadata for SL Hunt monitoring
            chain.metadata["recovery_sl_price"] = trade.sl
            chain.metadata["recovery_started_at"] = datetime.now().isoformat()
            chain.metadata["recovery_original_level"] = chain.current_level
            
            print(f"RECOVERY MODE: Chain {trade.chain_id} SL Hit -> Activating SL Hunt")
        else:
            chain.status = "stopped"
            chain.metadata["stop_reason"] = "Max recovery attempts exceeded"
            print(f"HARD STOP: Chain {trade.chain_id} -> MAX RECOVERIES EXCEEDED")
```

---

## SL HUNT RECOVERY

### Check SL Hunt Recovery (Lines 344-470)

```python
def check_sl_hunt_recovery(self, chain, current_price: float) -> Dict[str, Any]:
    """
    Check if SL hunt recovery conditions are met for chain in recovery_mode
    
    Monitors chains with status='recovery_mode' and checks:
    1. Recovery window not expired (symbol-specific)
    2. Price recovered beyond SL + 70% of original SL distance
    3. Trend still aligned
    4. Optional: Volatility check
    
    Returns: {
        "eligible": bool,
        "entry_price": float,
        "tight_sl_price": float,
        "resume_to_next_level": bool,
        "current_level": int,
        "next_level_on_success": int
    }
    """
    result = {"eligible": False, "reason": ""}
    
    # Check chain in recovery mode
    if chain.status != "recovery_mode":
        result["reason"] = "Chain not in recovery mode"
        return result
    
    # Get recovery metadata
    recovery_sl = chain.metadata.get("recovery_sl_price")
    recovery_start = chain.metadata.get("recovery_started_at")
    
    if not recovery_sl or not recovery_start:
        result["reason"] = "Missing recovery metadata"
        return result
    
    # Get config
    hunt_config = self.config.get("re_entry_config", {}).get("autonomous_config", {}).get("sl_hunt_recovery", {})
    if not hunt_config.get("enabled", False):
        result["reason"] = "SL hunt recovery disabled in config"
        return result
    
    # Check recovery window timeout (symbol-specific)
    symbol_windows = hunt_config.get("recovery_windows_by_symbol", {})
    symbol_window = symbol_windows.get(chain.symbol, hunt_config.get("recovery_window_minutes", 30))
    
    time_elapsed = (datetime.now() - datetime.fromisoformat(recovery_start)).total_seconds() / 60
    
    if time_elapsed > symbol_window:
        result["reason"] = f"Recovery window expired ({time_elapsed:.1f} min > {symbol_window} min)"
        chain.status = "stopped"
        chain.metadata["stop_reason"] = "Recovery window timeout"
        return result
    
    # Price recovery check (70% of SL Distance Rule)
    original_sl_dist = chain.original_sl_distance
    recovery_threshold = original_sl_dist * 0.70
    
    price_recovered = False
    target_price = 0.0
    
    if chain.direction == "buy":
        target_price = recovery_sl + recovery_threshold
        price_recovered = current_price >= target_price
    else:
        target_price = recovery_sl - recovery_threshold
        price_recovered = current_price <= target_price
    
    if not price_recovered:
        result["reason"] = f"Price not recovered 70% (Current: {current_price:.5f}, Target: {target_price:.5f})"
        return result
    
    # Trend alignment check
    if self.trend_analyzer:
        try:
            trend = self.trend_analyzer.get_current_trend(chain.symbol)
            is_aligned = self.trend_analyzer.is_aligned(chain.direction, trend)
            
            if not is_aligned:
                result["reason"] = f"Trend not aligned (Direction: {chain.direction}, Trend: {trend})"
                return result
        except Exception as e:
            result["reason"] = f"Trend check failed: {str(e)}"
            return result
    
    # Calculate tight SL (50% of original)
    tight_sl_multiplier = hunt_config.get("tight_sl_multiplier", 0.5)
    original_sl_pips = chain.metadata.get("applied_sl_pips", 50)
    pip_size = self.config.get("symbol_config", {}).get(chain.symbol, {}).get("pip_size", 0.01)
    tight_sl_distance = (original_sl_pips * pip_size) * tight_sl_multiplier
    
    # All checks passed!
    result["eligible"] = True
    result["entry_price"] = current_price
    result["tight_sl_price"] = (
        current_price - tight_sl_distance if chain.direction == "buy"
        else current_price + tight_sl_distance
    )
    result["current_level"] = chain.current_level
    result["next_level_on_success"] = chain.current_level + 1
    
    return result
```

---

## CONFIGURATION

### Re-Entry Config

```python
{
    "re_entry_config": {
        "max_chain_levels": 3,
        "recovery_window_minutes": 30,
        "min_time_between_re_entries": 60,
        "sl_reduction_per_level": 0.10,
        "autonomous_config": {
            "sl_hunt_recovery": {
                "enabled": true,
                "recovery_threshold_percent": 70,
                "tight_sl_multiplier": 0.5,
                "recovery_windows_by_symbol": {
                    "EURUSD": 30,
                    "GBPUSD": 25,
                    "XAUUSD": 20
                }
            },
            "tp_continuation": {
                "enabled": true,
                "continuation_window_minutes": 30
            },
            "safety_limits": {
                "daily_recovery_attempts": 10,
                "daily_recovery_losses": 5,
                "max_concurrent_recoveries": 3
            }
        }
    }
}
```

---

## RECOVERY FLOW DIAGRAM

```
SL Hit on Order A
       |
       v
+------------------+
| record_sl_hit()  |
| Set chain to     |
| "recovery_mode"  |
+------------------+
       |
       v
+------------------+
| Autonomous Loop  |
| check_sl_hunt_   |
| recovery()       |
+------------------+
       |
       +---> Check recovery window (not expired)
       |
       +---> Check price recovery (70% threshold)
       |
       +---> Check trend alignment
       |
       v
+------------------+
| Recovery Order   |
| Placed with      |
| Tight SL (50%)   |
+------------------+
       |
       v
+------------------+
| Chain Level      |
| Incremented      |
+------------------+
```

---

## RELATED FILES

- `src/core/trading_engine.py` - Uses ReEntryManager
- `src/managers/autonomous_system_manager.py` - Monitors recovery
- `src/managers/recovery_window_monitor.py` - Recovery monitoring
- `src/utils/trend_analyzer.py` - Trend alignment checks
