
import sys
import os
import asyncio
import logging
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.telegram.notification_bot import NotificationBot
from src.modules.voice_alert_system import VoiceAlertSystem
from src.modules.windows_audio_player import WindowsAudioPlayer  # Check import

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AlertVerification")

def load_config():
    try:
        with open('config/config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}

async def main():
    logger.info("Starting Alert Verification V2...")
    
    config = load_config()
    chat_id = config.get('allowed_telegram_user') or config.get('telegram_chat_id')
    
    # 1. Test Windows Logic
    logger.info("Testing Windows Audio Player initialization...")
    try:
        import pyttsx3
        logger.info("pyttsx3 imported successfully.")
    except ImportError:
        logger.error("CRITICAL: pyttsx3 not installed. Voice alerts will fail.")
        return

    # 2. Initialize Notification Bot
    token = config.get('telegram_notification_token')
    if not token:
        logger.warning("No notification token found. Using main token.")
        token = config.get('telegram_token')
    else:
        logger.info(f"Targeting Notification Bot Token: {token[:4]}...{token[-4:]}")
        
    bot = NotificationBot(token=token, chat_id=chat_id)
    
    # 3. VERIFY BOT IDENTITY VIA API
    import requests
    logger.info("--- VERIFYING BOT IDENTITY ---")
    try:
        me_url = f"https://api.telegram.org/bot{token}/getMe"
        resp = requests.get(me_url, timeout=10)
        if resp.status_code == 200:
            me_data = resp.json().get('result', {})
            logger.info(f"✅ TOKEN VALID. Bot Username: @{me_data.get('username')}")
            logger.info(f"✅ Bot Name: {me_data.get('first_name')}")
            logger.info(f"✅ Bot ID: {me_data.get('id')}")
        else:
            logger.error(f"❌ TOKEN INVALID. API Status: {resp.status_code} - {resp.text}")
            return
    except Exception as e:
        logger.error(f"❌ Connection Failed: {e}")
        return

    # 4. Initialize Voice System
    logger.info("Initializing Voice Alert System...")
    voice_system = VoiceAlertSystem(bot=bot, chat_id=chat_id) 
    
    # 5. Connect
    bot.set_voice_alert_system(voice_system)
    
    # 6. Send Simulated Alert (Async Router Path)
    logger.info("Sending simulated TRADE OPENED alert...")
    
    trade_data = {
        'plugin_name': 'TEST_PLUGIN',
        'symbol': 'EURUSD',
        'direction': 'BUY',
        'entry_price': 1.0500,
        'order_a_lot': 0.1,
        'order_a_sl': 1.0450,
        'order_a_tp': 1.0600,
        'ticket_a': 123456,
        'signal_type': 'VERIFICATION_TEST',
        'timeframe': 'M5',
        'logic_route': 'LOGIC1'
    }
    
    # Call send_notification (Async wrapper we just added)
    msg_id = await bot.send_notification('trade_opened', 'fallback message', trade_data=trade_data)
    
    if msg_id:
        logger.info(f"✅ MESSAGE SENT SUCCESSFULLY. Message ID: {msg_id}")
        logger.info(f"👉 CHECK TELEGRAM BOT: @{me_data.get('username')}")
    else:
        logger.error("❌ MESSAGE SEND FAILED. Check NotificationBot logs.")
    
    logger.info("1. Audio should have played.")
    logger.info("2. Telegram Msg should be visible in the bot verified above.")
    
    # Allow some time for async queue
    await asyncio.sleep(2)
    logger.info("Test Complete.")

if __name__ == "__main__":
    asyncio.run(main())
