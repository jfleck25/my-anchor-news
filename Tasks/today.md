# Today's Tasks - February 4, 2026

## 🎯 Task 1: Enhance Executive Summary Export (Quick Win)
**Priority:** High | **Estimated Time:** 1-2 hours | **Status:** Ready to start

**Current State:**
- Copy to clipboard functionality exists
- Basic text formatting works
- Missing: PDF export option, better email formatting

**What to Do:**
1. Enhance `handleCopySummary` with better formatting (email-friendly)
2. Add PDF download option using `jsPDF` or `html2pdf`
3. Include professional header with date and branding
4. Test on mobile and desktop

**Why This Matters:**
- Quick win for "Briefing Ben" persona
- Sales pitch: "Generate your morning team email in 1 click"
- Low risk, high value

**Files to Modify:**
- `index.html` - Enhance copy function, add PDF button
- Consider adding CDN link for PDF library

---

## 🚩 Task 2: Implement Red Flag Mode Frontend
**Priority:** High | **Estimated Time:** 2-3 hours | **Status:** Backend ready, frontend needs work

**Current State:**
- Backend filtering logic mentioned as "ready" but not visible in code
- Frontend toggle exists but buggy (per task notes)
- Need to verify backend implementation first

**What to Do:**
1. **First:** Verify/add backend Red Flag filtering logic
   - Add settings field for `red_flag_mode: boolean`
   - Modify LLM prompt to identify risk indicators
   - Filter/flag stories with risk keywords
2. **Then:** Fix frontend toggle in Settings Modal
   - Ensure state management works correctly
   - Add visual indicator for Red Flag stories
   - Display Red Flag stories prominently in UI

**Why This Matters:**
- Key differentiator for finance users
- High willingness-to-pay feature
- Currently blocked/deferred

**Files to Modify:**
- `main.py` - Add Red Flag logic to analysis prompt
- `index.html` - Fix Settings Modal toggle, add Red Flag UI

---

## ⭐ Task 3: Verify & Enhance Source Prioritization Display
**Priority:** Medium | **Estimated Time:** 1 hour | **Status:** Backend done, frontend needs verification

**Current State:**
- Backend already processes priority sources first
- Settings UI allows starring sources
- Need to verify frontend displays priority sources prominently

**What to Do:**
1. Verify priority sources appear first in story groups
2. Add visual indicator (badge/icon) for priority source stories
3. Ensure starred sources in settings sync with priority logic
4. Test with multiple sources (some starred, some not)

**Why This Matters:**
- Enhances existing functionality
- Improves user experience
- Quick polish task

**Files to Modify:**
- `index.html` - Add priority badges to story display
- Verify settings sync works correctly

---

## Recommendation: Start with Task 1

**Reasoning:**
- Lowest risk, highest immediate value
- Can be completed quickly
- Unblocks sales/marketing messaging
- Builds momentum for the day

Then move to Task 2 (Red Flag Mode) if time permits, or Task 3 for a quick polish.
