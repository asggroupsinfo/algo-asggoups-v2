import os
import subprocess
import datetime
import time

# Configuration
PROJECT_ROOT = r"c:\Users\Ansh Shivaay Gupta\Downloads\ZepixTradingBot-New-v1\ZepixTradingBot-old-v2-main"

# Define Logic Paths
PATH_PINE_V3 = os.path.join(PROJECT_ROOT, "docs", "TRADINGVIEW_PINE_SCRIPT_INDICATOR-v1-devin-1767306610-zepix-ultimate-bot-v3", "ZEPIX_ULTIMATE_BOT_v3.0_FINAL.pine")
PATH_COMBINED_LOGICS_IMPL = os.path.join(PROJECT_ROOT, "updates", "v5_hybrid_plugin_architecture", "COMBINED LOGICS")
PATH_PINE_V6 = os.path.join(PROJECT_ROOT, "docs", "TRADINGVIEW_PINE_SCRIPT_INDICATOR-v1-devin-1767306610-zepix-ultimate-bot-v3", "Signals_and_Overlays_V6_Enhanced_Build.pine")
PATH_V6_PLANNING = os.path.join(PROJECT_ROOT, "updates", "v5_hybrid_plugin_architecture", "V6_INTEGRATION_PROJECT", "02_PLANNING PRICE ACTION LOGIC")
PATH_HYBRID_ARCH = os.path.join(PROJECT_ROOT, "updates", "v5_hybrid_plugin_architecture", "01_PLANNING")

OUTPUT_FILE = os.path.join(PROJECT_ROOT, "DEEPSEEK_AUDIT_FINAL.md")
MODEL_NAME = "deepseek-coder-v2:16b"

def read_file(filepath):
    if not os.path.exists(filepath): return ""
    try:
        with open(filepath, 'r', encoding='utf-8') as f: return f.read()
    except: return ""

def scan_files(directory):
    if not os.path.exists(directory): return ""
    content = ""
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith(('.py', '.md')):
                content += f"\n--- FILE: {f} ---\n{read_file(os.path.join(root, f))[:10000]}\n"
    return content

def query_deepseek(prompt):
    try:
        process = subprocess.Popen(["ollama", "run", MODEL_NAME], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        stdout, stderr = process.communicate(input=prompt)
        return stdout if process.returncode == 0 else f"Error: {stderr}"
    except Exception as e: return f"Exception: {e}"

def run_segmented_audit():
    full_report = f"# DEEPSEEK SEGMENTED AUDIT REPORT\nDate: {datetime.datetime.now()}\n\n"
    
    # --- PART 1: V3 LOGIC AUDIT ---
    print("Running Part 1: V3 Logic Audit...")
    v3_context = f"PINE SCRIPT V3:\n{read_file(PATH_PINE_V3)}\n\nIMPLEMENTED PYTHON LOGIC:\n{scan_files(PATH_COMBINED_LOGICS_IMPL)}"
    prompt_v3 = f"""
    You are a Logic Auditor. 
    Analyze 'ZEPIX_ULTIMATE_BOT_v3.0_FINAL.pine' (Source of Truth).
    Compare it with 'IMPLEMENTED PYTHON LOGIC' files.
    
    TASK: Verify if the Python implementation correctly translates the Pine Script V3 logic.
    - Check Entry Conditions (Long/Short).
    - Check Exit Conditions (TP/SL/Reversal).
    - Identify any missing logic in Python.
    
    DATA:
    {v3_context[:50000]} 
    """
    report_v3 = query_deepseek(prompt_v3)
    full_report += "## PART 1: V3 LOGIC AUDIT\n" + report_v3 + "\n\n"
    
    # --- PART 2: V6 PLANNING AUDIT ---
    print("Running Part 2: V6 Planning Audit...")
    v6_context = f"PINE SCRIPT V6:\n{read_file(PATH_PINE_V6)}\n\nV6 PLANNING DOCS:\n{scan_files(PATH_V6_PLANNING)}"
    prompt_v6 = f"""
    You are a Planning Validator.
    Analyze 'Signals_and_Overlays_V6_Enhanced_Build.pine' (Complex Price Action).
    Review 'V6 PLANNING DOCS'.
    
    TASK: Determine if the Planning Documents accurately capture the complex V6 logic.
    - Does the plan cover Trendlines, Breakouts, and Pattern recognition?
    - Are the technical specifications detailed enough for implementation?
    - What is missing in the plan?
    
    DATA:
    {v6_context[:50000]}
    """
    report_v6 = query_deepseek(prompt_v6)
    full_report += "## PART 2: V6 PLANNING VALIDATION\n" + report_v6 + "\n\n"

    # --- PART 3: ARCHITECTURE ---
    print("Running Part 3: Architecture Audit...")
    arch_context = scan_files(PATH_HYBRID_ARCH)
    prompt_arch = f"""
    You are a System Architect.
    Review the 'Hybrid Plugin Architecture' plans.
    
    TASK: Assess if the architecture can support running BOTH V3 (Indicator based) and V6 (Price Action) logics simultaneously.
    - Check for potential conflicts (Database, Order Management).
    - Evaluate scalability for future plugins.
    
    DATA:
    {arch_context[:50000]}
    """
    report_arch = query_deepseek(prompt_arch)
    full_report += "## PART 3: ARCHITECTURE ASSESSMENT\n" + report_arch + "\n\n"

    return full_report

if __name__ == "__main__":
    final_report = run_segmented_audit()
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f: f.write(final_report)
    print(f"Segmented Audit Complete! Saved to: {OUTPUT_FILE}")
