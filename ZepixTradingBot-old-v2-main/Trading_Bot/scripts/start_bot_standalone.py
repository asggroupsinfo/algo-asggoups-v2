#!/usr/bin/env python3
"""
Standalone bot launcher - runs without web server
"""
import sys
import os
import uvicorn

# Add parent directory (Trading_Bot/) to path so we can find src/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Change to parent directory (Trading_Bot/) where src/ is located
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

if __name__ == "__main__":
    print("="*70)
    print("ZEPIX TRADING BOT - STANDALONE MODE")
    print("="*70)
    print("Server will start on: http://localhost:5000")
    print("Webhook endpoint: http://localhost:5000/webhook")
    print("Health endpoint: http://localhost:5000/health")
    print("\nPress Ctrl+C to stop the server")
    print("="*70)
    
    try:
        uvicorn.run(
            "src.api.webhook_handler:app",
            host="0.0.0.0",
            port=80,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n[INFO] Bot stopped by user")
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
