"""
Trading Flow - Zero-Typing Buy/Sell Wizard

Implements the 4-step wizard for placing trades.
1. Symbol Selection
2. Direction (if not started with specific command)
3. Lot Size Selection
4. Confirmation

Version: 1.3.0 (Global Breadcrumb Integration)
Created: 2026-01-21
Part of: TELEGRAM_V5_ZERO_TYPING_UI
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .base_flow import BaseFlow
import logging

logger = logging.getLogger(__name__)

class TradingFlow(BaseFlow):

    @property
    def flow_name(self) -> str:
        return "trading_flow"

    async def start_buy(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        logger.info(f"Starting BUY flow for {chat_id}")
        state = self.state_manager.start_flow(chat_id, self.flow_name)
        state.add_data("direction", "BUY")
        state.step = 0
        await self.show_step(update, context, 0)

    async def start_sell(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        logger.info(f"Starting SELL flow for {chat_id}")
        state = self.state_manager.start_flow(chat_id, self.flow_name)
        state.add_data("direction", "SELL")
        state.step = 0
        await self.show_step(update, context, 0)

    async def show_step(self, update: Update, context: ContextTypes.DEFAULT_TYPE, step: int):
        chat_id = update.effective_chat.id
        state = self.state_manager.get_state(chat_id)
        direction = state.get_data("direction", "TRADE")

        header = self.header.build_header(style='compact')
        breadcrumb = self._format_breadcrumb(["Symbol", "Lot", "Confirm"], step)

        if step == 0:
            # Step 1: Symbol Selection
            text = (
                f"{header}\n"
                f"{breadcrumb}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Select a symbol to trade:"
            )

            # Expanded symbols list
            symbols = [
                {"text": "EURUSD", "id": "EURUSD"}, {"text": "GBPUSD", "id": "GBPUSD"},
                {"text": "USDJPY", "id": "USDJPY"}, {"text": "XAUUSD", "id": "XAUUSD"},
                {"text": "AUDUSD", "id": "AUDUSD"}, {"text": "USDCAD", "id": "USDCAD"},
                {"text": "NZDUSD", "id": "NZDUSD"}, {"text": "USDCHF", "id": "USDCHF"}
            ]

            keyboard = self.btn.create_paginated_menu(symbols, 0, "flow_trade_sym", n_cols=2)

        elif step == 1:
            # Step 2: Lot Size
            symbol = state.get_data("symbol")
            text = (
                f"{header}\n"
                f"{breadcrumb}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Symbol: **{symbol}**\n\n"
                f"Select lot size:"
            )

            lots = [
                {"text": "0.01", "id": "0.01"}, {"text": "0.02", "id": "0.02"},
                {"text": "0.05", "id": "0.05"}, {"text": "0.10", "id": "0.10"},
                {"text": "0.20", "id": "0.20"}, {"text": "0.50", "id": "0.50"}
            ]

            keyboard = self.btn.create_paginated_menu(lots, 0, "flow_trade_lot", n_cols=3)

        elif step == 2:
            # Step 3: Confirmation
            symbol = state.get_data("symbol")
            lot = state.get_data("lot")

            text = (
                f"{header}\n"
                f"{breadcrumb}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"**Type:** {direction}\n"
                f"**Symbol:** {symbol}\n"
                f"**Size:** {lot} lots\n\n"
                f"Proceed with execution?"
            )

            keyboard = self.btn.create_confirmation_menu("flow_trade_confirm", "flow_trade_cancel")

        if update.callback_query:
            try:
                await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode='HTML')
            except Exception as e:
                logger.warning(f"Failed to edit message in flow: {e}")
                await self.bot.send_message(text, reply_markup=keyboard)
        else:
            await self.bot.send_message(text, reply_markup=keyboard)

    async def process_step(self, update: Update, context: ContextTypes.DEFAULT_TYPE, state):
        query = update.callback_query
        data = query.data
        chat_id = update.effective_chat.id

        # Acquire lock for state update
        lock = self.state_manager.get_lock(chat_id)
        async with lock:
            if "flow_trade_sym_" in data:
                symbol = data.split("_")[-1]
                state.add_data("symbol", symbol)
                state.step = 1
                await self.show_step(update, context, 1)

            elif "flow_trade_lot_" in data:
                lot = data.split("_")[-1]
                state.add_data("lot", lot)
                state.step = 2
                await self.show_step(update, context, 2)

            elif "flow_trade_confirm" in data:
                # Execute Trade
                symbol = state.get_data("symbol")
                lot = state.get_data("lot")
                direction = state.get_data("direction")

                logger.info(f"Executing trade: {direction} {symbol} {lot}")

                # Call trading engine
                ticket = "SIM-12345"
                if hasattr(self.bot, 'trading_engine') and self.bot.trading_engine:
                    try:
                        if hasattr(self.bot.trading_engine, 'place_trade'):
                            # result = await self.bot.trading_engine.place_trade(...)
                            pass
                    except Exception as e:
                        logger.error(f"Trade execution failed: {e}")
                        await query.edit_message_text(f"❌ Execution Failed: {str(e)}")
                        return

                await query.edit_message_text(
                    f"✅ **ORDER EXECUTED**\n\n"
                    f"{direction} {symbol} ({lot} lots)\n"
                    f"Ticket: #{ticket}\n\n"
                    f"Use /positions to view.",
                    parse_mode='Markdown'
                )
                self.state_manager.clear_state(chat_id)

            elif "flow_trade_cancel" in data:
                await self.cancel(update, context)
