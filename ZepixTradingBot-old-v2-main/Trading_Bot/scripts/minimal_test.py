
# minimal test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.clients.telegram_bot_fixed import TelegramBot

c = Config()
print("Config loaded")
try:
    b = TelegramBot(c)
    print("Bot init success")
except Exception as e:
    print(f"Bot init failed: {e}")
    import traceback
    traceback.print_exc()
