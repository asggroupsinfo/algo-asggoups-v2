# 🕵️‍♂️ MISSION: LEGACY FEATURE REGRESSION AUDIT

## 🔴 CRITICAL USER CONCERN
The user suspects that **Critical Features** from the original bot might have been:
1.  **Deleted** during V5 transformation.
2.  **Ignored** by the V5 Documentation Bible.
3.  **Broken** in the current build.

**Quote:** *"Devin ne documetion complete nahi banai hai... bot ke features gayab kar diye jaise real clock, calender, session maneger, profit protection..."*

## 📂 AUDIT SCOPE

### 1. The Comparison Sources
- **Legacy Docs (The "Promise"):** `DOCUMENTATION/` (especially `FEATURES_SPECIFICATION.md`, `SESSION_MANAGER_GUIDE.md`).
- **New Docs (The "Current Claims"):** `updates/v5_hybrid_plugin_architecture/06_DOCUMENTATION_BIBLE/`.
- **The Codebase (The "Truth"):** `src/` (Scan for feature implementation).

### 2. Specific Features to Hunt
You must verify availability (Is it in code?) and documentation status (Is it in Bible?) for:
1.  **Real-Time Clock** (Telegram Pinned Message updating every minute).
2.  **Economic Calendar** (News filtering/Impact analysis).
3.  **Session Manager** (Auto-session switching: Asian/London/NY).
4.  **Profit Protection** (Locking profits, trailing equity).
5.  **Smart Lot Multiplier** (V3 logic lot sizing).
6.  **Voice Alerts** (`VOICE_NOTIFICATION_SYSTEM_V3.md`).
7.  **Flash Dashboard** (If applicable/integrated).
8.  **Menu/UI Navigation** (Interactive buttons).

## 📋 YOUR TASK

### Step 1: Code Existence Verification
- Find the exact Python files handling these features.
- If found, mark **[CODE: PRESENT]**.
- If deleted, mark **[CODE: MISSING]** (Critical Alert).

### Step 2: Documentation Gap Analysis
- Check if `06_DOCUMENTATION_BIBLE` mentions these features.
- If missing, mark **[DOCS: MISSING]**.

### Step 3: Resolution Plan
- If Code is Missing: We must restore it from backup.
- If Docs are Missing: We must update the Bible immediately.

## 🚀 EXECUTION PLAN
1.  **Scan Legacy Docs:** List 20+ features from `FEATURES_SPECIFICATION.md`.
2.  **Scan Code:** Grep/Search for implementation of each.
3.  **Generate Report:** `01_MISSING_FEATURES_REPORT.md`.

**The Report Structure:**
| Feature | Code Status | Docs Status | File Location | Action Needed |
|---------|-------------|-------------|---------------|---------------|
| Session Manager | ✅ Present | ❌ Missing | `src/modules/session_manager.py` | Add to Bible |
| ... | ... | ... | ... | ... |

**START NOW.**
