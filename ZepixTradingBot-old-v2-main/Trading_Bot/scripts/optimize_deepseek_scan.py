import os
import subprocess
import datetime
import glob

# Configuration
PROJECT_ROOT = r"c:\Users\Ansh Shivaay Gupta\Downloads\ZepixTradingBot-New-v1\ZepixTradingBot-old-v2-main"

# Priority files to scan (High Impact)
PRIORITY_FILES = [
    "README.md",
    "src/main.py",
    "src/config.py",
    "src/core/plugin_system/base_plugin.py",
    "src/core/plugin_system/plugin_registry.py",
    "src/core/trading_engine.py",
    "updates/v5_hybrid_plugin_architecture/01_PLANNING/01_PROJECT_OVERVIEW.md",
    "updates/v5_hybrid_plugin_architecture/01_PLANNING/03_PHASES_2-6_CONSOLIDATED_PLAN.md",
    "DOCUMENTATION/TECHNICAL_ARCHITECTURE.md",
    "DOCUMENTATION/PROJECT_OVERVIEW.md"
]

OUTPUT_FILE = os.path.join(PROJECT_ROOT, "PROJECT_SCAN_REPORT_DEEPSEEK_V2.md")
MODEL_NAME = "deepseek-coder-v2:16b"

def read_file_content(relpath):
    filepath = os.path.join(PROJECT_ROOT, relpath)
    if not os.path.exists(filepath):
        return f"[FILE NOT FOUND: {relpath}]"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read(5000) # Read first 5000 chars
            if len(content) == 5000:
                content += "\n...[TRUNCATED]..."
            return content
    except Exception as e:
        return f"[ERROR READING FILE: {e}]"

def generate_context():
    context = "USER REQUEST: Perform a high-level architectural scan of the project. Focus on the Hybrid Plugin Architecture update and overall code structure.\n\n"
    context += "PROJECT SELECTED CRITICAL FILES:\n\n"

    for relpath in PRIORITY_FILES:
        content = read_file_content(relpath)
        context += f"--- FILE: {relpath} ---\n"
        context += f"{content}\n\n"
    
    return context

def run_deepseek_audit():
    print("Gathering optimized project context...")
    context = generate_context()
    
    print(f"Context size: {len(context)} characters (Optimized).")
    print(f"Sending to {MODEL_NAME} via Ollama...")
    
    prompt = f"""
    You are an expert Software Architect.
    Analyze the provided critical project files for 'ZepixTradingBot'.
    
    Focus on:
    1. The transition to 'Hybrid Plugin Architecture' (V5).
    2. Code organization in 'src/core' vs 'src/plugins'.
    3. Potential risks in the current implementation plan.
    4. Quality of documentation vs code reality.
    
    Provide a concise, professional assessment report.
    
    Project Context:
    {context}
    """
    
    try:
        # Using run with interactive flag might effectively wait, but let's use standard input piping
        # We use 'utf-8' specifically to avoid encoding issues
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
            return None
            
        return stdout
        
    except Exception as e:
        print(f"Execution Error: {e}")
        return None

if __name__ == "__main__":
    report = run_deepseek_audit()
    
    if report:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(f"# DEEPSEEK ARCHITECTURAL AUDIT REPORT (OPTIMIZED)\n")
            f.write(f"Date: {datetime.datetime.now()}\n")
            f.write(f"Model: {MODEL_NAME}\n\n")
            f.write(report)
        print(f"Scan Complete! Report saved to: {OUTPUT_FILE}")
        print("-" * 50)
        print(report[:2000] + "...") # Print first 2000 chars to console for immediate visibility
    else:
        print("Scan Failed.")
