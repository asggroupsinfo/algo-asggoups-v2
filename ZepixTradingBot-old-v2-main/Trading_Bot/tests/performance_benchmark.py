
import time
import sys
import os
import logging
import asyncio
from unittest.mock import MagicMock

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.managers.risk_manager import RiskManager
from src.processors.alert_processor import AlertProcessor
from src.core.trading_engine import TradingEngine

# Setup basic logging to avoid littering console
logging.basicConfig(level=logging.CRITICAL)

def benchmark_risk_manager():
    print(f"[{'BENCHMARK':<12}] Risk Manager Validation Speed")
    
    # Setup
    config = Config()
    mt5 = MagicMock()
    mt5.get_account_info.return_value = {"equity": 10000.0, "balance": 10000.0}
    mt5.get_account_balance.return_value = 10000.0
    risk = RiskManager(config)
    risk.set_mt5_client(mt5)
    
    start_time = time.perf_counter()
    iterations = 10000
    
    for _ in range(iterations):
        risk.can_trade()
        risk.get_fixed_lot_size(10000.0)
        
    end_time = time.perf_counter()
    total_time = end_time - start_time
    avg_time = (total_time / iterations) * 1000 # ms
    
    print(f"  > Iterations: {iterations}")
    print(f"  > Total Time: {total_time:.4f}s")
    print(f"  > Avg Time:   {avg_time:.4f} ms")
    if avg_time < 1.0:
        print("  ✅ STATUS: EXCELLENT (<1ms)")
    else:
        print("  ⚠️ STATUS: SLOW (>1ms)")
    print("-" * 40)
    return avg_time

async def benchmark_alert_processing():
    print(f"[{'BENCHMARK':<12}] Signal Processing Latency")
    
    telegram = MagicMock()
    config = Config()
    # Mock extensive dependencies for TradingEngine
    risk_manager = MagicMock()
    mt5_client = MagicMock()
    alert_processor = MagicMock()
    
    processor = TradingEngine(config, risk_manager, mt5_client, telegram, alert_processor)
    # Mock internal methods to avoid actual logic execution in benchmark
    processor._validate_signal = MagicMock(return_value=True)
    processor.execute_trades = MagicMock(return_value={"status": "executed"})
    processor.is_valid_symbol = MagicMock(return_value=True) # If it calls is_valid_symbol
    
    # Need to mock session manager in telegram because of __init__ access?
    telegram.session_manager = MagicMock()
    
    sample_alert = {
        "symbol": "XAUUSD",
        "type": "buy",
        "price": 2000.0,
        "sl": 1990.0,
        "tp": 2020.0,
        "strategy": "combinedlogic-1"
    }
    
    start_time = time.perf_counter()
    iterations = 1000
    
    for _ in range(iterations):
        await processor.process_alert(sample_alert)
        
    end_time = time.perf_counter()
    total_time = end_time - start_time
    avg_time = (total_time / iterations) * 1000 # ms
    
    print(f"  > Iterations: {iterations}")
    print(f"  > Total Time: {total_time:.4f}s")
    print(f"  > Avg Time:   {avg_time:.4f} ms")
    print("-" * 40)
    return avg_time

def main():
    print("🚀 STARTING PERFORMANCE BENCHMARKS\n" + "="*40)
    
    # 1. Risk Manager Benchmark
    t1 = benchmark_risk_manager()
    
    # 2. Alert Processing Benchmark
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    t2 = loop.run_until_complete(benchmark_alert_processing())
    
    # Summary
    print("\n📊 SUMMARY RESULTS (Target: <5ms)")
    print(f"Risk Validation: {t1:.4f} ms")
    print(f"Alert Parsing:   {t2:.4f} ms")
    
    if t1 < 5.0 and t2 < 5.0:
        print("\n✅ SYSTEM PERFORMANCE: OPTIMAL")
    else:
        print("\n⚠️ SYSTEM PERFORMANCE: OPTIMIZATION NEEDED")

if __name__ == "__main__":
    main()
