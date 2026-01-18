
import json
import requests
import sys
import time

def check_bot_status(name, token, chat_id, log_func):
    if not token:
        log_func(f"❌ {name}: No token provided")
        return False
        
    try:
        # 1. Identity Check
        me_url = f"https://api.telegram.org/bot{token}/getMe"
        resp = requests.get(me_url, timeout=10)
        me_data = resp.json()
        
        if resp.status_code != 200 or not me_data.get("ok"):
            log_func(f"❌ {name}: Invalid Token ({resp.status_code})")
            return False
            
        bot_user = me_data['result']['username']
        bot_id = me_data['result']['id']
        log_func(f"✅ {name}: IDENTITY CONFIRMED (@{bot_user}, ID: {bot_id})")
        
        # 2. Webhook Check
        webhook_url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
        wh_resp = requests.get(webhook_url, timeout=10)
        wh_data = wh_resp.json()
         
        has_webhook = False
        if wh_resp.status_code == 200 and wh_data.get("ok"):
            wh_info = wh_data['result']
            if wh_info.get("url"):
                log_func(f"⚠️ {name}: WEBHOOK ACTIVE -> {wh_info['url']}")
                log_func(f"   (This BLOCKS polling. Fix required!)")
                has_webhook = True
            else:
                log_func(f"✅ {name}: No Webhook (Polling Allowed)")
        
        # 3. Message Functionality Proof
        if chat_id:
            msg = f"✅ PROOF OF LIFE: {name} is ACTIVE and CONNECTED."
            send_url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {"chat_id": chat_id, "text": msg}
            
            send_resp = requests.post(send_url, json=payload, timeout=10)
            if send_resp.status_code == 200 and send_resp.json().get("ok"):
                log_func(f"✅ {name}: MESSAGE DELIVERED to {chat_id}")
            else:
                log_func(f"❌ {name}: MESSAGE FAILED ({send_resp.text})")
        else:
            log_func(f"⚠️ {name}: Skipped message test (No Chat ID)")
            
        return has_webhook

    except Exception as e:
        log_func(f"❌ {name}: Connection Error ({e})")
        return False

def main():
    with open('proof_log.txt', 'w', encoding='utf-8') as outfile:
        def log(msg):
            print(msg)
            outfile.write(str(msg) + "\n")
            outfile.flush()

        log("🕵️‍♂️ DETAILED TELEGRAM DIAGNOSTIC TOOL 🕵️‍♂️")
        log("=========================================")
        
        try:
            with open('config/config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            log(f"❌ Configuration Error: {e}")
            return

        chat_id = config.get("telegram_chat_id")
        
        # Check all 3 bots
        wb_controller = check_bot_status("Controller Bot", config.get("telegram_token"), chat_id, log)
        wb_notify = check_bot_status("Notification Bot", config.get("telegram_notification_token"), chat_id, log)
        wb_analytics = check_bot_status("Analytics Bot", config.get("telegram_analytics_token"), chat_id, log)
        
        log("\n--- DIAGNOSIS SUMMARY ---")
        if wb_notify or wb_analytics:
            log("❌ CRITICAL ISSUE: One or more secondary bots have active webhooks.")
            log("   This prevents them from responding to /start.")
            log("   Action: Run cleanup script.")
        else:
            log("✅ ALL SYSTEMS GO: No conflicting webhooks found.")
            log("   If bots don't reply, restart the main application.")

if __name__ == "__main__":
    main()
