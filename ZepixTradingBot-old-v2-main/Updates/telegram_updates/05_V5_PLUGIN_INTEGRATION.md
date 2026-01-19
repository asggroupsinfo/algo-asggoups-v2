# 🔌 V5 PLUGIN SYSTEM - TELEGRAM INTEGRATION

**Generated:** January 19, 2026  
**Architecture:** V5 Hybrid Plugin System  
**Plugins:** V3 Combined (3 logics) | V6 Price Action (4 timeframes)

---

## 📊 V5 PLUGIN SYSTEM OVERVIEW

### Architecture Diagram:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      V5 HYBRID PLUGIN ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                       PLUGIN MANAGER                              │   │
│  │  • Plugin discovery & loading                                     │   │
│  │  • Lifecycle management (enable/disable)                          │   │
│  │  • Configuration routing                                          │   │
│  └────────────────────────────┬─────────────────────────────────────┘   │
│                               │                                          │
│           ┌───────────────────┼───────────────────┐                     │
│           │                   │                   │                     │
│           ▼                   ▼                   ▼                     │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐           │
│  │   SERVICE API   │ │  CONFIG STORE   │ │   EVENT BUS     │           │
│  │                 │ │                 │ │                 │           │
│  │ • Notifications │ │ • Plugin config │ │ • Trade events  │           │
│  │ • DB access     │ │ • Per-instance  │ │ • Signal events │           │
│  │ • Trading ops   │ │ • Persistence   │ │ • State changes │           │
│  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘           │
│           │                   │                   │                     │
│           └───────────────────┼───────────────────┘                     │
│                               │                                          │
│                               ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                         PLUGINS                                   │   │
│  │                                                                   │   │
│  │  ┌────────────────────────┐    ┌────────────────────────────┐    │   │
│  │  │    V3 COMBINED         │    │    V6 PRICE ACTION         │    │   │
│  │  │                        │    │                            │    │   │
│  │  │  ├─ combinedlogic-1    │    │  ├─ v6_price_action_15m   │    │   │
│  │  │  ├─ combinedlogic-2    │    │  ├─ v6_price_action_30m   │    │   │
│  │  │  └─ combinedlogic-3    │    │  ├─ v6_price_action_1h    │    │   │
│  │  │                        │    │  └─ v6_price_action_4h    │    │   │
│  │  └────────────────────────┘    └────────────────────────────┘    │   │
│  │                                                                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔗 SECTION 1: SERVICE API - TELEGRAM INTEGRATION

### Service API Structure:

```python
# File: src/core/plugin_system/service_api.py

class ServiceAPI:
    """
    API provided to each plugin for interacting with the trading system.
    Includes Telegram notification capabilities.
    """
    
    def __init__(self, plugin_id: str, plugin_manager, config_store, notification_router):
        self.plugin_id = plugin_id
        self.plugin_manager = plugin_manager
        self.config_store = config_store
        self.notification_router = notification_router
        
    # ═══════════════════════════════════════════════════════
    # TELEGRAM NOTIFICATION METHODS
    # ═══════════════════════════════════════════════════════
    
    async def send_notification(
        self,
        notification_type: str,
        message: str,
        data: Dict[str, Any] = None,
        priority: str = "MEDIUM"
    ) -> bool:
        """
        Send notification via Telegram notification system.
        
        Args:
            notification_type: Type of notification (entry, exit, tp_hit, etc.)
            message: Human-readable message
            data: Additional structured data for templates
            priority: CRITICAL, HIGH, MEDIUM, LOW, INFO
            
        Returns:
            bool: True if notification was sent successfully
        """
        
        # Build notification payload
        payload = NotificationPayload(
            type=notification_type,
            plugin_id=self.plugin_id,
            message=message,
            data=data or {},
            priority=NotificationPriority[priority],
            timestamp=datetime.now()
        )
        
        # Route through unified notification system
        return await self.notification_router.route_notification(payload)
    
    async def send_trade_notification(
        self,
        trade: Trade,
        event_type: str,  # 'entry', 'exit', 'tp', 'sl', 'be'
        additional_data: Dict = None
    ) -> bool:
        """
        Convenience method for trade-related notifications.
        Automatically extracts trade data for templates.
        """
        
        # Map event type to notification type
        notif_type_map = {
            'entry': f'{self.plugin_id}_entry',
            'exit': f'{self.plugin_id}_exit',
            'tp': f'{self.plugin_id}_tp_hit',
            'sl': f'{self.plugin_id}_sl_hit',
            'be': f'{self.plugin_id}_breakeven',
        }
        
        notification_type = notif_type_map.get(event_type, f'{self.plugin_id}_{event_type}')
        
        # Build trade data
        trade_data = {
            'symbol': trade.symbol,
            'direction': trade.direction,
            'entry_price': trade.entry_price,
            'sl': trade.sl,
            'tp': trade.tp,
            'lot_size': trade.lot_size,
            'ticket': trade.ticket,
            'plugin_id': self.plugin_id,
            'plugin_name': self.get_display_name(),
            **(additional_data or {})
        }
        
        # Build message
        direction_emoji = "📈" if trade.direction == "BUY" else "📉"
        message = f"{direction_emoji} {trade.symbol} {trade.direction} @ {trade.entry_price}"
        
        return await self.send_notification(
            notification_type=notification_type,
            message=message,
            data=trade_data,
            priority="HIGH"
        )
    
    def get_display_name(self) -> str:
        """Get human-readable plugin name"""
        display_names = {
            'v3_combined': 'V3 Combined',
            'combinedlogic-1': 'Logic 1',
            'combinedlogic-2': 'Logic 2',
            'combinedlogic-3': 'Logic 3',
            'v6_price_action_15m': 'V6 15M',
            'v6_price_action_30m': 'V6 30M',
            'v6_price_action_1h': 'V6 1H',
            'v6_price_action_4h': 'V6 4H',
        }
        return display_names.get(self.plugin_id, self.plugin_id)
    
    def get_badge(self) -> str:
        """Get emoji badge for notifications"""
        badges = {
            'v3_combined': '🔷',
            'combinedlogic-1': '🔷1️⃣',
            'combinedlogic-2': '🔷2️⃣',
            'combinedlogic-3': '🔷3️⃣',
            'v6_price_action_15m': '🔶⏱️',
            'v6_price_action_30m': '🔶⏱️',
            'v6_price_action_1h': '🔶🕐',
            'v6_price_action_4h': '🔶🕓',
        }
        return badges.get(self.plugin_id, '⚙️')
```

---

## 📨 SECTION 2: PLUGIN NOTIFICATION FLOW

### How Plugins Send Notifications:

```
┌──────────────────────────────────────────────────────────────────┐
│                    PLUGIN NOTIFICATION FLOW                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. PLUGIN EVENT (Trade Entry/Exit/TP/SL)                        │
│         │                                                         │
│         ▼                                                         │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  plugin.on_trade_entry(trade)                             │    │
│  │  plugin.on_trade_exit(trade, result)                      │    │
│  │  plugin.on_tp_hit(trade, level)                           │    │
│  └─────────────────────────┬────────────────────────────────┘    │
│                            │                                      │
│  2. CALL SERVICE API                                              │
│         │                                                         │
│         ▼                                                         │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  await self.service_api.send_trade_notification(          │    │
│  │      trade=trade,                                         │    │
│  │      event_type='entry',                                  │    │
│  │      additional_data={'timeframe': '15M'}                 │    │
│  │  )                                                        │    │
│  └─────────────────────────┬────────────────────────────────┘    │
│                            │                                      │
│  3. NOTIFICATION ROUTER                                           │
│         │                                                         │
│         ▼                                                         │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  NotificationRouter.route_notification(payload)           │    │
│  │    • Determine target bot (Controller/Notification/Analytics)  │
│  │    • Apply template                                       │    │
│  │    • Set priority & options                               │    │
│  └─────────────────────────┬────────────────────────────────┘    │
│                            │                                      │
│  4. SEND TO TELEGRAM                                              │
│         │                                                         │
│         ▼                                                         │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  notification_bot.send_message(                           │    │
│  │      chat_id=notification_chat_id,                        │    │
│  │      text=formatted_message,                              │    │
│  │      reply_markup=inline_keyboard                         │    │
│  │  )                                                        │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔷 SECTION 3: V3 COMBINED PLUGIN TELEGRAM INTEGRATION

### Current Implementation (Working ✅):

```python
# File: src/logic_plugins/v3_combined/plugin.py

class V3CombinedPlugin:
    """V3 Combined plugin with full Telegram integration"""
    
    def __init__(self, service_api: ServiceAPI, config: Dict):
        self.service_api = service_api
        self.config = config
        self.enabled_logics = {
            'combinedlogic-1': config.get('logic1_enabled', True),
            'combinedlogic-2': config.get('logic2_enabled', True),
            'combinedlogic-3': config.get('logic3_enabled', True),
        }
    
    async def on_signal_received(self, signal: Signal):
        """Called when signal is received from TradingView"""
        
        # Notify about signal
        await self.service_api.send_notification(
            notification_type="signal_received",
            message=f"📡 Signal: {signal.symbol} {signal.direction} via {signal.logic}",
            data={
                'symbol': signal.symbol,
                'direction': signal.direction,
                'logic': signal.logic,
                'entry': signal.entry,
                'sl': signal.sl,
                'tp': signal.tp,
            },
            priority="HIGH"
        )
    
    async def on_trade_entry(self, trade: Trade):
        """Called when trade is placed"""
        
        await self.service_api.send_trade_notification(
            trade=trade,
            event_type='entry',
            additional_data={
                'logic': trade.logic,
                'logic_badge': self._get_logic_badge(trade.logic)
            }
        )
    
    async def on_trade_exit(self, trade: Trade, result: TradeResult):
        """Called when trade is closed"""
        
        # Determine exit type
        if result.exit_reason == 'tp_hit':
            event_type = 'tp'
        elif result.exit_reason == 'sl_hit':
            event_type = 'sl'
        else:
            event_type = 'exit'
        
        await self.service_api.send_trade_notification(
            trade=trade,
            event_type=event_type,
            additional_data={
                'exit_price': result.exit_price,
                'pnl': result.pnl,
                'pips': result.pips,
                'duration': str(result.duration),
                'logic': trade.logic,
            }
        )
    
    async def on_logic_toggled(self, logic: str, enabled: bool):
        """Called when logic is enabled/disabled via Telegram"""
        
        action = "enabled" if enabled else "disabled"
        emoji = "✅" if enabled else "❌"
        
        await self.service_api.send_notification(
            notification_type="plugin_config_changed",
            message=f"{emoji} {logic} {action}",
            data={
                'logic': logic,
                'enabled': enabled,
                'all_logics': self.enabled_logics
            },
            priority="MEDIUM"
        )
    
    def _get_logic_badge(self, logic: str) -> str:
        """Get visual badge for logic"""
        badges = {
            'combinedlogic-1': '🔷1️⃣',
            'combinedlogic-2': '🔷2️⃣',
            'combinedlogic-3': '🔷3️⃣',
        }
        return badges.get(logic, '🔷')
```

---

## 🔶 SECTION 4: V6 PRICE ACTION TELEGRAM INTEGRATION (MISSING ❌)

### Required Implementation:

```python
# File: src/logic_plugins/v6_price_action_15m/plugin.py

class V6PriceAction15MPlugin:
    """V6 Price Action 15M plugin with Telegram integration"""
    
    TIMEFRAME = "15m"
    DISPLAY_NAME = "V6 15M"
    BADGE = "🔶⏱️"
    
    def __init__(self, service_api: ServiceAPI, config: Dict):
        self.service_api = service_api
        self.config = config
        self.enabled = config.get('enabled', True)
    
    async def on_signal_received(self, signal: Signal):
        """Called when price action signal detected"""
        
        await self.service_api.send_notification(
            notification_type=f"v6_signal_{self.TIMEFRAME}",
            message=f"🎯 V6 {self.TIMEFRAME.upper()} Signal: {signal.symbol} {signal.direction}",
            data={
                'symbol': signal.symbol,
                'direction': signal.direction,
                'timeframe': self.TIMEFRAME,
                'entry': signal.entry,
                'sl': signal.sl,
                'tp': signal.tp,
                'pattern': signal.pattern,  # V6 specific
            },
            priority="HIGH"
        )
    
    async def on_trade_entry(self, trade: Trade):
        """Called when V6 trade is placed"""
        
        await self.service_api.send_notification(
            notification_type=f"v6_entry_{self.TIMEFRAME}",
            message=f"🎯 V6 {self.TIMEFRAME.upper()} Entry: {trade.symbol} {trade.direction}",
            data={
                'symbol': trade.symbol,
                'direction': trade.direction,
                'entry_price': trade.entry_price,
                'sl': trade.sl,
                'tp': trade.tp,
                'lot_size': trade.lot_size,
                'timeframe': self.TIMEFRAME,
                'timeframe_emoji': self._get_timeframe_emoji(),
                'plugin_badge': self.BADGE,
            },
            priority="HIGH"
        )
    
    async def on_trade_exit(self, trade: Trade, result: TradeResult):
        """Called when V6 trade is closed"""
        
        # Determine notification type
        if result.exit_reason == 'tp_hit':
            notif_type = f"v6_tp_hit"
        elif result.exit_reason == 'sl_hit':
            notif_type = f"v6_sl_hit"
        else:
            notif_type = f"v6_exit"
        
        await self.service_api.send_notification(
            notification_type=notif_type,
            message=f"🎯 V6 {self.TIMEFRAME.upper()} Exit: {trade.symbol} {'+' if result.pnl >= 0 else ''}{result.pnl:.2f}",
            data={
                'symbol': trade.symbol,
                'direction': trade.direction,
                'entry_price': trade.entry_price,
                'exit_price': result.exit_price,
                'pnl': result.pnl,
                'pips': result.pips,
                'duration': str(result.duration),
                'timeframe': self.TIMEFRAME,
                'timeframe_emoji': self._get_timeframe_emoji(),
                'exit_reason': result.exit_reason,
            },
            priority="HIGH" if abs(result.pnl) > 50 else "MEDIUM"
        )
    
    async def on_enabled_changed(self, enabled: bool):
        """Called when plugin is enabled/disabled via Telegram"""
        
        action = "enabled" if enabled else "disabled"
        emoji = "✅" if enabled else "❌"
        
        await self.service_api.send_notification(
            notification_type=f"v6_timeframe_{action}",
            message=f"{emoji} V6 {self.TIMEFRAME.upper()} {action}",
            data={
                'timeframe': self.TIMEFRAME,
                'enabled': enabled,
            },
            priority="MEDIUM"
        )
    
    def _get_timeframe_emoji(self) -> str:
        """Get emoji for timeframe"""
        emojis = {
            '15m': '⏱️',
            '30m': '⏱️',
            '1h': '🕐',
            '4h': '🕓',
        }
        return emojis.get(self.TIMEFRAME, '⏱️')
```

### Copy Pattern for Other V6 Timeframes:

```python
# File: src/logic_plugins/v6_price_action_30m/plugin.py
class V6PriceAction30MPlugin(V6PriceActionBasePlugin):
    TIMEFRAME = "30m"
    DISPLAY_NAME = "V6 30M"
    BADGE = "🔶⏱️"

# File: src/logic_plugins/v6_price_action_1h/plugin.py
class V6PriceAction1HPlugin(V6PriceActionBasePlugin):
    TIMEFRAME = "1h"
    DISPLAY_NAME = "V6 1H"
    BADGE = "🔶🕐"

# File: src/logic_plugins/v6_price_action_4h/plugin.py
class V6PriceAction4HPlugin(V6PriceActionBasePlugin):
    TIMEFRAME = "4h"
    DISPLAY_NAME = "V6 4H"
    BADGE = "🔶🕓"
```

---

## ⚙️ SECTION 5: PER-PLUGIN CONFIGURATION VIA TELEGRAM

### Configuration Structure:

```json
// File: config/config.json

{
  "plugins": {
    "v3_combined": {
      "enabled": true,
      "logics": {
        "combinedlogic-1": {
          "enabled": true,
          "lot_size": 0.02,
          "max_trades": 3
        },
        "combinedlogic-2": {
          "enabled": true,
          "lot_size": 0.02,
          "max_trades": 3
        },
        "combinedlogic-3": {
          "enabled": false,
          "lot_size": 0.01,
          "max_trades": 2
        }
      },
      "re_entry": {
        "tp_reentry_enabled": true,
        "sl_hunt_enabled": true,
        "max_levels": 3
      }
    },
    "v6_price_action": {
      "enabled": true,
      "timeframes": {
        "15m": {
          "enabled": true,
          "lot_size": 0.01,
          "max_trades": 2
        },
        "30m": {
          "enabled": true,
          "lot_size": 0.01,
          "max_trades": 2
        },
        "1h": {
          "enabled": false,
          "lot_size": 0.02,
          "max_trades": 1
        },
        "4h": {
          "enabled": false,
          "lot_size": 0.02,
          "max_trades": 1
        }
      },
      "re_entry": {
        "tp_reentry_enabled": false,
        "sl_hunt_enabled": true,
        "max_levels": 2
      }
    }
  }
}
```

### Telegram Config Commands:

```python
# Commands for per-plugin configuration

# V3 Combined
/logic1_config     - Show/edit Logic 1 config
/logic2_config     - Show/edit Logic 2 config
/logic3_config     - Show/edit Logic 3 config
/v3_reentry_config - V3 re-entry settings

# V6 Price Action
/v6_15m_config     - Show/edit V6 15M config
/v6_30m_config     - Show/edit V6 30M config
/v6_1h_config      - Show/edit V6 1H config
/v6_4h_config      - Show/edit V6 4H config
/v6_reentry_config - V6 re-entry settings
```

### Plugin Config Menu:

```
┌────────────────────────────────────────┐
│    ⚙️ V6 15M CONFIGURATION             │
│                                        │
│  Status: 🟢 ENABLED                    │
│                                        │
├────────────────────────────────────────┤
│  📊 TRADING SETTINGS:                  │
│  • Lot Size: 0.01                      │
│  • Max Trades: 2                       │
│  • Risk %: 1%                          │
│                                        │
├────────────────────────────────────────┤
│  🔄 RE-ENTRY SETTINGS:                 │
│  • TP Re-entry: 🔴 OFF                 │
│  • SL Hunt: 🟢 ON                      │
│  • Max Levels: 2                       │
│                                        │
├────────────────────────────────────────┤
│                                        │
│  [Toggle Status]  [Edit Lot Size]      │
│                                        │
│  [TP Re-entry]    [SL Hunt]            │
│                                        │
│  [🔙 Back to V6 Control]               │
│                                        │
└────────────────────────────────────────┘
```

---

## 🔗 SECTION 6: TELEGRAM COMMAND ROUTING TO PLUGINS

### Command Router:

```python
# File: src/clients/telegram_bot.py

class TelegramBot:
    async def route_plugin_command(self, command: str, params: List[str], user_id: int):
        """Route commands to appropriate plugin handler"""
        
        # V3 Combined commands
        if command.startswith('/logic'):
            return await self.v3_plugin_handler.handle_command(command, params)
        
        # V6 Price Action commands
        elif command.startswith('/v6_') or command.startswith('/tf'):
            return await self.v6_plugin_handler.handle_command(command, params)
        
        # Re-entry commands - route to correct plugin
        elif command.startswith('/reentry_'):
            plugin = params[0] if params else 'global'
            if plugin == 'v3':
                return await self.v3_plugin_handler.handle_reentry_command(command, params[1:])
            elif plugin == 'v6':
                return await self.v6_plugin_handler.handle_reentry_command(command, params[1:])
            else:
                return await self.global_reentry_handler.handle_command(command, params)
```

### Plugin Handler Interface:

```python
# File: src/telegram/plugin_handlers/base_plugin_handler.py

class BasePluginHandler(ABC):
    """Base class for plugin-specific Telegram handlers"""
    
    def __init__(self, telegram_bot, plugin_manager):
        self.bot = telegram_bot
        self.plugin_manager = plugin_manager
    
    @abstractmethod
    async def handle_command(self, command: str, params: List[str]) -> bool:
        """Handle plugin-specific command"""
        pass
    
    @abstractmethod
    async def handle_callback(self, callback_query) -> bool:
        """Handle plugin-specific callback"""
        pass
    
    @abstractmethod
    def show_status_menu(self, user_id: int, message_id: int = None):
        """Show plugin status menu"""
        pass
    
    @abstractmethod
    def show_config_menu(self, user_id: int, message_id: int = None):
        """Show plugin configuration menu"""
        pass
```

---

## 📊 SECTION 7: PLUGIN PERFORMANCE TRACKING

### Performance Queries:

```python
# File: src/database/plugin_analytics.py

class PluginAnalytics:
    """Analytics queries for plugin performance"""
    
    def get_plugin_performance(self, plugin_id: str, period: str = 'all') -> Dict:
        """Get performance metrics for specific plugin"""
        
        query = """
        SELECT 
            COUNT(*) as trade_count,
            SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN pnl <= 0 THEN 1 ELSE 0 END) as losses,
            SUM(pnl) as total_pnl,
            AVG(pnl) as avg_trade,
            AVG(CASE WHEN pnl > 0 THEN pnl END) as avg_win,
            AVG(CASE WHEN pnl <= 0 THEN pnl END) as avg_loss,
            MAX(pnl) as best_trade,
            MIN(pnl) as worst_trade
        FROM trades
        WHERE plugin_id = ?
        """
        
        if period == 'today':
            query += " AND DATE(close_time) = DATE('now')"
        elif period == 'week':
            query += " AND close_time >= DATE('now', '-7 days')"
        elif period == 'month':
            query += " AND close_time >= DATE('now', '-30 days')"
        
        result = self.db.execute(query, (plugin_id,)).fetchone()
        
        return {
            'trade_count': result[0] or 0,
            'wins': result[1] or 0,
            'losses': result[2] or 0,
            'win_rate': (result[1] / result[0] * 100) if result[0] > 0 else 0,
            'total_pnl': result[3] or 0,
            'avg_trade': result[4] or 0,
            'avg_win': result[5] or 0,
            'avg_loss': result[6] or 0,
            'best_trade': result[7] or 0,
            'worst_trade': result[8] or 0,
        }
    
    def get_all_plugins_comparison(self) -> Dict[str, Dict]:
        """Get performance comparison for all plugins"""
        
        plugins = [
            'combinedlogic-1', 'combinedlogic-2', 'combinedlogic-3',
            'v6_price_action_15m', 'v6_price_action_30m',
            'v6_price_action_1h', 'v6_price_action_4h'
        ]
        
        return {plugin: self.get_plugin_performance(plugin) for plugin in plugins}
```

---

## ✅ IMPLEMENTATION CHECKLIST

### Critical (Week 1):
- [ ] Add `send_notification()` calls to V6 plugins
- [ ] Create V6 notification types in NotificationType enum
- [ ] Wire V6 plugins to ServiceAPI
- [ ] Add V6 entries to notification router

### High (Week 2):
- [ ] Create per-plugin configuration menus
- [ ] Add plugin config commands
- [ ] Create plugin handler interface
- [ ] Implement per-plugin re-entry settings

### Medium (Week 3):
- [ ] Add plugin performance queries
- [ ] Create plugin comparison command
- [ ] Add plugin badges to all notifications
- [ ] Implement timeframe identification in V6 notifications

---

## 🔧 WIRING INSTRUCTIONS SUMMARY

### 1. Update V6 Plugins:

```python
# In each V6 plugin file, add notification calls:

async def on_trade_entry(self, trade: Trade):
    await self.service_api.send_notification(
        notification_type=f"v6_entry_{self.TIMEFRAME}",
        message=f"🎯 V6 {self.TIMEFRAME.upper()} Entry: {trade.symbol}",
        data={...},
        priority="HIGH"
    )
```

### 2. Update Notification Router:

```python
# Add V6 types to routing table:
self.routing_table.update({
    NotificationType.V6_ENTRY_15M: self.notification,
    NotificationType.V6_ENTRY_30M: self.notification,
    # ... etc
})
```

### 3. Update telegram_bot.py:

```python
# Add plugin handler wiring:
from src.telegram.plugin_handlers.v6_handler import V6PluginHandler

self.v6_handler = V6PluginHandler(self, self.trading_engine.plugin_manager)

# Add callback routing:
if callback_data.startswith("v6_"):
    await self.v6_handler.handle_callback(callback_query)
```

---

**END OF V5 PLUGIN INTEGRATION DOCUMENTATION**

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