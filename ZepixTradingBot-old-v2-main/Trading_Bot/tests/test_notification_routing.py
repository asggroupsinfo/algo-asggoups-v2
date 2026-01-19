"""
Notification Routing Test Script
Tests notification routing for all 78 notification types

This script tests:
1. NotificationRouter initialization
2. Routing rules for all notification types
3. Formatter output for sample notifications
4. Live message sending via notification bot

Version: 1.0.0
Date: 2026-01-19
"""
import asyncio
import sys
import os

# Add both src and parent directories to path
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
parent_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, src_path)
sys.path.insert(0, parent_path)

from telegram import Bot
from telegram.error import TelegramError

# Import notification router components
from src.telegram.notification_router import (
    NotificationRouter, 
    NotificationType, 
    NotificationFormatter,
    DEFAULT_ROUTING_RULES,
    create_default_router
)

# Bot Credentials
NOTIFICATION_TOKEN = "8311364103:AAHArQ0kHnS8e_hLGdBMzf9u8bLGlUKK4vM"
CHAT_ID = 2139792302


class NotificationRoutingTester:
    def __init__(self):
        self.notification_bot = Bot(token=NOTIFICATION_TOKEN)
        self.router = create_default_router()
        self.results = {"passed": 0, "failed": 0, "errors": []}
    
    def test_notification_type_count(self) -> bool:
        """Test that we have exactly 78 notification types"""
        count = len(NotificationType)
        if count == 78:
            print(f"[PASS] NotificationType count: {count}")
            self.results["passed"] += 1
            return True
        else:
            print(f"[FAIL] NotificationType count: {count} (expected 78)")
            self.results["failed"] += 1
            self.results["errors"].append(f"NotificationType count: {count} != 78")
            return False
    
    def test_routing_rules_complete(self) -> bool:
        """Test that all notification types have routing rules"""
        missing = []
        for notif_type in NotificationType:
            if notif_type not in DEFAULT_ROUTING_RULES:
                missing.append(notif_type.name)
        
        if not missing:
            print(f"[PASS] All 78 notification types have routing rules")
            self.results["passed"] += 1
            return True
        else:
            print(f"[FAIL] Missing routing rules for: {missing}")
            self.results["failed"] += 1
            self.results["errors"].append(f"Missing routing rules: {missing}")
            return False
    
    def test_formatter_registration(self) -> bool:
        """Test that formatters are registered for key notification types"""
        key_types = [
            NotificationType.ENTRY,
            NotificationType.EXIT,
            NotificationType.TP_HIT,
            NotificationType.SL_HIT,
            NotificationType.V6_ENTRY_15M,
            NotificationType.TP_CONTINUATION,
            NotificationType.SIGNAL_RECEIVED,
            NotificationType.DASHBOARD_UPDATE,
        ]
        
        missing = []
        for notif_type in key_types:
            if notif_type not in self.router.formatters:
                missing.append(notif_type.name)
        
        if not missing:
            print(f"[PASS] Key formatters registered ({len(key_types)} checked)")
            self.results["passed"] += 1
            return True
        else:
            print(f"[FAIL] Missing formatters for: {missing}")
            self.results["failed"] += 1
            self.results["errors"].append(f"Missing formatters: {missing}")
            return False
    
    def test_formatter_output(self) -> bool:
        """Test that formatters produce valid output"""
        test_cases = [
            (NotificationType.ENTRY, {"symbol": "XAUUSD", "type": "BUY", "price": 2650.50, "lot_size": 0.1}),
            (NotificationType.TP_HIT, {"symbol": "XAUUSD", "profit": 150.00, "pips": 50}),
            (NotificationType.RECOVERY_SUCCESS, {"symbol": "GBPUSD", "recovered_amount": 75.00}),
            (NotificationType.SIGNAL_RECEIVED, {"symbol": "EURUSD", "signal_type": "BUY", "timeframe": "1H"}),
        ]
        
        all_passed = True
        for notif_type, data in test_cases:
            try:
                if notif_type in self.router.formatters:
                    output = self.router.formatters[notif_type](data)
                    if output and len(output) > 0:
                        print(f"[PASS] Formatter {notif_type.name}: {len(output)} chars")
                    else:
                        print(f"[FAIL] Formatter {notif_type.name}: empty output")
                        all_passed = False
                else:
                    print(f"[SKIP] Formatter {notif_type.name}: not registered")
            except Exception as e:
                print(f"[FAIL] Formatter {notif_type.name}: {e}")
                all_passed = False
        
        if all_passed:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
            self.results["errors"].append("Some formatters failed")
        
        return all_passed
    
    async def test_live_notification_send(self) -> bool:
        """Test sending a sample notification via the notification bot"""
        try:
            # Format a sample notification
            data = {
                "symbol": "XAUUSD",
                "type": "BUY",
                "price": 2650.50,
                "lot_size": 0.1,
                "logic": "V3_COMBINED"
            }
            
            # Get formatted message
            if NotificationType.ENTRY in self.router.formatters:
                message = self.router.formatters[NotificationType.ENTRY](data)
            else:
                message = "<b>ENTRY NOTIFICATION TEST</b>\n\nSymbol: XAUUSD\nType: BUY\nPrice: 2650.50"
            
            # Send via notification bot
            msg = await self.notification_bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode='HTML'
            )
            print(f"[PASS] Live notification sent (ID: {msg.message_id})")
            self.results["passed"] += 1
            return True
        except TelegramError as e:
            print(f"[FAIL] Live notification failed: {e}")
            self.results["failed"] += 1
            self.results["errors"].append(f"Live notification: {e}")
            return False
    
    async def test_notification_categories(self) -> bool:
        """Test sending notifications from different categories"""
        test_notifications = [
            ("Autonomous System", NotificationType.TP_CONTINUATION, {"symbol": "EURUSD", "continuation_type": "TP1"}),
            ("Re-entry System", NotificationType.TP_REENTRY_EXECUTED, {"symbol": "GBPUSD", "reentry_price": 1.2650}),
            ("Signal Events", NotificationType.TREND_CHANGED, {"symbol": "USDJPY", "old_trend": "UP", "new_trend": "DOWN"}),
            ("Voice Alerts", NotificationType.VOICE_TP_HIT, {"symbol": "XAUUSD", "profit": 200.00}),
        ]
        
        all_passed = True
        for category, notif_type, data in test_notifications:
            try:
                if notif_type in self.router.formatters:
                    message = self.router.formatters[notif_type](data)
                else:
                    message = f"<b>{category.upper()} TEST</b>\n\nType: {notif_type.value}\nData: {data}"
                
                msg = await self.notification_bot.send_message(
                    chat_id=CHAT_ID,
                    text=message,
                    parse_mode='HTML'
                )
                print(f"[PASS] {category}: sent (ID: {msg.message_id})")
                await asyncio.sleep(1)  # Rate limiting
            except TelegramError as e:
                print(f"[FAIL] {category}: {e}")
                all_passed = False
        
        if all_passed:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
            self.results["errors"].append("Some category notifications failed")
        
        return all_passed
    
    async def run_all_tests(self):
        """Run all notification routing tests"""
        print("\n" + "="*60)
        print("NOTIFICATION ROUTING TESTS")
        print("="*60 + "\n")
        
        # Test 1: Notification Type Count
        print("Testing Notification Type Count...")
        print("-" * 40)
        self.test_notification_type_count()
        
        # Test 2: Routing Rules
        print("\nTesting Routing Rules...")
        print("-" * 40)
        self.test_routing_rules_complete()
        
        # Test 3: Formatter Registration
        print("\nTesting Formatter Registration...")
        print("-" * 40)
        self.test_formatter_registration()
        
        # Test 4: Formatter Output
        print("\nTesting Formatter Output...")
        print("-" * 40)
        self.test_formatter_output()
        
        # Test 5: Live Notification Send
        print("\nTesting Live Notification Send...")
        print("-" * 40)
        await self.test_live_notification_send()
        
        # Test 6: Category Notifications
        print("\nTesting Category Notifications...")
        print("-" * 40)
        await self.test_notification_categories()
        
        # Print Results
        print("\n" + "="*60)
        print("TEST RESULTS")
        print("="*60)
        print(f"Passed: {self.results['passed']}")
        print(f"Failed: {self.results['failed']}")
        total = self.results['passed'] + self.results['failed']
        pass_rate = (self.results['passed'] / total * 100) if total > 0 else 0
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        if self.results["errors"]:
            print("\nErrors:")
            for error in self.results["errors"]:
                print(f"  - {error}")
        
        return self.results["failed"] == 0


async def main():
    tester = NotificationRoutingTester()
    success = await tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
