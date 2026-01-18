
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.clients.telegram_bot_fixed import TelegramBot
from src.menu.menu_manager import MenuManager

def verify_menu_configuration():
    print("=" * 50)
    print("VERIFYING MENU CONFIGURATION & INTEGRATION")
    print("=" * 50)
    
    # 1. Initialize Bot
    print("\n[1] Initializing TelegramBotFixed...")
    try:
        config = Config()
        bot = TelegramBot(config)
        print("✅ TelegramBotFixed initialized")
    except Exception as e:
        print(f"❌ Failed to init bot: {e}")
        import traceback
        traceback.print_exc()
        return

    # 2. Verify MenuManager Attribute
    print("\n[2] Checking bot.menu_manager attribute...")
    if hasattr(bot, 'menu_manager') and bot.menu_manager:
        print(f"✅ bot.menu_manager is present: {type(bot.menu_manager)}")
    else:
        print("❌ bot.menu_manager is MISSING or None")
        # Initialize manually if missing for further tests
        bot.menu_manager = MenuManager(bot)

    # 3. Inspect Main Menu Keyboard
    print("\n[3] Inspecting Main Menu Structure...")
    try:
        # Generate the keyboard
        keyboard = bot.menu_manager._get_main_menu_keyboard()
        
        # Flatten and count buttons
        total_buttons = 0
        print("\n--- BUTTON LAYOUT ---")
        for row_idx, row in enumerate(keyboard):
            row_text = " | ".join([f"[{btn['text']}]" for btn in row])
            print(f"Row {row_idx + 1}: {row_text}")
            total_buttons += len(row)
            
        print(f"\nTotal Buttons: {total_buttons}")
        
        # Verify specific critical buttons exist
        required_buttons = ["Trading", "Risk", "Strategy", "Analytics", "Plugin", "System"]
        found_buttons = []
        for row in keyboard:
            for btn in row:
                for req in required_buttons:
                    if req.lower() in btn['text'].lower():
                        found_buttons.append(req)
        
        missing = set(required_buttons) - set(found_buttons)
        if not missing:
            print("✅ All critical categories found")
        else:
            print(f"⚠️ Missing categories: {missing}")

    except Exception as e:
        print(f"❌ Failed to inspect keyboard: {e}")

    # 4. Verify Command Categories
    print("\n[4] Verifying Command Categories (menu_constants.py)...")
    from src.menu.menu_constants import COMMAND_CATEGORIES
    
    print(f"Total Categories Defined: {len(list(COMMAND_CATEGORIES.keys()))}")
    for cat_key, cat_data in COMMAND_CATEGORIES.items():
        cmd_count = len(cat_data.get("commands", []))
        print(f"  - {cat_key.title()}: {cmd_count} commands")
        
    # Check total commands cover most of the 95
    total_commands = sum(len(c["commands"]) for c in COMMAND_CATEGORIES.values())
    print(f"\nTotal Interactive Commands: {total_commands}")
    if total_commands < 50:
        print("⚠️ Warning: Interactive command count seems low compared to 95+ total commands.")

if __name__ == "__main__":
    verify_menu_configuration()
