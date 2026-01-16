"""
Menu Builder - Dynamic Inline Keyboard Generator
Provides consistent menu building across all 3 bots

Features:
- Dynamic inline keyboard generation
- Sub-menu navigation logic
- Confirmation dialogs
- Parameter selection menus
- Pagination support

Version: 1.0.0
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from enum import Enum

logger = logging.getLogger(__name__)


class MenuType(Enum):
    """Types of menus"""
    MAIN = "main"
    CATEGORY = "category"
    COMMAND = "command"
    PARAMETER = "parameter"
    CONFIRMATION = "confirmation"
    PAGINATION = "pagination"


class MenuBuilder:
    """
    Dynamic menu builder for Telegram inline keyboards.
    Provides consistent menu generation across all bots.
    """
    
    # Maximum buttons per row
    MAX_BUTTONS_PER_ROW = 3
    
    # Maximum rows per menu (Telegram limit)
    MAX_ROWS_PER_MENU = 10
    
    def __init__(self):
        """Initialize MenuBuilder"""
        self.menu_stack: List[str] = []
        self.current_context: Dict[str, Any] = {}
    
    def build_inline_keyboard(
        self,
        buttons: List[Dict[str, str]],
        columns: int = 2,
        add_back: bool = True,
        add_home: bool = True,
        back_callback: str = "nav_back",
        home_callback: str = "menu_main"
    ) -> Dict:
        """
        Build an inline keyboard from button definitions.
        
        Args:
            buttons: List of button dicts with 'text' and 'callback_data'
            columns: Number of columns (default 2)
            add_back: Add back button (default True)
            add_home: Add home button (default True)
            back_callback: Callback for back button
            home_callback: Callback for home button
            
        Returns:
            Telegram InlineKeyboardMarkup dict
        """
        keyboard = []
        
        # Group buttons into rows
        row = []
        for button in buttons:
            row.append({
                "text": button.get("text", ""),
                "callback_data": button.get("callback_data", "")
            })
            
            if len(row) >= columns:
                keyboard.append(row)
                row = []
        
        # Add remaining buttons
        if row:
            keyboard.append(row)
        
        # Add navigation row
        if add_back or add_home:
            nav_row = []
            if add_back:
                nav_row.append({"text": "🔙 Back", "callback_data": back_callback})
            if add_home:
                nav_row.append({"text": "🏠 Home", "callback_data": home_callback})
            keyboard.append(nav_row)
        
        return {"inline_keyboard": keyboard}
    
    def build_category_menu(
        self,
        category_name: str,
        commands: Dict[str, Dict],
        category_key: str
    ) -> Dict:
        """
        Build a category sub-menu with commands.
        
        Args:
            category_name: Display name of category
            commands: Dict of command definitions
            category_key: Category identifier
            
        Returns:
            Telegram InlineKeyboardMarkup dict
        """
        buttons = []
        
        for cmd_key, cmd_data in commands.items():
            # Create button text from command key
            button_text = cmd_key.replace("_", " ").title()
            
            # Add emoji based on command type
            if "status" in cmd_key:
                button_text = f"📊 {button_text}"
            elif "on" in cmd_key or "enable" in cmd_key:
                button_text = f"✅ {button_text}"
            elif "off" in cmd_key or "disable" in cmd_key:
                button_text = f"❌ {button_text}"
            elif "set" in cmd_key:
                button_text = f"⚙️ {button_text}"
            elif "reset" in cmd_key:
                button_text = f"🔄 {button_text}"
            else:
                button_text = f"🔹 {button_text}"
            
            buttons.append({
                "text": button_text,
                "callback_data": f"cmd_{category_key}_{cmd_key}"
            })
        
        return self.build_inline_keyboard(buttons, columns=2)
    
    def build_parameter_menu(
        self,
        param_name: str,
        options: List[str],
        command: str,
        current_value: Optional[str] = None
    ) -> Dict:
        """
        Build a parameter selection menu.
        
        Args:
            param_name: Name of parameter
            options: List of option values
            command: Command this parameter belongs to
            current_value: Current value to highlight
            
        Returns:
            Telegram InlineKeyboardMarkup dict
        """
        buttons = []
        
        for option in options:
            # Highlight current value
            if current_value and str(option) == str(current_value):
                text = f"✅ {option} (Current)"
            else:
                text = str(option)
            
            buttons.append({
                "text": text,
                "callback_data": f"param_{param_name}_{command}_{option}"
            })
        
        # Add custom value option
        buttons.append({
            "text": "✏️ Custom Value",
            "callback_data": f"custom_{param_name}_{command}"
        })
        
        return self.build_inline_keyboard(buttons, columns=3)
    
    def build_confirmation_menu(
        self,
        action: str,
        confirm_callback: str,
        cancel_callback: str = "menu_main",
        confirm_text: str = "✅ Confirm",
        cancel_text: str = "❌ Cancel"
    ) -> Dict:
        """
        Build a confirmation dialog menu.
        
        Args:
            action: Action being confirmed
            confirm_callback: Callback for confirm button
            cancel_callback: Callback for cancel button
            confirm_text: Text for confirm button
            cancel_text: Text for cancel button
            
        Returns:
            Telegram InlineKeyboardMarkup dict
        """
        return {
            "inline_keyboard": [
                [
                    {"text": confirm_text, "callback_data": confirm_callback},
                    {"text": cancel_text, "callback_data": cancel_callback}
                ]
            ]
        }
    
    def build_toggle_menu(
        self,
        feature_name: str,
        is_enabled: bool,
        toggle_callback: str,
        status_callback: Optional[str] = None
    ) -> Dict:
        """
        Build a toggle menu for on/off features.
        
        Args:
            feature_name: Name of feature
            is_enabled: Current state
            toggle_callback: Callback for toggle action
            status_callback: Optional callback for status
            
        Returns:
            Telegram InlineKeyboardMarkup dict
        """
        toggle_text = "❌ Disable" if is_enabled else "✅ Enable"
        status_emoji = "🟢" if is_enabled else "🔴"
        
        buttons = [
            {"text": f"{toggle_text} {feature_name}", "callback_data": toggle_callback}
        ]
        
        if status_callback:
            buttons.append({
                "text": f"{status_emoji} View Status",
                "callback_data": status_callback
            })
        
        return self.build_inline_keyboard(buttons, columns=1)
    
    def build_pagination_menu(
        self,
        items: List[Dict[str, str]],
        page: int,
        items_per_page: int = 5,
        base_callback: str = "page"
    ) -> Dict:
        """
        Build a paginated menu.
        
        Args:
            items: List of item dicts with 'text' and 'callback_data'
            page: Current page (0-indexed)
            items_per_page: Items per page
            base_callback: Base callback for pagination
            
        Returns:
            Telegram InlineKeyboardMarkup dict
        """
        total_pages = (len(items) + items_per_page - 1) // items_per_page
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(items))
        
        keyboard = []
        
        # Add items for current page
        for item in items[start_idx:end_idx]:
            keyboard.append([{
                "text": item.get("text", ""),
                "callback_data": item.get("callback_data", "")
            }])
        
        # Add pagination controls
        if total_pages > 1:
            nav_row = []
            
            if page > 0:
                nav_row.append({
                    "text": "⬅️ Previous",
                    "callback_data": f"{base_callback}_{page - 1}"
                })
            
            nav_row.append({
                "text": f"📄 {page + 1}/{total_pages}",
                "callback_data": "noop"
            })
            
            if page < total_pages - 1:
                nav_row.append({
                    "text": "➡️ Next",
                    "callback_data": f"{base_callback}_{page + 1}"
                })
            
            keyboard.append(nav_row)
        
        # Add back/home
        keyboard.append([
            {"text": "🔙 Back", "callback_data": "nav_back"},
            {"text": "🏠 Home", "callback_data": "menu_main"}
        ])
        
        return {"inline_keyboard": keyboard}
    
    def build_tier_selection_menu(
        self,
        tiers: List[str],
        command: str,
        current_tier: Optional[str] = None
    ) -> Dict:
        """
        Build a tier selection menu for risk management.
        
        Args:
            tiers: List of tier values
            command: Command this selection belongs to
            current_tier: Current tier to highlight
            
        Returns:
            Telegram InlineKeyboardMarkup dict
        """
        buttons = []
        
        for tier in tiers:
            if current_tier and str(tier) == str(current_tier):
                text = f"✅ ${tier} (Current)"
            else:
                text = f"${tier}"
            
            buttons.append({
                "text": text,
                "callback_data": f"param_tier_{command}_{tier}"
            })
        
        return self.build_inline_keyboard(buttons, columns=2)
    
    def build_symbol_selection_menu(
        self,
        symbols: List[str],
        command: str,
        selected_symbol: Optional[str] = None
    ) -> Dict:
        """
        Build a symbol selection menu.
        
        Args:
            symbols: List of trading symbols
            command: Command this selection belongs to
            selected_symbol: Currently selected symbol
            
        Returns:
            Telegram InlineKeyboardMarkup dict
        """
        buttons = []
        
        for symbol in symbols:
            if selected_symbol and symbol == selected_symbol:
                text = f"✅ {symbol}"
            else:
                text = symbol
            
            buttons.append({
                "text": text,
                "callback_data": f"param_symbol_{command}_{symbol}"
            })
        
        return self.build_inline_keyboard(buttons, columns=3)
    
    def build_timeframe_selection_menu(
        self,
        timeframes: List[str],
        command: str,
        selected_tf: Optional[str] = None
    ) -> Dict:
        """
        Build a timeframe selection menu.
        
        Args:
            timeframes: List of timeframes
            command: Command this selection belongs to
            selected_tf: Currently selected timeframe
            
        Returns:
            Telegram InlineKeyboardMarkup dict
        """
        buttons = []
        
        for tf in timeframes:
            if selected_tf and tf == selected_tf:
                text = f"✅ {tf}"
            else:
                text = tf
            
            buttons.append({
                "text": text,
                "callback_data": f"param_tf_{command}_{tf}"
            })
        
        return self.build_inline_keyboard(buttons, columns=3)
    
    def build_quick_actions_menu(self) -> Dict:
        """
        Build quick actions menu.
        
        Returns:
            Telegram InlineKeyboardMarkup dict
        """
        return {
            "inline_keyboard": [
                [
                    {"text": "📊 Dashboard", "callback_data": "action_dashboard"},
                    {"text": "⏸️ Pause/Resume", "callback_data": "action_pause_resume"}
                ],
                [
                    {"text": "📈 Trades", "callback_data": "action_trades"},
                    {"text": "💰 Performance", "callback_data": "action_performance"}
                ],
                [
                    {"text": "🎙️ Voice Test", "callback_data": "action_voice_test"},
                    {"text": "⏰ Clock", "callback_data": "action_clock"}
                ],
                [
                    {"text": "🏠 Main Menu", "callback_data": "menu_main"}
                ]
            ]
        }
    
    def build_settings_menu(self) -> Dict:
        """
        Build settings menu.
        
        Returns:
            Telegram InlineKeyboardMarkup dict
        """
        return {
            "inline_keyboard": [
                [
                    {"text": "🛡️ Risk Settings", "callback_data": "menu_risk"},
                    {"text": "⚙️ SL System", "callback_data": "menu_sl_system"}
                ],
                [
                    {"text": "📈 Profit Booking", "callback_data": "menu_profit"},
                    {"text": "🔄 Re-entry", "callback_data": "menu_reentry"}
                ],
                [
                    {"text": "⏱️ Timeframe Logic", "callback_data": "menu_timeframe"},
                    {"text": "⚡ Fine-Tune", "callback_data": "menu_fine_tune"}
                ],
                [
                    {"text": "🔍 Diagnostics", "callback_data": "menu_diagnostics"}
                ],
                [
                    {"text": "🔙 Back", "callback_data": "nav_back"},
                    {"text": "🏠 Home", "callback_data": "menu_main"}
                ]
            ]
        }
    
    def build_error_menu(self, error_message: str) -> Dict:
        """
        Build an error display menu.
        
        Args:
            error_message: Error message to display
            
        Returns:
            Telegram InlineKeyboardMarkup dict
        """
        return {
            "inline_keyboard": [
                [
                    {"text": "🔄 Retry", "callback_data": "nav_retry"},
                    {"text": "🏠 Home", "callback_data": "menu_main"}
                ]
            ]
        }
    
    def push_menu(self, menu_id: str):
        """Push menu to navigation stack"""
        self.menu_stack.append(menu_id)
    
    def pop_menu(self) -> Optional[str]:
        """Pop menu from navigation stack"""
        if self.menu_stack:
            return self.menu_stack.pop()
        return None
    
    def get_previous_menu(self) -> Optional[str]:
        """Get previous menu without popping"""
        if len(self.menu_stack) > 1:
            return self.menu_stack[-2]
        return None
    
    def clear_stack(self):
        """Clear navigation stack"""
        self.menu_stack.clear()
    
    def set_context(self, key: str, value: Any):
        """Set context value"""
        self.current_context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get context value"""
        return self.current_context.get(key, default)
    
    def clear_context(self):
        """Clear context"""
        self.current_context.clear()


class MenuFactory:
    """
    Factory for creating common menu configurations.
    """
    
    @staticmethod
    def create_main_menu() -> Dict:
        """Create main menu"""
        builder = MenuBuilder()
        return builder.build_inline_keyboard(
            buttons=[
                {"text": "📊 Dashboard", "callback_data": "action_dashboard"},
                {"text": "⏸️ Pause/Resume", "callback_data": "action_pause_resume"},
                {"text": "📈 Trades", "callback_data": "action_trades"},
                {"text": "💰 Performance", "callback_data": "action_performance"},
                {"text": "🕒 Sessions", "callback_data": "session_dashboard"},
                {"text": "💱 Trading", "callback_data": "menu_trading"},
                {"text": "⏱️ Timeframe", "callback_data": "menu_timeframe"},
                {"text": "🔄 Re-entry", "callback_data": "menu_reentry"},
                {"text": "📍 Trends", "callback_data": "menu_trends"},
                {"text": "🛡️ Risk", "callback_data": "menu_risk"},
                {"text": "⚙️ SL System", "callback_data": "menu_sl_system"},
                {"text": "💎 Orders", "callback_data": "menu_orders"},
                {"text": "📈 Profit", "callback_data": "menu_profit"},
                {"text": "🔧 Settings", "callback_data": "menu_settings"},
                {"text": "🔍 Diagnostics", "callback_data": "menu_diagnostics"},
                {"text": "⚡ Fine-Tune", "callback_data": "menu_fine_tune"},
                {"text": "🆘 Help", "callback_data": "action_help"}
            ],
            columns=2,
            add_back=False,
            add_home=False
        )
    
    @staticmethod
    def create_panic_menu() -> Dict:
        """Create PANIC CLOSE confirmation menu"""
        builder = MenuBuilder()
        return builder.build_confirmation_menu(
            action="panic_close",
            confirm_callback="confirm_panic_close",
            cancel_callback="menu_main",
            confirm_text="✅ YES - CLOSE ALL",
            cancel_text="❌ CANCEL"
        )
    
    @staticmethod
    def create_back_only_menu(back_callback: str = "nav_back") -> Dict:
        """Create menu with only back button"""
        return {
            "inline_keyboard": [
                [{"text": "🔙 Back", "callback_data": back_callback}]
            ]
        }
    
    @staticmethod
    def create_home_only_menu() -> Dict:
        """Create menu with only home button"""
        return {
            "inline_keyboard": [
                [{"text": "🏠 Main Menu", "callback_data": "menu_main"}]
            ]
        }
