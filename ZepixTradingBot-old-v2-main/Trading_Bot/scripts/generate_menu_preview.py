
import sys
import os
import json
import inspect

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock objects needed for MenuManager
class MockContextManager:
    def __init__(self): pass

class MockCommandExecutor:
    def __init__(self, bot, context_manager): pass

class MockConfig:
    def get(self, key, default=None): return default

class MockBot:
    def __init__(self):
        self.config = MockConfig()
        self.session_manager = MockSessionManager()
        self.captured_layout = None
        self.captured_text = None
    
    def send_message_with_keyboard(self, text, reply_markup):
        self.captured_text = text
        self.captured_layout = reply_markup
        return True

class MockSessionManager:
    def __init__(self):
        self.current_state = {'active_session': 'LONDON'}

class MockConfig:
    def get(self, key, default=None):
        if key == "symbol": return "XAUUSD"
        return default
    
    def send_message_with_keyboard(self, text, reply_markup):
        self.captured_text = text
        self.captured_layout = reply_markup
        return True
        
    def edit_message(self, text, message_id, reply_markup):
        return True

# Prepare Mock Modules to bypass imports in MenuManager
# We need to ensure when MenuManager imports things, it works or uses our mocks if dependencies are missing
try:
    from menu.menu_manager import MenuManager
    from menu.menu_constants import REPLY_MENU_MAP
except ImportError:
    # If script run from wrong dir
    sys.path.append(os.path.join(os.getcwd(), 'src'))
    from menu.menu_manager import MenuManager
    from menu.menu_constants import REPLY_MENU_MAP

def generate_html_preview():
    bot = MockBot()
    manager = MenuManager(bot)
    
    # 1. Capture Persistent Keybaord
    persistent_menu = manager.get_persistent_main_menu()
    persistent_keyboard = persistent_menu['keyboard']
    
    # 2. Capture Inline Keyboard
    # We call show_main_menu, which calls bot.send_message_with_keyboard, which we verified saves to bot.captured_layout
    manager.show_main_menu(user_id=123)
    inline_keyboard = bot.captured_layout['inline_keyboard']
    inline_text = bot.captured_text
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Zepix Bot Menu Preview</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background-color: #0e1621;
                color: white;
                margin: 0;
                padding: 20px;
                display: flex;
                justify-content: center;
            }}
            .phone-container {{
                width: 375px;
                background-color: #17212b;
                border: 1px solid #333;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 0 20px rgba(0,0,0,0.5);
                position: relative;
                min-height: 800px;
                display: flex;
                flex-direction: column;
            }}
            .header {{
                background-color: #242f3d;
                padding: 15px;
                font-weight: bold;
                border-bottom: 1px solid #101010;
            }}
            .chat-area {{
                flex: 1;
                padding: 15px;
                overflow-y: auto;
                background-image: url('https://web.telegram.org/img/bg_0.png'); /* Fallback or similar pattern */
                background-size: cover;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }}
            .message {{
                background-color: #182533;
                padding: 10px 15px;
                border-radius: 10px 10px 10px 0;
                max-width: 85%;
                font-size: 14px;
                line-height: 1.4;
                white-space: pre-wrap;
            }}
            .inline-keyboard {{
                display: flex;
                flex-direction: column;
                gap: 5px;
                margin-top: 10px;
            }}
            .inline-row {{
                display: flex;
                gap: 5px;
                width: 100%;
            }}
            .inline-btn {{
                background-color: #2b5278; /* Telegram blue-ish */
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                text-align: center;
                flex: 1;
                font-size: 13px;
                cursor: pointer;
                font-weight: 500;
            }}
            .persistent-keyboard {{
                background-color: #242f3d;
                padding: 5px;
                display: flex;
                flex-direction: column;
                gap: 2px;
                border-top: 1px solid #101010;
            }}
            .persist-row {{
                display: flex;
                gap: 2px;
                width: 100%;
            }}
            .persist-btn {{
                background-color: #2b5278; # #242f3d with lighter hover
                background: #2b52781a; /* Slight tint */
                background-color: #2f3a49;
                color: white;
                border: none;
                padding: 12px 0;
                text-align: center;
                flex: 1;
                font-size: 12px;
                border-radius: 2px;
                box-shadow: 0 1px 0 #101010;
            }}
            .timestamp {{
                font-size: 10px;
                color: #6c7883;
                text-align: right;
                margin-top: 5px;
            }}
            .section-label {{
                font-size: 12px;
                color: #aaa;
                margin: 5px 0;
                text-align: center;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
        </style>
    </head>
    <body>

    <div class="phone-container">
        <div class="header">Zepix Bot</div>
        
        <div class="chat-area">
            <!-- User Message -->
            <div class="message" style="align-self: flex-end; background-color: #2b5278; border-radius: 10px 10px 0 10px;">
                /start
                <div class="timestamp">12:00 PM</div>
            </div>

            <!-- Bot Message -->
            <div class="message">
                {inline_text.replace('*', '').replace('\n', '<br>')}
                
                <div class="inline-keyboard">
                    {"".join(render_inline_keyboard(inline_keyboard))}
                </div>
                <div class="timestamp">12:00 PM</div>
            </div>
        </div>

        <!-- Persistent Menu -->
        <div class="section-label">Persistent Keyboard (Always Visible)</div>
        <div class="persistent-keyboard">
            {"".join(render_persistent_keyboard(persistent_keyboard))}
        </div>
    </div>

    </body>
    </html>
    """
    
    output_path = os.path.join(os.path.dirname(__file__), 'menu_preview.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML Preview generated at: {output_path}")

def render_inline_keyboard(keyboard):
    html_rows = []
    for row in keyboard:
        btns = []
        for btn in row:
            text = btn['text']
            btns.append(f'<button class="inline-btn">{text}</button>')
        html_rows.append(f'<div class="inline-row">{"".join(btns)}</div>')
    return html_rows

def render_persistent_keyboard(keyboard):
    html_rows = []
    for row in keyboard:
        btns = []
        for btn in row:
             # Handle both string and dict formats if any
            text = btn if isinstance(btn, str) else btn['text']
            btns.append(f'<button class="persist-btn">{text}</button>')
        html_rows.append(f'<div class="persist-row">{"".join(btns)}</div>')
    return html_rows

if __name__ == "__main__":
    generate_html_preview()
