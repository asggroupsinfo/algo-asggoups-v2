# 🚑 MISSION: V4 FOREX SESSION SYSTEM RESTORATION

## 🔴 CRITICAL USER EVIDENCE
The user states: **"Mere pass proof hai ki V4 Forex Session update complete implement ho chuka tha."**
Path: `updates/v4_forex_session_system/` (contains final reports and plans).

## 🧩 THE MISSING PIECES
The V5 transformation likely overwrote or ignored these V4 features:
1.  **Fixed Clock System** (The "Real-time Update" on Telegram).
2.  **Voice Notification System** (Detailed in `11_VOICE_NOTIFICATION_IMPLEMENTATION_REPORT.md` in V4 folder).
3.  **Forex Session System** (Asian/London/NY logic).

## 📋 YOUR TASK: THE "RE-INTEGRATION" PROTOCOL

### Step 1: V4 Forensics (The Base Plan)
**CRITICAL:** Treat the documents in `updates/v4_forex_session_system/` as the **Source of Truth** for logic.
- **Base Plan Reference:** `01_IMPLEMENTATION_PLAN.md`, `10_VOICE_NOTIFICATION_FINAL_IMPLEMENTATION_PLAN.md`.
- **Logic:** Understand strictly *how* it worked before.

### Step 2: V5 Specific Adaptation Planning
**DO NOT just copy-paste.** You must **ADAPT** the V4 logic to fit the new **V5 Hybrid Plugin Architecture**.
- **Clock:** Move logic from monolithic bot -> `ControllerBot` background task.
- **Session:** Create a `SessionService` in `src/core/services/` that Plugins can rely on.
- **Voice:** Integrate `VoiceAlertSystem` with the `NotificationBot` (so it sends audio files/alerts via Telegram).

**Create a New Plan:** `updates/v5_hybrid_plugin_architecture/09_LEGACY_RESTORATION/01_V5_ADAPTATION_PLAN.md`.
- Detail exactly *where* each V4 component fits in V5.

### Step 3: Execution (The Restoration)
1.  **Code:** Re-write/Recover the missing Python files.
2.  **Wiring:** Connect them to the V5 `main.py` and `3-Bot System`.
3.  **Testing:** Verify they work (Create `tests/integration/test_legacy_features.py`).

### Step 4: Final Documentation Audit (Zero Gaps)
Once verified:
1.  Compare the **Original Bot Docs** (`DOCUMENTATION/`) vs **Current V5 Bot**.
2.  Ensure **EVERY SINGLE FEATURE** (Clock, Calendar, Sessions, Smart Lot, Profit Locking) is:
    - **Present in Code.**
    - **Documented in Bible.**
3.  Update the `06_DOCUMENTATION_BIBLE` to be truly complete. Nothing should be missing.

## 🚀 EXECUTION INSTRUCTION
1.  **Analyze V4 Docs.**
2.  **Create V5 Adaptation Plan.**
3.  **Implement & Test.**
4.  **Update Documentation Bible.**

**START NOW.**
