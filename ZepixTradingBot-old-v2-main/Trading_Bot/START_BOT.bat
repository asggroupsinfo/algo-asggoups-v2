@echo off
cd /d "%~dp0"
echo ========================================
echo ZEPIX TRADING BOT - STARTING...
echo ========================================
echo.

REM Start the bot
python scripts/start_full_bot.py

echo.
echo ========================================
echo BOT STOPPED
echo ========================================
pause
