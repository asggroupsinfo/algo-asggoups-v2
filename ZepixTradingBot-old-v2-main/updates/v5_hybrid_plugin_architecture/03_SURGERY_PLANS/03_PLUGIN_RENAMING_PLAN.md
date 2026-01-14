# PLUGIN RENAMING PLAN - User-Defined Naming Schema

**Objective:** Rename all plugins to user-defined names that clearly identify Pine source (V3/V6) and timeframe.

**Estimated Effort:** 4-6 hours

---

## PART 1: USER-DEFINED NAMING SCHEMA (MANDATORY)

### 1.1 V3 Plugin Group (combinedv3)

| Current Name | New Name | Timeframe | Logic Type |
|--------------|----------|-----------|------------|
| combined_v3 | v3-logic-01-5min | 5-minute | Scalping (Logic-1) |
| combined_v3 | v3-logic-02-15min | 15-minute | Intraday (Logic-2) |
| combined_v3 | v3-logic-03-1h | 1-hour | Swing (Logic-3) |

**Note:** Currently there's ONE combined_v3 plugin that handles all 3 logics. We need to either:
- Option A: Keep single plugin, use internal routing (simpler)
- Option B: Split into 3 separate plugins (cleaner architecture)

**Recommendation:** Option A - Keep single plugin named `v3-logic-combined` that internally routes to Logic-1/2/3 based on timeframe.

### 1.2 V6 Plugin Group (price-action-v6)

| Current Name | New Name | Timeframe | Strategy |
|--------------|----------|-----------|----------|
| price_action_1m | v6-logic-01-1min | 1-minute | Scalping |
| price_action_5m | v6-logic-02-5min | 5-minute | Momentum |
| price_action_15m | v6-logic-03-15min | 15-minute | Intraday |
| price_action_1h | v6-logic-04-1h | 1-hour | Swing |

---

## PART 2: FOLDER STRUCTURE CHANGES

### 2.1 Current Structure

```
src/logic_plugins/
├── _template/
├── combined_v3/
│   ├── __init__.py
│   ├── config.json
│   ├── order_manager.py
│   ├── plugin.py
│   ├── signal_handlers.py
│   └── trend_validator.py
├── price_action_1m/
│   ├── __init__.py
│   ├── config.json
│   └── plugin.py
├── price_action_5m/
│   ├── __init__.py
│   ├── config.json
│   └── plugin.py
├── price_action_15m/
│   ├── __init__.py
│   ├── config.json
│   └── plugin.py
├── price_action_1h/
│   ├── __init__.py
│   ├── config.json
│   └── plugin.py
└── README.md
```

### 2.2 New Structure

```
src/logic_plugins/
├── _template/
├── v3-logic-combined/          # Renamed from combined_v3
│   ├── __init__.py
│   ├── config.json
│   ├── order_manager.py
│   ├── plugin.py
│   ├── signal_handlers.py
│   └── trend_validator.py
├── v6-logic-01-1min/           # Renamed from price_action_1m
│   ├── __init__.py
│   ├── config.json
│   └── plugin.py
├── v6-logic-02-5min/           # Renamed from price_action_5m
│   ├── __init__.py
│   ├── config.json
│   └── plugin.py
├── v6-logic-03-15min/          # Renamed from price_action_15m
│   ├── __init__.py
│   ├── config.json
│   └── plugin.py
├── v6-logic-04-1h/             # Renamed from price_action_1h
│   ├── __init__.py
│   ├── config.json
│   └── plugin.py
└── README.md
```

---

## PART 3: FILE-BY-FILE UPDATE INSTRUCTIONS

### 3.1 Rename Folders

```bash
# V3 Plugin
mv src/logic_plugins/combined_v3 src/logic_plugins/v3-logic-combined

# V6 Plugins
mv src/logic_plugins/price_action_1m src/logic_plugins/v6-logic-01-1min
mv src/logic_plugins/price_action_5m src/logic_plugins/v6-logic-02-5min
mv src/logic_plugins/price_action_15m src/logic_plugins/v6-logic-03-15min
mv src/logic_plugins/price_action_1h src/logic_plugins/v6-logic-04-1h
```

### 3.2 Update Plugin Class Names

#### v3-logic-combined/plugin.py

**Current (line 28):**
```python
class CombinedV3Plugin(BaseLogicPlugin):
```

**New:**
```python
class V3LogicCombinedPlugin(BaseLogicPlugin):
```

#### v6-logic-01-1min/plugin.py

**Current:**
```python
class PriceAction1mPlugin(BaseLogicPlugin):
```

**New:**
```python
class V6Logic011minPlugin(BaseLogicPlugin):
```

#### v6-logic-02-5min/plugin.py

**Current:**
```python
class PriceAction5mPlugin(BaseLogicPlugin):
```

**New:**
```python
class V6Logic025minPlugin(BaseLogicPlugin):
```

#### v6-logic-03-15min/plugin.py

**Current:**
```python
class PriceAction15mPlugin(BaseLogicPlugin):
```

**New:**
```python
class V6Logic0315minPlugin(BaseLogicPlugin):
```

#### v6-logic-04-1h/plugin.py

**Current:**
```python
class PriceAction1hPlugin(BaseLogicPlugin):
```

**New:**
```python
class V6Logic041hPlugin(BaseLogicPlugin):
```

### 3.3 Update config.json Files

#### v3-logic-combined/config.json

**Current:**
```json
{
  "plugin_id": "combined_v3",
  "name": "Combined V3 Logic",
  ...
}
```

**New:**
```json
{
  "plugin_id": "v3-logic-combined",
  "name": "V3 Combined Logic (Pine Script V3)",
  "pine_source": "V3",
  "supported_timeframes": ["5", "15", "60", "240"],
  "logic_mapping": {
    "5": "logic-01-scalping",
    "15": "logic-02-intraday",
    "60": "logic-03-swing",
    "240": "logic-03-swing"
  },
  ...
}
```

#### v6-logic-01-1min/config.json

**Current:**
```json
{
  "plugin_id": "price_action_1m",
  ...
}
```

**New:**
```json
{
  "plugin_id": "v6-logic-01-1min",
  "name": "V6 Logic 01 - 1 Minute Scalping",
  "pine_source": "V6",
  "timeframe": "1",
  "strategy": "scalping",
  "order_type": "ORDER_B_ONLY",
  ...
}
```

### 3.4 Update Import Statements

#### Files to Update:

| File | Current Import | New Import |
|------|----------------|------------|
| plugin_registry.py | `from src.logic_plugins.combined_v3.plugin import CombinedV3Plugin` | `from src.logic_plugins.v3_logic_combined.plugin import V3LogicCombinedPlugin` |

**Note:** Python imports use underscores, so folder names with hyphens need to be accessed differently. We have two options:

**Option A: Use underscores in folder names (Python-friendly)**
```
v3_logic_combined/
v6_logic_01_1min/
v6_logic_02_5min/
v6_logic_03_15min/
v6_logic_04_1h/
```

**Option B: Use hyphens but access via importlib (as currently done)**
```python
# plugin_registry.py already uses importlib.import_module()
# This works with hyphenated folder names
module_path = f"{package_path}.{plugin_id}.plugin"
plugin_module = importlib.import_module(module_path)
```

**Recommendation:** Use Option A (underscores) for Python compatibility, but display names can use hyphens.

### 3.5 REVISED Folder Names (Python-Compatible)

```
src/logic_plugins/
├── v3_logic_combined/          # Underscore for Python import
├── v6_logic_01_1min/
├── v6_logic_02_5min/
├── v6_logic_03_15min/
├── v6_logic_04_1h/
```

---

## PART 4: FILES REQUIRING UPDATES

### 4.1 Core Files

| File | Lines | Find | Replace |
|------|-------|------|---------|
| trading_engine.py | Multiple | `combined_v3` | `v3_logic_combined` |
| trading_engine.py | Multiple | `combinedlogic-1` | `v3-logic-01-5min` |
| trading_engine.py | Multiple | `combinedlogic-2` | `v3-logic-02-15min` |
| trading_engine.py | Multiple | `combinedlogic-3` | `v3-logic-03-1h` |

### 4.2 Plugin System Files

| File | Lines | Find | Replace |
|------|-------|------|---------|
| plugin_registry.py | N/A | Dynamic loading | No changes needed |
| service_api.py | Multiple | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |

### 4.3 Service Files

| File | Find | Replace |
|------|------|---------|
| order_execution_service.py | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |
| trend_management_service.py | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |

### 4.4 Manager Files

| File | Find | Replace |
|------|------|---------|
| dual_order_manager.py | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |
| profit_booking_manager.py | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |
| timeframe_trend_manager.py | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |
| session_manager.py | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |

### 4.5 Menu Files

| File | Find | Replace |
|------|------|---------|
| profit_booking_menu_handler.py | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |
| timeframe_menu_handler.py | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |
| menu_constants.py | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |
| menu_manager.py | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |
| command_mapping.py | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |
| command_executor.py | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |

### 4.6 Utility Files

| File | Find | Replace |
|------|------|---------|
| pip_calculator.py | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |
| profit_sl_calculator.py | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |
| optimized_logger.py | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |

### 4.7 Client Files

| File | Find | Replace |
|------|------|---------|
| telegram_bot_fixed.py | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |
| menu_callback_handler.py | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |
| timeframe_handlers_ext.py | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |

### 4.8 Model Files

| File | Find | Replace |
|------|------|---------|
| models.py | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |
| v3_alert_models.py | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |
| models/v3_alert.py | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |

### 4.9 Config Files

| File | Find | Replace |
|------|------|---------|
| config.py | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |

### 4.10 Telegram Files

| File | Find | Replace |
|------|------|---------|
| notification_bot.py | `combinedlogic-1/2/3` | `v3-logic-01/02/03` |

---

## PART 5: DATABASE TABLE NAME UPDATES

### 5.1 Current Table Names

```sql
-- In data/schemas/combined_v3_schema.sql
combined_v3_trades
v3_profit_bookings
v3_signals_log
v3_daily_stats

-- In data/schemas/price_action_v6_schema.sql
price_action_1m_trades
price_action_5m_trades
price_action_15m_trades
price_action_1h_trades
```

### 5.2 New Table Names

```sql
-- V3 Tables
v3_logic_combined_trades
v3_logic_profit_bookings
v3_logic_signals_log
v3_logic_daily_stats

-- V6 Tables
v6_logic_01_1min_trades
v6_logic_02_5min_trades
v6_logic_03_15min_trades
v6_logic_04_1h_trades
```

---

## PART 6: TELEGRAM NOTIFICATION UPDATES

### 6.1 Current Notification Format

```
🎯 V3 DUAL ORDER PLACED
Signal: Institutional_Launchpad
Logic: combinedlogic-1
```

### 6.2 New Notification Format

```
🎯 V3 DUAL ORDER PLACED
Signal: Institutional_Launchpad
Logic: v3-logic-01-5min (Scalping)
```

---

## PART 7: DOCUMENTATION UPDATES

### 7.1 Files to Update

| File | Description |
|------|-------------|
| docs/USER_GUIDE_V5.md | Update plugin names |
| docs/MIGRATION_GUIDE.md | Update plugin names |
| updates/v5_hybrid_plugin_architecture/01_PLANNING/*.md | Update all references |
| README.md | Update plugin names |

---

## PART 8: VERIFICATION CHECKLIST

After renaming, verify:

- [ ] All plugin folders renamed correctly
- [ ] All plugin class names updated
- [ ] All config.json files updated
- [ ] All imports work correctly
- [ ] All find-replace completed in 30+ files
- [ ] Database table names updated
- [ ] Telegram notifications show new names
- [ ] Documentation updated
- [ ] Bot starts without import errors
- [ ] Plugins load correctly

---

## PART 9: ROLLBACK PLAN

If renaming causes issues:

1. **Git Revert:** All changes in single commit
2. **Backup:** Original folders saved with .backup suffix
3. **Mapping File:** Create old-to-new name mapping for reference

---

## SUCCESS CRITERIA

1. **All plugins use user-defined naming schema**
2. **Names clearly indicate Pine source (V3/V6)**
3. **Names clearly indicate timeframe**
4. **No references to old names remain**
5. **Bot starts and loads all plugins correctly**
