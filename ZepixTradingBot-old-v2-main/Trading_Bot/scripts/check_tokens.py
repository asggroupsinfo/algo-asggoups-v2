
import json
import requests
import sys

def check_token(name, token, log_func):
    if not token:
        log_func(f"❌ {name}: No token provided")
        return
        
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        if resp.status_code == 200 and data.get("ok"):
            bot_user = data['result']['username']
            log_func(f"✅ {name}: Valid (@{bot_user})")
        else:
            log_func(f"❌ {name}: INVALID (Error {resp.status_code}: {data.get('description', 'Unknown error')})")
            log_func(f"   Token: {token[:10]}...{token[-5:]}")
    except Exception as e:
        log_func(f"❌ {name}: Connection Error ({e})")

def main():
    with open('token_report.txt', 'w', encoding='utf-8') as outfile:
        def log(msg):
            print(msg)
            outfile.write(str(msg) + "\n")

        log("🔍 CHECKING TELEGRAM BOT TOKENS...")
        try:
            with open('config/config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            log(f"❌ Could not load config.json: {e}")
            return

        check_token("Controller Bot", config.get("telegram_token"), log)
        check_token("Notification Bot", config.get("telegram_notification_token"), log)
        check_token("Analytics Bot", config.get("telegram_analytics_token"), log)

if __name__ == "__main__":
    main()
