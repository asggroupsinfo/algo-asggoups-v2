"""
Voice Menu - Level 1 Navigation

Implements the Voice Control submenu.
src/telegram/menus/voice_menu.py
"""

from telegram import InlineKeyboardMarkup
from ..core.base_menu_builder import BaseMenuBuilder
from ..core.button_builder import ButtonBuilder as Btn

class VoiceMenu(BaseMenuBuilder):

    def build_menu(self) -> dict:
        """Build the Voice menu"""

        buttons = [
            Btn.create_button("🔊 Status", "voice_status"),
            Btn.create_button("⚡ Toggle", "voice_toggle"),
            Btn.create_button("🗣️ Test", "voice_test"),
            Btn.create_button("📢 Alerts", "voice_alerts"),
            Btn.create_button("🔇 Mute", "voice_mute"),
            Btn.create_button("⚙️ Config", "voice_config")
        ]

        # Grid layout (2 cols)
        menu = Btn.build_menu(buttons, n_cols=2)

        # Add Navigation
        menu = Btn.add_navigation(menu)

        return {
            "text": "🔊 **VOICE SYSTEM**\n━━━━━━━━━━━━━━━━━━━━━━━━\nManage Audio Alerts:",
            "reply_markup": InlineKeyboardMarkup(menu)
        }
