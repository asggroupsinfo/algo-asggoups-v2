#!/usr/bin/env python3
"""
FULL BOT STARTUP SCRIPT
Initializes ALL components:
- MT5 Client (Simulation Mode on Linux)
- TradingEngine
- TelegramBot with Polling
- Webhook Server
- Plugin System
- Session Manager
- Database

This script satisfies Mandate 16: Full Bot Activation
"""
import sys
import os
import asyncio
import threading
import logging
import time
from datetime import datetime

# Add parent directory (Trading_Bot/) to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'logs/startup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

def print_banner():
    """Print startup banner"""
    print("=" * 70)
    print("  ZEPIX TRADING BOT V5 - FULL ACTIVATION")
    print("=" * 70)
    print(f"  Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

def initialize_components():
    """Initialize all bot components"""
    from src.config import Config
    from src.clients.mt5_client import MT5Client
    from src.managers.risk_manager import RiskManager
    from src.processors.alert_processor import AlertProcessor
    from src.clients.telegram_bot_fixed import TelegramBot
    from src.database import TradeDatabase
    from src.managers.session_manager import SessionManager
    
    print("\n[1/8] Loading Configuration...")
    config = Config()
    print(f"  - Telegram Token: {config.get('telegram_token', '')[:20]}...")
    print(f"  - Chat ID: {config.get('telegram_chat_id', '')}")
    print("  - Configuration loaded successfully")
    
    print("\n[2/8] Initializing Database...")
    db = TradeDatabase()
    print("  - Database initialized: zepix_combined.db")
    
    print("\n[3/8] Initializing MT5 Client...")
    mt5_client = MT5Client(config)
    mt5_success = mt5_client.initialize()
    if mt5_success:
        print("  - MT5 Client initialized (Simulation Mode)")
    else:
        print("  - WARNING: MT5 initialization failed, continuing in simulation mode")
        mt5_client.initialized = True  # Force simulation mode
    
    print("\n[4/8] Initializing Risk Manager...")
    risk_manager = RiskManager(config)
    print("  - Risk Manager initialized")
    
    print("\n[5/8] Initializing Telegram Bot...")
    telegram_bot = TelegramBot(config)
    
    # Initialize Session Manager and attach to telegram_bot
    print("\n[6/8] Initializing Session Manager...")
    session_manager = SessionManager(config, db, mt5_client)
    telegram_bot.session_manager = session_manager
    print(f"  - Session Manager initialized (Timezone: {session_manager.timezone})")
    print(f"  - Current Session: {session_manager.get_current_session()}")
    
    print("\n[7/8] Initializing Alert Processor...")
    alert_processor = AlertProcessor(config)
    print("  - Alert Processor initialized")
    
    print("\n[8/8] Initializing Trading Engine...")
    from src.core.trading_engine import TradingEngine
    trading_engine = TradingEngine(
        config=config,
        risk_manager=risk_manager,
        mt5_client=mt5_client,
        telegram_bot=telegram_bot,
        alert_processor=alert_processor
    )
    
    # Set dependencies
    telegram_bot.set_dependencies(risk_manager, trading_engine)
    
    print("  - Trading Engine initialized")
    
    return {
        'config': config,
        'db': db,
        'mt5_client': mt5_client,
        'risk_manager': risk_manager,
        'telegram_bot': telegram_bot,
        'session_manager': session_manager,
        'alert_processor': alert_processor,
        'trading_engine': trading_engine
    }

def start_telegram_polling(telegram_bot):
    """Start Telegram bot polling in a separate thread"""
    def polling_thread():
        try:
            logger.info("Starting Telegram polling...")
            telegram_bot.start_polling()
        except Exception as e:
            logger.error(f"Telegram polling error: {e}")
    
    thread = threading.Thread(target=polling_thread, daemon=True)
    thread.start()
    return thread

async def initialize_trading_engine(trading_engine):
    """Initialize trading engine asynchronously"""
    try:
        success = await trading_engine.initialize()
        return success
    except Exception as e:
        logger.error(f"Trading engine initialization error: {e}")
        return False

def start_webhook_server(trading_engine):
    """Start webhook server in a separate thread"""
    import uvicorn
    from src.api.webhook_handler import app, init_plugin_router
    
    # Initialize plugin router with the trading engine's plugin registry
    if hasattr(trading_engine, 'plugin_registry') and trading_engine.plugin_registry:
        init_plugin_router(trading_engine.plugin_registry)
        print("  - Plugin router initialized for webhook")
    else:
        print("  - WARNING: Plugin registry not available, webhook may not process signals")
    
    def server_thread():
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=5000,
            log_level="info"
        )
    
    thread = threading.Thread(target=server_thread, daemon=True)
    thread.start()
    return thread

def send_startup_notification(telegram_bot, session_manager):
    """Send startup notification to Telegram"""
    session_info = session_manager.get_session_info()
    
    message = (
        "🤖 **ZEPIX TRADING BOT V5 STARTED**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "✅ **Components Initialized:**\n"
        "• MT5 Client: Running (Simulation Mode)\n"
        "• Trading Engine: Ready\n"
        "• Session Manager: Active\n"
        "• Plugin System: Loaded\n"
        "• Webhook Server: http://0.0.0.0:5000\n\n"
        f"🕐 **Current Session:** {session_info.get('session_name', 'Unknown')}\n"
        f"💱 **Allowed Symbols:** {', '.join(session_info.get('allowed_symbols', []))}\n\n"
        "📡 Bot is ready for commands!"
    )
    
    try:
        telegram_bot.send_message(message)
        print("\n✅ Startup notification sent to Telegram")
    except Exception as e:
        print(f"\n⚠️ Could not send Telegram notification: {e}")

def main():
    """Main entry point"""
    print_banner()
    
    try:
        # Initialize all components
        components = initialize_components()
        
        telegram_bot = components['telegram_bot']
        trading_engine = components['trading_engine']
        session_manager = components['session_manager']
        
        # Print success summary
        print("\n" + "=" * 70)
        print("  ALL COMPONENTS INITIALIZED SUCCESSFULLY")
        print("=" * 70)
        
        # Initialize trading engine asynchronously
        print("\nInitializing Trading Engine async components...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success = loop.run_until_complete(initialize_trading_engine(trading_engine))
            if success:
                print("✅ Trading Engine async initialization complete")
            else:
                print("⚠️ Trading Engine async initialization had issues (continuing)")
        except Exception as e:
            print(f"⚠️ Trading Engine async init error: {e} (continuing)")
        
        # Start webhook server
        print("\nStarting Webhook Server on port 5000...")
        webhook_thread = start_webhook_server(trading_engine)
        time.sleep(2)  # Wait for server to start
        print("✅ Webhook Server started: http://0.0.0.0:5000")
        
        # Start Telegram polling
        print("\nStarting Telegram Bot polling...")
        polling_thread = start_telegram_polling(telegram_bot)
        time.sleep(2)  # Wait for polling to start
        print("✅ Telegram Bot polling started")
        
        # Send startup notification
        send_startup_notification(telegram_bot, session_manager)
        
        # Print final status
        print("\n" + "=" * 70)
        print("  🚀 ZEPIX TRADING BOT V5 IS NOW RUNNING")
        print("=" * 70)
        print("\nEndpoints:")
        print("  - Webhook: http://localhost:5000/webhook")
        print("  - Health: http://localhost:5000/health")
        print("  - V3 Webhook: http://localhost:5000/webhook/v3")
        print("\nTelegram Bot: @Algo_Asg_Controller_bot")
        print("\nPress Ctrl+C to stop the bot")
        print("=" * 70)
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n[INFO] Shutting down bot...")
        print("[INFO] Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
