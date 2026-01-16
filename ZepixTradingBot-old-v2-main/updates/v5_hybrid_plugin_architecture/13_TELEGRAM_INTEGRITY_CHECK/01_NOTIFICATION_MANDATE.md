# 🔔 NOTIFICATION INTEGRITY MANDATE: LEGACY + V5 + V6

## 🎯 USER OBJECTIVE
The user demands a rigorous audit of the **Notification System**:
1.  **Legacy Validation:** Did we keep ALL old notification types? (Source: `docs/developer_notes/TELEGRAM_NOTIFICATIONS.md`)
2.  **Migration Check:** Are they correctly routed to the new `NotificationBot`?
3.  **V6 Expansion Check:** Did we add new notifications for V6 Price Action Logic? (e.g., ADX Filter alerts, Pattern Recognition alerts).
4.  **Comparison:** "Pehle kitne the vs Ab kitne hain."

## 📂 SOURCE OF TRUTH
1.  **Old Docs:** `docs/developer_notes/TELEGRAM_NOTIFICATIONS.md`
2.  **V6 Logic:** `src/plugins/v6_price_action/plugin.py` (New logic needs new alerts).

## 🔍 THE AUDIT TASKS

### Task 1: The Legacy Comparison
- Create `NOTIFICATION_COMPARISON_MATRIX.md`.
- List every alert from Old Docs.
- Verify if it exists in `src/telegram/notification_bot.py`.

### Task 2: The V6 Alert Audit
- Did we create alerts for:
  - "V6 Entry Triggered (15m ADX confirmed)"?
  - "V6 Pattern Match"?
- If MISSING, mark as **CRITICAL GAP**.

### Task 3: The Ultimate Notification Manual
- Create `docs/V5_BIBLE/03_TELEGRAM/COMPLETE_NOTIFICATION_MANUAL.md`.
- Document every single alert the bot can throw (Legacy + V6).
- Include screenshots/examples of the text format.

## 🤖 EXECUTION PROTOCOL
1.  **Scan Code:** `unified_notification_router.py` and `notification_bot.py`.
2.  **Identify Gaps:** If V6 logic code has `alert()` but Notification Bot has no handler -> **FAIL**.
3.  **Fix & Document.**

**GO.**
