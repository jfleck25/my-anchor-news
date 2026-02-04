# Phase 8: Strategic Expansion & The "TV" Vision (Weeks 15-18+)

**Objective:** Enterprise & Deep Tech differentiation  
**Theme:** Integration & Immersion  
**Status:** Planned

## Week 15

### Product Build: Calendar Integration
**Status:** Planned  
**Priority:** Medium  
**Dependencies:** Google Calendar API

**Description:**  
Connect Google Calendar. Inject meeting topics into queries to prioritize relevant news.

**Acceptance Criteria:**
- [ ] Google Calendar OAuth integration
- [ ] Extract meeting titles/topics from calendar
- [ ] Use topics as keywords for news filtering
- [ ] Briefing includes "Upcoming Meetings" section
- [ ] Respects user privacy (opt-in)

**Technical Notes:**
- Add Google Calendar scope to OAuth
- Parse calendar events for next 24 hours
- Extract keywords from meeting titles
- Integrate with existing keyword filtering

**B2B Sales Pitch:**  
"We automate meeting prep for your driving reps."

---

### Product Build: Twitter/X Integration
**Status:** Planned  
**Priority:** Low  
**Dependencies:** Twitter API

**Description:**  
Build parallel ingestion for tweets from verified accounts or specific lists.

**Acceptance Criteria:**
- [ ] Twitter API integration (OAuth or API key)
- [ ] User can add Twitter accounts/lists to sources
- [ ] Tweets included in briefing analysis
- [ ] Handles rate limits gracefully

**Technical Notes:**
- Twitter API v2 requires OAuth 2.0
- Consider rate limits (300 requests per 15 min)
- May need separate processing pipeline
- Cost considerations (API pricing)

**Marketing:**  
Newsletter Sponsorships: Buy ad slots in aggregated Substacks.

---

## Week 16

### Product Build: "Tell Me More"
**Status:** Planned  
**Priority:** High  
**Dependencies:** None

**Description:**  
Interactive button triggers dedicated LLM call for a deep 3-paragraph report on one story.

**Acceptance Criteria:**
- [ ] "Tell Me More" button on each story group
- [ ] Generates 3-paragraph deep dive
- [ ] Loading state during generation
- [ ] Cached to avoid duplicate API calls
- [ ] Works on mobile

**Technical Notes:**
- New API endpoint: `/api/deep_dive`
- Takes story group ID as input
- Uses Gemini with expanded prompt
- Cache results per story group

**Upsell Campaign:**  
Market "Tell Me More" as the killer Pro Tier upgrade.

---

## Week 17

### Product Build: Continuous Presentation
**Status:** Planned  
**Priority:** Medium  
**Dependencies:** None

**Description:**  
"Playlist Mode" stitching briefings into a non-stop stream.

**Acceptance Criteria:**
- [ ] "Playlist Mode" toggle in settings
- [ ] Automatically plays next briefing when current ends
- [ ] Queue management (skip, pause, next)
- [ ] Works offline (cached briefings)

**Technical Notes:**
- Store multiple briefings in cache
- Audio player queue management
- Consider Web Audio API for seamless transitions

**Engagement Metric:**  
Track "Time Spent Listening" to validate the 24/7 channel concept.

---

## Week 18+

### Product Build: The "CNN Competitor"
**Status:** Vision  
**Priority:** Low  
**Dependencies:** Multiple APIs

**Description:**  
Livestream output (RTMP) + AI Video Anchor (HeyGen/D-ID) + Scrolling tickers.

**Acceptance Criteria:**
- [ ] RTMP stream generation
- [ ] AI video anchor with lip sync
- [ ] Scrolling news ticker
- [ ] 24/7 continuous stream
- [ ] Multiple output formats (YouTube, Twitch, etc.)

**Technical Notes:**
- Requires significant infrastructure
- Video generation APIs: HeyGen, D-ID, Synthesia
- RTMP streaming server needed
- High compute costs

**Partnerships:**  
License the "24/7 AI News Feed" to media outlets or lobbies.

---

## Phase 8 Success Criteria

- [ ] Calendar integration functional
- [ ] Twitter integration (if feasible)
- [ ] "Tell Me More" feature launched
- [ ] Playlist Mode available
- [ ] B2B sales pipeline established
- [ ] Partnership discussions initiated

## Notes

- Phase 8 focuses on enterprise and differentiation
- "Tell Me More" is highest value feature for Pro tier
- Calendar integration enables B2B sales motion
- "CNN Competitor" is long-term vision, not immediate priority
