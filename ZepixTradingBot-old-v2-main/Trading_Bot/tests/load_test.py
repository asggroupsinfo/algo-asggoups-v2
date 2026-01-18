
import asyncio
import time
import sys
import os
import logging
from unittest.mock import MagicMock

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.trading_engine import TradingEngine
from src.config import Config

# Disable logs for load testing
logging.basicConfig(level=logging.ERROR)

async def run_load_test():
    print(f"[{'LOAD TEST':<12}] Burst Signal Handling")
    
    # Setup
    telegram = MagicMock()
    telegram.session_manager = MagicMock()
    config = Config()
    risk_manager = MagicMock()
    mt5_client = MagicMock()
    alert_processor = MagicMock()
    
    processor = TradingEngine(config, risk_manager, mt5_client, telegram, alert_processor)
    processor._validate_signal = MagicMock(return_value=True)
    processor.execute_trades = MagicMock(return_value={"status": "executed"})
    
    # Create batch of signals
    count = 5000
    signals = []
    for i in range(count):
        signals.append({
            "symbol": "EURUSD",
            "type": "buy" if i % 2 == 0 else "sell",
            "price": 1.0500,
            "sl": 1.0400,
            "tp": 1.0600,
            "strategy": "combinedlogic-1",
            "id": f"sig-{i}"
        })
    
    print(f"  > Preparing to process {count} signals...")
    
    start_time = time.perf_counter()
    
    # Process concurrently? In reality, webhook is serial per request handler, but queue is concurrent.
    # We'll simulate rapid sequential arrival (as typical loop).
    for sig in signals:
        await processor.process_alert(sig)
        
    end_time = time.perf_counter()
    duration = end_time - start_time
    rate = count / duration
    
    print(f"  > Processed:   {count} signals")
    print(f"  > Duration:    {duration:.4f}s")
    print(f"  > Throughput:  {rate:.2f} signals/sec")
    
    if rate > 500:
        print("  ✅ STATUS: HIGH CAPACITY (>500/s)")
    else:
        print("  ⚠️ STATUS: LOW CAPACITY (<500/s)")
    print("-" * 40)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_load_test())
    except KeyboardInterrupt:
        print("\nTest Cancelled")
