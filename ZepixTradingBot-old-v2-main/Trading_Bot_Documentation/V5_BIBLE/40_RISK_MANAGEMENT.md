# RISK MANAGEMENT

**Files:**
- `src/managers/risk_manager.py`
- `src/core/services/risk_management_service.py`
- `src/utils/pip_calculator.py`

**Purpose:** Risk tier management, lot sizing, and loss limit enforcement

---

## OVERVIEW

The Risk Management system enforces trading limits based on account balance tiers. It calculates appropriate lot sizes, tracks daily/lifetime losses, and prevents over-exposure.

---

## RISK TIERS

### Tier Structure

| Tier | Balance Range | Daily Loss Limit | Lifetime Loss Limit | Max Lot |
|------|---------------|------------------|---------------------|---------|
| Tier 1 | $0 - $1,000 | $50 | $200 | 0.10 |
| Tier 2 | $1,000 - $5,000 | $100 | $500 | 0.50 |
| Tier 3 | $5,000 - $10,000 | $200 | $1,000 | 1.00 |
| Tier 4 | $10,000 - $50,000 | $500 | $2,500 | 2.00 |
| Tier 5 | $50,000+ | $1,000 | $5,000 | 5.00 |

---

## LOT SIZE CALCULATION

### Formula

```python
def calculate_lot_size(self, symbol: str, sl_pips: float, 
                      account_balance: float) -> float:
    """
    Calculate lot size based on risk parameters.
    
    Formula:
    lot_size = (risk_amount) / (sl_pips * pip_value_per_std_lot)
    
    Where:
    - risk_amount = account_balance * risk_percent
    - sl_pips = distance to SL in pips
    - pip_value_per_std_lot = pip value for 1.0 lot
    """
    # Get risk tier
    tier = self.get_risk_tier(account_balance)
    risk_params = self.config["risk_tiers"][tier]
    
    # Calculate risk amount (typically 1-2% of balance)
    risk_percent = risk_params.get("risk_percent", 0.01)
    risk_amount = account_balance * risk_percent
    
    # Get pip value
    symbol_config = self.config["symbol_config"][symbol]
    pip_value_std = symbol_config["pip_value_per_std_lot"]
    
    # Calculate lot size
    lot_size = risk_amount / (sl_pips * pip_value_std)
    
    # Apply limits
    min_lot = symbol_config.get("min_lot", 0.01)
    max_lot = min(risk_params.get("max_lot", 1.0), symbol_config.get("max_lot", 10.0))
    
    return max(min_lot, min(lot_size, max_lot))
```

---

## LOSS TRACKING

### Daily Loss Tracking

```python
class RiskManager:
    def __init__(self, config):
        self.config = config
        self.daily_loss = 0.0
        self.lifetime_loss = 0.0
        self.last_reset_date = datetime.now().date()
    
    def record_loss(self, amount: float):
        """Record a trading loss"""
        self.daily_loss += amount
        self.lifetime_loss += amount
    
    def check_daily_limit(self, account_balance: float) -> bool:
        """Check if daily loss limit reached"""
        tier = self.get_risk_tier(account_balance)
        limit = self.config["risk_tiers"][tier]["daily_loss_limit"]
        return self.daily_loss < limit
    
    def check_lifetime_limit(self, account_balance: float) -> bool:
        """Check if lifetime loss limit reached"""
        tier = self.get_risk_tier(account_balance)
        limit = self.config["risk_tiers"][tier]["max_total_loss"]
        return self.lifetime_loss < limit
    
    def reset_daily_loss(self):
        """Reset daily loss counter (called at day rollover)"""
        self.daily_loss = 0.0
        self.last_reset_date = datetime.now().date()
```

---

## SL SYSTEMS

### Dual SL System

The bot uses a dual SL system with two configurations:

**SL-1 (Conservative):**
- Wider SL for volatile conditions
- Used during high-impact news

**SL-2 (Aggressive):**
- Tighter SL for normal conditions
- Default system

```python
{
    "sl_systems": {
        "sl-1": {
            "symbols": {
                "EURUSD": {
                    "tier1": {"sl_pips": 30},
                    "tier2": {"sl_pips": 35},
                    "tier3": {"sl_pips": 40}
                }
            }
        },
        "sl-2": {
            "symbols": {
                "EURUSD": {
                    "tier1": {"sl_pips": 20},
                    "tier2": {"sl_pips": 25},
                    "tier3": {"sl_pips": 30}
                }
            }
        }
    },
    "active_sl_system": "sl-2"
}
```

---

## VALIDATION

### Trade Validation

```python
def validate_trade(self, trade: Trade, account_balance: float) -> Dict[str, Any]:
    """
    Validate if trade passes all risk checks.
    
    Checks:
    1. Daily loss limit
    2. Lifetime loss limit
    3. Max concurrent trades
    4. Symbol exposure limit
    5. Lot size within limits
    """
    result = {"valid": True, "errors": []}
    
    # Check daily limit
    if not self.check_daily_limit(account_balance):
        result["valid"] = False
        result["errors"].append("Daily loss limit reached")
    
    # Check lifetime limit
    if not self.check_lifetime_limit(account_balance):
        result["valid"] = False
        result["errors"].append("Lifetime loss limit reached")
    
    # Check concurrent trades
    if self.open_trade_count >= self.config.get("max_concurrent_trades", 10):
        result["valid"] = False
        result["errors"].append("Max concurrent trades reached")
    
    # Check lot size
    tier = self.get_risk_tier(account_balance)
    max_lot = self.config["risk_tiers"][tier].get("max_lot", 1.0)
    if trade.lot_size > max_lot:
        result["valid"] = False
        result["errors"].append(f"Lot size {trade.lot_size} exceeds max {max_lot}")
    
    return result
```

---

## CONFIGURATION

```python
{
    "risk_tiers": {
        "tier1": {
            "min_balance": 0,
            "max_balance": 1000,
            "risk_percent": 0.01,
            "daily_loss_limit": 50,
            "max_total_loss": 200,
            "max_lot": 0.10,
            "max_concurrent_trades": 3
        },
        "tier2": {
            "min_balance": 1000,
            "max_balance": 5000,
            "risk_percent": 0.015,
            "daily_loss_limit": 100,
            "max_total_loss": 500,
            "max_lot": 0.50,
            "max_concurrent_trades": 5
        }
    },
    "symbol_config": {
        "EURUSD": {
            "pip_size": 0.0001,
            "pip_value_per_std_lot": 10.0,
            "min_lot": 0.01,
            "max_lot": 10.0
        }
    }
}
```

---

## RELATED FILES

- `src/core/trading_engine.py` - Uses RiskManager
- `src/managers/dual_order_manager.py` - Risk validation for dual orders
- `src/utils/pip_calculator.py` - Pip calculations
