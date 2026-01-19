"""
Live Telegram Bot Testing Script
Tests all 3 bots with real credentials

This script tests:
1. Bot connections (get_me)
2. Message sending capability
3. HTML formatting support

Version: 1.0.0
Date: 2026-01-19
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from telegram import Bot
from telegram.error import TelegramError

# Bot Credentials
CONTROLLER_TOKEN = "8598624206:AAGWD7y35HUkrSDvSCrFuTL-FZZx8bjqwwo"
NOTIFICATION_TOKEN = "8311364103:AAHArQ0kHnS8e_hLGdBMzf9u8bLGlUKK4vM"
ANALYTICS_TOKEN = "8513021073:AAHxk9Z9CxKpc2UKNVn1vhYUIGshDJ2L1Ys"
CHAT_ID = 2139792302


class LiveBotTester:
    def __init__(self):
        self.controller_bot = Bot(token=CONTROLLER_TOKEN)
        self.notification_bot = Bot(token=NOTIFICATION_TOKEN)
        self.analytics_bot = Bot(token=ANALYTICS_TOKEN)
        self.results = {"passed": 0, "failed": 0, "errors": []}
        self.bot_usernames = {}
    
    async def test_bot_connection(self, bot: Bot, name: str) -> bool:
        """Test if bot can connect and get info"""
        try:
            info = await bot.get_me()
            print(f"[PASS] {name} connected: @{info.username}")
            self.bot_usernames[name] = info.username
            self.results["passed"] += 1
            return True
        except TelegramError as e:
            print(f"[FAIL] {name} connection failed: {e}")
            self.results["failed"] += 1
            self.results["errors"].append(f"{name}: {e}")
            return False
    
    async def test_send_message(self, bot: Bot, name: str, message: str) -> bool:
        """Test sending a message"""
        try:
            msg = await bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode='HTML'
            )
            print(f"[PASS] {name} sent message (ID: {msg.message_id})")
            self.results["passed"] += 1
            return True
        except TelegramError as e:
            print(f"[FAIL] {name} send failed: {e}")
            self.results["failed"] += 1
            self.results["errors"].append(f"{name} send: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all live bot tests"""
        print("\n" + "="*60)
        print("LIVE TELEGRAM BOT TESTING")
        print("="*60 + "\n")
        
        # Test 1: Bot Connections
        print("Testing Bot Connections...")
        print("-" * 40)
        await self.test_bot_connection(self.controller_bot, "Controller Bot")
        await self.test_bot_connection(self.notification_bot, "Notification Bot")
        await self.test_bot_connection(self.analytics_bot, "Analytics Bot")
        
        # Test 2: Send Test Messages
        print("\nTesting Message Sending...")
        print("-" * 40)
        await self.test_send_message(
            self.controller_bot, 
            "Controller Bot",
            "<b>CONTROLLER BOT TEST</b>\n\n[PASS] Live connection verified!\n105 commands ready\n\nTimestamp: " + str(asyncio.get_event_loop().time())
        )
        await asyncio.sleep(1)  # Rate limiting
        
        await self.test_send_message(
            self.notification_bot,
            "Notification Bot", 
            "<b>NOTIFICATION BOT TEST</b>\n\n[PASS] Live connection verified!\n78 notification types ready\n\nTimestamp: " + str(asyncio.get_event_loop().time())
        )
        await asyncio.sleep(1)
        
        await self.test_send_message(
            self.analytics_bot,
            "Analytics Bot",
            "<b>ANALYTICS BOT TEST</b>\n\n[PASS] Live connection verified!\nAnalytics features ready\n\nTimestamp: " + str(asyncio.get_event_loop().time())
        )
        
        # Print Results
        print("\n" + "="*60)
        print("TEST RESULTS")
        print("="*60)
        print(f"Passed: {self.results['passed']}")
        print(f"Failed: {self.results['failed']}")
        total = self.results['passed'] + self.results['failed']
        pass_rate = (self.results['passed'] / total * 100) if total > 0 else 0
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        if self.bot_usernames:
            print("\nBot Usernames:")
            for name, username in self.bot_usernames.items():
                print(f"  - {name}: @{username}")
        
        if self.results["errors"]:
            print("\nErrors:")
            for error in self.results["errors"]:
                print(f"  - {error}")
        
        return self.results["failed"] == 0


async def main():
    tester = LiveBotTester()
    success = await tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
