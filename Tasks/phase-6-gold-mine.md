# Phase 6: The "Gold Mine" (Weeks 11-12)

**Objective:** Capture the Finance/Strategy user (High WTP)  
**Theme:** Risk, Customization & Efficiency  
**Status:** In Progress

## Week 11

### Product Build: Red Flag Mode
**Status:** NOT STARTED  
**Priority:** High  
**Dependencies:** None

**Description:**  
Backend logic NOT implemented. Need to add Red Flag detection to LLM prompt and fix frontend toggle.

**Acceptance Criteria:**
- [ ] Add `red_flag_mode` setting to user settings (backend)
- [ ] Modify LLM prompt to identify risk indicators when `red_flag_mode` is enabled
- [ ] Add `is_red_flag: boolean` field to story groups in JSON output
- [ ] Fix frontend toggle in Settings Modal (state management)
- [ ] UI displays Red Flag stories prominently with badge/indicator
- [ ] Test with finance newsletters (WSJ, Bloomberg)

**Technical Notes:**
- Backend: Modify `analyze_news_with_llm()` to accept `red_flag_mode` parameter
- Backend: Update prompt to include risk detection instructions when enabled
- Backend: Risk keywords: "lawsuit", "investigation", "regulatory", "breach", "decline", "loss", "warning"
- Frontend: Fix Settings Modal toggle state management
- Frontend: Add visual indicator (red badge/icon) for Red Flag stories

---

### Product Build: Executive Summary Export
**Status:** NEXT  
**Priority:** High  
**Dependencies:** None

**Description:**  
Add "Copy to Clipboard" or "Download PDF" button that formats the analysis into a bulleted email summary.

**Acceptance Criteria:**
- [ ] "Copy Summary" button copies formatted text to clipboard
- [ ] Format includes date, story groups, and remaining stories
- [ ] Optional: PDF download with professional formatting
- [ ] Works on mobile and desktop

**Technical Notes:**
- Use `navigator.clipboard.writeText()` for copy functionality
- Consider libraries: `jsPDF` or `html2pdf` for PDF generation
- Format should be email-friendly (plain text or HTML)

**Sales Pitch:**  
"Generate your morning team email in 1 click."

---

### Commercialization: Direct Outreach
**Status:** Active  
**Priority:** High

**Description:**  
DM 50 finance pros on LinkedIn/Twitter: "I built an AI risk analyst that scans WSJ/Axios for you. Want a beta invite?"

**Tasks:**
- [ ] Create list of 50 finance professionals
- [ ] Draft personalized outreach message
- [ ] Set up tracking for responses
- [ ] Create beta invite system

**Success Metrics:**
- Response rate >10%
- Beta signups >5
- Feedback collection

---

## Week 12

### Product Build: Source Prioritization & Watchlists
**Status:** Planned  
**Priority:** Medium  
**Dependencies:** None

**Description:**  
Implement weighting logic to process "Starred" sources first and regex pre-filters for keywords.

**Acceptance Criteria:**
- [ ] Starred sources appear first in analysis
- [ ] Keyword watchlist filters emails before processing
- [ ] Settings UI allows starring/unstarring sources
- [ ] Performance: No significant slowdown with filtering

**Technical Notes:**
- Already have `priority_sources` in settings
- Need to implement sorting logic in `fetch_emails` route
- Keyword filtering already exists, verify it works correctly

---

### Commercialization: Waitlist Launch
**Status:** Planned  
**Priority:** Medium

**Description:**  
Deploy landing page highlighting "Red Flag Mode" to capture emails.

**Tasks:**
- [ ] Create landing page (separate from main app)
- [ ] Highlight Red Flag Mode as key feature
- [ ] Email capture form
- [ ] Integration with email service (Mailchimp/SendGrid)

**Success Metrics:**
- Email signups >100
- Conversion rate tracking

---

## Phase 6 Success Criteria

- [ ] Red Flag Mode functional and tested
- [ ] Executive Summary Export working
- [ ] Source prioritization implemented
- [ ] 5+ beta users from finance sector
- [ ] Waitlist launched with 50+ signups

## Notes

- Red Flag Mode is highest priority but currently blocked by frontend bug
- Executive Summary Export is quick win for "Briefing Ben" persona
- Source prioritization enhances existing functionality
