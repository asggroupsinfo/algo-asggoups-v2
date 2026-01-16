# PROJECT MEMORY RESTORED: Zepix Trading Bot V6 Integration
*Restored Date: 2026-01-13*
*Persona: Devin (Prompt Engineer)*

## 🧠 CONTEXT RESTORED
**Project:** Update Zepix Bot to support Pine Script V6 "Signals & Overlays"
**Current Status:** NON-FUNCTIONAL (Critical Mismatch Found)
**Last Action:** Autonomous Audit of Pine Script vs Python Bot

## 🚨 CRITICAL FINDINGS (The "Memory")
The previous analysis (`PINE_BOT_AUTONOMOUS_AUDIT.md`) revealed a major breakage:
1.  **Format Mismatch:**
    - Pine V6 sends: `BULLISH_ENTRY|EURUSD|...` (Pipe Separated)
    - Bot Expects: JSON Object or Attribute Access
    - **Result:** Bot crashes or ignores all V6 signals.
2.  **Signal Count Mismatch:**
    - Pine V6 has **14 new alerts** (Momentum, State Change, etc.)
    - Bot only knows V3 alerts.
3.  **Missing Logic:**
    - No router to handle 1m/5m/15m/1h logic separation.

## 📋 EXECUTION PLAN (Immediate Next Steps)
Derived from `EXECUTION_ROADMAP.md` and Audit Recommendations:

### Priority 1: V6 Alert Parser (CRITICAL)
- Create `src/logic_plugins/price_action_v6/alert_parser.py`
- Logic: Split string by `|`, map to Python Dict.

### Priority 2: Signal Mapper
- Update `src/logic_plugins/price_action_v6/plugin.py`
- Logic: Map `BULLISH_ENTRY` -> `handle_breakout_entry`.

### Priority 3: Timeframe Router
- Create `src/logic_plugins/price_action_v6/timeframe_router.py`
- Logic: `if tf==1m -> use 1m_plugin`

## 🎯 GOAL
Make V6 Pine generated alerts 100% readable by the Python Bot.
