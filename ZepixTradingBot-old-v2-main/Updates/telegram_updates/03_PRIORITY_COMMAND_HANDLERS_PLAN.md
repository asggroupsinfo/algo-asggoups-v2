# PHASE 3: PRIORITY COMMAND HANDLERS

**Phase:** 3 of 6  
**Priority:** HIGH  
**Timeline:** Week 3-4 (32 hours)  
**Status:** Planning  
**Dependencies:** Phase 2 (V6 Timeframe Menu)

---

## OBJECTIVE

Implement top 20 most-critical command handlers to provide:
1. Plugin-aware status and control commands
2. V3 vs V6 performance comparison
3. Re-entry chain management
4. Risk management controls
5. On-demand analytics triggers
6. V6 timeframe toggle commands

---

## CURRENT STATE

### Commands Implemented ✅ (28 commands)

**File:** `Trading_Bot/src/telegram/controller_bot.py`

1. System: `/start`, `/status`, `/pause`, `/resume`, `/help`, `/health`, `/version`, `/config`
2. Plugin: `/plugin`, `/plugins`, `/enable`, `/disable`, `/upgrade`, `/rollback`
3. Trading: `/positions`, `/pnl`, `/balance`, `/trade`, `/close`, `/closeall`
4. Strategy: `/logic1`, `/logic2`, `/logic3`, `/v3`, `/v6`, `/signals`

### Commands Missing ❌ (67+ commands)

**Documented but NOT implemented:**

**Trading (9):** `/buy`, `/sell`, `/orders`, `/history`, `/trades`, `/margin`, `/lot`, `/price`, `/spread`  
**Risk (12):** `/risk`, `/setlot`, `/setsl`, `/settp`, `/dailylimit`, `/maxloss`, `/maxprofit`, `/risktier`, `/slsystem`, `/trailsl`, `/breakeven`, `/protection`  
**Timeframe (8):** `/timeframe`, `/tf1m`, `/tf5m`, `/tf15m`, `/tf1h`, `/tf4h`, `/tf1d`, `/trends`  
**Re-entry (8):** `/reentry`, `/slhunt`, `/tpcontinue`, `/recovery`, `/cooldown`, `/chains`, `/autonomous`, `/chainlimit`  
**Profit Booking (6):** `/profit`, `/booking`, `/levels`, `/partial`, `/orderb`, `/dualorder`  
**Analytics (8):** `/analytics`, `/performance`, `/daily`, `/weekly`, `/monthly`, `/report`, `/winrate`, `/drawdown`  
**Session (6):** `/session`, `/london`, `/newyork`, `/tokyo`, `/sydney`, `/overlap`  
**Voice (4):** `/voice`, `/voicetest`, `/mute`, `/unmute`  
**Compare (2):** `/shadow`, `/compare`  
**Fine-tune (4):** Various parameters

---

## PRIORITY RANKING

### Tier 1: CRITICAL (Must Have - Week 3)

**Impact:** Essential for V5 functionality  
**User Need:** Daily operations  
**Complexity:** Low-Medium

| # | Command | Description | Effort | User Benefit |
|---|---------|-------------|--------|--------------|
| 1 | `/status` | Enhanced with V3 vs V6 breakdown | 2h | See which plugins are active/performing |
| 2 | `/positions` | Filter by plugin (V3/V6/specific timeframe) | 3h | Know which plugin opened which trade |
| 3 | `/pnl` | Per-plugin P&L breakdown | 3h | Track V3 vs V6 profitability |
| 4 | `/chains` | Re-entry chain status for all plugins | 4h | Monitor autonomous re-entry system |
| 5 | `/daily` | Trigger daily analytics report | 2h | On-demand performance review |
| 6 | `/weekly` | Trigger weekly analytics report | 2h | Weekly performance summary |
| 7 | `/compare` | V3 vs V6 performance comparison | 4h | Make data-driven plugin decisions |
| 8 | `/setlot` | Set lot size (global or per-plugin) | 3h | Adjust risk without config file |
| 9 | `/risktier` | Change risk tier (Aggressive/Balanced/Conservative) | 3h | Quick risk adjustment |
| 10 | `/autonomous` | Toggle autonomous re-entry system | 2h | Enable/disable re-entry chains |

**Total:** 28 hours

### Tier 2: IMPORTANT (Should Have - Week 4)

**Impact:** Enhanced functionality  
**User Need:** Weekly operations  
**Complexity:** Medium

| # | Command | Description | Effort | User Benefit |
|---|---------|-------------|--------|--------------|
| 11 | `/tf15m` | Toggle V6 15M plugin | 1h | Quick timeframe enable/disable |
| 12 | `/tf30m` | Toggle V6 30M plugin | 1h | Quick timeframe enable/disable |
| 13 | `/tf1h` | Toggle V6 1H plugin | 1h | Quick timeframe enable/disable |
| 14 | `/tf4h` | Toggle V6 4H plugin | 1h | Quick timeframe enable/disable |
| 15 | `/slhunt` | SL Hunt recovery system status | 2h | Monitor SL Hunt performance |
| 16 | `/tpcontinue` | TP Continuation system status | 2h | Monitor TP Continuation |
| 17 | `/reentry` | Re-entry system overview | 2h | Complete re-entry status |
| 18 | `/levels` | Profit booking levels status | 2h | Monitor profit booking |
| 19 | `/shadow` | Shadow mode status & comparison | 3h | Compare live vs shadow |
| 20 | `/trends` | Multi-timeframe trend overview | 2h | See all timeframe trends |

**Total:** 20 hours

### Tier 3: NICE TO HAVE (Future)

**Commands for later phases:**
- Session management: `/london`, `/newyork`, `/tokyo`
- Voice: `/voice`, `/voicetest`, `/mute`, `/unmute`
- Advanced risk: `/trailsl`, `/breakeven`, `/protection`
- Fine-tuning: Parameter adjustments

---

## DETAILED COMMAND SPECIFICATIONS

### 1. Enhanced `/status` Command

**Current Implementation:**
```
🤖 BOT STATUS

Status: ✅ Running
Uptime: 2 days, 5 hours
Active Plugins: 2
Open Positions: 3
```

**New V5 Implementation:**
```
🤖 BOT STATUS - V5 HYBRID

⏱️ SYSTEM
├─ Status: ✅ Running
├─ Uptime: 2 days, 5 hours
└─ Last Restart: Jan 17, 10:30 AM

🔌 ACTIVE PLUGINS
├─ V3 Combined Logic: ✅ Enabled
│  └─ LOGIC1(5m) ✅ | LOGIC2(15m) ✅ | LOGIC3(1h) ✅
└─ V6 Price Action: ✅ Enabled
   └─ 15M ✅ | 30M ✅ | 1H ✅ | 4H ❌

📊 TODAY'S PERFORMANCE
├─ V3: 5 trades | 60% WR | +$25.00
├─ V6: 8 trades | 75% WR | +$60.00
└─ Total: 13 trades | 69% WR | +$85.00

💼 OPEN POSITIONS
├─ V3: 2 positions | +$5.00 unrealized
└─ V6: 1 position | +$10.00 unrealized

⚡ QUICK ACTIONS
[Pause All] [V3 Only] [V6 Only] [Refresh]
```

**Implementation:**
```python
def handle_status(self, message: Dict = None) -> Optional[int]:
    """Enhanced status with V3 vs V6 breakdown"""
    
    # Get system status
    uptime = self._calculate_uptime()
    
    # Get plugin status
    v3_status = self._get_v3_plugin_status()
    v6_status = self._get_v6_timeframe_status()
    
    # Get performance metrics
    today_stats = self._get_today_performance_by_plugin()
    
    # Get open positions
    positions = self._get_positions_by_plugin()
    
    # Format message
    message = self._format_enhanced_status(
        uptime, v3_status, v6_status, today_stats, positions
    )
    
    # Build keyboard
    keyboard = self._build_status_keyboard()
    
    return self.send_message(message, reply_markup=keyboard)
```

---

### 2. Plugin-Aware `/positions` Command

**Current Implementation:**
```
📊 OPEN POSITIONS (3)

1. EURUSD BUY
   Entry: 1.08450 | SL: 1.08350 | TP: 1.08650
   P&L: +$5.00 (+5.0 pips)

2. GBPUSD SELL
   Entry: 1.26800 | SL: 1.26900 | TP: 1.26600
   P&L: +$10.00 (+10.0 pips)

3. USDJPY BUY
   Entry: 148.50 | SL: 148.30 | TP: 148.90
   P&L: -$2.00 (-2.0 pips)
```

**New V5 Implementation:**
```
📊 OPEN POSITIONS (3)

🔵 V3 POSITIONS (2)
┌─ #1: EURUSD BUY
│  ├─ Plugin: V3-LOGIC1 (5m)
│  ├─ Entry: 1.08450 @ 14:30
│  ├─ Current: 1.08500 (+50 pips)
│  ├─ SL: 1.08350 | TP: 1.08650
│  └─ P&L: +$5.00 🟢
│
└─ #2: GBPUSD SELL
   ├─ Plugin: V3-LOGIC2 (15m)
   ├─ Entry: 1.26800 @ 12:15
   ├─ Current: 1.26700 (+100 pips)
   ├─ SL: 1.26900 | TP: 1.26600
   └─ P&L: +$10.00 🟢

🟢 V6 POSITIONS (1)
└─ #3: USDJPY BUY
   ├─ Plugin: V6-1H
   ├─ Entry: 148.50 @ 11:00
   ├─ Current: 148.30 (-20 pips)
   ├─ SL: 148.30 | TP: 148.90
   ├─ Pattern: Bullish Engulfing
   └─ P&L: -$2.00 🔴

💰 TOTAL: +$13.00 (+128 pips)

⚡ FILTERS
[V3 Only] [V6 Only] [By Symbol] [Close All]
```

**Command Variations:**
- `/positions` - All positions
- `/positions v3` - V3 positions only
- `/positions v6` - V6 positions only
- `/positions 15m` - V6 15M positions only
- `/positions EURUSD` - EURUSD positions only

**Implementation:**
```python
def handle_positions(self, message: Dict = None, filter: str = None) -> Optional[int]:
    """Show positions with plugin filtering"""
    
    # Get all positions
    all_positions = self.trading_engine.get_open_positions()
    
    # Apply filter
    if filter == 'v3':
        positions = [p for p in all_positions if 'v3' in p['plugin_name'].lower()]
    elif filter == 'v6':
        positions = [p for p in all_positions if 'v6' in p['plugin_name'].lower()]
    elif filter in ['15m', '30m', '1h', '4h']:
        positions = [p for p in all_positions if filter in p['plugin_name'].lower()]
    elif filter:  # Symbol filter
        positions = [p for p in all_positions if p['symbol'] == filter.upper()]
    else:
        positions = all_positions
    
    # Format message
    message = self._format_positions_by_plugin(positions)
    
    # Build filter keyboard
    keyboard = self._build_position_filter_keyboard()
    
    return self.send_message(message, reply_markup=keyboard)
```

---

### 3. Per-Plugin `/pnl` Command

**Current Implementation:**
```
💰 P&L SUMMARY

Today: +$85.00
This Week: +$420.00
This Month: +$1,250.00
All Time: +$3,500.00
```

**New V5 Implementation:**
```
💰 P&L SUMMARY - V5 HYBRID

📅 TODAY (+$85.00)
├─ V3 Combined: +$25.00 (29%)
│  ├─ LOGIC1 (5m): +$10.00
│  ├─ LOGIC2 (15m): +$15.00
│  └─ LOGIC3 (1h): $0.00
└─ V6 Price Action: +$60.00 (71%) 🏆
   ├─ 15M: +$20.00
   ├─ 30M: +$15.00
   ├─ 1H: +$25.00 🏆 BEST
   └─ 4H: $0.00

📊 THIS WEEK (+$420.00)
├─ V3: +$180.00 (43%)
└─ V6: +$240.00 (57%) 🏆

📈 THIS MONTH (+$1,250.00)
├─ V3: +$550.00 (44%)
└─ V6: +$700.00 (56%) 🏆

🔍 INSIGHTS
├─ Best Performer: V6-1H (+$25.00 today)
├─ Worst Performer: V3-LOGIC3 ($0.00 today)
└─ Recommendation: Consider disabling LOGIC3

⚡ ACTIONS
[View Details] [Export CSV] [V3 Report] [V6 Report]
```

**Command Variations:**
- `/pnl` - Overall P&L with breakdown
- `/pnl v3` - V3 P&L only
- `/pnl v6` - V6 P&L only
- `/pnl today` - Today only
- `/pnl week` - This week
- `/pnl month` - This month

---

### 4. `/chains` Re-entry Chain Status

**New Command:**
```
🔗 RE-ENTRY CHAIN STATUS

🎯 ACTIVE CHAINS (3)

┌─ EURUSD Chain #1
│  ├─ Type: SL Hunt Recovery
│  ├─ Plugin: V6-1H
│  ├─ Started: Jan 19, 14:30
│  ├─ Original Loss: -$10.00
│  ├─ Recovery Progress: $5.00 / $10.00 (50%)
│  ├─ Recovery Trades: 2 / Max 5
│  ├─ Status: 🟢 Active
│  └─ Next Entry: Waiting for price @ 1.08400
│
├─ GBPUSD Chain #2
│  ├─ Type: TP Continuation
│  ├─ Plugin: V3-LOGIC2
│  ├─ Started: Jan 19, 12:00
│  ├─ Original Profit: +$15.00
│  ├─ Additional Profit: +$10.00
│  ├─ Continuation Trades: 1 / Max 3
│  ├─ Status: 🟡 Cooldown (5 min remaining)
│  └─ Next Entry: Cooldown active
│
└─ USDJPY Chain #3
   ├─ Type: Profit Booking SL Hunt
   ├─ Plugin: V6-30M
   ├─ Started: Jan 19, 11:00
   ├─ Original Trade: +$20.00
   ├─ SL Hunt Loss: -$5.00
   ├─ Recovery Progress: $3.00 / $5.00 (60%)
   ├─ Recovery Trades: 1 / Max 3
   ├─ Status: 🟢 Active
   └─ Next Entry: Ready, watching 148.30

📊 STATISTICS (Last 7 Days)
├─ Total Chains: 18
├─ Successful Recovery: 14 (78%)
├─ Failed Recovery: 2 (11%)
├─ In Progress: 2 (11%)
├─ Total Recovered: +$140.00
└─ Avg Recovery Time: 2.5 hours

⚡ ACTIONS
[Pause All Chains] [SL Hunt Only] [TP Continue Only]
[View History] [Settings]
```

**Implementation:**
```python
def handle_chains(self, message: Dict = None) -> Optional[int]:
    """Show all active re-entry chains"""
    
    # Get active chains from database
    active_chains = self.reentry_manager.get_active_chains()
    
    # Get chain statistics
    stats = self.reentry_manager.get_chain_statistics(days=7)
    
    # Format message
    message = self._format_chain_status(active_chains, stats)
    
    # Build keyboard
    keyboard = self._build_chain_management_keyboard()
    
    return self.send_message(message, reply_markup=keyboard)
```

---

### 5. `/daily` Analytics Trigger

**New Command:**
```
📊 TRIGGERING DAILY REPORT...

Generating report for: January 19, 2026

⏳ Analyzing:
├─ ✅ Trade performance
├─ ✅ Plugin breakdown
├─ ✅ Risk metrics
├─ ✅ Win rate statistics
└─ ✅ Top performers

📬 Report will be sent by Analytics Bot in ~10 seconds

[View Last Report] [Cancel]
```

**Then Analytics Bot sends:**
```
📊 DAILY PERFORMANCE REPORT
━━━━━━━━━━━━━━━━━━━━━━━━
Date: January 19, 2026

📈 TRADE SUMMARY
├─ Total Trades: 13
├─ Winners: 9 (69.2%)
├─ Losers: 4 (30.8%)
├─ Total P&L: +$85.00
└─ Total Pips: +42.5 pips

🔌 PLUGIN BREAKDOWN
┌─ V3 Combined Logic
│  ├─ Trades: 5
│  ├─ Win Rate: 60.0%
│  ├─ P&L: +$25.00
│  └─ Pips: +12.5 pips
│
└─ V6 Price Action
   ├─ Trades: 8
   ├─ Win Rate: 75.0%
   ├─ P&L: +$60.00
   └─ Pips: +30.0 pips

🏆 TOP PERFORMERS
├─ #1: V6-1H (4 trades, 100% WR, +$40.00)
├─ #2: V6-15M (3 trades, 66% WR, +$15.00)
└─ #3: V3-LOGIC2 (2 trades, 100% WR, +$20.00)

⚠️ UNDERPERFORMERS
├─ V3-LOGIC3 (0 trades)
└─ V6-4H (1 trade, 0% WR, -$5.00)

[Export CSV] [Weekly Report] [Monthly Report]
```

---

### 6. `/compare` V3 vs V6 Comparison

**New Command:**
```
⚖️ V3 vs V6 COMPARISON

Period: Last 7 Days

┌─ 🔵 V3 COMBINED LOGIC
│  ├─ Total Trades: 28
│  ├─ Win Rate: 64.3%
│  ├─ Total P&L: +$180.00
│  ├─ Avg per Trade: +$6.43
│  ├─ Best Day: +$45.00 (Jan 17)
│  ├─ Worst Day: -$10.00 (Jan 15)
│  └─ Max Drawdown: -$15.00
│
└─ 🟢 V6 PRICE ACTION
   ├─ Total Trades: 42
   ├─ Win Rate: 71.4%
   ├─ Total P&L: +$240.00
   ├─ Avg per Trade: +$5.71
   ├─ Best Day: +$60.00 (Jan 19) 🏆
   ├─ Worst Day: -$5.00 (Jan 16)
   └─ Max Drawdown: -$8.00

📊 HEAD-TO-HEAD
├─ Total Trades: V6 +50%
├─ Win Rate: V6 +7.1% 🏆
├─ Total Profit: V6 +$60.00 🏆
├─ Avg per Trade: V3 +$0.72
├─ Best Day: V6 +$15.00 🏆
├─ Max Drawdown: V6 -$7.00 🏆
└─ Consistency: V6 (lower drawdown)

💡 RECOMMENDATION
V6 Price Action is outperforming V3:
├─ Higher win rate (+7.1%)
├─ More total profit (+$60.00)
├─ Better risk control (lower drawdown)
└─ More trade opportunities (+50%)

Consider allocating more risk to V6 or
reducing V3 exposure.

⚡ ACTIONS
[Switch to V6 Only] [Increase V6 Lot Size]
[View Details] [Export Comparison]
```

---

### 7. `/setlot` Lot Size Control

**New Command:**
```
💼 SET LOT SIZE

Current Configuration:
├─ V3 Combined: 0.01 lots
└─ V6 Price Action: 0.01 lots

Select action:

[Global Lot Size] - Set for all plugins
[V3 Lot Size] - Set for V3 only
[V6 Lot Size] - Set for V6 only
[Per-Timeframe] - Set per V6 timeframe

[Cancel]
```

**If "Global Lot Size" selected:**
```
💼 SET GLOBAL LOT SIZE

Current: 0.01 lots

Choose new lot size:

[0.01] [0.02] [0.03] [0.05]
[0.10] [0.20] [0.50] [1.00]

[Custom] [Cancel]

⚠️ This will apply to ALL plugins
(V3 and all V6 timeframes)
```

**If "Per-Timeframe" selected:**
```
💼 V6 TIMEFRAME LOT SIZES

┌─ 15M: 0.01 lots [Change]
├─ 30M: 0.01 lots [Change]
├─ 1H: 0.02 lots [Change]
└─ 4H: 0.03 lots [Change]

V3: 0.01 lots [Change]

[Save Changes] [Reset All] [Cancel]
```

**Implementation:**
```python
def handle_setlot(self, message: Dict = None, args: List[str] = None) -> Optional[int]:
    """Set lot size with plugin-aware options"""
    
    if not args:
        # Show lot size menu
        return self._show_lot_size_menu(message['chat']['id'])
    
    # Parse arguments
    scope = args[0]  # 'global', 'v3', 'v6', 'v6_15m', etc.
    lot_size = float(args[1])
    
    # Validate lot size
    if lot_size < 0.01 or lot_size > 10:
        return self.send_message("❌ Invalid lot size. Must be between 0.01 and 10.00")
    
    # Apply lot size
    if scope == 'global':
        self.risk_manager.set_global_lot_size(lot_size)
    elif scope == 'v3':
        self.risk_manager.set_plugin_lot_size('v3_combined', lot_size)
    elif scope.startswith('v6_'):
        timeframe = scope.replace('v6_', '')
        self.risk_manager.set_plugin_lot_size(f'v6_price_action_{timeframe}', lot_size)
    
    # Confirmation
    return self.send_message(f"✅ Lot size updated: {scope} → {lot_size} lots")
```

---

## IMPLEMENTATION STRATEGY

### File Structure

**Primary File:** `Trading_Bot/src/telegram/controller_bot.py`

**New Methods to Add:**
```python
class ControllerBot(BaseTelegramBot):
    # ... existing methods ...
    
    # TIER 1 COMMANDS:
    def handle_status(self, message: Dict = None) -> Optional[int]:
        """Enhanced status with V3 vs V6 breakdown"""
        pass
    
    def handle_positions(self, message: Dict = None, filter: str = None) -> Optional[int]:
        """Show positions with plugin filtering"""
        pass
    
    def handle_pnl(self, message: Dict = None, scope: str = None) -> Optional[int]:
        """Per-plugin P&L breakdown"""
        pass
    
    def handle_chains(self, message: Dict = None) -> Optional[int]:
        """Show all active re-entry chains"""
        pass
    
    def handle_daily(self, message: Dict = None) -> Optional[int]:
        """Trigger daily analytics report"""
        pass
    
    def handle_weekly(self, message: Dict = None) -> Optional[int]:
        """Trigger weekly analytics report"""
        pass
    
    def handle_compare(self, message: Dict = None) -> Optional[int]:
        """V3 vs V6 performance comparison"""
        pass
    
    def handle_setlot(self, message: Dict = None, args: List[str] = None) -> Optional[int]:
        """Set lot size with plugin-aware options"""
        pass
    
    def handle_risktier(self, message: Dict = None, tier: str = None) -> Optional[int]:
        """Change risk tier"""
        pass
    
    def handle_autonomous(self, message: Dict = None, action: str = None) -> Optional[int]:
        """Toggle autonomous re-entry system"""
        pass
    
    # TIER 2 COMMANDS:
    def handle_tf15m(self, message: Dict = None) -> Optional[int]:
        """Toggle V6 15M plugin"""
        pass
    
    def handle_tf30m(self, message: Dict = None) -> Optional[int]:
        """Toggle V6 30M plugin"""
        pass
    
    def handle_tf1h(self, message: Dict = None) -> Optional[int]:
        """Toggle V6 1H plugin"""
        pass
    
    def handle_tf4h(self, message: Dict = None) -> Optional[int]:
        """Toggle V6 4H plugin"""
        pass
    
    def handle_slhunt(self, message: Dict = None) -> Optional[int]:
        """SL Hunt recovery system status"""
        pass
    
    def handle_tpcontinue(self, message: Dict = None) -> Optional[int]:
        """TP Continuation system status"""
        pass
    
    def handle_reentry(self, message: Dict = None) -> Optional[int]:
        """Re-entry system overview"""
        pass
    
    def handle_levels(self, message: Dict = None) -> Optional[int]:
        """Profit booking levels status"""
        pass
    
    def handle_shadow(self, message: Dict = None) -> Optional[int]:
        """Shadow mode status & comparison"""
        pass
    
    def handle_trends(self, message: Dict = None) -> Optional[int]:
        """Multi-timeframe trend overview"""
        pass
```

### Command Registry Integration

**File:** `Trading_Bot/src/telegram/command_registry.py`

**Required Changes:**
```python
COMMAND_REGISTRY = {
    # ... existing commands ...
    
    # TIER 1 COMMANDS (UPDATE):
    '/status': {
        'handler': 'handle_status',
        'category': 'System',
        'description': 'Enhanced bot status with V3 vs V6 breakdown',
        'version': '2.0'  # Updated
    },
    '/positions': {
        'handler': 'handle_positions',
        'category': 'Trading',
        'description': 'Show positions with plugin filtering',
        'version': '2.0',  # Updated
        'args': ['filter?']  # Optional filter
    },
    '/pnl': {
        'handler': 'handle_pnl',
        'category': 'Trading',
        'description': 'Per-plugin P&L breakdown',
        'version': '2.0',  # Updated
        'args': ['scope?']  # Optional scope
    },
    
    # TIER 1 COMMANDS (NEW):
    '/chains': {
        'handler': 'handle_chains',
        'category': 'Re-entry',
        'description': 'Re-entry chain status for all plugins',
        'version': '1.0'
    },
    '/daily': {
        'handler': 'handle_daily',
        'category': 'Analytics',
        'description': 'Trigger daily analytics report',
        'version': '1.0'
    },
    '/weekly': {
        'handler': 'handle_weekly',
        'category': 'Analytics',
        'description': 'Trigger weekly analytics report',
        'version': '1.0'
    },
    '/compare': {
        'handler': 'handle_compare',
        'category': 'Analytics',
        'description': 'V3 vs V6 performance comparison',
        'version': '1.0'
    },
    '/setlot': {
        'handler': 'handle_setlot',
        'category': 'Risk',
        'description': 'Set lot size (global or per-plugin)',
        'version': '1.0',
        'args': ['scope?', 'value?']
    },
    '/risktier': {
        'handler': 'handle_risktier',
        'category': 'Risk',
        'description': 'Change risk tier',
        'version': '1.0',
        'args': ['tier?']
    },
    '/autonomous': {
        'handler': 'handle_autonomous',
        'category': 'Re-entry',
        'description': 'Toggle autonomous re-entry system',
        'version': '1.0',
        'args': ['action?']
    },
    
    # TIER 2 COMMANDS (NEW):
    '/tf15m': {
        'handler': 'handle_tf15m',
        'category': 'Plugin',
        'description': 'Toggle V6 15M plugin',
        'version': '1.0'
    },
    '/tf30m': {
        'handler': 'handle_tf30m',
        'category': 'Plugin',
        'description': 'Toggle V6 30M plugin',
        'version': '1.0'
    },
    '/tf1h': {
        'handler': 'handle_tf1h',
        'category': 'Plugin',
        'description': 'Toggle V6 1H plugin',
        'version': '1.0'
    },
    '/tf4h': {
        'handler': 'handle_tf4h',
        'category': 'Plugin',
        'description': 'Toggle V6 4H plugin',
        'version': '1.0'
    },
    # ... rest of Tier 2 commands ...
}
```

---

## TESTING PLAN

### Unit Tests

**Test File:** `tests/telegram/test_priority_commands.py`

**Test Cases (50+ tests):**
1. `test_status_command()` - Basic status display
2. `test_status_with_v3_enabled()` - V3 section shown
3. `test_status_with_v6_enabled()` - V6 section shown
4. `test_status_with_both_enabled()` - Both sections shown
5. `test_positions_no_filter()` - All positions
6. `test_positions_v3_filter()` - V3 positions only
7. `test_positions_v6_filter()` - V6 positions only
8. `test_positions_timeframe_filter()` - Specific timeframe
9. `test_pnl_overall()` - Overall P&L
10. `test_pnl_v3_only()` - V3 P&L
11. `test_pnl_v6_only()` - V6 P&L
12. `test_chains_active()` - Active chains display
13. `test_chains_empty()` - No active chains
14. `test_daily_trigger()` - Analytics trigger
15. `test_compare_v3_vs_v6()` - Comparison display
16. `test_setlot_global()` - Global lot size
17. `test_setlot_per_plugin()` - Per-plugin lot size
18. `test_risktier_change()` - Risk tier change
19. `test_autonomous_toggle()` - Re-entry toggle
20. `test_tf_commands()` - Timeframe toggle commands

### Integration Tests

**Test Scenarios:**
1. User sends `/status` → Receives V3 + V6 breakdown
2. User sends `/positions v6` → Receives only V6 positions
3. User sends `/pnl` → Receives per-plugin P&L
4. User sends `/chains` → Receives active chain status
5. User sends `/daily` → Analytics Bot sends report
6. User sends `/compare` → Receives V3 vs V6 comparison
7. User sends `/setlot global 0.02` → Lot size updated for all
8. User sends `/tf1h` → V6 1H plugin toggled
9. All commands work without errors
10. All commands return formatted messages

### End-to-End Test

```
1. Start with V3 enabled, V6 disabled
2. Send /status → See V3 active, V6 disabled
3. Enable V6 via menu
4. Send /status → See both active
5. Open trades with both plugins
6. Send /positions → See V3 and V6 positions
7. Send /positions v6 → See only V6 positions
8. Send /pnl → See per-plugin breakdown
9. Send /compare → See V3 vs V6 comparison
10. Send /tf1h → Disable V6 1H
11. Send /status → See V6 1H disabled
12. Send /setlot v6 0.02 → V6 lot size updated
13. Verify new V6 trades use 0.02 lots
```

---

## SUCCESS CRITERIA

### Must Have ✅
- [ ] All Tier 1 commands (10) implemented and tested
- [ ] Enhanced `/status` shows V3 vs V6 breakdown
- [ ] `/positions` can filter by plugin
- [ ] `/pnl` shows per-plugin breakdown
- [ ] `/compare` shows V3 vs V6 head-to-head
- [ ] `/setlot` supports per-plugin configuration
- [ ] `/daily` triggers Analytics Bot report
- [ ] All commands return properly formatted messages
- [ ] No errors in production

### Should Have 📋
- [ ] All Tier 2 commands (10) implemented
- [ ] Timeframe toggle commands (`/tf15m`, etc.)
- [ ] Re-entry system commands (`/slhunt`, `/tpcontinue`)
- [ ] Shadow mode command (`/shadow`)
- [ ] Trend overview command (`/trends`)
- [ ] Interactive keyboards for all commands
- [ ] Confirmation dialogs for risky actions

### Nice to Have 🎁
- [ ] Export capabilities (CSV, PDF)
- [ ] Scheduled analytics reports
- [ ] Advanced filtering options
- [ ] Voice confirmation for critical commands
- [ ] Command usage statistics

---

## ROLLOUT STRATEGY

### Week 3: Tier 1 Commands
**Days 1-2:** Implement `/status`, `/positions`, `/pnl`
**Days 3-4:** Implement `/chains`, `/daily`, `/weekly`, `/compare`
**Days 5-6:** Implement `/setlot`, `/risktier`, `/autonomous`
**Day 7:** Unit testing

### Week 4: Tier 2 Commands
**Days 1-2:** Implement timeframe commands (`/tf15m`, `/tf30m`, `/tf1h`, `/tf4h`)
**Days 3-4:** Implement re-entry commands (`/slhunt`, `/tpcontinue`, `/reentry`)
**Days 5-6:** Implement remaining commands (`/levels`, `/shadow`, `/trends`)
**Day 7:** Integration testing, beta user testing

### Deployment
**Phase 1:** Enable for beta users (commands active)
**Phase 2:** Monitor usage and errors for 48 hours
**Phase 3:** Enable for all users

---

## DOCUMENT VERSION

**Version:** 1.0  
**Created:** January 19, 2026  
**Last Updated:** January 19, 2026  
**Status:** Ready for Implementation  
**Approved By:** Pending

---

**Previous:** [02_V6_TIMEFRAME_MENU_PLAN.md](02_V6_TIMEFRAME_MENU_PLAN.md)  
**Next:** [04_ANALYTICS_INTERFACE_PLAN.md](04_ANALYTICS_INTERFACE_PLAN.md)

---

## ⚠️ DEVELOPER NOTE - IMPORTANT

**Bot Source Code Location:**  
`C:\Users\Ansh Shivaay Gupta\Downloads\ZepixTradingBot-New-v1\ZepixTradingBot-old-v2-main\Trading_Bot`

### Implementation Guidelines:

> ⚠️ **This is a Planning & Research Document - DO NOT Apply Blindly!**

**Implementation Process:**

1. **First, Complete Scan of the Bot**
   - Analyze the complete bot code
   - Understand the current architecture
   - Review existing implementations

2. **Map Ideas According to the Bot**
   - Check how the ideas given here will be implemented in the bot
   - Identify dependencies
   - Look for conflicts

3. **Create New Plan According to the Bot**
   - Create a new implementation plan according to the bot's current state
   - Adapt ideas that don't directly fit

4. **Make Improvements (Full Freedom)**
   - You have full freedom to improve the ideas
   - Use a better approach if available
   - Optimize according to the bot's architecture

5. **Then Implement**
   - Implement only after planning is complete

### Critical Rules:

| Rule | Description |
|------|-------------|
| ✅ **Idea Must Be Fully Implemented** | The core idea/concept must be fully implemented |
| ✅ **Improvements Allowed** | You can improve the implementation |
| ❌ **Idea Should Not Change** | The core concept of the idea must remain the same |
| ❌ **Do Not Apply Blindly** | First scan, plan, then implement |

**Remember:** This document provides ideas & possibilities - the final implementation will depend on the bot's actual architecture.

---

**END OF DOCUMENT**