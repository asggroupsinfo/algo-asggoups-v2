# 🚨 CLARIFICATION: PRESERVE & ENRICH (DO NOT DELETE)

## 🔴 USER INSTRUCTION
The user has clarified the "Merge Strategy":
1.  **NO DELETION:** Do not just "delete duplicates" blindly.
2.  **PRESERVE LEGACY KNOWLEDGE:** The Old Documentation (`DOCUMENTATION/`) contains critical feature details (Legacy Features) that V5 docs might miss.
3.  **ENRICH V5 DOCS:** The goal is to TAKE the deep details from Old Docs and INJECT them into the new V5 structure.
4.  **INTELLIGENT MERGE:** Read Old Doc -> Read New Code -> Create "Unified Doc".

## 🛠️ THE NEW MERGE PROTOCOL

### Step 1: Content Extraction
- Read `DOCUMENTATION/` to extract logic for: Legacy features, original bot behaviors, command nuances.
- Read `updates/.../06_DOCUMENTATION_BIBLE/` for V5 architecture specifics.

### Step 2: Synthesis (The "Milana" Process)
- **Feature X:**
  - Old Doc says: "Feature X does A, B, C."
  - V5 Doc says: "Feature X is now a plugin."
  - **Unified Doc must say:** "Feature X is a plugin that does A, B, C (migrated from legacy)."

### Step 3: Structure
Create `docs/V5_BIBLE/` with rich content.
- Use Old Docs to fill the *content* logic.
- Use V5 Docs to describe the *implementation* logic.

**CRITICAL:** Do not lose a single feature description. If it was in the old bot and exists in the code, it MUST be in the new Bible.
