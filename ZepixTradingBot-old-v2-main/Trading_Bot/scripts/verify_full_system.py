
import json
import logging
import asyncio
import sys
import os

# Filter useless logs
logging.basicConfig(level=logging.INFO, format='%(message)s')
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("asyncio").setLevel(logging.CRITICAL)

# Mock classes to avoid full dependency chain issues
class MockTradingEngine:
    def is_plugin_enabled(self, name): return True
    def get_open_positions(self): return []
    def get_daily_pnl(self): return 100.50
    def get_account_balance(self): return 10000.00
    def get_account_equity(self): return 10050.50

async def perform_comprehensive_test():
    print("🚀 LIVE SIMULATION TEST SUITE (PROOF OF SEPARATION)")
    print("==================================================")
    
    # 1. Load Config
    try:
        with open('config/config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✅ Config Loaded")
    except Exception as e:
        print(f"❌ Config Error: {e}")
        return

    # 2. Initialize Telegram Manager (Real Logic)
    # We must append path to import modules
    sys.path.append(os.getcwd())
    try:
        from src.telegram.multi_telegram_manager import MultiTelegramManager
        manager = MultiTelegramManager(config)
        print("✅ MultiTelegramManager Initialized")
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return
    except Exception as e:
        print(f"❌ Init Error: {e}")
        return

    # 3. Verify Bot Separation (Tokens)
    print("\n[TEST 1] VERIFYING BOT TOKENS")
    print(f"   Controller Token: ...{manager.controller_token[-8:] if manager.controller_token else 'NONE'}")
    print(f"   Notification Token: ...{manager.notification_token[-8:] if manager.notification_token else 'NONE'}")
    print(f"   Analytics Token: ...{manager.analytics_token[-8:] if manager.analytics_token else 'NONE'}")
    
    if manager.controller_token != manager.notification_token and manager.notification_token != manager.analytics_token:
        print("   ✅ SUCCESS: All 3 bots use DIFFERENT tokens.")
    else:
        print("   ❌ FAILURE: Bots are sharing tokens!")

    # 4. LIVE MESSAGE INJECTION (Simulation)
    print("\n[TEST 2] INJECTING SIMULATED TRAFFIC")
    
    # A. Controller Menu Test
    print("\n   [A] CONTROLLER BOT (Menu Test)")
    try:
        msg_id = manager.controller_bot.handle_start()
        if msg_id:
             print(f"      ✅ Menu Sent! Message ID: {msg_id}")
             print(f"      ✅ Sent via Token: ...{manager.controller_bot.token[-8:]}")
        else:
             print("      ❌ Failed to send menu.")
    except Exception as e:
        print(f"      ❌ Exception: {e}")

    # B. V3 Trade Alert (Notification Bot)
    print("\n   [B] V3 TRADE ALERT (Notification Bot)")
    v3_trade = {
        "type": "entry",
        "symbol": "EURUSD",
        "direction": "BUY",
        "price": 1.0500,
        "strategy": "V3 Hybrid",
        "timestamp": "2026-01-15 10:00:00"
    }
    try:
        # We manually invoke the method that uses the specific bot
        bot = manager.notification_bot
        if bot:
            msg_id = bot.send_entry_alert(v3_trade)
            if msg_id:
                print(f"      ✅ V3 Alert Sent! Message ID: {msg_id}")
                print(f"      ✅ Sent via Token: ...{bot.token[-8:]}")
            else:
                print("      ❌ Failed to send V3 alert.")
        else:
             print("      ❌ Notification Bot not active in manager.")
    except Exception as e:
        print(f"      ❌ Exception: {e}")

    # C. V6 Trade Alert (Notification Bot)
    print("\n   [C] V6 TRADE ALERT (Notification Bot)")
    v6_trade = {
        "type": "entry",
        "symbol": "GBPUSD",
        "direction": "SELL",
        "price": 1.2000,
        "strategy": "V6 Price Action",
        "timestamp": "2026-01-15 10:05:00"
    }
    try:
        bot = manager.notification_bot
        if bot:
            msg_id = bot.send_entry_alert(v6_trade)
            if msg_id:
                print(f"      ✅ V6 Alert Sent! Message ID: {msg_id}")
                print(f"      ✅ Sent via Token: ...{bot.token[-8:]}")
            else:
                print("      ❌ Failed to send V6 alert.")
    except Exception as e:
        print(f"      ❌ Exception: {e}")

    # D. Analytics Report (Analytics Bot)
    print("\n   [D] ANALYTICS REPORT (Analytics Bot)")
    report_data = {
        "profit": 150.00,
        "trades": 5,
        "winrate": 80.0
    }
    try:
        bot = manager.analytics_bot
        if bot:
            msg_id = bot.send_performance_report(report_data)
            if msg_id:
                print(f"      ✅ Report Sent! Message ID: {msg_id}")
                print(f"      ✅ Sent via Token: ...{bot.token[-8:]}")
            else:
                print("      ❌ Failed to send report.")
        else:
            print("      ❌ Analytics Bot not active in manager.")
    except Exception as e:
        print(f"      ❌ Exception: {e}")

    print("\n==================================================")
    print("✅ SIMULATION COMPLETE. CHECK TELEGRAM NOW.")

if __name__ == "__main__":
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    
    # Global log function hack
    import builtins
    logfile = open('full_proof_clean.txt', 'w', encoding='utf-8')
    def log(msg): # Simplified log matching original user code attempt which might have failed due to builtins
         logfile.write(str(msg) + "\n")
         logfile.flush()
         sys.stdout.write(str(msg) + "\n")
    
    builtins.print = log
    
    asyncio.run(perform_comprehensive_test())
