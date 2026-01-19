# TELEGRAM V5 UPGRADE - IMPLEMENTATION ROADMAP

**Project:** ZepixTradingBot V5 Telegram System Complete Upgrade  
**Roadmap Version:** 1.0  
**Created:** January 19, 2026  
**Timeline:** 10 Weeks (Jan 20 - March 30, 2026)

---

## WEEK-BY-WEEK BREAKDOWN

### WEEK 1-2: Phase 1 - V6 Notification System
**Dates:** Jan 20 - Feb 2  
**Effort:** 16 hours  
**Owner:** Lead Developer

**Deliverables:**
- [ ] V6 entry alert with timeframe identification
- [ ] V6 exit alert with pattern details
- [ ] Trend Pulse detection notifications
- [ ] Shadow mode trade alerts
- [ ] Price Action pattern notifications
- [ ] Unit tests (11 test cases)
- [ ] Integration with notification router

**Files Modified:**
- `Trading_Bot/src/telegram/notification_bot.py` (add 5 new methods)
- `Trading_Bot/src/telegram/notification_router.py` (update routing)
- `tests/telegram/test_notification_bot_v6.py` (new file)

**Success Criteria:**
- V6 notifications visually distinct from V3
- Timeframe (15M/30M/1H/4H) clearly shown
- All unit tests passing
- No errors in production

**Risks:**
- V6 alert payload format might change (Mitigation: Version payload format)
- Notification spam (Mitigation: Phase 5 filtering system)

---

### WEEK 2-3: Phase 2 - V6 Timeframe Plugin Menu
**Dates:** Feb 2 - Feb 16  
**Effort:** 20 hours  
**Owner:** Lead Developer

**Deliverables:**
- [ ] V6 submenu showing 4 timeframes
- [ ] Individual timeframe enable/disable
- [ ] Per-timeframe configuration menus
- [ ] Performance comparison view
- [ ] Bulk actions (Enable All, Disable All)
- [ ] Fix `menu_v6_settings` callback
- [ ] Unit tests (12 test cases)
- [ ] Integration tests

**Files Modified:**
- `Trading_Bot/src/telegram/v6_timeframe_menu_builder.py` (new file)
- `Trading_Bot/src/telegram/plugin_control_menu.py` (wire callback)
- `tests/telegram/test_v6_timeframe_menu.py` (new file)

**Success Criteria:**
- Can control each V6 timeframe independently
- No bot restart needed for changes
- Configuration persists across restarts
- Performance metrics display correctly

**Risks:**
- Plugin manager might not support individual timeframe control (Mitigation: Extend plugin manager API)
- Database queries might be slow (Mitigation: Add indexes, caching)

---

### WEEK 3-4: Phase 3 - Priority Command Handlers
**Dates:** Feb 16 - Mar 2  
**Effort:** 32 hours  
**Owner:** Lead Developer

**Deliverables:**

**Tier 1 (Week 3):**
- [ ] Enhanced `/status` with V3 vs V6 breakdown
- [ ] Plugin-aware `/positions` command
- [ ] Per-plugin `/pnl` breakdown
- [ ] `/chains` re-entry chain status
- [ ] `/daily` analytics trigger
- [ ] `/weekly` analytics trigger
- [ ] `/compare` V3 vs V6 comparison
- [ ] `/setlot` lot size control
- [ ] `/risktier` risk tier selection
- [ ] `/autonomous` re-entry toggle

**Tier 2 (Week 4):**
- [ ] `/tf15m`, `/tf30m`, `/tf1h`, `/tf4h` timeframe toggles
- [ ] `/slhunt` SL Hunt status
- [ ] `/tpcontinue` TP Continuation status
- [ ] `/reentry` re-entry overview
- [ ] `/levels` profit booking status
- [ ] `/shadow` shadow mode comparison
- [ ] `/trends` multi-timeframe trends

**Files Modified:**
- `Trading_Bot/src/telegram/controller_bot.py` (add 20+ handlers)
- `Trading_Bot/src/telegram/command_registry.py` (register commands)
- `tests/telegram/test_priority_commands.py` (new file, 50+ tests)

**Success Criteria:**
- All 20 priority commands functional
- Commands are plugin-aware
- No delegation to broken legacy bot
- All tests passing

**Risks:**
- Complex logic for chains/autonomous (Mitigation: Delegate to existing managers)
- Database query performance (Mitigation: Optimize queries, add pagination)

---

### WEEK 4-5: Phase 4 - Analytics Command Interface
**Dates:** Mar 2 - Mar 16  
**Effort:** 24 hours  
**Owner:** Lead Developer

**Deliverables:**
- [ ] Wire `/performance` command to Analytics Bot
- [ ] Wire `/daily`, `/weekly` commands
- [ ] Wire `/compare` command
- [ ] Interactive date range selection menu
- [ ] Plugin filtering (V3/V6/Specific Timeframe)
- [ ] Symbol filtering
- [ ] Export to CSV functionality
- [ ] V6 timeframe breakdown in reports

**Files Modified:**
- `Trading_Bot/src/telegram/analytics_bot.py` (add command handlers)
- `Trading_Bot/src/telegram/analytics_menu_builder.py` (new file)
- `Trading_Bot/src/telegram/command_registry.py` (register analytics commands)
- `tests/telegram/test_analytics_commands.py` (new file)

**Success Criteria:**
- On-demand analytics work
- Date range selection functional
- V6 timeframe breakdown shown
- No timeout errors
- CSV export works

**Risks:**
- Large datasets might timeout (Mitigation: Pagination, caching, loading indicators)
- Export file size limits (Mitigation: Compress, split large files)

---

### WEEK 5-6: Phase 5 - Notification Filtering System
**Dates:** Mar 16 - Mar 30  
**Effort:** 28 hours  
**Owner:** Lead Developer

**Deliverables:**
- [ ] Notification preferences menu
- [ ] Per-type notification toggles (50+ types)
- [ ] Per-plugin filtering (V3/V6)
- [ ] Quiet hours configuration
- [ ] Priority levels (Critical/Important/Info)
- [ ] `/notifications` command
- [ ] Quick presets (All On, Critical Only, etc.)
- [ ] Notification bundling (5-min window)
- [ ] Preferences persistence

**Files Modified:**
- `Trading_Bot/src/telegram/notification_preferences_menu.py` (new file)
- `Trading_Bot/src/telegram/notification_router.py` (update routing logic)
- `Trading_Bot/config/notification_preferences.json` (new file)
- `tests/telegram/test_notification_filtering.py` (new file)

**Success Criteria:**
- Users can toggle each notification type
- Plugin filtering works
- Quiet hours functional
- Settings persist across restarts
- Notification spam reduced

**Risks:**
- State management complexity (Mitigation: Use simple JSON file, validate on load)
- Preference conflicts (Mitigation: Clear defaults, validation rules)

---

### WEEK 6-7: Phase 6 - Menu Callback Wiring
**Dates:** Mar 30 - Apr 6  
**Effort:** 20 hours  
**Owner:** Lead Developer

**Deliverables:**
- [ ] Wire session menu callbacks
- [ ] Wire re-entry menu callbacks
- [ ] Wire fine-tune menu callbacks
- [ ] Fix all dead-end buttons
- [ ] Add "Back" navigation to all menus
- [ ] Complete callback handler coverage
- [ ] End-to-end menu flow testing

**Files Modified:**
- `Trading_Bot/src/telegram/controller_bot.py` (add callback routing)
- `Trading_Bot/src/telegram/session_menu_handler.py` (wire callbacks)
- `Trading_Bot/src/telegram/reentry_menu_handler.py` (if exists, wire callbacks)
- `Trading_Bot/src/telegram/finetune_menu_handler.py` (if exists, wire callbacks)
- `tests/telegram/test_menu_callbacks.py` (new file)

**Success Criteria:**
- 100% of menu buttons work
- No callback errors
- All orphaned handlers wired
- Complete menu navigation

**Risks:**
- Orphaned handlers might not exist (Mitigation: Document missing handlers, implement if critical)
- Complex callback routing (Mitigation: Use handler map pattern)

---

### WEEK 7: Integration Testing
**Dates:** Apr 6 - Apr 13  
**Effort:** 40 hours (full week)  
**Owner:** Lead Developer + QA

**Testing Tasks:**
- [ ] End-to-end testing of all 6 phases
- [ ] Regression testing (ensure V3 still works)
- [ ] Performance testing (1000+ trades, rapid clicks)
- [ ] Error recovery testing (network failures, API limits)
- [ ] Edge case testing (no data, invalid inputs)
- [ ] Cross-bot testing (Controller → Notification → Analytics)
- [ ] Database integrity testing
- [ ] Configuration migration testing

**Test Scenarios (100+ scenarios):**
1. V3 plugin enabled → All V3 features work
2. V6 plugin enabled → All V6 features work
3. Both plugins enabled → Distinct notifications, commands filter correctly
4. Enable V6 15M → Receive V6 15M entry alerts
5. Disable V6 1H → No new V6 1H entries, existing trades remain
6. Send `/status` → See V3 + V6 breakdown
7. Send `/positions v6` → Only V6 positions shown
8. Send `/compare` → V3 vs V6 metrics correct
9. Set notification filter V6 only → No V3 notifications received
10. Enable quiet hours → Critical notifications only during quiet hours

**Tools:**
- pytest for unit tests
- Selenium for bot interaction automation
- Custom test harness for Telegram API mocking
- Database snapshot/restore for repeatable tests

**Success Criteria:**
- All tests passing
- No critical bugs
- Performance acceptable (<2s command response)
- Error recovery works

---

### WEEK 8: Beta User Testing
**Dates:** Apr 13 - Apr 20  
**Effort:** 20 hours (monitoring + bug fixes)  
**Owner:** Lead Developer

**Beta Group:**
- 2-3 experienced users
- Daily check-ins
- Feedback collection
- Bug reporting channel (Telegram group)

**Testing Focus:**
- Real-world usage patterns
- Feature discovery (can users find new features?)
- UI/UX feedback
- Edge cases not covered in automated tests
- Performance under actual trading conditions

**Deliverables:**
- [ ] Beta user guide
- [ ] Feedback collection form
- [ ] Bug tracking sheet
- [ ] Daily bug fix releases
- [ ] User satisfaction survey

**Success Criteria:**
- No critical bugs reported
- >90% user satisfaction
- All reported bugs fixed within 24h
- Feature adoption rate >50%

**Rollback Plan:**
- If >5 critical bugs, disable new features
- Route to old system
- Fix issues, re-deploy to beta

---

### WEEK 9: Limited Production Rollout
**Dates:** Apr 20 - Apr 27  
**Effort:** 20 hours (monitoring)  
**Owner:** Lead Developer

**Rollout Strategy:**
- Enable for 50% of users (random selection)
- Feature flag system for gradual rollout
- Monitor error rates, usage metrics
- Daily performance reviews

**Monitoring Metrics:**
- Command usage frequency
- Notification delivery rate
- Error rate (<0.1% target)
- Response time (<2s target)
- User complaints (<5/day target)

**Deliverables:**
- [ ] Feature flag system
- [ ] Usage analytics dashboard
- [ ] Error monitoring alerts
- [ ] Daily performance reports
- [ ] Rollback procedure

**Success Criteria:**
- Error rate <0.1%
- No performance degradation
- User complaints <5/day
- Feature adoption increasing

**Rollback Triggers:**
- Error rate >1%
- Performance degradation >20%
- User complaints >10/day
- Critical bug discovered

---

### WEEK 10: Full Production Rollout
**Dates:** Apr 27 - May 4  
**Effort:** 10 hours (monitoring)  
**Owner:** Lead Developer

**Rollout Plan:**
- Enable for 100% of users
- Announcement message to all users
- User guide published
- Video tutorial (optional)
- Support monitoring

**Announcement Message:**
```
🎉 ZEPIX TRADING BOT V5 - NEW TELEGRAM FEATURES

We're excited to announce major Telegram upgrades:

🟢 V6 PRICE ACTION SUPPORT
├─ Individual timeframe control (15M, 30M, 1H, 4H)
├─ V6-specific notifications with pattern details
├─ Per-timeframe performance metrics
└─ Shadow mode tracking

📊 ENHANCED ANALYTICS
├─ On-demand reports (/daily, /weekly)
├─ V3 vs V6 performance comparison (/compare)
├─ Plugin-aware status and positions
└─ Export to CSV

🎯 NEW COMMANDS (20+ added)
├─ /chains - Re-entry chain status
├─ /setlot - Adjust lot sizes per plugin
├─ /risktier - Change risk settings
├─ /tf15m, /tf1h - Quick timeframe toggles
└─ [View Full List](/help)

🔔 NOTIFICATION CONTROLS
├─ Filter by plugin (V3/V6)
├─ Quiet hours
├─ Priority levels
└─ Per-type toggles (/notifications)

📚 Learn More: /help or visit docs.zepixbot.com
🐛 Report Issues: @ZepixSupport

Thank you for using Zepix Trading Bot! 🚀
```

**Deliverables:**
- [ ] Full user guide (PDF + Web)
- [ ] Command reference card
- [ ] Video tutorial (5-10 min)
- [ ] FAQ document
- [ ] Support team briefing

**Success Criteria:**
- All users have access
- User guide published
- Support team trained
- No critical issues

---

## MILESTONE TRACKER

| Milestone | Target Date | Status | Notes |
|-----------|-------------|--------|-------|
| Phase 1 Complete | Feb 2 | ⏳ Planned | V6 Notifications |
| Phase 2 Complete | Feb 16 | ⏳ Planned | V6 Timeframe Menu |
| Phase 3 Complete | Mar 2 | ⏳ Planned | Priority Commands |
| Phase 4 Complete | Mar 16 | ⏳ Planned | Analytics Interface |
| Phase 5 Complete | Mar 30 | ⏳ Planned | Notification Filtering |
| Phase 6 Complete | Apr 6 | ⏳ Planned | Menu Callback Wiring |
| Integration Tests Pass | Apr 13 | ⏳ Planned | All phases tested |
| Beta Testing Complete | Apr 20 | ⏳ Planned | User feedback collected |
| Limited Production | Apr 27 | ⏳ Planned | 50% rollout |
| Full Production | May 4 | ⏳ Planned | 100% rollout |

**Legend:**
- ⏳ Planned
- 🚧 In Progress
- ✅ Complete
- ⚠️ Delayed
- ❌ Blocked

---

## RESOURCE ALLOCATION

### Development Team
**Lead Developer:**
- Phases 1-6 implementation: 140 hours
- Integration testing: 40 hours
- Beta support: 20 hours
- Production support: 30 hours
- **Total: 230 hours (5.75 weeks full-time)**

**QA/Testing:**
- Manual testing: 20 hours
- Test case creation: 10 hours
- Beta user coordination: 10 hours
- **Total: 40 hours (1 week full-time)**

**Documentation:**
- User guide: 10 hours
- Developer docs: 6 hours
- Video tutorial: 4 hours
- **Total: 20 hours (0.5 weeks full-time)**

**Total Effort:** 290 hours (~7.25 weeks full-time equivalent)

---

## BUDGET ESTIMATE

### Development Costs
- Lead Developer: 230 hours × $50/hr = **$11,500**
- QA/Testing: 40 hours × $30/hr = **$1,200**
- Documentation: 20 hours × $40/hr = **$800**

**Total Labor:** $13,500

### Infrastructure Costs
- Test Telegram accounts: $0 (free)
- Test MT5 account: $0 (demo)
- Cloud storage (backups): $10/month × 3 = **$30**
- Monitoring tools: $20/month × 3 = **$60**

**Total Infrastructure:** $90

### Contingency (10%): $1,359

**GRAND TOTAL: ~$15,000**

---

## RISK REGISTER

| Risk | Probability | Impact | Mitigation | Owner |
|------|-------------|--------|------------|-------|
| Database performance issues | Medium | High | Add indexes, caching, pagination | Dev |
| Notification spam overwhelms users | High | Medium | Phase 5 filtering, bundling | Dev |
| V6 payload format changes | Low | High | Version payload, validation layer | Dev |
| Command complexity confuses users | Medium | Medium | Clear docs, tutorials, tooltips | Doc |
| Telegram API rate limits | Low | High | Rate limiter, notification bundling | Dev |
| Beta users find critical bug | Medium | High | Daily bug fixes, rollback plan | Dev |
| Production deployment issues | Low | Critical | Gradual rollout, feature flags, rollback | Dev |
| User adoption too slow | Medium | Low | Announcements, tutorials, support | PM |

---

## SUCCESS METRICS

### Quantitative KPIs
1. **Functionality Coverage:**
   - Command Implementation: 29% → **100%** (Target: Q1 2026)
   - Notification Implementation: 14% → **100%** (Target: Q1 2026)
   - V6 Feature Parity: 5% → **100%** (Target: Q1 2026)

2. **Performance Metrics:**
   - Command Response Time: **<2 seconds** (Target: Ongoing)
   - Notification Delivery: **<5 seconds** (Target: Ongoing)
   - Error Rate: **<0.1%** (Target: Ongoing)
   - Uptime: **>99.9%** (Target: Ongoing)

3. **User Engagement:**
   - Commands/Day: Baseline → **+300%** (Target: Month 1 post-launch)
   - Config File Edits: Baseline → **-80%** (Target: Month 1 post-launch)
   - Analytics Requests: 0 → **10+ per day** (Target: Month 1 post-launch)

### Qualitative KPIs
1. **User Satisfaction:**
   - User satisfaction score: **>90%** (Target: Month 1 post-launch)
   - User feedback: **>80% positive** (Target: Ongoing)
   - Support tickets: **<5 per week** (Target: Month 1 post-launch)

2. **Code Quality:**
   - Test coverage: 0% → **>80%** (Target: Before production)
   - Code documentation: 60% → **>95%** (Target: Before production)
   - Code review approval: **100%** (Target: Ongoing)

---

## DEPENDENCIES & BLOCKERS

### External Dependencies
1. **Telegram Bot API:** Stable, no changes expected
2. **MT5 Terminal:** No changes needed
3. **Database Schema:** V6 tables must exist (already exists)
4. **Pine Script Alerts:** V6 payload format documented (already done)

### Internal Dependencies
1. **Plugin Manager:** Must support individual V6 timeframe control
   - **Status:** Exists, may need extension
   - **Owner:** Backend Team
   - **Deadline:** Before Phase 2

2. **Database Indexes:** For performance queries
   - **Status:** Needed
   - **Owner:** Database Admin
   - **Deadline:** Before Phase 4

3. **Config System:** Per-timeframe settings support
   - **Status:** Exists, needs validation
   - **Owner:** Config Team
   - **Deadline:** Before Phase 2

### Current Blockers
- **NONE** - All critical dependencies resolved

---

## COMMUNICATION PLAN

### Weekly Status Updates
**Every Monday:**
- Progress report
- Blockers/Issues
- Plan for upcoming week
- Risk updates

**Stakeholders:**
- Project Manager
- Product Owner
- Development Team
- QA Team

### Milestone Reviews
**After each phase:**
- Demo of completed features
- Retrospective (what went well, what didn't)
- Adjust plan if needed

### User Communication
**Week 8 (Beta):**
- Beta user onboarding
- Daily check-ins
- Feedback collection

**Week 10 (Production):**
- Announcement to all users
- User guide published
- Support channel active

---

## POST-LAUNCH PLAN

### Week 11-14: Stabilization
- Bug fixes only
- Performance optimization
- User feedback collection
- Documentation updates

### Month 2-3: Optimization
- Refactor based on usage
- Add shortcuts for frequent commands
- Optimize slow queries
- Implement caching

### Quarter 2: Enhancements
- Voice alerts (if system ready)
- Multi-language support
- Advanced analytics (ML recommendations)
- Mobile app integration (if planned)

---

## APPROVAL & SIGN-OFF

**Document Prepared By:**  
AI Assistant | January 19, 2026

**Requires Approval From:**
- [ ] Project Manager
- [ ] Lead Developer
- [ ] Product Owner
- [ ] QA Lead

**Approved By:**
- Name: _________________ Date: _______
- Name: _________________ Date: _______

**Status:** ⏳ Awaiting Approval

---

## DOCUMENT VERSION HISTORY

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Jan 19, 2026 | AI Assistant | Initial roadmap created |
| | | | |
| | | | |

---

**End of Roadmap**

**Related Documents:**
- [00_MASTER_PLAN.md](00_MASTER_PLAN.md)
- [01_V6_NOTIFICATION_SYSTEM_PLAN.md](01_V6_NOTIFICATION_SYSTEM_PLAN.md)
- [02_V6_TIMEFRAME_MENU_PLAN.md](02_V6_TIMEFRAME_MENU_PLAN.md)
- [03_PRIORITY_COMMAND_HANDLERS_PLAN.md](03_PRIORITY_COMMAND_HANDLERS_PLAN.md)
- [04_PHASES_4_5_6_SUMMARY.md](04_PHASES_4_5_6_SUMMARY.md)

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