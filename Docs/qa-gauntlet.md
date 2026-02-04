# Quality Assurance: The Gauntlet

**Purpose:** Maintain stability as we scale features. All tests must pass before production deployment.

## Test Suite

### 1. The Empty Inbox
**Trigger Condition:**  
Query `newer_than:1m` (or nonsense subject that returns no results)

**Success Criteria:**
- UI shows "No new newsletters found" message
- App does NOT crash or show 500 error
- Graceful handling with user-friendly message

**Test Command:**
```bash
# Set time_window_hours to 1 minute in settings
# Or use invalid source domain
```

---

### 2. Data Overload
**Trigger Condition:**  
Query `category:updates + newer_than:7d` (50+ items)

**Success Criteria:**
1. LLM successfully generates JSON (Truncation logic works)
2. Audio successfully generates (Chunking logic works)
3. No timeout errors
4. Response time acceptable (<60s)

**Test Command:**
```bash
# Configure settings with broad sources and 7-day window
# Ensure multiple newsletters are in inbox
```

---

### 3. Malformed Content
**Trigger Condition:**  
Forward an email with complex tables/emojis/special characters

**Success Criteria:**
- JSON parser finds the payload via Regex
- `sanitize_for_llm()` strips control characters
- No parsing errors
- Content is readable in output

**Test Command:**
```bash
# Send test email with:
# - Complex HTML tables
# - Emojis (🎉 📊 💰)
# - Special characters (© ® ™)
# - Control characters
```

---

### 4. The Impatient User
**Trigger Condition:**  
Click "Fetch" button repeatedly while loading

**Success Criteria:**
- Button is disabled (`disabled={isFetching}`)
- No double-submission to backend
- No duplicate API calls
- No race conditions

**Test Command:**
```bash
# Rapidly click "Refresh" button 10+ times
# Monitor network tab for duplicate requests
```

---

## Pre-Deployment Checklist

Before deploying any new feature or change:

- [ ] All 4 Gauntlet tests pass
- [ ] Error handling tested for edge cases
- [ ] Cache invalidation verified
- [ ] Database migrations tested (if applicable)
- [ ] Environment variables configured
- [ ] Logs reviewed for errors

## Continuous Testing

These tests should be run:
- Before every production deployment
- After major feature additions
- When changing core pipeline logic
- Weekly regression testing

## Known Issues

### Red Flag Mode
- **Status:** NOT IMPLEMENTED - Backend logic does not exist, Frontend toggle UI-only
- **Action:** Need to implement backend Red Flag detection in LLM prompt
- **Impact:** Feature deferred to Phase 6 Week 11
- **Implementation Plan:**
  1. Add `red_flag_mode: boolean` to user settings
  2. Modify LLM prompt to identify risk indicators when enabled
  3. Add `is_red_flag: boolean` to story groups in JSON output
  4. Fix frontend toggle in Settings Modal
  5. Display Red Flag stories with prominent badge/indicator
