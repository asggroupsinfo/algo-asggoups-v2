# 🦅 MISSION: THE TELEGRAM INTEGRITY & LEGACY VERIFICATION

## 🎯 USER OBJECTIVE
The user demands a **Final Verification** of the Telegram Ecosystem.
Specifically:
1.  **Legacy Command Parity:** The old bot had **95+ Commands**. Are they ALL present in V5? Where are they?
2.  **Notification Parity:** Are ALL legacy notification types supported in V5?
3.  **Documentation:** Create a definitive guide for Commands & Notifications answering "Kaise hai, Kaha hai, Kya naya hai".

## 📂 SOURCE OF TRUTH (LEGACY)
1.  `docs/developer_notes/TELEGRAM_COMMAND_STRUCTURE.md` ( The 95+ Command List)
2.  `docs/developer_notes/TELEGRAM_NOTIFICATIONS.md` (The Notification Types)

## 🔍 WHAT TO AUDIT (CODE SCAN)
1.  `src/telegram/command_registry.py` (Does it register 95+ commands?)
2.  `src/telegram/controller_bot.py` (Is it wired to the registry?)
3.  `src/telegram/notification_bot.py` (Does it handle all alert types?)
4.  `src/telegram/ui/plugin_control_menu.py` (Where is the new UI?)

## 📝 DELIVERABLES (MUST CREATE)

### 1. The Command Matrix Report
- **File:** `updates/.../13_TELEGRAM_INTEGRITY_CHECK/COMMAND_INTEGRITY_REPORT.md`
- **Columns:** `Legacy Command` | `V5 Handler` | `Status (Active/Missing)` | `New/Legacy`.
- **Verdict:** Must match 100% or highlight specific gaps.

### 2. The Notification Matrix Report
- **File:** `updates/.../13_TELEGRAM_INTEGRITY_CHECK/NOTIFICATION_INTEGRITY_REPORT.md`
- **Columns:** `Alert Type` | `V5 Handler` | `Status`.

### 3. The Ultimate Telegram Manual
- **File:** `docs/V5_BIBLE/03_TELEGRAM/COMPLETE_TELEGRAM_MANUAL.md`
- **Content:**
  - Full list of commands with usage.
  - How to use the new Plugin Menu (`/plugins`).
  - Explanation of Notifications.

## 🤖 EXECUTION PROTOCOL
1.  **Scan Legacy Docs:** Extract every single command and alert type.
2.  **Scan V5 Code:** grep for these commands in `src`.
3.  **Prove Wiring:** Show WHERE the command is handled.
4.  **Report & Document.**

**GO.**
