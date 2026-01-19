# TELEGRAM V5 - DUAL ORDER & RE-ENTRY MANAGEMENT UPGRADE

**Status:** Planning Phase  
**Priority:** HIGH (User Requested Feature)  
**Complexity:** MEDIUM-HIGH (Backend exists, need Telegram interface + per-plugin granularity)  
**Estimated Effort:** 32-40 hours  
**Target Integration:** Telegram V5 Upgrade (Phase 2 or 3)

---

## 📋 EXECUTIVE SUMMARY

### What User Wants
User wants **granular control** over:
1. **Dual Order Management** - Toggle Order A, Order B, or Both per plugin per logic via Telegram
2. **Re-entry System Toggles** - Enable/disable SL Hunt, TP Continuation, Exit Continuation per plugin via Telegram

### Current State
✅ **Backend Infrastructure EXISTS:**
- Dual order system fully implemented (V3 different SLs, V6 same SL)
- Order routing config: `ORDER_A_ONLY`, `ORDER_B_ONLY`, `DUAL_ORDERS`
- Re-entry toggles exist: `sl_hunt_reentry_enabled`, `tp_reentry_enabled`, `exit_continuation_enabled`
- Global re-entry menu handler exists (lines 1-710 in `reentry_menu_handler.py`)

❌ **Missing Components:**
- NO Telegram interface for dual order management
- Re-entry toggles are **GLOBAL** (not per-plugin)
- NO per-logic granular control for dual orders
- NO integration with plugin selection interceptor [V3] [V6] [Both]

---

## 🔍 RESEARCH FINDINGS

### 1. Dual Order System Analysis

#### Backend Files (EXISTING)
```
Trading_Bot/src/managers/dual_order_manager.py (347 lines)
Trading_Bot/src/core/services/dual_order_service.py (437 lines)
Trading_Bot/src/core/plugin_system/dual_order_interface.py (107 lines)
```

#### How It Works Now
1. **V3 Plugin:**
   - **Always** creates dual orders (Order A + Order B)
   - Order A: TP Continuation Trail (V3 Smart SL - progressive trailing)
   - Order B: Profit Booking Trail (Fixed $10 risk SL)
   - Same lot size for both orders (no split)
   - Comment tags: `OrderA_TP_Trail`, `OrderB_Profit_Trail`

2. **V6 Plugin:**
   - **Conditional routing** based on timeframe:
     - `1M → ORDER_B_ONLY` (Profit booking only)
     - `5M → DUAL_ORDERS` (Both orders)
     - `15M → ORDER_A_ONLY` (TP trail only)
     - `1H → ORDER_A_ONLY` (TP trail only)
     - `4H → ORDER_A_ONLY` (TP trail only)

3. **Config Structure:**
```json
{
  "dual_order_config": {
    "enabled": true
  },
  "v3_combined": {
    "dual_orders": {
      "enabled": true,
      "order_a_comment": "OrderA_TP_Trail",
      "order_b_comment": "OrderB_Profit_Trail",
      "order_b_fixed_sl_dollars": 10.0
    }
  }
}
```

#### ServiceAPI Methods (EXISTING)
```python
# V3 Dual Orders (Different SLs)
place_dual_orders_v3(symbol, direction, lot_size_total, order_a_sl, order_a_tp, order_b_sl, order_b_tp, logic_route)

# V6 Dual Orders (Same SL)
place_dual_orders_v6(symbol, direction, lot_size_total, sl_price, tp1_price, tp2_price)

# Single Orders
place_single_order_a(symbol, direction, lot_size, sl_price, tp_price, comment='ORDER_A')
place_single_order_b(symbol, direction, lot_size, sl_price, tp_price, comment='ORDER_B')
```

#### Test Coverage (EXISTING)
```python
# test_batch_03_services.py
test_place_dual_orders_v3()  # Different SLs for Order A and B
test_place_dual_orders_v6()  # Same SL for Order A and B
test_place_single_order_a()  # Order A only
test_place_single_order_b()  # Order B only

# test_batch_02_schemas.py
'order_routing' == 'ORDER_A_ONLY'
'order_routing' == 'ORDER_B_ONLY'
'order_routing' == 'DUAL_ORDERS'
```

---

### 2. Re-entry Toggle System Analysis

#### Backend Config (EXISTING)
```json
{
  "re_entry_config": {
    "tp_reentry_enabled": true,
    "sl_hunt_reentry_enabled": true,
    "exit_continuation_enabled": true,
    "autonomous_config": {
      "enabled": false,
      "tp_continuation": {
        "enabled": false,
        "cooldown_seconds": 5,
        "max_levels": 5
      },
      "sl_hunt_recovery": {
        "enabled": false,
        "detection_threshold_minutes": 2,
        "max_recovery_attempts": 3
      },
      "exit_continuation": {
        "enabled": false,
        "min_exit_profit": 5.0
      }
    }
  }
}
```

#### Existing Telegram Menu (GLOBAL TOGGLES)
**File:** `src/menu/reentry_menu_handler.py` (710 lines)

**Features:**
- 🤖 Master Autonomous Mode toggle
- 🎯 TP Continuation toggle
- 🛡 SL Hunt toggle
- 🔄 Exit Continuation toggle
- ⚔️ Reverse Shield toggle (root level config)

**Limitations:**
- ⚠️ **All toggles are GLOBAL** (affect both V3 and V6)
- ⚠️ NO per-plugin control
- ⚠️ NO per-logic control
- ⚠️ NO integration with plugin selection

#### Usage in Codebase
```python
# trading_engine.py - Lines 344-345, 989, 1005, 1505, 1527, 1732, 2161, 2175-2176
if self.config.get("re_entry_config", {}).get("sl_hunt_reentry_enabled", False):
    # Execute SL hunt re-entry

# price_monitor_service.py - Lines 68-69, 552, 645
if self.trading_engine.config.get("re_entry_config", {}).get("tp_reentry_enabled", False):
    # Execute TP continuation

# reentry_service.py - Lines 176-177
exit_cont_enabled = self.config.get("re_entry_config", {}).get("exit_continuation_enabled", False)
if exit_cont_enabled:
    # Execute exit continuation
```

---

## 🎯 REQUIREMENTS BREAKDOWN

### User Requirements (Hindi Translation)
1. **"v6 me sirf hai dual order ko mange karne ka"**
   - V6 में dual order management चाहिए (Order A only, Order B only, Both)
   - Per timeframe control: 1M, 5M, 15M, 1H, 4H

2. **"sabhi re-entry ke liye bhi bana hai ki off karna hai on karna hai"**
   - सभी re-entry systems के लिए ON/OFF toggle चाहिए
   - Per plugin control: V3 और V6 separately
   - Types: SL Hunt, TP Continuation, Exit Continuation, Profit Booking SL Hunt

3. **"telegram ke sahi command set karen pe kaise set hoge dono plugin pe alga alag"**
   - Plugin selection layer: [V3] [V6] [Both]
   - फिर features manage करें selected plugin के लिए

---

### Technical Requirements

#### A. Dual Order Management

**1. Per-Plugin Selection Layer**
```
User: /dualorder
Bot: Select Plugin:
     [V3 Combined] [V6 Price Action] [Both Plugins]
```

**2. V3 Logic Selection**
```
User: [V3 Combined]
Bot: Select Logic:
     [LOGIC1 - Aggressive] [LOGIC2 - Moderate] [LOGIC3 - Conservative]
     [ALL LOGICS]
```

**3. V6 Timeframe Selection**
```
User: [V6 Price Action]
Bot: Select Timeframe:
     [1M] [5M] [15M] [1H] [4H] [ALL TIMEFRAMES]
```

**4. Order Mode Selection**
```
Bot: Select Order Mode for V3 > LOGIC1:
     Current: ✅ DUAL_ORDERS
     
     [Order A Only - TP Trail]
     [Order B Only - Profit Booking]
     [Both Orders - Current]
     [Back]
```

**5. Confirmation & Status**
```
Bot: ✅ Dual Order Mode Updated
     
     Plugin: V3 Combined
     Logic: LOGIC1
     Mode: ORDER_A_ONLY ← Changed
     
     📊 Order A: TP Continuation Trail
     📊 Order B: DISABLED
     
     [Configure Another] [View All Settings] [Main Menu]
```

#### B. Re-entry Toggle System

**1. Per-Plugin Selection Layer**
```
User: /reentry
Bot: Select Plugin:
     [V3 Combined] [V6 Price Action] [Global Settings]
```

**2. Re-entry Type Selection**
```
User: [V3 Combined]
Bot: V3 Combined - Re-entry Settings:
     
     Current Status:
     🎯 TP Continuation: ON ✅
     🛡 SL Hunt Recovery: OFF ❌
     🔄 Exit Continuation: ON ✅
     📈 Profit Booking SL Hunt: OFF ❌
     
     [Toggle TP Continuation]
     [Toggle SL Hunt]
     [Toggle Exit Continuation]
     [Toggle Profit Booking]
     [Global Settings] [Back]
```

**3. Individual Toggle Confirmation**
```
User: [Toggle SL Hunt]
Bot: ✅ SL Hunt Recovery Toggled
     
     Plugin: V3 Combined
     Feature: SL Hunt Recovery
     Status: ON ← Changed from OFF
     
     ⚙️ Settings:
     • Detection Threshold: 2 minutes
     • Max Recovery Attempts: 3
     
     [Configure Settings] [Back to Re-entry Menu]
```

**4. Global vs Per-Plugin View**
```
User: [Global Settings]
Bot: 🌐 Global Re-entry Overview:
     
     V3 COMBINED:
     🎯 TP Continuation: ON ✅
     🛡 SL Hunt: OFF ❌
     🔄 Exit Continuation: ON ✅
     
     V6 PRICE ACTION:
     🎯 TP Continuation: OFF ❌
     🛡 SL Hunt: ON ✅
     🔄 Exit Continuation: OFF ❌
     
     [Configure V3] [Configure V6] [Main Menu]
```

---

## 🏗️ IMPLEMENTATION ARCHITECTURE

### Phase 1: Config Structure Upgrade (8 hours)

#### 1.1 New Config Schema
```json
{
  "dual_order_config": {
    "enabled": true,
    "v3_combined": {
      "enabled": true,
      "per_logic_routing": {
        "LOGIC1": "DUAL_ORDERS",  // ← NEW: Per-logic control
        "LOGIC2": "DUAL_ORDERS",
        "LOGIC3": "ORDER_A_ONLY"
      },
      "order_a_settings": {
        "sl_system": "V3_SMART_SL",
        "trailing_enabled": true
      },
      "order_b_settings": {
        "sl_system": "FIXED_RISK",
        "fixed_sl_dollars": 10.0
      }
    },
    "v6_price_action": {
      "enabled": true,
      "per_timeframe_routing": {  // ← NEW: Per-timeframe control
        "1M": "ORDER_B_ONLY",
        "5M": "DUAL_ORDERS",
        "15M": "ORDER_A_ONLY",
        "1H": "ORDER_A_ONLY",
        "4H": "ORDER_A_ONLY"
      }
    }
  },
  
  "re_entry_config": {
    "global": {  // ← NEW: Global defaults
      "tp_reentry_enabled": true,
      "sl_hunt_reentry_enabled": true,
      "exit_continuation_enabled": true
    },
    "per_plugin": {  // ← NEW: Per-plugin overrides
      "v3_combined": {
        "tp_continuation": {
          "enabled": true,
          "cooldown_seconds": 5,
          "max_levels": 5
        },
        "sl_hunt_recovery": {
          "enabled": false,
          "detection_threshold_minutes": 2,
          "max_recovery_attempts": 3
        },
        "exit_continuation": {
          "enabled": true,
          "min_exit_profit": 5.0
        }
      },
      "v6_price_action": {
        "tp_continuation": {
          "enabled": false
        },
        "sl_hunt_recovery": {
          "enabled": true
        },
        "exit_continuation": {
          "enabled": false
        }
      }
    }
  }
}
```

#### 1.2 Config Migration Script
**File:** `scripts/migrate_dual_order_reentry_config.py`
- Read existing config
- Migrate global toggles to per-plugin structure
- Preserve existing settings
- Backup old config
- Save new structure

---

### Phase 2: Backend Service Upgrades (12 hours)

#### 2.1 Dual Order Manager Upgrade
**File:** `src/managers/dual_order_manager.py`

**New Methods:**
```python
def get_order_routing_for_v3(self, logic: str) -> str:
    """Get order routing mode for V3 logic"""
    routing = self.config.get("dual_order_config", {}) \
        .get("v3_combined", {}) \
        .get("per_logic_routing", {}) \
        .get(logic, "DUAL_ORDERS")
    return routing

def get_order_routing_for_v6(self, timeframe: str) -> str:
    """Get order routing mode for V6 timeframe"""
    routing = self.config.get("dual_order_config", {}) \
        .get("v6_price_action", {}) \
        .get("per_timeframe_routing", {}) \
        .get(timeframe, "ORDER_A_ONLY")
    return routing

def update_order_routing(self, plugin: str, context: str, mode: str) -> bool:
    """
    Update order routing mode
    
    Args:
        plugin: 'v3_combined' or 'v6_price_action'
        context: Logic name (V3) or Timeframe (V6)
        mode: 'ORDER_A_ONLY', 'ORDER_B_ONLY', or 'DUAL_ORDERS'
    
    Returns:
        Success boolean
    """
    try:
        if plugin == "v3_combined":
            self.config.update_nested(
                f"dual_order_config.v3_combined.per_logic_routing.{context}",
                mode
            )
        elif plugin == "v6_price_action":
            self.config.update_nested(
                f"dual_order_config.v6_price_action.per_timeframe_routing.{context}",
                mode
            )
        else:
            return False
        
        self.config.save()
        self.logger.info(f"Order routing updated: {plugin} > {context} → {mode}")
        return True
    except Exception as e:
        self.logger.error(f"Failed to update order routing: {e}")
        return False
```

#### 2.2 Re-entry Service Upgrade
**New File:** `src/services/reentry_config_service.py`

```python
class ReentryConfigService:
    """Service for per-plugin re-entry configuration management"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def is_tp_continuation_enabled(self, plugin_id: str) -> bool:
        """Check if TP continuation enabled for plugin"""
        # Check per-plugin config first, fallback to global
        per_plugin = self.config.get("re_entry_config", {}) \
            .get("per_plugin", {}) \
            .get(plugin_id, {}) \
            .get("tp_continuation", {}) \
            .get("enabled")
        
        if per_plugin is not None:
            return per_plugin
        
        # Fallback to global
        return self.config.get("re_entry_config", {}) \
            .get("global", {}) \
            .get("tp_reentry_enabled", True)
    
    def is_sl_hunt_enabled(self, plugin_id: str) -> bool:
        """Check if SL hunt enabled for plugin"""
        per_plugin = self.config.get("re_entry_config", {}) \
            .get("per_plugin", {}) \
            .get(plugin_id, {}) \
            .get("sl_hunt_recovery", {}) \
            .get("enabled")
        
        if per_plugin is not None:
            return per_plugin
        
        return self.config.get("re_entry_config", {}) \
            .get("global", {}) \
            .get("sl_hunt_reentry_enabled", True)
    
    def is_exit_continuation_enabled(self, plugin_id: str) -> bool:
        """Check if exit continuation enabled for plugin"""
        per_plugin = self.config.get("re_entry_config", {}) \
            .get("per_plugin", {}) \
            .get(plugin_id, {}) \
            .get("exit_continuation", {}) \
            .get("enabled")
        
        if per_plugin is not None:
            return per_plugin
        
        return self.config.get("re_entry_config", {}) \
            .get("global", {}) \
            .get("exit_continuation_enabled", True)
    
    def toggle_feature(
        self,
        plugin_id: str,
        feature_type: str,  # 'tp_continuation', 'sl_hunt_recovery', 'exit_continuation'
        new_value: Optional[bool] = None
    ) -> bool:
        """
        Toggle re-entry feature for plugin
        
        Args:
            plugin_id: Plugin identifier
            feature_type: Feature to toggle
            new_value: Force specific value (None = toggle current)
        
        Returns:
            New value
        """
        # Get current value
        if feature_type == 'tp_continuation':
            current = self.is_tp_continuation_enabled(plugin_id)
        elif feature_type == 'sl_hunt_recovery':
            current = self.is_sl_hunt_enabled(plugin_id)
        elif feature_type == 'exit_continuation':
            current = self.is_exit_continuation_enabled(plugin_id)
        else:
            raise ValueError(f"Invalid feature type: {feature_type}")
        
        # Determine new value
        target_value = not current if new_value is None else new_value
        
        # Update config
        config_path = f"re_entry_config.per_plugin.{plugin_id}.{feature_type}.enabled"
        self.config.update_nested(config_path, target_value)
        self.config.save()
        
        self.logger.info(
            f"Re-entry toggle: {plugin_id} > {feature_type} → {target_value}"
        )
        
        return target_value
    
    def get_plugin_status(self, plugin_id: str) -> Dict[str, Any]:
        """Get all re-entry settings for a plugin"""
        return {
            'tp_continuation': {
                'enabled': self.is_tp_continuation_enabled(plugin_id),
                'config': self.config.get("re_entry_config", {}) \
                    .get("per_plugin", {}) \
                    .get(plugin_id, {}) \
                    .get("tp_continuation", {})
            },
            'sl_hunt_recovery': {
                'enabled': self.is_sl_hunt_enabled(plugin_id),
                'config': self.config.get("re_entry_config", {}) \
                    .get("per_plugin", {}) \
                    .get(plugin_id, {}) \
                    .get("sl_hunt_recovery", {})
            },
            'exit_continuation': {
                'enabled': self.is_exit_continuation_enabled(plugin_id),
                'config': self.config.get("re_entry_config", {}) \
                    .get("per_plugin", {}) \
                    .get(plugin_id, {}) \
                    .get("exit_continuation", {})
            }
        }
```

#### 2.3 Update Existing Code to Use Per-Plugin Toggles
**Files to Update:**
- `trading_engine.py` - Replace global checks with per-plugin checks
- `price_monitor_service.py` - Use ReentryConfigService
- `reentry_service.py` - Use ReentryConfigService

**Example Change:**
```python
# OLD CODE (trading_engine.py line 344)
if self.config.get("re_entry_config", {}).get("sl_hunt_reentry_enabled", False):
    # Execute SL hunt

# NEW CODE
from src.services.reentry_config_service import ReentryConfigService
reentry_service = ReentryConfigService(self.config)

if reentry_service.is_sl_hunt_enabled(plugin_id):
    # Execute SL hunt
```

---

### Phase 3: Telegram Menu Builders (12 hours)

#### 3.1 Dual Order Menu Handler
**New File:** `src/menu/dual_order_menu_handler.py`

```python
class DualOrderMenuHandler:
    """Telegram menu for dual order management"""
    
    def __init__(self, bot, dual_order_manager):
        self.bot = bot
        self.dual_order_manager = dual_order_manager
        self.config = bot.config
        
        # User session state
        self._user_sessions = {}  # user_id -> session_data
    
    def show_plugin_selection(self, user_id: int):
        """Show plugin selection menu"""
        keyboard = [
            [self._btn("🔵 V3 Combined", "dual_plugin_v3")],
            [self._btn("🟢 V6 Price Action", "dual_plugin_v6")],
            [self._btn("🌐 Global Settings", "dual_plugin_global")],
            [self._btn("🏠 Main Menu", "menu_main")]
        ]
        
        message = (
            "🎛️ <b>DUAL ORDER MANAGEMENT</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Select plugin to configure:\n"
            "• <b>V3 Combined:</b> Per-logic routing\n"
            "• <b>V6 Price Action:</b> Per-timeframe routing\n"
            "• <b>Global:</b> View all settings\n\n"
            "💡 Order types:\n"
            "  📊 Order A = TP Continuation Trail\n"
            "  📈 Order B = Profit Booking Trail\n"
        )
        
        self.bot.send_message_with_keyboard(
            message,
            self._create_keyboard(keyboard),
            parse_mode="HTML"
        )
    
    def handle_plugin_selection(self, callback_data: str, user_id: int):
        """Handle plugin selection callback"""
        if callback_data == "dual_plugin_v3":
            self.show_v3_logic_selection(user_id)
        elif callback_data == "dual_plugin_v6":
            self.show_v6_timeframe_selection(user_id)
        elif callback_data == "dual_plugin_global":
            self.show_global_overview(user_id)
    
    def show_v3_logic_selection(self, user_id: int):
        """Show V3 logic selection menu"""
        # Get current routing for each logic
        logic1_routing = self.dual_order_manager.get_order_routing_for_v3("LOGIC1")
        logic2_routing = self.dual_order_manager.get_order_routing_for_v3("LOGIC2")
        logic3_routing = self.dual_order_manager.get_order_routing_for_v3("LOGIC3")
        
        keyboard = [
            [self._btn(
                f"⚡ LOGIC1 - Aggressive [{self._routing_icon(logic1_routing)}]",
                "dual_v3_logic1"
            )],
            [self._btn(
                f"⚖️ LOGIC2 - Moderate [{self._routing_icon(logic2_routing)}]",
                "dual_v3_logic2"
            )],
            [self._btn(
                f"🛡️ LOGIC3 - Conservative [{self._routing_icon(logic3_routing)}]",
                "dual_v3_logic3"
            )],
            [self._btn("⬅️ Back", "dual_menu_main")]
        ]
        
        message = (
            "🔵 <b>V3 COMBINED - DUAL ORDER ROUTING</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>LOGIC1 (Aggressive):</b> {self._routing_name(logic1_routing)}\n"
            f"<b>LOGIC2 (Moderate):</b> {self._routing_name(logic2_routing)}\n"
            f"<b>LOGIC3 (Conservative):</b> {self._routing_name(logic3_routing)}\n\n"
            "Select logic to configure:\n"
        )
        
        self.bot.send_message_with_keyboard(
            message,
            self._create_keyboard(keyboard),
            parse_mode="HTML"
        )
    
    def show_order_mode_selection(
        self,
        user_id: int,
        plugin: str,
        context: str,
        message_id: Optional[int] = None
    ):
        """Show order mode selection menu"""
        # Get current routing
        if plugin == "v3_combined":
            current_mode = self.dual_order_manager.get_order_routing_for_v3(context)
        else:
            current_mode = self.dual_order_manager.get_order_routing_for_v6(context)
        
        keyboard = [
            [self._mode_btn("📊 Order A Only - TP Trail", "ORDER_A_ONLY", current_mode)],
            [self._mode_btn("📈 Order B Only - Profit Booking", "ORDER_B_ONLY", current_mode)],
            [self._mode_btn("🎯 Both Orders - Full System", "DUAL_ORDERS", current_mode)],
            [self._btn("⬅️ Back", f"dual_plugin_{plugin.split('_')[0]}")]
        ]
        
        message = (
            f"🎛️ <b>ORDER MODE SELECTION</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Plugin:</b> {plugin.replace('_', ' ').title()}\n"
            f"<b>Context:</b> {context}\n"
            f"<b>Current Mode:</b> {self._routing_name(current_mode)} ✅\n\n"
            f"Select new order mode:\n"
        )
        
        # Store session data
        self._user_sessions[user_id] = {
            'plugin': plugin,
            'context': context,
            'current_mode': current_mode
        }
        
        if message_id:
            self.bot.edit_message(
                message,
                message_id,
                self._create_keyboard(keyboard),
                parse_mode="HTML"
            )
        else:
            self.bot.send_message_with_keyboard(
                message,
                self._create_keyboard(keyboard),
                parse_mode="HTML"
            )
    
    def handle_mode_selection(self, callback_data: str, user_id: int):
        """Handle order mode selection"""
        # Get session data
        session = self._user_sessions.get(user_id, {})
        plugin = session.get('plugin')
        context = session.get('context')
        
        # Extract mode from callback
        mode = callback_data.replace('dual_mode_', '')
        
        # Update config
        success = self.dual_order_manager.update_order_routing(plugin, context, mode)
        
        if success:
            self.bot.send_message(
                f"✅ <b>Order Mode Updated</b>\n\n"
                f"Plugin: {plugin.replace('_', ' ').title()}\n"
                f"Context: {context}\n"
                f"Mode: {self._routing_name(mode)} ← <b>Changed</b>\n\n"
                f"{self._get_mode_description(mode)}",
                parse_mode="HTML"
            )
        else:
            self.bot.send_message("❌ Failed to update order mode")
        
        # Clear session
        self._user_sessions.pop(user_id, None)
    
    def _routing_icon(self, routing: str) -> str:
        """Get icon for routing mode"""
        icons = {
            'ORDER_A_ONLY': 'A',
            'ORDER_B_ONLY': 'B',
            'DUAL_ORDERS': 'AB'
        }
        return icons.get(routing, '?')
    
    def _routing_name(self, routing: str) -> str:
        """Get readable name for routing mode"""
        names = {
            'ORDER_A_ONLY': 'Order A Only',
            'ORDER_B_ONLY': 'Order B Only',
            'DUAL_ORDERS': 'Both Orders'
        }
        return names.get(routing, 'Unknown')
    
    def _mode_btn(self, label: str, mode: str, current_mode: str):
        """Create mode selection button with current indicator"""
        is_current = mode == current_mode
        label_with_indicator = f"{label} {'✅' if is_current else ''}"
        return self._btn(label_with_indicator, f"dual_mode_{mode}")
    
    def _get_mode_description(self, mode: str) -> str:
        """Get description for order mode"""
        descriptions = {
            'ORDER_A_ONLY': (
                "📊 <b>Order A Only</b>\n"
                "• TP Continuation Trail\n"
                "• V3 Smart SL (progressive)\n"
                "• Full lot size\n"
                "• Best for: Trend following"
            ),
            'ORDER_B_ONLY': (
                "📈 <b>Order B Only</b>\n"
                "• Profit Booking Trail\n"
                "• Fixed $10 risk SL\n"
                "• Full lot size\n"
                "• Best for: Quick profits"
            ),
            'DUAL_ORDERS': (
                "🎯 <b>Both Orders</b>\n"
                "• Order A: TP Trail\n"
                "• Order B: Profit Booking\n"
                "• Same lot size each\n"
                "• Best for: Balanced approach"
            )
        }
        return descriptions.get(mode, "Unknown mode")
    
    def _btn(self, text: str, callback_data: str):
        """Helper to create button"""
        return {"text": text, "callback_data": callback_data}
    
    def _create_keyboard(self, rows: list):
        """Helper to create keyboard"""
        return {"inline_keyboard": rows}
```

#### 3.2 Enhanced Re-entry Menu Handler
**File:** `src/menu/reentry_menu_handler.py` (UPGRADE EXISTING)

**New Methods to Add:**
```python
def show_plugin_selection_for_reentry(self, user_id: int):
    """Show plugin selection for re-entry config"""
    keyboard = [
        [self._btn("🔵 V3 Combined", "reentry_plugin_v3")],
        [self._btn("🟢 V6 Price Action", "reentry_plugin_v6")],
        [self._btn("🌐 Global Overview", "reentry_plugin_global")],
        [self._btn("🏠 Main Menu", "menu_main")]
    ]
    
    message = (
        "🔄 <b>RE-ENTRY SYSTEM MANAGEMENT</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Select plugin to configure:\n"
        "• <b>V3 Combined:</b> 12-signal logic system\n"
        "• <b>V6 Price Action:</b> Multi-timeframe system\n"
        "• <b>Global:</b> View all settings\n\n"
        "💡 Re-entry types:\n"
        "  🎯 TP Continuation = Re-enter on TP hit\n"
        "  🛡 SL Hunt = Recover from stop hunt\n"
        "  🔄 Exit Continuation = Re-enter on manual exit\n"
    )
    
    self.bot.send_message_with_keyboard(
        message,
        self._create_keyboard(keyboard),
        parse_mode="HTML"
    )

def show_plugin_reentry_settings(
    self,
    user_id: int,
    plugin_id: str,
    message_id: Optional[int] = None
):
    """Show re-entry settings for specific plugin"""
    from src.services.reentry_config_service import ReentryConfigService
    reentry_service = ReentryConfigService(self.config)
    
    # Get plugin status
    status = reentry_service.get_plugin_status(plugin_id)
    
    tp_enabled = status['tp_continuation']['enabled']
    sl_enabled = status['sl_hunt_recovery']['enabled']
    exit_enabled = status['exit_continuation']['enabled']
    
    # Build keyboard
    keyboard = [
        [self._toggle_btn_v2(
            "🎯 TP Continuation",
            tp_enabled,
            f"reentry_toggle_{plugin_id}_tp"
        )],
        [self._toggle_btn_v2(
            "🛡 SL Hunt Recovery",
            sl_enabled,
            f"reentry_toggle_{plugin_id}_sl"
        )],
        [self._toggle_btn_v2(
            "🔄 Exit Continuation",
            exit_enabled,
            f"reentry_toggle_{plugin_id}_exit"
        )],
        [
            self._btn("⚙️ Advanced", f"reentry_advanced_{plugin_id}"),
            self._btn("⬅️ Back", "reentry_menu_main")
        ]
    ]
    
    plugin_name = plugin_id.replace('_', ' ').title()
    
    message = (
        f"🔄 <b>{plugin_name} - RE-ENTRY SETTINGS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>Current Status:</b>\n"
        f"🎯 TP Continuation: {'ON ✅' if tp_enabled else 'OFF ❌'}\n"
        f"🛡 SL Hunt Recovery: {'ON ✅' if sl_enabled else 'OFF ❌'}\n"
        f"🔄 Exit Continuation: {'ON ✅' if exit_enabled else 'OFF ❌'}\n\n"
        f"<b>💡 Click buttons to toggle ON/OFF</b>\n"
    )
    
    if message_id:
        self.bot.edit_message(
            message,
            message_id,
            self._create_keyboard(keyboard),
            parse_mode="HTML"
        )
    else:
        self.bot.send_message_with_keyboard(
            message,
            self._create_keyboard(keyboard),
            parse_mode="HTML"
        )

def handle_per_plugin_toggle(self, callback_data: str, user_id: int):
    """Handle per-plugin toggle callbacks"""
    # Parse callback: reentry_toggle_{plugin_id}_{feature}
    parts = callback_data.split('_')
    plugin_id = parts[2]  # v3 or v6
    full_plugin_id = f"{plugin_id}_combined" if plugin_id == 'v3' else f"{plugin_id}_price_action"
    feature = parts[3]  # tp, sl, or exit
    
    # Map feature code to config key
    feature_map = {
        'tp': 'tp_continuation',
        'sl': 'sl_hunt_recovery',
        'exit': 'exit_continuation'
    }
    feature_type = feature_map.get(feature)
    
    # Toggle feature
    from src.services.reentry_config_service import ReentryConfigService
    reentry_service = ReentryConfigService(self.config)
    
    new_value = reentry_service.toggle_feature(full_plugin_id, feature_type)
    
    # Send confirmation
    feature_names = {
        'tp': 'TP Continuation',
        'sl': 'SL Hunt Recovery',
        'exit': 'Exit Continuation'
    }
    
    self.bot.send_message(
        f"✅ <b>{feature_names[feature]} Toggled</b>\n\n"
        f"Plugin: {full_plugin_id.replace('_', ' ').title()}\n"
        f"Status: {'ON ✅' if new_value else 'OFF ❌'} ← <b>Changed</b>",
        parse_mode="HTML"
    )

def _toggle_btn_v2(self, label: str, is_enabled: bool, callback: str):
    """Create toggle button with visual indicator"""
    status = "ON ✅" if is_enabled else "OFF ❌"
    return self._btn(f"{label} [{status}]", callback)
```

---

### Phase 4: Command Handlers Integration (4-6 hours)

#### 4.1 Register New Commands
**File:** `src/clients/telegram_bot.py`

```python
# ADD to command registration
self.bot.set_my_commands([
    # ... existing commands ...
    {"command": "dualorder", "description": "🎛️ Dual Order Management"},
    {"command": "reentry", "description": "🔄 Re-entry System Settings"},
    # ... existing commands ...
])

# ADD command handlers
@self.bot.message_handler(commands=['dualorder'])
def handle_dualorder_command(message):
    user_id = message.from_user.id
    if self.dual_order_menu_handler:
        self.dual_order_menu_handler.show_plugin_selection(user_id)
    else:
        self.bot.send_message("❌ Dual order menu not available")

@self.bot.message_handler(commands=['reentry'])
def handle_reentry_command(message):
    user_id = message.from_user.id
    if self.reentry_menu_handler:
        self.reentry_menu_handler.show_plugin_selection_for_reentry(user_id)
    else:
        self.bot.send_message("❌ Re-entry menu not available")
```

#### 4.2 Register Callback Handlers
```python
# ADD to callback query handler
@self.bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    callback_data = call.data
    user_id = call.from_user.id
    message_id = call.message.message_id
    
    # Dual Order callbacks
    if callback_data.startswith('dual_'):
        if self.dual_order_menu_handler:
            if callback_data.startswith('dual_plugin_'):
                self.dual_order_menu_handler.handle_plugin_selection(callback_data, user_id)
            elif callback_data.startswith('dual_mode_'):
                self.dual_order_menu_handler.handle_mode_selection(callback_data, user_id)
            # ... other dual order callbacks
    
    # Re-entry callbacks (per-plugin)
    elif callback_data.startswith('reentry_plugin_'):
        if self.reentry_menu_handler:
            plugin_id = callback_data.replace('reentry_plugin_', '')
            self.reentry_menu_handler.show_plugin_reentry_settings(user_id, plugin_id, message_id)
    
    elif callback_data.startswith('reentry_toggle_'):
        if self.reentry_menu_handler:
            self.reentry_menu_handler.handle_per_plugin_toggle(callback_data, user_id)
    
    # ... existing callbacks ...
```

---

### Phase 5: Testing & Validation (4-6 hours)

#### 5.1 Unit Tests
**File:** `tests/test_dual_order_telegram.py`

```python
import pytest
from src.menu.dual_order_menu_handler import DualOrderMenuHandler
from src.managers.dual_order_manager import DualOrderManager

class TestDualOrderTelegram:
    """Test dual order Telegram interface"""
    
    def test_plugin_selection_menu(self, mock_bot, mock_config):
        """Test plugin selection menu generation"""
        manager = DualOrderManager(mock_config, None, None, None)
        handler = DualOrderMenuHandler(mock_bot, manager)
        
        handler.show_plugin_selection(user_id=12345)
        
        # Verify message sent
        assert mock_bot.last_message is not None
        assert "DUAL ORDER MANAGEMENT" in mock_bot.last_message
        assert "V3 Combined" in mock_bot.last_message
        assert "V6 Price Action" in mock_bot.last_message
    
    def test_v3_logic_selection(self, mock_bot, mock_config):
        """Test V3 logic selection menu"""
        manager = DualOrderManager(mock_config, None, None, None)
        handler = DualOrderMenuHandler(mock_bot, manager)
        
        handler.show_v3_logic_selection(user_id=12345)
        
        assert "LOGIC1" in mock_bot.last_message
        assert "LOGIC2" in mock_bot.last_message
        assert "LOGIC3" in mock_bot.last_message
    
    def test_order_mode_toggle(self, mock_bot, mock_config):
        """Test order mode toggle"""
        manager = DualOrderManager(mock_config, None, None, None)
        handler = DualOrderMenuHandler(mock_bot, manager)
        
        # Set initial mode
        initial_mode = manager.get_order_routing_for_v3("LOGIC1")
        
        # Toggle
        success = manager.update_order_routing("v3_combined", "LOGIC1", "ORDER_A_ONLY")
        assert success
        
        # Verify changed
        new_mode = manager.get_order_routing_for_v3("LOGIC1")
        assert new_mode == "ORDER_A_ONLY"
        assert new_mode != initial_mode
```

**File:** `tests/test_reentry_per_plugin.py`

```python
import pytest
from src.services.reentry_config_service import ReentryConfigService

class TestReentryPerPlugin:
    """Test per-plugin re-entry configuration"""
    
    def test_per_plugin_tp_toggle(self, mock_config):
        """Test TP continuation toggle for specific plugin"""
        service = ReentryConfigService(mock_config)
        
        # Toggle for V3
        initial_v3 = service.is_tp_continuation_enabled("v3_combined")
        new_v3 = service.toggle_feature("v3_combined", "tp_continuation")
        
        assert new_v3 != initial_v3
        
        # Verify V6 not affected
        v6_status = service.is_tp_continuation_enabled("v6_price_action")
        # Should remain unchanged
    
    def test_fallback_to_global(self, mock_config):
        """Test fallback to global settings"""
        service = ReentryConfigService(mock_config)
        
        # Remove per-plugin config
        mock_config.data["re_entry_config"]["per_plugin"] = {}
        
        # Should fallback to global
        tp_enabled = service.is_tp_continuation_enabled("v3_combined")
        global_tp = mock_config.get("re_entry_config", {}).get("global", {}).get("tp_reentry_enabled", True)
        
        assert tp_enabled == global_tp
    
    def test_get_plugin_status(self, mock_config):
        """Test getting all re-entry settings for plugin"""
        service = ReentryConfigService(mock_config)
        
        status = service.get_plugin_status("v3_combined")
        
        assert 'tp_continuation' in status
        assert 'sl_hunt_recovery' in status
        assert 'exit_continuation' in status
        
        assert 'enabled' in status['tp_continuation']
        assert 'config' in status['tp_continuation']
```

#### 5.2 Integration Tests
**File:** `tests/integration/test_dual_order_workflow.py`

```python
class TestDualOrderWorkflow:
    """Test complete dual order Telegram workflow"""
    
    @pytest.mark.integration
    def test_complete_v3_routing_change(
        self,
        telegram_bot,
        dual_order_manager,
        v3_plugin
    ):
        """Test complete workflow: Telegram → Config → Plugin"""
        
        # Step 1: User clicks /dualorder
        telegram_bot.send_command("/dualorder")
        
        # Step 2: User selects V3 Combined
        telegram_bot.click_button("dual_plugin_v3")
        
        # Step 3: User selects LOGIC1
        telegram_bot.click_button("dual_v3_logic1")
        
        # Step 4: User selects ORDER_A_ONLY
        telegram_bot.click_button("dual_mode_ORDER_A_ONLY")
        
        # Step 5: Verify config updated
        routing = dual_order_manager.get_order_routing_for_v3("LOGIC1")
        assert routing == "ORDER_A_ONLY"
        
        # Step 6: Verify plugin uses new routing
        signal = {"symbol": "XAUUSD", "direction": "BUY", "logic": "LOGIC1"}
        result = v3_plugin.create_dual_orders(signal)
        
        # Should only create Order A
        assert result.order_a_id is not None
        assert result.order_b_id is None
```

---

## 📊 TESTING MATRIX

### Test Scenarios

| Test ID | Scenario | Expected Result | Status |
|---------|----------|-----------------|--------|
| DT-01 | V3 LOGIC1 → ORDER_A_ONLY | Only Order A created | ⏳ Pending |
| DT-02 | V3 LOGIC2 → ORDER_B_ONLY | Only Order B created | ⏳ Pending |
| DT-03 | V3 LOGIC3 → DUAL_ORDERS | Both orders created | ⏳ Pending |
| DT-04 | V6 1M → ORDER_B_ONLY | Only Order B created | ⏳ Pending |
| DT-05 | V6 5M → DUAL_ORDERS | Both orders created | ⏳ Pending |
| DT-06 | V6 15M → ORDER_A_ONLY | Only Order A created | ⏳ Pending |
| RT-01 | V3 TP toggle → ON | TP re-entry enabled for V3 only | ⏳ Pending |
| RT-02 | V6 SL Hunt toggle → OFF | SL hunt disabled for V6 only | ⏳ Pending |
| RT-03 | Global view | Shows all plugin statuses | ⏳ Pending |
| RT-04 | Per-plugin override | Plugin config overrides global | ⏳ Pending |
| RT-05 | Fallback to global | Uses global if no plugin config | ⏳ Pending |

---

## 🚀 DEPLOYMENT PLAN

### Prerequisites
- ✅ Telegram V5 Phase 1 (Plugin Selection Interceptor) completed
- ✅ Config migration script tested
- ✅ All unit tests passing
- ✅ Integration tests passing

### Deployment Steps

1. **Phase 1: Config Migration (Day 1)**
   - Run config migration script
   - Backup existing config
   - Verify new config structure
   - Restart bot to load new config

2. **Phase 2: Backend Services (Day 2-3)**
   - Deploy ReentryConfigService
   - Update dual_order_manager with new methods
   - Update existing code to use per-plugin toggles
   - Run backend unit tests

3. **Phase 3: Telegram Menus (Day 4-5)**
   - Deploy DualOrderMenuHandler
   - Upgrade ReentryMenuHandler
   - Register command handlers
   - Register callback handlers
   - Run Telegram menu tests

4. **Phase 4: Integration Testing (Day 6)**
   - Full workflow testing
   - User acceptance testing
   - Performance testing
   - Bug fixes

5. **Phase 5: Live Deployment (Day 7)**
   - Deploy to production
   - Monitor for issues
   - Collect user feedback
   - Documentation updates

---

## 📈 SUCCESS METRICS

### Functional Metrics
- ✅ All 10 test scenarios passing
- ✅ Config migration 100% successful
- ✅ Zero errors in Telegram menu navigation
- ✅ Per-plugin toggles working independently

### User Experience Metrics
- ⏱️ Menu response time < 1 second
- 📊 Zero-typing interface (all buttons)
- 🎯 Clear visual indicators (ON ✅ / OFF ❌)
- 💬 Confirmation messages for all changes

### Performance Metrics
- 🚀 Config save time < 100ms
- 📦 Memory overhead < 5MB
- 🔄 No impact on trade execution speed

---

## 🔗 INTEGRATION WITH EXISTING SYSTEMS

### Plugin Selection Interceptor Integration
```
User Flow:
1. /dualorder
2. [V3] [V6] [Both] ← Plugin selection layer
3. If [V3] → Show LOGIC1/2/3 selection
4. If [V6] → Show 1M/5M/15M/1H/4H selection
5. Select order mode: A/B/Both
6. Confirm & save

Same flow for /reentry command
```

### Backward Compatibility
- ✅ Existing global toggles still work
- ✅ Per-plugin config optional (fallback to global)
- ✅ No breaking changes to existing code
- ✅ Config migration automatic

---

## 📝 DOCUMENTATION UPDATES

### User Documentation
**File:** `docs/TELEGRAM_DUAL_ORDER_GUIDE.md`
- Command reference: `/dualorder`, `/reentry`
- Menu navigation guide
- Use cases and examples
- Troubleshooting

### Developer Documentation
**File:** `docs/DUAL_ORDER_ARCHITECTURE.md`
- Config structure explanation
- Service layer architecture
- Adding new plugins
- Extending menu system

### API Documentation
**File:** `docs/REENTRY_CONFIG_API.md`
- ReentryConfigService methods
- Per-plugin toggle API
- Integration examples

---

## 💰 COST & TIME ESTIMATES

### Development Hours
| Phase | Hours | Rate | Cost |
|-------|-------|------|------|
| Phase 1: Config Upgrade | 8h | $75/h | $600 |
| Phase 2: Backend Services | 12h | $75/h | $900 |
| Phase 3: Telegram Menus | 12h | $75/h | $900 |
| Phase 4: Command Integration | 6h | $75/h | $450 |
| Phase 5: Testing | 6h | $75/h | $450 |
| **TOTAL** | **44h** | **$75/h** | **$3,300** |

### Timeline
- **Week 1:** Phase 1-2 (Config + Backend) - 20 hours
- **Week 2:** Phase 3-5 (Telegram + Testing) - 24 hours
- **Total Duration:** 2 weeks

---

## ⚠️ RISKS & MITIGATION

### Risk 1: Config Migration Failure
**Impact:** HIGH  
**Probability:** LOW  
**Mitigation:**
- Automatic backup before migration
- Rollback script ready
- Test migration on staging first

### Risk 2: Performance Degradation
**Impact:** MEDIUM  
**Probability:** LOW  
**Mitigation:**
- Per-plugin config cached in memory
- Config save debounced (100ms)
- Load testing before deployment

### Risk 3: User Confusion
**Impact:** MEDIUM  
**Probability:** MEDIUM  
**Mitigation:**
- Clear visual indicators (ON ✅ / OFF ❌)
- Confirmation messages for all changes
- User guide with screenshots
- In-menu tooltips

---

## 🎯 NEXT STEPS

1. **✅ THIS DOCUMENT:** Get user approval on approach
2. **⏳ CREATE:** Config migration script
3. **⏳ IMPLEMENT:** Phase 1 (Config structure)
4. **⏳ IMPLEMENT:** Phase 2 (Backend services)
5. **⏳ IMPLEMENT:** Phase 3 (Telegram menus)
6. **⏳ TEST:** All test scenarios
7. **⏳ DEPLOY:** Production rollout

---

## 📞 CONTACT & SUPPORT

**Project Lead:** Ansh Shivaay Gupta  
**Documentation Date:** December 2024  
**Last Updated:** December 2024  
**Version:** 1.0

---

## ✅ APPROVAL CHECKLIST

- [ ] User approval on approach
- [ ] Config migration script reviewed
- [ ] Test scenarios approved
- [ ] Timeline approved
- [ ] Budget approved
- [ ] Integration plan approved
- [ ] Documentation plan approved
- [ ] Deployment plan approved

---

**Note:** यह planning document है जो dual order management और re-entry toggle system के लिए complete Telegram interface provide करेगा। Backend infrastructure already exist करता है, सिर्फ Telegram menus और per-plugin granularity add करनी है। Total 44 hours का effort estimate है 2 weeks में complete करने के लिए।

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