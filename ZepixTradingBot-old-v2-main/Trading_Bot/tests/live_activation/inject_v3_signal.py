#!/usr/bin/env python3
"""
V3 Signal Injection Script for Mandate 16: Full Bot Activation
Sends a test V3 alert to the webhook to verify end-to-end flow.
"""
import requests
import json
import time
from datetime import datetime

# Webhook URL
WEBHOOK_URL = "http://localhost:5000/webhook/v3"

# V3 Alert Payload (CombinedLogic-1 BUY signal for EURUSD)
# Updated with high consensus score to pass validation
V3_ALERT_PAYLOAD = {
    "alert_type": "combinedlogic-1",
    "symbol": "EURUSD",
    "action": "BUY",
    "timeframe": "15m",
    "price": 1.08500,
    "sl": 1.08300,
    "tp1": 1.08700,
    "tp2": 1.08900,
    "tp3": 1.09100,
    "timestamp": datetime.now().isoformat(),
    "source": "TradingView",
    "confidence": 95,
    "consensus_score": 10,  # High consensus score to pass validation (min is 5)
    "mtf_alignment": {
        "1m": "BULLISH",
        "5m": "BULLISH",
        "15m": "BULLISH",
        "1h": "BULLISH"
    },
    "indicators": {
        "rsi": 55,
        "macd": "BULLISH",
        "ema_cross": True,
        "volume_spike": True,
        "trend_strength": 8
    }
}

def inject_signal():
    """Send V3 alert to webhook and capture response."""
    print("=" * 60)
    print("  V3 SIGNAL INJECTION TEST")
    print("=" * 60)
    print(f"  Timestamp: {datetime.now().isoformat()}")
    print(f"  Webhook URL: {WEBHOOK_URL}")
    print("=" * 60)
    
    print("\n[STEP 1] Preparing V3 Alert Payload...")
    print(f"  Symbol: {V3_ALERT_PAYLOAD['symbol']}")
    print(f"  Action: {V3_ALERT_PAYLOAD['action']}")
    print(f"  Alert Type: {V3_ALERT_PAYLOAD['alert_type']}")
    print(f"  Timeframe: {V3_ALERT_PAYLOAD['timeframe']}")
    print(f"  Entry Price: {V3_ALERT_PAYLOAD['price']}")
    print(f"  Stop Loss: {V3_ALERT_PAYLOAD['sl']}")
    print(f"  Take Profit 1: {V3_ALERT_PAYLOAD['tp1']}")
    
    print("\n[STEP 2] Sending V3 Alert to Webhook...")
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=V3_ALERT_PAYLOAD,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"  HTTP Status: {response.status_code}")
        print(f"  Response: {response.text[:500] if response.text else 'No response body'}")
        
        if response.status_code == 200:
            print("\n[STEP 3] Signal Accepted by Webhook!")
            try:
                result = response.json()
                print(f"  Result: {json.dumps(result, indent=2)}")
            except:
                pass
        else:
            print(f"\n[ERROR] Webhook returned status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to webhook. Is the bot running?")
        return False
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        return False
    
    print("\n[STEP 4] Waiting for Processing (3 seconds)...")
    time.sleep(3)
    
    print("\n[STEP 5] Checking Health Endpoint...")
    try:
        health_response = requests.get("http://localhost:5000/health", timeout=10)
        print(f"  Health Status: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"  Health Response: {health_response.json()}")
    except Exception as e:
        print(f"  Health check failed: {e}")
    
    print("\n" + "=" * 60)
    print("  V3 SIGNAL INJECTION COMPLETE")
    print("=" * 60)
    print("\nExpected Flow:")
    print("  1. Webhook receives V3 alert")
    print("  2. V3 Plugin processes signal")
    print("  3. Session Manager validates trading session")
    print("  4. Trading Engine creates order (simulation mode)")
    print("  5. Database records the trade")
    print("  6. Telegram notification sent")
    print("\nCheck bot logs for detailed processing information.")
    
    return True

if __name__ == "__main__":
    inject_signal()
