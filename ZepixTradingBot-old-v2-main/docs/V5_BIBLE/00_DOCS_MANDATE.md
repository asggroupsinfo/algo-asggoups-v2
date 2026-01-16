# 📚 MISSION: CREATE THE "ZEPIX V5 DOCUMENTATION BIBLE"

## ⏸️ STATUS UPDATE
**HOLD:** Phase 5 (Restructuring) is PAUSED indefinitely by user request.
**START:** Phase 6 (Comprehensive Documentation) begins NOW.

## 🎯 USER OBJECTIVE
**"Complete bot ka documentation chaiye... sab kuch jo maine nahi bataya wo bhi."**
(I want complete bot documentation... everything, even things I haven't explicitly mentioned.)

**Key Requirement:**
A new developer should be able to read this "Bible" and understand **100%** of the bot without asking a single question.

## 📋 YOUR TASK: THE "DEEP SCAN & DOCUMENT" PROTOCOL

### 1. The Deep Scan
You must scan `src/`, `config/`, `tests/`, and `data/` to uncover every single feature, including:
- **Hidden Logic:** Features present in code but not in current docs.
- **V5 New Features:** Plugins, 3-Bot System, Autonomous Manager, Shadow Mode.
- **V3 Legacy Logic:** The 12 original strategies and their triggers.
- **Flows:** User Interaction Flow, Order Execution Flow, Data Flow.

### 2. The Documentation Structure (You Decide the Details)
You have full autonomy ("Devin hi decide karega") to structure this. However, it MUST cover at least:

#### 🏛️ A. System Architecture
- High-level diagram (text/mermaid).
- Hybrid Plugin Architecture explained.
- 3-Bot Telegram Cluster (Controller, Notification, Analytics).
- Database Schema (Core vs Plugins).

#### 🧠 B. Trading Logic Engineering
- **V3 Combined:** Detailed breakdown of all 12 signals.
- **V6 Price Action:** 4-Pillar Trend Validation, Entry criteria.
- **Shadow Mode:** How it works, how to use it.
- **Dual Order System:** Order A vs Order B logic.
- **Re-Entry & Recovery:** SL Hunt, TP Continuation, Reverse Shield.

#### 🎮 C. User Manual & Telegram Mastery
- **Command Reference:** All commands for all 3 bots.
- **Menu Navigation:** Full tree of buttons and callbacks.
- **Configuration:** What every key in `config.json` does.

#### 🛡️ D. Autonomous & Safety Systems
- Daily Loss Limits.
- Profit Protection logic.
- Risk Shields.
- Auto-Shutdown triggers.

#### 👨‍💻 E. Developer's Internal Guide
- How to add a NEW plugin (template guide).
- How to run tests.
- Project file structure (current state).

### 3. Execution Plan
1.  **Output Folder:** `updates/v5_hybrid_plugin_architecture/06_DOCUMENTATION_BIBLE/`
2.  **Step 1:** Create `00_MASTER_INDEX.md` (Table of Contents).
3.  **Step 2:** Generate the content files one by one.

## 🚀 INSTRUCTION
1.  **Acknowledge this new mission.**
2.  **Scan the code.**
3.  **Create the Folder Structure** for the documentation.
4.  **Start writing.** Do not ask for verification after every file. Generate the **complete set**.

**DELIVERABLE:** A folder full of high-quality Markdown files that represents the "Truth" of the Zepix V5 Bot.
