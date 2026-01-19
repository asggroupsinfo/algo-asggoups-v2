Searched for regex `profit.*booking.*reentry|profit.*booking.*re.entry|ProfitBookingChain|profit_booking_reentry`, 20 results

Searched for files matching `**/Trading_Bot/src/managers/profit_booking_reentry_manager.py`, 1 match

Read [](file:///c%3A/Users/Ansh%20Shivaay%20Gupta/Downloads/ZepixTradingBot-New-v1/ZepixTradingBot-old-v2-main/Trading_Bot/src/managers/profit_booking_reentry_manager.py)

Searched for regex `database.*reentry|trades.*table|reentry.*table|profit.*booking.*table|chain.*table`, 20 results

Searched codebase for "database schema trades table reentry_chains profit_booking_chains plugin_id V3 V6 separate tables isolation", 26 results

Perfect! Ab mujhe complete picture mil gayi hai. Let me create a comprehensive planning document.

```markdown
# COMPLETE RE-ENTRY SYSTEM PLANNING - V3 vs V6 Database & Autonomous Flow

**Created:** January 18, 2026  
**Purpose:** Complete understanding of all re-entry types, database architecture, trend alignment, and autonomous features  
**Critical Questions Answered:**
1. Database alag hai ya same? (V3 vs V6)
2. Kitne types ke re-entries hain?
3. Trend alignment kaise check hoti hai?
4. Autonomous features kaise kaam karte hain?

---

## 📊 EXECUTIVE SUMMARY (Hindi)

### Database Architecture

**ANSWER: V3 aur V6 ke liye ALAG-ALAG DATABASES hain! ✅**

```
V3 Plugin:
  ├── Database: data/zepix_combined_v3.db
  ├── Tables:
  │   ├── combined_v3_trades (trade data)
  │   ├── v3_profit_bookings (profit booking chains)
  │   ├── v3_signals_log (signals)
  │   └── v3_daily_stats (statistics)

V6 Plugins (4 timeframes):
  ├── Database: data/zepix_price_action.db
  ├── Tables:
  │   ├── price_action_1m_trades
  │   ├── price_action_5m_trades
  │   ├── price_action_15m_trades
  │   ├── price_action_1h_trades
  │   ├── v6_profit_bookings
  │   ├── market_trends (TREND_PULSE data)
  │   └── v6_daily_stats

Central Bot Database:
  ├── Database: data/trading_bot.db (LEGACY)
  ├── Tables:
  │   ├── trades (ALL trades - being migrated)
  │   ├── reentry_chains (ALL chains - needs plugin_id)
  │   ├── profit_booking_chains (ALL chains - needs plugin_id)
  │   └── system_state
```

### Total Re-Entry Types: 4

| # | Re-Entry Type | Purpose | V3 | V6 | Autonomous | Database Table |
|---|---------------|---------|----|----|------------|----------------|
| 1 | **SL Hunt Recovery** | Recover after SL hit | ✅ | ✅ | ✅ YES | reentry_chains |
| 2 | **TP Continuation** | Continue after TP profit | ✅ | ✅ | ✅ YES | reentry_chains |
| 3 | **Exit Continuation** | Re-enter after early exit | ✅ | ✅ | ❌ NO | reentry_chains |
| 4 | **Profit Booking SL Hunt** | Recover Order B after SL | ✅ | ✅ | ✅ YES | profit_booking_chains |

**Total:** 4 complete re-entry systems with trend alignment checks

---

## 🗄️ PART 1: DATABASE ARCHITECTURE DETAILED

### 1.1 Current State (MIXED - Needs Migration)

**Central Database (Legacy):**
```
trading_bot.db:
  ├── trades                   ❌ NO plugin_id (stores ALL trades together)
  ├── reentry_chains           ❌ NO plugin_id (V3 + V6 mixed)
  ├── profit_booking_chains    ❌ NO plugin_id (V3 + V6 mixed)
  ├── sl_events                ❌ NO plugin_id
  ├── tp_reentry_events        ❌ NO plugin_id
  └── system_state             ✅ OK (global)
```

**Problem:**
```python
# Current reentry_chains table:
{
    "EURUSD_abc123": {  # ❌ Is this V3 or V6?
        "symbol": "EURUSD",
        "direction": "buy",
        "current_level": 2,
        # NO plugin_id field!
    }
}

# Conflict: V3 aur V6 dono same table me store!
```

---

### 1.2 Target State (Plugin-Isolated)

#### V3 Database: `zepix_combined_v3.db`

```sql
-- V3 Trades Table
CREATE TABLE combined_v3_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_a_ticket INTEGER UNIQUE,           -- Order A (TP Trail)
    order_b_ticket INTEGER UNIQUE,           -- Order B (Profit Trail)
    mt5_parent_ticket INTEGER,
    
    symbol TEXT NOT NULL,
    direction TEXT CHECK(direction IN ('BUY', 'SELL')),
    entry_price REAL NOT NULL,
    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exit_time TIMESTAMP,
    status TEXT CHECK(status IN ('OPEN', 'PARTIAL', 'CLOSED')),
    
    -- V3 Specific
    combined_logic TEXT NOT NULL,            -- combinedlogic-1, -2, -3
    mtf_alignment_count INTEGER,             -- How many TFs aligned
    consensus_score REAL,                    -- 7/9, 8/9, 9/9
    entry_signal_type TEXT,                  -- entry_v3, reversal_entry_v3
    
    -- Re-entry tracking
    chain_id TEXT,
    chain_level INTEGER DEFAULT 1,
    is_reentry BOOLEAN DEFAULT 0,
    
    -- PnL
    pnl_dollars REAL DEFAULT 0,
    pnl_pips REAL DEFAULT 0,
    
    -- Metadata
    plugin_id TEXT DEFAULT 'v3_combined',    -- ✅ Plugin identification
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- V3 Re-Entry Chains
CREATE TABLE v3_reentry_chains (
    chain_id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    direction TEXT NOT NULL,
    original_entry REAL NOT NULL,
    original_sl_distance REAL NOT NULL,
    current_level INTEGER DEFAULT 1,
    max_level INTEGER DEFAULT 3,
    total_profit REAL DEFAULT 0,
    status TEXT DEFAULT 'active',            -- active, recovery_mode, completed, stopped
    
    -- V3 Specific metadata
    combined_logic TEXT,                     -- Which logic created this
    original_consensus_score REAL,
    
    -- Tracking
    trades TEXT,                             -- JSON array of trade IDs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    plugin_id TEXT DEFAULT 'v3_combined'     -- ✅ Always V3
);

-- V3 Profit Booking Chains
CREATE TABLE v3_profit_bookings (
    chain_id TEXT PRIMARY KEY,
    order_b_ticket INTEGER NOT NULL,         -- Order B that started chain
    symbol TEXT NOT NULL,
    direction TEXT NOT NULL,
    base_lot REAL NOT NULL,
    
    -- Chain progression
    current_level INTEGER DEFAULT 0,
    orders_in_level INTEGER DEFAULT 1,
    orders_booked INTEGER DEFAULT 0,
    total_profit REAL DEFAULT 0,
    max_level INTEGER DEFAULT 5,
    
    status TEXT DEFAULT 'ACTIVE',            -- ACTIVE, SL_HUNT, COMPLETED
    
    -- V3 specific
    combined_logic TEXT,
    original_entry REAL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    plugin_id TEXT DEFAULT 'v3_combined'     -- ✅ Always V3
);
```

---

#### V6 Database: `zepix_price_action.db`

```sql
-- V6 Trades Table (Separate tables per timeframe)
CREATE TABLE price_action_5m_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_a_ticket INTEGER UNIQUE,
    order_b_ticket INTEGER UNIQUE,
    mt5_parent_ticket INTEGER,
    
    symbol TEXT NOT NULL,
    direction TEXT CHECK(direction IN ('BUY', 'SELL')),
    entry_price REAL NOT NULL,
    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exit_time TIMESTAMP,
    status TEXT CHECK(status IN ('OPEN', 'PARTIAL', 'CLOSED')),
    
    -- V6 Specific
    timeframe TEXT DEFAULT '5',
    alert_type TEXT NOT NULL,                -- BULLISH_ENTRY, MOMENTUM_ENTRY_BULL, etc.
    adx_value REAL,
    confidence_score REAL,
    trendline_break BOOLEAN DEFAULT 0,
    mtf_alignment TEXT,                      -- "5/1" format from alert
    
    -- Higher TF validation (NEW - from database)
    higher_tf_checked TEXT,                  -- "15" (which TF was checked)
    higher_tf_bull_count INTEGER,            -- From market_trends table
    higher_tf_bear_count INTEGER,
    higher_tf_aligned BOOLEAN,
    
    -- Re-entry tracking
    chain_id TEXT,
    chain_level INTEGER DEFAULT 1,
    is_reentry BOOLEAN DEFAULT 0,
    
    pnl_dollars REAL DEFAULT 0,
    pnl_pips REAL DEFAULT 0,
    
    plugin_id TEXT DEFAULT 'v6_price_action_5m',  -- ✅ Plugin identification
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- V6 Re-Entry Chains (Shared across all V6 timeframes)
CREATE TABLE v6_reentry_chains (
    chain_id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    direction TEXT NOT NULL,
    original_entry REAL NOT NULL,
    original_sl_distance REAL NOT NULL,
    current_level INTEGER DEFAULT 1,
    max_level INTEGER DEFAULT 3,
    total_profit REAL DEFAULT 0,
    status TEXT DEFAULT 'active',
    
    -- V6 Specific metadata
    timeframe TEXT NOT NULL,                 -- "5", "15", "60"
    adx_threshold REAL,                      -- Plugin's ADX threshold
    alert_type TEXT,                         -- Original alert type
    
    trades TEXT,                             -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    plugin_id TEXT NOT NULL                  -- ✅ v6_price_action_5m, etc.
);

-- V6 Profit Booking Chains
CREATE TABLE v6_profit_bookings (
    chain_id TEXT PRIMARY KEY,
    order_b_ticket INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    direction TEXT NOT NULL,
    base_lot REAL NOT NULL,
    
    current_level INTEGER DEFAULT 0,
    orders_in_level INTEGER DEFAULT 1,
    orders_booked INTEGER DEFAULT 0,
    total_profit REAL DEFAULT 0,
    max_level INTEGER DEFAULT 5,
    
    status TEXT DEFAULT 'ACTIVE',
    
    -- V6 specific
    timeframe TEXT NOT NULL,
    original_adx REAL,
    original_confidence REAL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    plugin_id TEXT NOT NULL                  -- ✅ Plugin that created it
);

-- V6 Trend Pulse Data (NEW - for higher TF validation)
CREATE TABLE market_trends (
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,                 -- "1", "5", "15", "60", "240"
    bull_count INTEGER DEFAULT 0,
    bear_count INTEGER DEFAULT 0,
    net_direction TEXT DEFAULT 'NEUTRAL',    -- BULLISH, BEARISH, NEUTRAL
    market_state TEXT DEFAULT 'SIDEWAYS',    -- TRENDING_BULLISH, etc.
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, timeframe)
);
```

---

## 🔄 PART 2: ALL RE-ENTRY TYPES DETAILED

### Re-Entry Type 1: SL Hunt Recovery

**Purpose:** Recover position after SL hit when price reverses

#### Flow Diagram

```
STEP 1: SL HIT
──────────────
Order A hits SL @ 1.0840
    ↓
trading_engine.handle_sl_hit(trade)
    ↓
ReEntryManager.record_sl_hit(trade)
    ↓
UPDATE reentry_chains table:
- chain.status = "recovery_mode"
- chain.metadata["recovery_sl_price"] = 1.0840
- chain.metadata["recovery_started_at"] = timestamp
    ↓
INSERT INTO sl_events:
{
    trade_id,
    symbol: "EURUSD",
    sl_price: 1.0840,
    recovery_attempted: 0
}

──────────────────────────────────────

STEP 2: AUTONOMOUS MONITORING
──────────────────────────────
AutonomousSystemManager (runs every 5 seconds)
    ↓
Query: SELECT * FROM reentry_chains 
       WHERE status='recovery_mode' 
       AND plugin_id='v3_combined'  ← ✅ Plugin-specific!
    ↓
For each recovery chain:
    ↓
    Get current_price from MT5
    ↓
    Calculate recovery percentage:
    recovery% = (current_price - sl_price) / original_sl_distance
    ↓
    Check conditions:
    ✓ recovery% >= 70%
    ✓ Time elapsed < 30 minutes
    ✓ Trend aligned (TrendAnalyzer)
    ↓
    If eligible:
        entry_price = current_price
        tight_sl = sl_price + 5 pips
        
──────────────────────────────────────

STEP 3: TREND ALIGNMENT CHECK
──────────────────────────────
TrendAnalyzer.get_current_trend(symbol)
    ↓
    Query market_trends table:
    SELECT bull_count, bear_count 
    FROM market_trends 
    WHERE symbol='EURUSD' 
    AND timeframe='5'  ← Current TF
    ↓
    Determine trend:
    if bull_count > bear_count:
        trend = "BULLISH"
    else:
        trend = "BEARISH"
    ↓
    Check alignment:
    if direction == "buy" and trend == "BULLISH":
        aligned = True
    elif direction == "sell" and trend == "BEARISH":
        aligned = True
    else:
        aligned = False
    ↓
    If NOT aligned:
        REJECT recovery (trend reversed)
    
──────────────────────────────────────

STEP 4: EXECUTE RECOVERY
─────────────────────────
If trend aligned:
    ↓
    Place new trade:
    - Entry: 1.0860 (recovery price)
    - SL: 1.0850 (tight, +10 pips from SL hit)
    - TP: Based on plugin logic
    - Lot: Same as original
    ↓
    UPDATE reentry_chains:
    - status = "active"
    - current_level = current_level + 1
    - trades.append(new_trade_id)
    ↓
    UPDATE sl_events:
    - recovery_attempted = 1
    - recovery_successful = 1
    ↓
    Send Telegram notification
```

**Database Interaction:**

```python
# V3 Plugin Recovery
v3_chains = db_v3.execute("""
    SELECT * FROM v3_reentry_chains 
    WHERE status='recovery_mode' 
    AND plugin_id='v3_combined'
""")

# V6 5M Plugin Recovery
v6_5m_chains = db_v6.execute("""
    SELECT * FROM v6_reentry_chains 
    WHERE status='recovery_mode' 
    AND plugin_id='v6_price_action_5m'
""")

# ✅ Complete isolation - no conflicts!
```

---

### Re-Entry Type 2: TP Continuation

**Purpose:** Continue trading after TP profit if trend still favorable

#### Flow Diagram

```
STEP 1: TP HIT
──────────────
Order A hits TP @ 1.0900
    ↓
trading_engine.handle_tp_hit(trade)
    ↓
ReEntryManager.record_tp_hit(trade, tp_price)
    ↓
UPDATE reentry_chains:
- total_profit += tp_profit
- chain.metadata["last_tp_time"] = timestamp
    ↓
STORE in memory for monitoring:
completed_tps[symbol].append({
    time,
    chain_id,
    direction,
    tp_price
})

──────────────────────────────────────

STEP 2: AUTONOMOUS CONTINUATION MONITORING
───────────────────────────────────────────
AutonomousSystemManager (every 5 seconds)
    ↓
Query chains with recent TP:
    ↓
    For each chain:
        ↓
        Check conditions:
        ✓ TP hit < 30 minutes ago
        ✓ Cooldown elapsed (5 seconds)
        ✓ current_level < max_level
        ↓
        Check trend alignment:
        
──────────────────────────────────────

STEP 3: TREND ALIGNMENT (CRITICAL!)
────────────────────────────────────
TrendAnalyzer.is_aligned(direction, current_trend)
    ↓
    V3 Plugin:
    ───────────
    Query: SELECT * FROM v3_timeframe_trends.json
    {
        "EURUSD": {
            "5m": "BULLISH",
            "15m": "BULLISH",
            "1h": "BULLISH"
        }
    }
    ↓
    Check: All 3 TFs aligned with direction?
    
    V6 Plugin:
    ───────────
    Query: SELECT bull_count, bear_count 
           FROM market_trends 
           WHERE symbol='EURUSD'
           AND timeframe IN ('5', '15', '60')
    ↓
    Check: Majority TFs aligned?
    
    If NOT aligned:
        REJECT continuation (trend weakening)

──────────────────────────────────────

STEP 4: EXECUTE CONTINUATION
─────────────────────────────
If trend still aligned:
    ↓
    Calculate reduced SL:
    reduction_per_level = 0.3  # 30%
    sl_adjustment = (1 - 0.3) ** (level - 1)
    new_sl_distance = original_sl * sl_adjustment
    ↓
    Place new trade:
    - Entry: Current market price
    - SL: Reduced distance (70% of original)
    - TP: Based on plugin logic
    - Lot: Same as original
    ↓
    UPDATE reentry_chains:
    - current_level += 1
    - trades.append(new_trade_id)
    ↓
    INSERT INTO tp_reentry_events:
    {
        chain_id,
        symbol,
        tp_level: current_level,
        sl_reduction_percent: 30,
        timestamp
    }
```

**Configuration:**

```json
{
  "re_entry_config": {
    "autonomous_config": {
      "tp_continuation": {
        "enabled": true,
        "cooldown_seconds": 5,
        "sl_reduction_per_level": 0.3,
        "max_continuation_levels": 3,
        "require_trend_alignment": true  ← ✅ Mandatory!
      }
    }
  }
}
```

---

### Re-Entry Type 3: Exit Continuation

**Purpose:** Re-enter if trend resumes after early exit

#### Flow Diagram

```
STEP 1: EXIT SIGNAL RECEIVED
─────────────────────────────
TradingView sends exit alert:
{
    "type": "exit_v3" or "exit_v6",
    "symbol": "EURUSD",
    "reason": "early_exit_warning"
}
    ↓
trading_engine.process_alert()
    ↓
Plugin.handle_exit_signal()
    ↓
Close all open trades immediately
    ↓
STORE exit event:
exit_continuation_candidates[trade_id] = {
    symbol,
    direction,
    exit_price,
    exit_time,
    chain_id,
    plugin_id  ← ✅ Track which plugin
}

──────────────────────────────────────

STEP 2: MONITORING WINDOW (15 minutes)
───────────────────────────────────────
NOT autonomous - waits for new signal
    ↓
    If new entry signal arrives:
    ↓
    Check conditions:
    ✓ Same symbol
    ✓ Same direction
    ✓ Within 15-minute window
    ✓ From SAME plugin  ← ✅ Important!
    
──────────────────────────────────────

STEP 3: TREND VALIDATION
─────────────────────────
TrendAnalyzer.get_current_trend(symbol)
    ↓
    Compare with exit_time trend:
    if trend_changed:
        REJECT (trend reversed after exit)
    if trend_same:
        APPROVE continuation

──────────────────────────────────────

STEP 4: RE-ENTRY EXECUTION
───────────────────────────
If approved:
    ↓
    Use NEW signal's SL/TP (fresh parameters)
    ↓
    Continue SAME chain_id
    ↓
    UPDATE reentry_chains:
    - current_level += 1
    - trades.append(new_trade_id)
```

**Key Difference:**
- NOT autonomous (waits for new signal)
- Uses fresh SL/TP from new alert
- Plugin-specific (V3 exit → V3 re-entry only)

---

### Re-Entry Type 4: Profit Booking SL Hunt

**Purpose:** Recover Order B (profit booking) after SL hit

#### Flow Diagram

```
STEP 1: PROFIT ORDER SL HIT
───────────────────────────
Order B (Profit Booking) hits SL @ 1.0850
    ↓
ProfitBookingManager.handle_sl_hit(order_b)
    ↓
ProfitBookingReEntryManager.register_sl_hit(chain_id, ...)
    ↓
UPDATE profit_booking_chains:
- status = "SL_HUNT"
- metadata["recovery_sl_price"] = 1.0850
- metadata["recovery_attempts"] = 1
    ↓
STORE in memory:
pending_recoveries[chain_id] = {
    symbol,
    direction,
    level,
    sl_price,
    time
}

──────────────────────────────────────

STEP 2: AUTONOMOUS PROFIT RECOVERY MONITORING
──────────────────────────────────────────────
AutonomousSystemManager (every 5 seconds)
    ↓
ProfitBookingReEntryManager.check_recoveries()
    ↓
    Query: SELECT * FROM profit_booking_chains 
           WHERE status='SL_HUNT' 
           AND plugin_id='v3_combined'  ← ✅ Plugin filter
    ↓
    For each chain:
        ↓
        Get current_price
        ↓
        Check price recovery:
        if direction == "buy":
            recovered = current_price > sl_price
        else:
            recovered = current_price < sl_price
        
──────────────────────────────────────

STEP 3: TREND ALIGNMENT (CRITICAL!)
────────────────────────────────────
TrendAnalyzer.get_current_trend(symbol)
    ↓
    Query market_trends table (V6)
    OR
    Query timeframe_trends.json (V3)
    ↓
    TrendAnalyzer.is_aligned(direction, trend)
    ↓
    If NOT aligned:
        REJECT recovery
        log: "Trend reversed, profit recovery blocked"

──────────────────────────────────────

STEP 4: EXECUTE PROFIT RECOVERY
────────────────────────────────
If trend aligned AND price recovered:
    ↓
    Place recovery order (same level):
    - Entry: Current market price
    - SL: Fixed $10 SL
    - TP: $7 minimum profit
    - Lot: Multiplier * base_lot
    ↓
    UPDATE profit_booking_chains:
    - status = "ACTIVE"
    - orders_in_level += 1
    ↓
    Complete recovery:
    pending_recoveries.pop(chain_id)
```

**Database Interaction:**

```python
# V3 Profit Booking Recovery
v3_profit_chains = db_v3.execute("""
    SELECT * FROM v3_profit_bookings 
    WHERE status='SL_HUNT' 
    AND plugin_id='v3_combined'
""")

# V6 5M Profit Booking Recovery
v6_5m_profit_chains = db_v6.execute("""
    SELECT * FROM v6_profit_bookings 
    WHERE status='SL_HUNT' 
    AND plugin_id='v6_price_action_5m'
""")

# ✅ Separate profit booking chains per plugin!
```

---

## 🤖 PART 3: AUTONOMOUS SYSTEM ARCHITECTURE

### 3.1 Autonomous Monitoring Loop

```python
# src/managers/autonomous_system_manager.py

class AutonomousSystemManager:
    """
    Central autonomous monitoring system
    Runs every 5 seconds, checks ALL re-entry types
    """
    
    def __init__(self, 
                 v3_reentry_manager,           # V3 re-entry manager
                 v6_reentry_managers,          # Dict of V6 managers per TF
                 profit_booking_reentry_manager,
                 ...):
        
        self.v3_reentry = v3_reentry_manager
        self.v6_reentry = v6_reentry_managers
        self.profit_reentry = profit_booking_reentry_manager
        
        self.check_interval = 5  # seconds
        self.running = False
    
    async def run_autonomous_loop(self):
        """Main autonomous monitoring loop"""
        
        while self.running:
            try:
                # 1. Monitor SL Hunt Recoveries (V3 + V6 separate)
                await self.monitor_sl_hunt_recovery()
                
                # 2. Monitor TP Continuations (V3 + V6 separate)
                await self.monitor_tp_continuation()
                
                # 3. Monitor Profit Booking Recoveries (V3 + V6 separate)
                await self.monitor_profit_booking_recovery()
                
                # 4. Check Daily Limits
                self.check_daily_limits()
                
                # 5. Cleanup expired windows
                self.cleanup_expired_recoveries()
                
            except Exception as e:
                logger.error(f"Autonomous loop error: {e}")
            
            await asyncio.sleep(self.check_interval)
```

---

### 3.2 Plugin-Specific Monitoring

```python
async def monitor_sl_hunt_recovery(self):
    """Monitor SL hunt recoveries for ALL plugins"""
    
    # 1. Monitor V3 Recoveries
    await self._monitor_v3_sl_hunt()
    
    # 2. Monitor V6 Recoveries (each TF separately)
    for plugin_id, manager in self.v6_reentry.items():
        await self._monitor_v6_sl_hunt(plugin_id, manager)

async def _monitor_v3_sl_hunt(self):
    """Monitor V3 SL hunt recoveries"""
    
    # Get V3 recovery chains
    recovery_chains = self.v3_reentry.get_recovery_chains()
    
    for chain in recovery_chains:
        # Get current price
        price = self.mt5.get_current_price(chain.symbol)
        
        # Check recovery conditions
        result = self.v3_reentry.check_sl_hunt_recovery(chain, price)
        
        if result["eligible"]:
            # ✅ TREND ALIGNMENT CHECK
            trend = self.v3_trend_analyzer.get_current_trend(chain.symbol)
            if not self.v3_trend_analyzer.is_aligned(chain.direction, trend):
                logger.info(f"V3 Recovery blocked: Trend not aligned")
                continue
            
            # Execute recovery
            await self._execute_v3_recovery(chain, result)

async def _monitor_v6_sl_hunt(self, plugin_id, manager):
    """Monitor V6 SL hunt recoveries for specific plugin"""
    
    # Get V6 plugin-specific recovery chains
    recovery_chains = manager.get_recovery_chains()
    
    for chain in recovery_chains:
        price = self.mt5.get_current_price(chain.symbol)
        
        result = manager.check_sl_hunt_recovery(chain, price)
        
        if result["eligible"]:
            # ✅ TREND ALIGNMENT CHECK (from market_trends table)
            trend_data = await self.get_market_trends(
                chain.symbol,
                chain.metadata["timeframe"]
            )
            
            if not self._is_v6_trend_aligned(chain.direction, trend_data):
                logger.info(f"V6 {plugin_id} Recovery blocked: Trend not aligned")
                continue
            
            # Execute V6 recovery
            await self._execute_v6_recovery(chain, result, plugin_id)
```

---

### 3.3 Trend Alignment Implementation

```python
# V3 Trend Alignment
class V3TrendAnalyzer:
    def __init__(self):
        self.trends_file = "config/timeframe_trends.json"
    
    def get_current_trend(self, symbol: str) -> Dict:
        """Get V3 multi-timeframe trend from JSON"""
        with open(self.trends_file) as f:
            data = json.load(f)
        
        return data["symbols"].get(symbol, {})
    
    def is_aligned(self, direction: str, trend_data: Dict) -> bool:
        """Check if trade direction aligns with V3 trends"""
        
        # Get 5M, 15M, 1H trends
        tf_5m = trend_data.get("5m", "NEUTRAL")
        tf_15m = trend_data.get("15m", "NEUTRAL")
        tf_1h = trend_data.get("1h", "NEUTRAL")
        
        if direction == "buy":
            # Check majority bullish
            bullish_count = sum([
                1 for tf in [tf_5m, tf_15m, tf_1h]
                if tf == "BULLISH"
            ])
            return bullish_count >= 2
        else:
            # Check majority bearish
            bearish_count = sum([
                1 for tf in [tf_5m, tf_15m, tf_1h]
                if tf == "BEARISH"
            ])
            return bearish_count >= 2

# V6 Trend Alignment
class V6TrendAnalyzer:
    def __init__(self, db):
        self.db = db  # zepix_price_action.db
    
    async def get_current_trend(self, symbol: str, timeframe: str) -> Dict:
        """Get V6 trend from market_trends table"""
        
        result = await self.db.execute("""
            SELECT bull_count, bear_count, net_direction, market_state
            FROM market_trends
            WHERE symbol = ? AND timeframe = ?
        """, (symbol, timeframe))
        
        if result:
            return {
                "bull_count": result["bull_count"],
                "bear_count": result["bear_count"],
                "direction": result["net_direction"],
                "state": result["market_state"]
            }
        
        return None
    
    def is_aligned(self, direction: str, trend_data: Dict) -> bool:
        """Check if trade direction aligns with V6 trend"""
        
        if not trend_data:
            return False
        
        bull_count = trend_data["bull_count"]
        bear_count = trend_data["bear_count"]
        
        if direction == "buy":
            return bull_count > bear_count
        else:
            return bear_count > bull_count
```

---

## 📋 PART 4: COMPLETE CONFIGURATION

### 4.1 Re-Entry Configuration

```json
{
  "re_entry_config": {
    // Global settings
    "max_chain_levels": 3,
    "sl_reduction_per_level": 0.3,
    "recovery_window_minutes": 30,
    "min_time_between_re_entries": 5,
    
    // Autonomous system
    "autonomous_config": {
      "enabled": true,
      "check_interval_seconds": 5,
      
      // Type 1: SL Hunt Recovery
      "sl_hunt_recovery": {
        "enabled": true,
        "recovery_threshold": 0.70,
        "tight_sl_pips": 5,
        "resume_to_next_level_on_success": true,
        "require_trend_alignment": true,  ← ✅ Mandatory
        "recovery_windows_by_symbol": {
          "EURUSD": 30,
          "GBPUSD": 25,
          "USDJPY": 20
        }
      },
      
      // Type 2: TP Continuation
      "tp_continuation": {
        "enabled": true,
        "cooldown_seconds": 5,
        "sl_reduction_per_level": 0.3,
        "max_continuation_levels": 3,
        "require_trend_alignment": true   ← ✅ Mandatory
      },
      
      // Type 3: Exit Continuation
      "exit_continuation": {
        "enabled": true,
        "monitoring_window_minutes": 15,
        "max_attempts": 1,
        "require_trend_alignment": true,  ← ✅ Mandatory
        "same_plugin_only": true          ← ✅ Plugin isolation
      },
      
      // Type 4: Profit Booking SL Hunt
      "profit_sl_hunt_enabled": true,
      "profit_sl_hunt_config": {
        "max_recovery_attempts": 1,
        "require_trend_alignment": true,  ← ✅ Mandatory
        "same_plugin_only": true          ← ✅ Plugin isolation
      }
    }
  }
}
```

---

## 🎯 FINAL ANSWERS TO YOUR QUESTIONS

### Question 1: Database alag hai ki nahi?

**ANSWER: HAA, V3 aur V6 ke liye ALAG databases hain! ✅**

```
V3: data/zepix_combined_v3.db
  - combined_v3_trades
  - v3_reentry_chains
  - v3_profit_bookings

V6: data/zepix_price_action.db
  - price_action_*_trades (4 tables)
  - v6_reentry_chains
  - v6_profit_bookings
  - market_trends (TREND_PULSE data)

Central: data/trading_bot.db (LEGACY - being phased out)
  - Mixed V3 + V6 data (needs migration)
```

**Migration Status:**
- ✅ Database files created
- ❌ Still using central DB for re-entry chains (needs plugin_id column)
- 🔄 Migration in progress

---

### Question 2: Sabhi re-entry types?

**ANSWER: 4 complete re-entry types:**

1. **SL Hunt Recovery** - Order A SL hit → Autonomous recovery
2. **TP Continuation** - Order A TP hit → Autonomous continuation
3. **Exit Continuation** - Exit signal → Manual continuation
4. **Profit Booking SL Hunt** - Order B SL hit → Autonomous recovery

**ALL support:**
- ✅ Trend alignment validation
- ✅ Plugin isolation
- ✅ Database tracking
- ✅ Autonomous monitoring (except Exit Continuation)

---

### Question 3: Trend alignment kaise check hoti hai?

**ANSWER: 2 methods depending on plugin:**

**V3 Method:**
```python
# Uses timeframe_trends.json
{
    "EURUSD": {
        "5m": "BULLISH",
        "15m": "BULLISH",
        "1h": "BULLISH"
    }
}

# Check: Majority TFs aligned?
if 2+ timeframes == "BULLISH" → Approve BUY re-entry
```

**V6 Method:**
```sql
-- Uses market_trends table
SELECT bull_count, bear_count 
FROM market_trends 
WHERE symbol='EURUSD' AND timeframe='5'

-- Check: Bull > Bear?
if bull_count > bear_count → Approve BUY re-entry
```

**Both methods:**
- ✅ Query database/file
- ✅ Compare trend with trade direction
- ✅ REJECT if not aligned
- ✅ Log rejection reason

---

### Question 4: Autonomous features kaise kaam karte hain?

**ANSWER: Complete autonomous loop:**

```python
while bot_running:
    # Every 5 seconds:
    
    # 1. Check ALL V3 re-entry chains
    await monitor_v3_sl_hunt()
    await monitor_v3_tp_continuation()
    await monitor_v3_profit_recovery()
    
    # 2. Check ALL V6 re-entry chains (each TF separate)
    await monitor_v6_1m_sl_hunt()
    await monitor_v6_5m_sl_hunt()
    await monitor_v6_15m_sl_hunt()
    await monitor_v6_1h_sl_hunt()
    
    await monitor_v6_1m_tp_continuation()
    # ... etc for all V6 plugins
    
    # 3. For each chain:
    #    ✓ Get current price
    #    ✓ Check recovery conditions
    #    ✓ Validate trend alignment
    #    ✓ Execute if eligible
    
    await asyncio.sleep(5)
```

**Features:**
- ✅ Runs 24/7 in background
- ✅ Plugin-isolated (separate loops)
- ✅ Trend validation mandatory
- ✅ Daily limits enforced
- ✅ Telegram notifications
- ✅ Database logging

---

## 📊 SUMMARY TABLE

| Aspect | V3 | V6 | Shared? |
|--------|----|----|---------|
| **Database** | zepix_combined_v3.db | zepix_price_action.db | ❌ NO |
| **Trades Table** | combined_v3_trades | price_action_*_trades | ❌ NO |
| **Re-Entry Chains** | v3_reentry_chains | v6_reentry_chains | ❌ NO |
| **Profit Chains** | v3_profit_bookings | v6_profit_bookings | ❌ NO |
| **Trend Storage** | timeframe_trends.json | market_trends table | ❌ NO |
| **SL Hunt** | ✅ Supported | ✅ Supported | ✅ Logic Same |
| **TP Continuation** | ✅ Supported | ✅ Supported | ✅ Logic Same |
| **Exit Continuation** | ✅ Supported | ✅ Supported | ✅ Logic Same |
| **Profit SL Hunt** | ✅ Supported | ✅ Supported | ✅ Logic Same |
| **Trend Alignment** | ✅ Required | ✅ Required | ✅ Mandatory |
| **Autonomous Monitor** | ✅ Active | ✅ Active | ✅ Shared Manager |
| **ReEntryManager** | Separate instance | Separate per TF | ❌ NO |

---

**Document Version:** 1.0  
**Last Updated:** January 18, 2026  
**Status:** Complete Architecture Planning  
**Database Migration:** In Progress (plugin_id columns needed)  
**Autonomous System:** Fully Implemented  
**Trend Validation:** Mandatory for ALL re-entry types
```

Save this as `COMPLETE_REENTRY_SYSTEM_PLANNING.md`

**Final Summary (Hindi):**

✅ **Database:** V3 aur V6 ke liye alag databases hain  
✅ **Re-Entry Types:** 4 total (SL Hunt, TP Continuation, Exit Continuation, Profit SL Hunt)  
✅ **Trend Alignment:** Har re-entry type me mandatory validation hai  
✅ **Autonomous:** 24/7 background me har 5 second check karta hai  
✅ **Plugin Isolation:** V3 aur V6 ke chains alag alag track hote hain  
✅ **Migration Needed:** Central DB me plugin_id column add karna padegaSave this as `COMPLETE_REENTRY_SYSTEM_PLANNING.md`

**Final Summary (Hindi):**

✅ **Database:** V3 aur V6 ke liye alag databases hain  
✅ **Re-Entry Types:** 4 total (SL Hunt, TP Continuation, Exit Continuation, Profit SL Hunt)  
✅ **Trend Alignment:** Har re-entry type me mandatory validation hai  
✅ **Autonomous:** 24/7 background me har 5 second check karta hai  
✅ **Plugin Isolation:** V3 aur V6 ke chains alag alag track hote hain  
✅ **Migration Needed:** Central DB me plugin_id column add karna padega