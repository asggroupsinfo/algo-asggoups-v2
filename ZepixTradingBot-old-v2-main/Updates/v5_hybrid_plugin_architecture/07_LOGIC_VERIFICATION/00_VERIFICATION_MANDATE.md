# 🕵️‍♂️ MISSION: V3 & V6 DEEP LOGIC AUDIT (ZERO TOLERANCE)

## 🎯 USER OBJECTIVE
**"Mujhe complete report chaiye 2 alag alag V3 ke liye aur V6 ke liye."**
(I want two separate, complete reports for V3 and V6.)

The user specifically mentions:
1.  **V3 Logic Parsing:** The V3 documentation explains how `Logic 1`, `Logic 2`, and `Logic 3` handle different Pine alerts.
2.  **V6 Logic Parsing:** The V6 documentation explains its specific alert handling.
3.  **Execution Flow:** It's not just about receiving the alert, but **how the bot executes it**. Does it match the documented behavior?

## 📂 SOURCE OF TRUTH (DOCUMENTATION)

**V3 Documentation:**
- Search in: `updates/v5_hybrid_plugin_architecture/COMBINED LOGICS/V3_FINAL_REPORTS`
- Check for Logic 1/2/3 specific rules.

**V6 Documentation:**
- Search in: `updates/v5_hybrid_plugin_architecture/V6_INTEGRATION_PROJECT`
- Check for 4-Pillar validation and Price Action rules.

## 📋 YOUR TASK
**Do not ask me what to check.**
You must autonomously read the documentation and verify the code against it effectively.

**Verification Steps:**
1.  **Read the Docs:** Understand exactly how V3 and V6 alerts *should* be processed.
2.  **Read the Code:** Scan the actual implementation in `src/logic_plugins/` and `src/core/`.
3.  **Compare:**
    - Does the code handle `Logic 1`, `Logic 2`, `Logic 3` distinction correctly?
    - Does `signal_parser.py` correctly identify V6 vs V3?
    - Do the **Action Executions** (Order Placement, SL/TP, Recovery) match the text?

## � DELIVERABLES (2 SEPARATE REPORTS)

You must generate two detailed reports in `updates/v5_hybrid_plugin_architecture/07_LOGIC_VERIFICATION/`:

### 1. `V3_DEEP_AUDIT_REPORT.md`
- logic 1/2/3 mapping verification.
- Alert-to-Action flow verification.
- Bugs/Errors/Missing implementation.

### 2. `V6_DEEP_AUDIT_REPORT.md`
- Price Action logic verification.
- Alert-to-Action flow verification.
- Bugs/Errors/Missing implementation.

**START NOW.**
