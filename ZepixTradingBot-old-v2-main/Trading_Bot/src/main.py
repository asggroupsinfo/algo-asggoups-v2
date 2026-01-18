import os
import sys
import time
import logging
import signal
import threading
import asyncio

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.clients.mt5_client import MT5Client
from src.managers.risk_manager import RiskManager
from src.core.trading_engine import TradingEngine
from src.clients.telegram_bot import TelegramBot
from src.processors.alert_processor import AlertProcessor
from src.managers.session_manager import SessionManager
from src.database import TradeDatabase

# Setup Logging to file and console
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot_startup.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("Main")

running_event = threading.Event()
running_event.set()

def handle_exit(signum, frame):
    print("\nShutdown signal received...")
    running_event.clear()

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

def main():
    logger.info("-" * 50)
    logger.info("🚀 STARTING ZEPIX TRADING BOT V2.0")
    logger.info("-" * 50)
    
    try:
        # 1. Config
        logger.info("Loading Configuration...")
        config = Config()
        
        # 2. MT5 Client
        logger.info("Initializing MT5 Client...")
        mt5_client = MT5Client(config)
        
        if mt5_client.initialize():
            logger.info("✅ MT5 Connection Successful")
        else:
            logger.warning("⚠️ MT5 Connection Failed! Bot running in restricted mode.")

        # 3. Database & Session Manager (Dependency Injection)
        logger.info("Initializing Database & Session Manager...")
        db = TradeDatabase()
        session_manager = SessionManager(config, db, mt5_client)

        # 4. Risk Manager
        logger.info("Initializing Risk Manager...")
        risk_manager = RiskManager(config)
        risk_manager.set_mt5_client(mt5_client)
        
        # 5. Telegram Bot (Early Init)
        logger.info("Initializing Telegram Bot...")
        telegram_bot = TelegramBot(config)
        
        # INJECT SESSION MANAGER (Critical fix for circular dependency)
        telegram_bot.session_manager = session_manager
        
        # 6. Alert Processor
        logger.info("Initializing Alert Processor...")
        alert_processor = AlertProcessor(config, telegram_bot=telegram_bot)
        
        # 7. Trading Engine (The Brain)
        logger.info("Initializing Trading Engine...")
        trading_engine = TradingEngine(config, risk_manager, mt5_client, telegram_bot, alert_processor)
        
        # 8. Wire Dependencies
        logger.info("Wiring Dependencies...")
        telegram_bot.set_dependencies(risk_manager, trading_engine)
        
        # 9. Start Systems (Async Init)
        logger.info("Starting Subsystems...")
        
        # Run async initialization
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(trading_engine.initialize())
        except Exception as e:
            logger.error(f"Trading Engine Init Error: {e}")
        
        # 10. Start Telegram Polling (Threaded)
        logger.info("Starting Telegram Polling...")
        telegram_bot.start_polling()
        
        logger.info("✅ BOT STARTUP COMPLETE. Waiting for commands.")
        
        # 11. Main Loop
        while running_event.is_set():
            time.sleep(1)
            
    except Exception as e:
        logger.critical(f"🔥 FATAL ERROR DURING STARTUP: {e}", exc_info=True)
        # Keep window open for debugging if needed (remove in prod)
        # time.sleep(10)
    finally:
        logger.info("Bot Shutdown.")

if __name__ == "__main__":
    main()
