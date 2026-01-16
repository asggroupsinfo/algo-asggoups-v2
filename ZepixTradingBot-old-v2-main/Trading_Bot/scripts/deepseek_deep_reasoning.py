import os
import subprocess
import datetime
import shutil

# Configuration
PROJECT_ROOT = r"c:\Users\Ansh Shivaay Gupta\Downloads\ZepixTradingBot-New-v1\ZepixTradingBot-old-v2-main"

# Define Paths as requested by User
PATH_V5_HYBRID = os.path.join(PROJECT_ROOT, "updates", "v5_hybrid_plugin_architecture") # Main Hybrid Plan
PATH_PINE_V3 = os.path.join(PROJECT_ROOT, "docs", "TRADINGVIEW_PINE_SCRIPT_INDICATOR-v1-devin-1767306610-zepix-ultimate-bot-v3", "ZEPIX_ULTIMATE_BOT_v3.0_FINAL.pine") # 1st Pine (Combined Logic)
PATH_COMBINED_LOGICS_IMPL = os.path.join(PROJECT_ROOT, "updates", "v5_hybrid_plugin_architecture", "COMBINED LOGICS") # Implemented Logic for V3
PATH_PINE_V6 = os.path.join(PROJECT_ROOT, "docs", "TRADINGVIEW_PINE_SCRIPT_INDICATOR-v1-devin-1767306610-zepix-ultimate-bot-v3", "Signals_and_Overlays_V6_Enhanced_Build.pine") # 2nd Pine (New/Future)
PATH_V6_PLANNING = os.path.join(PROJECT_ROOT, "updates", "v5_hybrid_plugin_architecture", "V6_INTEGRATION_PROJECT", "02_PLANNING PRICE ACTION LOGIC") # Logic Plan for V6

OUTPUT_FILE = os.path.join(PROJECT_ROOT, "DEEPSEEK_DEEP_REASONING_AUDIT_REPORT.md")
MODEL_NAME = "deepseek-coder-v2:16b"

def read_file(filepath):
    """Read full file content safely"""
    if not os.path.exists(filepath):
        return f"[FILE NOT FOUND: {filepath}]"
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"[ERROR READING FILE: {e}]"

def scan_directory(directory_path, extension_filter=None):
    """Recursively scan a directory and return concatenated content of files"""
    content = ""
    if not os.path.exists(directory_path):
        return f"[DIRECTORY NOT FOUND: {directory_path}]\n"
    
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if extension_filter and not file.endswith(extension_filter):
                continue
            if file.endswith(('.md', '.py', '.txt', '.json')):
                filepath = os.path.join(root, file)
                relpath = os.path.relpath(filepath, PROJECT_ROOT)
                file_content = read_file(filepath)
                # Limit very large files to prevent context overflow, but keep enough for reasoning
                if len(file_content) > 15000: 
                    file_content = file_content[:15000] + "\n...[TRUNCATED FOR CONTEXT LIMIT]..."
                content += f"\n--- FILE: {relpath} ---\n{file_content}\n"
    return content

def generate_context():
    print("Gathering specific context for Deep Reasoning...")
    context = "USER OBJECTIVE: Analyze the ZepixTradingBot for a major Hybrid Plugin update involving two specific Pine Scripts. Verify if the 1st Pine (V3 Combined Logic) is fully implemented and if the 2nd Pine (V6 Price Action) plans are solid for future implementation.\n\n"
    
    # 1. Hybrid Architecture Context
    context += "### CONTEXT 1: V5 HYBRID ARCHITECTURE (Future Roadmap)\n"
    context += scan_directory(PATH_V5_HYBRID, extension_filter=".md")
    
    # 2. Pine Script V3 (Implemented?)
    context += "\n### CONTEXT 2: PINE SCRIPT V3 (ZEPIX_ULTIMATE_BOT_v3.0_FINAL.pine)\n"
    context += read_file(PATH_PINE_V3)
    
    # 3. Combined Logic Implementation (Check V3 Implementation)
    context += "\n### CONTEXT 3: IMPLEMENTED V3 LOGIC (COMBINED LOGICS)\n"
    context += scan_directory(PATH_COMBINED_LOGICS_IMPL)
    
    # 4. Pine Script V6 (Future/New)
    context += "\n### CONTEXT 4: PINE SCRIPT V6 (Signals_and_Overlays_V6_Enhanced_Build.pine)\n"
    context += read_file(PATH_PINE_V6)
    
    # 5. V6 Planning (Price Action Logic)
    context += "\n### CONTEXT 5: V6 LOGIC PLANNING (PRICE ACTION)\n"
    context += scan_directory(PATH_V6_PLANNING)

    return context

def run_deepseek_reasoning():
    context = generate_context()
    print(f"Total Context Size: {len(context)} characters. Trimming if necessary...")
    
    # HARD LIMIT to avoid hitting model context limits (approx 128k token context for DeepSeek V2, but let's be safe with 50-60k chars per prompt in parts if needed, or just truncated full context)
    # We will pass as much as possible.
    if len(context) > 100000:
        print("Context is very large. Truncating non-critical sections...")
        context = context[:100000] + "\n...[TRUNCATED END OF CONTEXT]..."

    prompt = f"""
    You are an Expert Trading Systems Architect and Lead Developer.
    Your capabilities: Deep Reasoning, Logic Verification, Code-to-Logic Mapping, Audit.

    CRITICAL MISSION:
    The user is migrating to a "Hybrid Plugin Architecture" (V5) to support two distinct trading logics based on Pine Scripts:
    1. **V3 Logic (Combined):** Should be ALREADY IMPLEMENTED.
    2. **V6 Logic (Price Action):** Currently in PLANNING phase, needs full implementation.

    YOUR TASKS (Use Deep Reasoning):
    
    1. **V3 Verification (Audit):**
       - Analyze 'ZEPIX_ULTIMATE_BOT_v3.0_FINAL.pine'.
       - Compare it against the files in 'COMBINED LOGICS' implementation.
       - Question: Is every trading condition (Entry/Exit/SL/TP) from Pine V3 effectively translated into the Python logic? 
       - Identify Gaps: Are there missing conditions, wrong parameters, or logic errors?

    2. **V6 Planning Review (Validation):**
       - Analyze 'Signals_and_Overlays_V6_Enhanced_Build.pine'.
       - Review the 'V6_INTEGRATION_PROJECT/02_PLANNING PRICE ACTION LOGIC' documents.
       - Question: Does the plan accurately capture the complex Price Action logic (Trendlines, Breakouts, Patterns) from Pine V6?
       - Identify Missing Specs: Is the plan detailed enough to start coding? What is missing?

    3. **Architecture Check (Hybrid V5):**
       - Does the 'updates/v5_hybrid_plugin_architecture' plan correctly support running BOTH these logics (V3 & V6) simultaneously or separately as plugins?
       - Are there conflicts?

    OUTPUT FORMAT (Markdown):
    - **Executive Reasoning Summary**: Your high-level assessment.
    - **V3 Implementation Audit**:
      - ✅ Verified Features
      - ❌ Missing/Broken Features (Be specific)
      - ⚠️ Logical Discrepancies
    - **V6 Planning Validation**:
      - ✅ Plan Strengths
      - ❌ Plan Gaps/Missing Logic
    - **Final Recommendations**: Step-by-step fix/update list.

    DATA:
    {context}
    """

    print(f"Sending to {MODEL_NAME} via Ollama...")
    
    try:
        process = subprocess.Popen(
            ["ollama", "run", MODEL_NAME],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        stdout, stderr = process.communicate(input=prompt)
        
        if process.returncode != 0:
            print(f"Ollama Error: {stderr}")
            if stderr: return f"Error: {stderr}"
            return "Unknown Error"
            
        return stdout
    except Exception as e:
        return f"Execution Exception: {e}"

if __name__ == "__main__":
    report = run_deepseek_reasoning()
    
    if report:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("# DEEPSEEK DEEP REASONING AUDIT\n")
            f.write(f"Date: {datetime.datetime.now()}\n\n")
            f.write(report)
        print(f"Deep Reasoning Complete. Report saved to: {OUTPUT_FILE}")
    else:
        print("Analysis Failed.")
