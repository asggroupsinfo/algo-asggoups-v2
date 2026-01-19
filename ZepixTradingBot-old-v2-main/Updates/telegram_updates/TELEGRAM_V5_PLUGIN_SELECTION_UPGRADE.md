# TELEGRAM V5 - PLUGIN SELECTION INTERCEPTOR SYSTEM

**Feature:** Plugin Selection Before Every Command  
**Priority:** CRITICAL  
**Status:** Missing from V5 - Must Implement  
**Created:** January 19, 2026

---

## PROBLEM STATEMENT (हिंदी में)

### Current Problem ❌

**User ka experience:**
```
User: /status भेजता है
Bot: Overall status दिखाता है (V3 + V6 mixed)
User: Confusing! Mujhe V3 ka status chahiye ya V6 ka?

User: /pause भेजता है  
Bot: Sab plugins pause kar deta hai
User: Galat! Main sirf V6 ko pause karna chahta tha!

User: /setlot भेजता है
Bot: Global lot size set ho jata hai
User: Nahi! Main sirf V3 ke liye lot size badhana chahta tha!
```

**Core Issue:**
- User ko pata nahi ki command **KON SE PLUGIN** pe apply hoga
- V3 aur V6 dono control ek saath hote hain
- Alag alag control ka koi rasta nahi hai
- Har command **global** hai, plugin-specific nahi

### What User Needs ✅

**User chahta hai:**
```
User: /status bhejta hai

Bot: 🔌 SELECT PLUGIN
     [V3 Combined Logic]
     [V6 Price Action]
     [Both Plugins]

User: V3 pe click karta hai

Bot: 🔵 V3 COMBINED LOGIC STATUS
     Status: ✅ Running
     LOGIC1: ✅ | LOGIC2: ✅ | LOGIC3: ✅
     Trades Today: 5
     P&L: +$25.00
```

**Benefits:**
- ✅ User ko clear choice milta hai
- ✅ V3 aur V6 alag alag control hote hain  
- ✅ Koi confusion nahi
- ✅ Precise control

---

## SOLUTION DESIGN

### Plugin Selection Interceptor

**Concept:**
- Har command se **PEHLE** plugin selection screen dikha do
- User select kare: V3, V6, ya Both
- Uske baad command execute ho **selected plugin** pe

**Flow:**
```
User Command → Plugin Selection Screen → User Selects → Command Executes on Selected Plugin
```

### Example Flows

#### Flow 1: `/status` Command
```
1. User: /status
2. Bot: 🔌 Which plugin status?
        [V3 Combined] [V6 Price Action] [Both]
3. User clicks: V3 Combined
4. Bot: Shows V3-only status
5. User satisfied ✅
```

#### Flow 2: `/pause` Command
```
1. User: /pause
2. Bot: 🔌 Which plugin to pause?
        [V3 Combined] [V6 Price Action] [Both]
3. User clicks: V6 Price Action
4. Bot: ⏸️ V6 Price Action paused
        V3 Combined still running ✅
5. User satisfied ✅
```

#### Flow 3: `/setlot` Command
```
1. User: /setlot
2. Bot: 🔌 Set lot size for which plugin?
        [V3 Combined] [V6 Price Action] [Both]
3. User clicks: V3 Combined
4. Bot: 💼 V3 Lot Size
        Current: 0.01
        [0.01] [0.02] [0.03] [0.05]
5. User clicks: 0.02
6. Bot: ✅ V3 lot size = 0.02
        V6 lot size unchanged (0.01) ✅
```

#### Flow 4: `/positions` Command
```
1. User: /positions
2. Bot: 🔌 Show positions for which plugin?
        [V3 Combined] [V6 Price Action] [Both]
3. User clicks: V6 Price Action
4. Bot: Shows ONLY V6 positions
5. User: Perfect! ✅
```

---

## TECHNICAL IMPLEMENTATION

### Architecture

**Plugin Context Manager**
```python
class PluginContextManager:
    """
    Manages plugin selection context for each user session.
    Stores: Which plugin user selected for current command.
    """
    
    # User session storage
    _user_contexts = {}  # {chat_id: {plugin: 'v3', timestamp: ...}}
    
    @classmethod
    def set_plugin_context(cls, chat_id: int, plugin: str):
        """Set plugin context for user"""
        cls._user_contexts[chat_id] = {
            'plugin': plugin,  # 'v3', 'v6', 'both'
            'timestamp': datetime.now(),
            'expires_in': 300  # 5 minutes
        }
    
    @classmethod
    def get_plugin_context(cls, chat_id: int) -> str:
        """Get current plugin context for user"""
        if chat_id not in cls._user_contexts:
            return None
        
        context = cls._user_contexts[chat_id]
        
        # Check if expired
        if (datetime.now() - context['timestamp']).seconds > context['expires_in']:
            del cls._user_contexts[chat_id]
            return None
        
        return context['plugin']
    
    @classmethod
    def clear_plugin_context(cls, chat_id: int):
        """Clear plugin context after command execution"""
        if chat_id in cls._user_contexts:
            del cls._user_contexts[chat_id]
```

**Command Interceptor**
```python
class CommandInterceptor:
    """
    Intercepts all commands and shows plugin selection if needed.
    """
    
    # Commands that need plugin selection
    PLUGIN_AWARE_COMMANDS = [
        '/status', '/pause', '/resume', '/positions', '/pnl',
        '/setlot', '/risktier', '/chains', '/autonomous',
        '/logic1', '/logic2', '/logic3',
        '/tf15m', '/tf30m', '/tf1h', '/tf4h',
        # ... 95+ commands
    ]
    
    @classmethod
    def intercept_command(cls, command: str, chat_id: int, message: Dict) -> bool:
        """
        Intercept command and check if plugin selection needed.
        
        Returns:
            True if plugin selection shown (command paused)
            False if plugin already selected (command can proceed)
        """
        # Check if this command needs plugin selection
        if command not in cls.PLUGIN_AWARE_COMMANDS:
            return False  # Let command execute normally
        
        # Check if user already selected plugin
        plugin_context = PluginContextManager.get_plugin_context(chat_id)
        if plugin_context:
            return False  # Plugin selected, command can proceed
        
        # Show plugin selection screen
        cls._show_plugin_selection(command, chat_id)
        return True  # Command paused, waiting for selection
    
    @classmethod
    def _show_plugin_selection(cls, command: str, chat_id: int):
        """Show plugin selection screen"""
        message = (
            f"🔌 <b>SELECT PLUGIN FOR {command.upper()}</b>\n\n"
            f"Choose which plugin to control:\n"
        )
        
        keyboard = {
            'inline_keyboard': [
                [
                    {'text': '🔵 V3 Combined Logic', 'callback_data': f'plugin_select_v3_{command}'},
                    {'text': '🟢 V6 Price Action', 'callback_data': f'plugin_select_v6_{command}'}
                ],
                [
                    {'text': '🔷 Both Plugins', 'callback_data': f'plugin_select_both_{command}'}
                ],
                [
                    {'text': '❌ Cancel', 'callback_data': 'plugin_select_cancel'}
                ]
            ]
        }
        
        # Send selection screen
        bot.send_message(chat_id, message, reply_markup=keyboard)
```

**Callback Handler**
```python
def handle_plugin_selection_callback(callback_data: str, chat_id: int, message_id: int):
    """
    Handle plugin selection callback.
    
    Callback format: plugin_select_v3_/status
    """
    parts = callback_data.split('_')
    
    if parts[2] == 'cancel':
        bot.edit_message(chat_id, message_id, "❌ Command cancelled")
        return
    
    plugin = parts[2]  # 'v3', 'v6', 'both'
    command = '_'.join(parts[3:])  # '/status'
    
    # Store plugin context
    PluginContextManager.set_plugin_context(chat_id, plugin)
    
    # Edit message to show selection
    bot.edit_message(
        chat_id, 
        message_id, 
        f"✅ Plugin selected: {plugin.upper()}\nExecuting {command}..."
    )
    
    # Execute command with plugin context
    controller_bot.execute_command(command, chat_id, plugin_context=plugin)
    
    # Clear context after execution
    PluginContextManager.clear_plugin_context(chat_id)
```

**Updated Command Handler**
```python
def handle_status(self, message: Dict = None, plugin_context: str = None) -> Optional[int]:
    """
    Enhanced status command with plugin filtering.
    
    Args:
        plugin_context: 'v3', 'v6', 'both' from plugin selection
    """
    
    # If no plugin context (shouldn't happen with interceptor), default to both
    if not plugin_context:
        plugin_context = 'both'
    
    # Get data based on plugin context
    if plugin_context == 'v3':
        # Show V3 only
        message = self._format_v3_status()
        
    elif plugin_context == 'v6':
        # Show V6 only
        message = self._format_v6_status()
        
    else:  # both
        # Show V3 + V6
        message = self._format_combined_status()
    
    return self.send_message(message)
```

---

## FILES TO CREATE/MODIFY

### New Files (5)

1. **`plugin_context_manager.py`**
   - Location: `Trading_Bot/src/telegram/`
   - Purpose: Store plugin selection context per user
   - Lines: ~150

2. **`command_interceptor.py`**
   - Location: `Trading_Bot/src/telegram/`
   - Purpose: Intercept commands and show plugin selection
   - Lines: ~200

3. **`plugin_selection_menu_builder.py`**
   - Location: `Trading_Bot/src/telegram/`
   - Purpose: Build plugin selection screens
   - Lines: ~100

4. **`test_plugin_selection.py`**
   - Location: `tests/telegram/`
   - Purpose: Test plugin selection system
   - Lines: ~300

5. **`PLUGIN_SELECTION_INTEGRATION_GUIDE.md`**
   - Location: `Important_Doc_Trading_Bot/05_Unsorted/developer_notes/`
   - Purpose: Developer guide for plugin selection
   - Lines: ~500

### Files to Modify (95+)

**All command handlers in `controller_bot.py`:**
- `handle_status()` - Add plugin_context parameter
- `handle_pause()` - Add plugin_context parameter
- `handle_resume()` - Add plugin_context parameter
- `handle_positions()` - Add plugin_context parameter
- `handle_pnl()` - Add plugin_context parameter
- `handle_setlot()` - Add plugin_context parameter
- `handle_risktier()` - Add plugin_context parameter
- `handle_chains()` - Add plugin_context parameter
- ... (87+ more handlers)

**Pattern for each handler:**
```python
# BEFORE (without plugin selection):
def handle_status(self, message: Dict = None) -> Optional[int]:
    # Show combined status
    pass

# AFTER (with plugin selection):
def handle_status(self, message: Dict = None, plugin_context: str = None) -> Optional[int]:
    # Filter by plugin_context
    if plugin_context == 'v3':
        # V3 only
    elif plugin_context == 'v6':
        # V6 only
    else:
        # Both
    pass
```

---

## INTEGRATION WITH EXISTING PHASES

### Phase 1: V6 Notifications
**No changes needed** - Notifications work independently

### Phase 2: V6 Timeframe Menu
**Integration point:**
- Plugin selection shows: [V3 Combined] [V6 Price Action]
- If V6 selected → Show V6 timeframe menu (15M/30M/1H/4H)
- Seamless integration

### Phase 3: Priority Commands
**Major integration:**
- ALL 20 priority commands get plugin selection
- `/status`, `/positions`, `/pnl`, etc. now plugin-aware
- This makes Phase 3 complete

### Phase 4: Analytics Interface
**Integration:**
- Analytics commands also get plugin selection
- `/daily v3`, `/weekly v6`, `/compare` work better

### Phase 5: Notification Filtering
**No changes needed** - Works independently

### Phase 6: Menu Callbacks
**Integration:**
- All menu callbacks also check plugin context
- Consistent experience

---

## IMPLEMENTATION PLAN

### Week 0 (Before Phase 1): Plugin Selection System
**Priority:** CRITICAL - Must implement FIRST  
**Effort:** 24 hours  
**Timeline:** 3 days

**Day 1 (8 hours):**
- [ ] Create `plugin_context_manager.py`
- [ ] Create `command_interceptor.py`
- [ ] Create `plugin_selection_menu_builder.py`
- [ ] Unit tests for context manager

**Day 2 (8 hours):**
- [ ] Integrate interceptor into `controller_bot.py`
- [ ] Update 20 priority commands with `plugin_context` parameter
- [ ] Test plugin selection flow end-to-end

**Day 3 (8 hours):**
- [ ] Update remaining 75 commands
- [ ] Integration testing
- [ ] Documentation

**Dependencies:**
- None - can start immediately
- Blocks: Phase 3 (needs this for plugin-aware commands)

### Integration Checklist

**Before Phase 1 starts:**
- [x] Plugin Selection System implemented
- [x] All command handlers updated
- [x] Integration tests passing
- [x] Documentation complete

**During Phase 3:**
- Use existing plugin selection for all new commands
- No additional work needed

---

## USER FLOWS

### Flow 1: Pause Specific Plugin

**Scenario:** User wants to pause V6 but keep V3 running

```
👤 User: /pause

🤖 Bot: 🔌 SELECT PLUGIN TO PAUSE
        [V3 Combined Logic]
        [V6 Price Action]
        [Both Plugins]

👤 User: Clicks "V6 Price Action"

🤖 Bot: ✅ Plugin selected: V6 PRICE ACTION
        Executing /pause...
        
        ⏸️ V6 PRICE ACTION PAUSED
        
        All 4 timeframes paused:
        ├─ 15M: ⏸️ Paused
        ├─ 30M: ⏸️ Paused
        ├─ 1H: ⏸️ Paused
        └─ 4H: ⏸️ Paused
        
        V3 Combined Logic: ✅ Still Running
        
        [Resume V6] [Pause V3 Too] [Back]

👤 User: Happy! V3 still trading, V6 paused ✅
```

### Flow 2: Check V3 Positions Only

**Scenario:** User has both V3 and V6 trades, wants to see V3 only

```
👤 User: /positions

🤖 Bot: 🔌 SHOW POSITIONS FOR WHICH PLUGIN?
        [V3 Combined Logic]
        [V6 Price Action]
        [Both Plugins]

👤 User: Clicks "V3 Combined Logic"

🤖 Bot: ✅ Plugin selected: V3 COMBINED LOGIC
        Executing /positions...
        
        🔵 V3 COMBINED LOGIC - OPEN POSITIONS (2)
        
        #1: EURUSD BUY
        ├─ Plugin: V3-LOGIC1 (5m)
        ├─ Entry: 1.08450
        ├─ P&L: +$5.00 🟢
        └─ SL: 1.08350 | TP: 1.08650
        
        #2: GBPUSD SELL
        ├─ Plugin: V3-LOGIC2 (15m)
        ├─ Entry: 1.26800
        ├─ P&L: +$10.00 🟢
        └─ SL: 1.26900 | TP: 1.26600
        
        💰 Total V3 P&L: +$15.00
        
        [V6 Positions] [Close All V3] [Back]

👤 User: Perfect! Only V3 positions shown ✅
```

### Flow 3: Set Different Lot Sizes

**Scenario:** User wants V3 = 0.01 lots, V6 = 0.02 lots

```
Step 1: Set V3 Lot Size
👤 User: /setlot

🤖 Bot: 🔌 SET LOT SIZE FOR WHICH PLUGIN?
        [V3 Combined Logic]
        [V6 Price Action]
        [Both Plugins]

👤 User: Clicks "V3 Combined Logic"

🤖 Bot: 💼 V3 COMBINED LOGIC - LOT SIZE
        Current: 0.01 lots
        
        [0.01] [0.02] [0.03] [0.05]
        [0.10] [0.20] [Custom]

👤 User: Clicks "0.01" (keep same)

🤖 Bot: ✅ V3 lot size = 0.01 lots

---

Step 2: Set V6 Lot Size
👤 User: /setlot

🤖 Bot: 🔌 SET LOT SIZE FOR WHICH PLUGIN?
        [V3 Combined Logic]
        [V6 Price Action]
        [Both Plugins]

👤 User: Clicks "V6 Price Action"

🤖 Bot: 💼 V6 PRICE ACTION - LOT SIZE
        Current: 0.01 lots
        
        [0.01] [0.02] [0.03] [0.05]
        [0.10] [0.20] [Custom]

👤 User: Clicks "0.02"

🤖 Bot: ✅ V6 lot size = 0.02 lots

---

Result:
✅ V3: 0.01 lots
✅ V6: 0.02 lots
✅ Different lot sizes for different plugins!
```

---

## COMMAND CATEGORIES & PLUGIN SELECTION

### Always Need Plugin Selection (95 commands)

**Trading Control (6):**
- `/pause`, `/resume`, `/status`, `/trades`, `/signal_status`, `/simulation_mode`

**Performance (6):**
- `/performance`, `/stats`, `/performance_report`, `/pair_report`, `/strategy_report`, `/chains`

**Plugin Control (10):**
- `/plugins`, `/enable`, `/disable`, `/v3`, `/v6`, `/upgrade`, `/rollback`, `/shadow`, `/compare`, `/plugin`

**Position Management (8):**
- `/positions`, `/close`, `/closeall`, `/trade`, `/buy`, `/sell`, `/orders`, `/history`

**Risk Management (12):**
- `/risk`, `/setlot`, `/setsl`, `/settp`, `/dailylimit`, `/maxloss`, `/maxprofit`, `/risktier`, `/slsystem`, `/trailsl`, `/breakeven`, `/protection`

**Re-entry System (14):**
- `/reentry`, `/slhunt`, `/tpcontinue`, `/recovery`, `/cooldown`, `/chains`, `/autonomous`, `/chainlimit`, `/maxrecovery`, `/reentry_enable`, `/reentry_disable`, `/reentry_config`, `/reentry_status`, `/reentry_history`

**Profit Booking (16):**
- `/profit`, `/booking`, `/levels`, `/partial`, `/orderb`, `/dualorder`, `/pb_enable`, `/pb_disable`, `/pb_config`, `/pb_chains`, `/pb_history`, `/pb_stats`, `/pb_multiplier`, `/pb_tier1`, `/pb_tier2`, `/pb_tier3`

**Timeframe Control (8):**
- `/timeframe`, `/tf1m`, `/tf5m`, `/tf15m`, `/tf1h`, `/tf4h`, `/tf1d`, `/trends`

**Analytics (8):**
- `/analytics`, `/performance`, `/daily`, `/weekly`, `/monthly`, `/report`, `/winrate`, `/drawdown`

**Session Management (6):**
- `/session`, `/london`, `/newyork`, `/tokyo`, `/sydney`, `/overlap`

**Strategy Control (8):**
- `/logic1`, `/logic2`, `/logic3`, `/signals`, `/filter`, `/entry`, `/exit`, `/conditions`

### Never Need Plugin Selection (10 commands)

**System Commands:**
- `/start` - Shows main menu
- `/help` - Shows help
- `/health` - System health (all plugins)
- `/version` - Bot version
- `/config` - Configuration menu
- `/balance` - Account balance (global)
- `/margin` - Margin info (global)
- `/price` - Current prices
- `/spread` - Current spreads
- `/notifications` - Notification settings

---

## BENEFITS SUMMARY

### For Users ✅

1. **Clear Control:**
   - Always know which plugin being controlled
   - No confusion between V3 and V6
   - Precise command execution

2. **Flexibility:**
   - Can pause V6, keep V3 running
   - Can set different lot sizes per plugin
   - Can check V3 performance separately

3. **Safety:**
   - Won't accidentally affect wrong plugin
   - Confirmation before action
   - Clear visual feedback

4. **Better UX:**
   - Intuitive selection screen
   - Consistent across all commands
   - Quick selection (2 clicks)

### For Developers ✅

1. **Clean Architecture:**
   - Separation of concerns
   - Plugin context managed centrally
   - Easy to add new plugins

2. **Maintainable:**
   - Single interceptor for all commands
   - Consistent pattern
   - Easy to test

3. **Extensible:**
   - Can add new plugins easily
   - Can add new commands easily
   - Plugin-agnostic design

---

## TESTING PLAN

### Unit Tests (50+ tests)

**PluginContextManager:**
- `test_set_plugin_context()` - Set context
- `test_get_plugin_context()` - Get context
- `test_context_expiry()` - 5-minute expiry
- `test_clear_context()` - Clear after use
- `test_multiple_users()` - Different users, different contexts

**CommandInterceptor:**
- `test_intercept_plugin_aware_command()` - Intercepts correctly
- `test_skip_non_plugin_command()` - Skips /start, /help
- `test_plugin_already_selected()` - Doesn't show selection if already selected
- `test_selection_screen_format()` - Correct buttons
- `test_callback_data_format()` - Correct callback data

**Command Handlers:**
- `test_status_v3_only()` - V3 context → V3 status only
- `test_status_v6_only()` - V6 context → V6 status only
- `test_status_both()` - Both context → Combined status
- `test_pause_v3_only()` - Pauses only V3
- `test_pause_v6_only()` - Pauses only V6
- ... (40+ more handler tests)

### Integration Tests (20+ scenarios)

1. User sends `/status` → Selection shown → Selects V3 → V3 status shown
2. User sends `/pause` → Selection shown → Selects V6 → V6 paused, V3 running
3. User sends `/setlot` → Selection shown → Selects V3 → V3 lot size changed, V6 unchanged
4. User sends `/positions` → Selection shown → Selects V6 → Only V6 positions shown
5. User sends `/status` twice in 5 min → Second time no selection (context reused)
6. User waits 6 min → Sends `/status` → Selection shown again (context expired)
7. Multiple users → Each has independent context
8. User selects "Cancel" → Command cancelled, no execution
9. User selects "Both" → Shows combined data
10. User sends `/start` → No selection shown (excluded command)

### End-to-End Test

```
1. User sends /status
2. Bot shows plugin selection
3. User selects V3
4. Bot shows V3-only status
5. Context stored (5 min)

6. User sends /pause (within 5 min)
7. Bot shows plugin selection (new command)
8. User selects V6
9. Bot pauses V6
10. V3 still running ✅

11. User sends /positions
12. Bot shows plugin selection
13. User selects Both
14. Bot shows V3 + V6 positions ✅

15. User waits 6 minutes
16. User sends /status
17. Bot shows plugin selection (context expired)
18. User selects V6
19. Bot shows V6-only status ✅

All tests pass ✅
```

---

## ROLLOUT PLAN

### Week 0: Plugin Selection Implementation
**Before Phase 1 starts**

**Day 1:**
- [ ] Create PluginContextManager
- [ ] Create CommandInterceptor
- [ ] Unit tests

**Day 2:**
- [ ] Integrate into controller_bot.py
- [ ] Update 20 priority commands
- [ ] Integration tests

**Day 3:**
- [ ] Update remaining 75 commands
- [ ] Documentation
- [ ] End-to-end testing

### Beta Testing
**Parallel with Phase 1 beta**

- Deploy to 2-3 beta users
- Collect feedback on selection UX
- Measure: How many clicks to complete command?
- Target: 3 clicks (command → selection → confirmation)

### Production Rollout
**With Phase 1 production**

- Enable for all users
- Monitor usage patterns
- Track: Which selection most used (V3? V6? Both?)
- Optimize based on data

---

## SUCCESS CRITERIA

### Must Have ✅
- [ ] Plugin selection shown for all 95 plugin-aware commands
- [ ] Selection screen has 3 options: V3, V6, Both
- [ ] Context stored for 5 minutes
- [ ] Commands execute ONLY on selected plugin
- [ ] V3 and V6 can be controlled independently
- [ ] No confusion about which plugin is being controlled

### Should Have 📋
- [ ] Selection screen loads <1 second
- [ ] Context expiry works correctly
- [ ] Multiple users have independent contexts
- [ ] Cancel option works
- [ ] "Both" option shows combined data

### Nice to Have 🎁
- [ ] Remember user's last selection per command type
- [ ] Quick toggle: "Use last selection"
- [ ] Keyboard shortcuts: "1" for V3, "2" for V6
- [ ] Voice confirmation: "V3 selected"

---

## ALTERNATIVES CONSIDERED

### Alternative 1: No Plugin Selection (Current State)
**Pros:** Simple  
**Cons:** Confusing, no control  
**Verdict:** ❌ Rejected - Poor UX

### Alternative 2: Separate Commands for V3/V6
**Example:** `/status_v3`, `/status_v6`, `/pause_v3`, `/pause_v6`  
**Pros:** No selection needed  
**Cons:** 190 commands instead of 95, cluttered  
**Verdict:** ❌ Rejected - Too many commands

### Alternative 3: Global Plugin Mode Toggle
**Example:** User sets "V3 Mode" globally, all commands apply to V3  
**Pros:** Set once, forget  
**Cons:** Dangerous (forgot which mode), inflexible  
**Verdict:** ❌ Rejected - Safety concern

### Alternative 4: Plugin Selection Interceptor (Chosen)
**Pros:** 
- Clear selection per command
- Flexible (can switch easily)
- Safe (always know what's affected)
- Context reuse (5 min expiry)

**Cons:**
- Extra click per command

**Verdict:** ✅ SELECTED - Best balance of safety and UX

---

## FUTURE ENHANCEMENTS

### Phase 2: Smart Context
- Remember user's preference per command
- Example: User always selects V3 for `/status`, V6 for `/positions`
- After 10 usages, auto-select based on pattern
- Still show selection, but pre-select most likely choice

### Phase 3: Voice Commands
- "Status for V3"
- "Pause V6"
- "Positions for both"
- Voice selection parsing

### Phase 4: Bulk Commands
- "Pause all except V6-1H"
- "Enable all V6 timeframes"
- "Set lot size 0.02 for all V6"

---

## FINAL SUMMARY (हिंदी में)

### समस्या (Problem) ❌
- Telegram में plugin selection नहीं है
- User को पता नहीं कि कौन सा plugin control कर रहा है
- V3 और V6 दोनों साथ में control होते हैं
- Galat plugin affect हो सकता है

### समाधान (Solution) ✅
- हर menu command से पहले plugin selection screen दिखा दो
- User choose करे: V3, V6, या Both
- Command execute हो **selected plugin** पे ही
- 5 minute के लिए context save रहे (fast re-use)

### फायदे (Benefits) 🎯
1. **साफ कंट्रोल:** User को हमेशा पता कि कौन सा plugin affect हो रहा
2. **लचीलापन:** V3 और V6 को अलग अलग control कर सकते हैं
3. **सुरक्षा:** गलत plugin affect नहीं होगा
4. **बेहतर UX:** Consistent, intuitive, safe

### Implementation 🔧
- **5 new files:** Context manager, Interceptor, Menu builder, Tests, Docs
- **95+ command handlers update:** Add `plugin_context` parameter
- **3 days effort:** 24 hours total
- **Before Phase 1:** Must implement first (critical dependency)

### Status 🚨
**CRITICAL MISSING PIECE** in V5 architecture!  
Without this, V5 Hybrid Architecture incomplete.  
User cannot properly control V3 vs V6.

**Priority:** HIGHEST  
**Implement:** IMMEDIATELY (Week 0, before Phase 1)

---

## DOCUMENT VERSION

**Version:** 1.0  
**Created:** January 19, 2026  
**Status:** Ready for Implementation  
**Priority:** CRITICAL (Must implement before Phase 1)

---

**Related Documents:**
- [00_MASTER_PLAN.md](00_MASTER_PLAN.md) - Overall V5 upgrade plan
- [02_V6_TIMEFRAME_MENU_PLAN.md](02_V6_TIMEFRAME_MENU_PLAN.md) - V6 submenu (integrates with this)
- [03_PRIORITY_COMMAND_HANDLERS_PLAN.md](03_PRIORITY_COMMAND_HANDLERS_PLAN.md) - Commands that need this

---

---

## ⚠️ DEVELOPER NOTE - IMPORTANT

**Bot Source Code Location:**  
`C:\Users\Ansh Shivaay Gupta\Downloads\ZepixTradingBot-New-v1\ZepixTradingBot-old-v2-main\Trading_Bot`

### Implementation Guidelines:

> ⚠️ **This is a Planning & Research Document - DO NOT Apply Blindly!**

**Implementation Process:**

1. **First, Complete Scan of the Bot**
   - Analyze the complete bot code
   - Understand the current architecture
   - Review existing implementations

2. **Map Ideas According to the Bot**
   - Check how the ideas given here will be implemented in the bot
   - Identify dependencies
   - Look for conflicts

3. **Create New Plan According to the Bot**
   - Create a new implementation plan according to the bot's current state
   - Adapt ideas that don't directly fit

4. **Make Improvements (Full Freedom)**
   - You have full freedom to improve the ideas
   - Use a better approach if available
   - Optimize according to the bot's architecture

5. **Then Implement**
   - Implement only after planning is complete

### Critical Rules:

| Rule | Description |
|------|-------------|
| ✅ **Idea Must Be Fully Implemented** | The core idea/concept must be fully implemented |
| ✅ **Improvements Allowed** | You can improve the implementation |
| ❌ **Idea Should Not Change** | The core concept of the idea must remain the same |
| ❌ **Do Not Apply Blindly** | First scan, plan, then implement |

**Remember:** This document provides ideas & possibilities - the final implementation will depend on the bot's actual architecture.

---

**END OF DOCUMENT**