# My Anchor - Product Vision & Goals

## Product Vision

My Anchor transforms your daily newsletter inbox into concise, voice-powered briefings tailored to your interests and schedule. We provide **signal, not noise**—extracting specific facts, quotes, and insights rather than generic summaries.

**Long-term Vision:** Become the trusted AI news analyst for professionals who need deep insights, not surface-level summaries. Evolve from a briefing tool into a 24/7 personalized news channel.

## Core Value Proposition

**What makes My Anchor unique:**

1. **Deep Analysis, Not Summaries:** Extracts specific facts/quotes and filters ads/fluff automatically
2. **Risk Detection:** Red Flag Mode identifies high-impact stories for finance/strategy professionals
3. **One-Click Efficiency:** Generate executive summaries for team communication in seconds
4. **Personalized Intelligence:** User-defined sources, keywords, and priority weighting
5. **Seamless Audio Experience:** High-quality TTS with multiple persona options (Professional, Fast, Casual)

## Target Milestones

### Phase 1: MVP ✅
- [x] Gmail integration
- [x] Newsletter analysis with Gemini AI
- [x] Text-to-speech audio generation
- [x] Multiple persona options (Anchor, Analyst, DJ)
- [x] Source prioritization
- [x] Keyword watchlist filtering
- [x] Shareable briefings

### Phase 2: Enhancement
- [ ] *[Add your next milestones]*
- [ ] 
- [ ] 

### Phase 3: Scale
- [ ] *[Future goals]*
- [ ] 
- [ ] 

## Success Metrics

### User Engagement
- **Daily Active Users:** Target 50 by end of Phase 6 (baseline: 0)
- **Briefings Generated per Week:** Target 200/week (10 active users × 20 briefings)
- **Average Session Duration:** Target 5+ minutes
- **Audio Playback Completion Rate:** Target 70% (baseline: unknown)
- **Time Spent Listening:** Target 30+ min/week per user (validates 24/7 channel concept)

### Product Quality
- **User Satisfaction Score:** Target 4.5/5.0 (NPS-style survey)
- **Briefing Accuracy/Helpfulness Rating:** Target 90% "helpful" responses
- **Source Coverage Diversity:** Track number of unique sources per user
- **Red Flag Detection Accuracy:** Target 85% true positive rate (for finance users)

### Technical Performance
- **API Response Times:** Target <1s with cache, ~45s without (current: meeting target)
- **Audio Generation Latency:** Target <30s for 5-minute briefing
- **Error Rates:** Target <1% of requests
- **Cache Hit Rates:** Target 80%+ (15m TTL)
- **LLM JSON Generation Success Rate:** Target 95%+ (handles 50+ emails)

### Commercial Metrics
- **Free-to-Pro Conversion Rate:** Target 10% (industry avg: 2-5%)
- **Monthly Recurring Revenue (MRR):** Target $200 by end of Phase 6 (10 Pro users)
- **Customer Acquisition Cost (CAC):** Target <$50 (organic + paid)
- **Lifetime Value (LTV):** Target $240+ (12-month retention × $20/mo)
- **API Cost per User:** Target <$2/month (with caching)

## Key Decisions & Trade-offs

### Strategic Pivot
- **Decision:** Shift from "Engineering Mode" to "Product-Led Growth"
- **Rationale:** Focus on specific user value (Finance/Strategy) rather than mass-market appeal
- **Trade-off:** Narrower initial market, but higher willingness-to-pay

### Target Audience Prioritization
- **Primary:** "Briefing Ben" (Finance/Strategy) - High income ($150k+), needs risk detection
- **Secondary:** "Drive-Time Dave" (Commuters) - Volume growth, entertainment focus
- **Tertiary:** "Political Pam" (Niche) - High news volume, keyword tracking

### Technical Architecture
- **Decision:** Single-file React app (Babel standalone) vs. build pipeline
- **Rationale:** Faster iteration, simpler deployment
- **Trade-off:** Less optimal performance, but acceptable for MVP

### Caching Strategy
- **Decision:** 15-minute TTL with local JSON cache
- **Rationale:** Reduces API costs and latency dramatically
- **Trade-off:** Stale data risk, but acceptable for news briefings

### API Selection
- **Decision:** Google Cloud TTS (current) vs. alternatives (ElevenLabs, AWS Polly)
- **Rationale:** Integrated with existing Google auth, high quality
- **Trade-off:** Cost per character, but manageable with caching
