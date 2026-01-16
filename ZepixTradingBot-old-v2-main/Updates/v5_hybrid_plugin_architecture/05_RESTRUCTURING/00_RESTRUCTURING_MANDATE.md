# 🧹 MISSION: COMPLETE PROJECT RESTRUCTURING & CLEANUP

## 🔴 CRITICAL CONTEXT
The **V5 Hybrid Plugin Architecture** implementation is successfully **COMPLETE**.
However, the physical file structure is messy. We have:
- An `updates/` folder cluttering the root.
- Legacy files mixed with new V5 files.
- Documentation scattered across multiple folders.
- Inconsistent naming conventions.

## 🎯 USER OBJECTIVE
**"Complete bot ke har ek files aur folder ko scan kar ke complete structure karna hai."**
(Scan every file/folder and organize them into a correct, professional project structure.)

## ❓ CAPABILITY CHECK (ANSWER THIS FIRST)
The user explicitly asks: **"Batao ki tum ye kar sakte ho ki nahi?"** (Tell me if you can do this or not?)

**You must confirm:**
1. Can you scan the entire directory tree?
2. Can you distinguish between *essential code*, *documentation*, *logs*, and *junk*?
3. Can you move files SAFELY and **automatically update all Python imports** (`from src.x import y`) so the bot doesn't break?
4. Can you ensure `git` history is preserved (using `git mv`)?

---

## 📋 YOUR TASK: PHASE 1 - AUDIT & PLANNING

**DO NOT MOVE ANY FILES YET.**
You must first create a master plan.

### Step 1: Deep Scan & Inventory
Scan the entire `ZepixTradingBot-old-v2-main` directory.
Create a file `05_RESTRUCTURING/01_CURRENT_INVENTORY.md` listing:
- All top-level directories.
- All files in root.
- Breakdown of `src/`.
- Breakdown of `updates/` (what needs to be kept vs archived).

### Step 2: The "Golden Standard" Structure Proposal
Create a file `05_RESTRUCTURING/02_TARGET_STRUCTURE_PROPOSAL.md`.
Propose a standard Python production structure. Example (you define the best one):

```text
ZepixTradingBotv5/
├── bin/                 # Boot scripts (run.bat, run.sh)
├── config/              # All json/yaml configs
├── data/                # Database files (*.db)
├── docs/                # documentation (cleaned up)
│   ├── archive/         # Old updates/ logs
│   ├── user_guide/      # Current guides
│   └── developer/       # Architecture docs
├── logs/                # Log files
├── src/                 # PURE Python source code
│   ├── core/
│   ├── plugins/
│   └── ...
├── tests/               # All test files
├── .gitignore
├── README.md
├── requirements.txt
└── main.py              # Entry point
```

### Step 3: Mapping Strategy
In the proposal, include a **Migration Strategy**:
- How you will handle `git mv`.
- How you will use `sed` or regex to fix imports in bulk.
- How you will verify the bot still runs after moving.

## 🚀 EXECUTION INSTRUCTION
1. **Acknowledge this mandate.**
2. **Confirm your capability** to the user.
3. **Execute Step 1 (Inventory) & Step 2 (Proposal).**
4. **Wait for User Approval** before moving files.

**START NOW.**
