import os
import subprocess
import datetime

# Configuration
PROJECT_ROOT = r"c:\Users\Ansh Shivaay Gupta\Downloads\ZepixTradingBot-New-v1\ZepixTradingBot-old-v2-main"
TARGET_DIRS = [
    os.path.join(PROJECT_ROOT, "src"),
    os.path.join(PROJECT_ROOT, "updates", "v5_hybrid_plugin_architecture", "01_PLANNING"),
    os.path.join(PROJECT_ROOT, "DOCUMENTATION")
]
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "PROJECT_SCAN_REPORT_DEEPSEEK.md")
MODEL_NAME = "deepseek-coder-v2:16b"

def read_file_content(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read(10000) # Read first 10k chars to limit context
    except Exception as e:
        return f"Error reading file: {e}"

def generate_context():
    context = "USER REQUEST: Perform a complete scan of the project structure and key files. Identify issues, improvements for Hybrid Plugin Architecture, and code quality gaps.\n\n"
    context += "PROJECT FILES CONTENT:\n\n"

    for directory in TARGET_DIRS:
        if not os.path.exists(directory):
            print(f"Skipping missing directory: {directory}")
            continue
            
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(('.py', '.md', '.json')):
                    filepath = os.path.join(root, file)
                    relpath = os.path.relpath(filepath, PROJECT_ROOT)
                    content = read_file_content(filepath)
                    
                    context += f"--- FILE: {relpath} ---\n"
                    context += f"{content}\n\n"
                    
                    print(f"Added {relpath} to scan context.")
    
    return context

def run_deepseek_audit():
    print("Gathering project context...")
    context = generate_context()
    
    print(f"Context size: {len(context)} characters.")
    print(f"Sending to {MODEL_NAME} via Ollama... This may take a while.")
    
    prompt = f"""
    You are an expert Software Architect and Code Auditor.
    I will provide you with the file structure and contents of the 'ZepixTradingBot' project.
    
    Your Task:
    1. Analyze the project structure and organization.
    2. Review the Python code in 'src/' for quality, errors, and best practices.
    3. Evaluate the 'Hybrid Plugin Architecture' plans in 'updates/'.
    4. Provide a detailed markdown report with:
       - Executive Summary
       - Critical Issues Detected
       - Architecture Review
       - Code Quality Assessment
       - Recommendations for V5 Update
    
    Here is the project data:
    {context}
    """
    
    try:
        process = subprocess.Popen(
            ["ollama", "run", MODEL_NAME],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8' # Ensure UTF-8 encoding
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
            f.write(f"# DEEPSEEK PROJECT SCAN REPORT\n")
            f.write(f"Date: {datetime.datetime.now()}\n")
            f.write(f"Model: {MODEL_NAME}\n\n")
            f.write(report)
        print(f"Scan Complete! Report saved to: {OUTPUT_FILE}")
    else:
        print("Scan Failed.")
