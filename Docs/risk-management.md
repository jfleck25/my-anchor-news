# Risk Management

**Date:** January 20, 2026  
**Status:** Active monitoring

## Risk Categories & Mitigation

### Financial Risks

#### Risk: API Costs Exceed Subscription Revenue
**Description:**  
Gemini and TTS API costs could exceed $20/month subscription revenue if users generate many briefings.

**Mitigation Strategy:**
- Strict caching (15m TTL) reduces API calls by ~90%
- Rate limiting on "Fetch" button (prevent spam clicks)
- Force "Free" users to lower-cost models (if implemented)
- Monitor API usage per user
- Set usage caps for free tier (3 briefings/day)

**Cost Calculation:**
```
Per Briefing Costs:
- Gemini 2.5 Flash Lite: $0.075 per 1M input tokens
  - Average briefing: ~50k tokens = $0.00375 per briefing
- Google Cloud TTS: $16 per 1M characters
  - Average briefing: ~5k characters = $0.08 per briefing
- Total per briefing: ~$0.084

Monthly Costs (without cache):
- 30 briefings/month = $2.52/user
- 60 briefings/month = $5.04/user

With 15m cache (90% hit rate):
- 30 briefings: 3 API calls = $0.25/user/month
- 60 briefings: 6 API calls = $0.50/user/month

Break-even Analysis:
- Pro tier: $20/month
- API cost: $0.25-0.50/month (with cache)
- Margin: 98.75%+ (excellent)
```

**Monitoring:**
- Track API costs vs. MRR monthly
- Alert if cost per user exceeds $2/month (indicates cache issues)
- Monitor cache hit rates (target: 80%+)

---

### Retention Risks

#### Risk: Users Try It Once and Forget to Return
**Description:**  
Users may generate one briefing, forget about the product, and never return.

**Mitigation Strategy:**
- Push Notifications (via PWA) at 7:30 AM: "Your briefing is ready. 3 Red Flags detected."
- Email reminders for inactive users
- "Briefing of the Day" feature to encourage daily use
- Social sharing incentives

**Monitoring:**
- Track Day 1 → Day 7 retention
- Track weekly active users (WAU)
- Monitor churn rate

---

### Technical Risks

#### Risk: AI Hallucinations (Making Up Facts)
**Description:**  
LLM may generate false information or make up quotes that don't exist in source material.

**Mitigation Strategy:**
- Maintain "Strict Constraints" prompt emphasizing fact-based extraction
- Add "Source Citations" (e.g., "According to WSJ...")
- Implement fact-checking layer (future)
- User feedback loop to flag inaccuracies

**Monitoring:**
- Track user-reported accuracy issues
- Review sample outputs weekly
- Compare LLM output to source material

---

### Platform Risks

#### Risk: Google Blocks Gmail API Access Due to Volume
**Description:**  
High API usage could trigger Google's rate limits or security reviews.

**Mitigation Strategy:**
- This uses the User's Gmail quota, not ours. As long as users authenticate their own accounts, this scales.
- Each user has their own OAuth token
- Respect Gmail API rate limits (250 quota units per user per second)
- Implement exponential backoff for rate limit errors

**Monitoring:**
- Track Gmail API error rates
- Monitor quota usage per user
- Alert on rate limit errors

---

### Competitive Risks

#### Risk: Competitors Launch Similar Products
**Description:**  
Large tech companies or well-funded startups may launch competing products.

**Mitigation Strategy:**
- Focus on niche (Finance/Strategy) for defensibility
- Build deep integrations (Calendar, Twitter) for switching costs
- Emphasize "Deep Analysis" vs. generic summaries
- Build brand and user loyalty

---

### Data Privacy Risks

#### Risk: User Data Breach or Privacy Violations
**Description:**  
Gmail access and user settings could be compromised.

**Mitigation Strategy:**
- OAuth tokens stored securely in session (not database)
- PostgreSQL connection encrypted
- No storage of email content (only processed summaries)
- GDPR compliance considerations
- Clear privacy policy

**Monitoring:**
- Security audits quarterly
- Monitor for suspicious access patterns
- Regular dependency updates

---

## Risk Monitoring Dashboard

**Metrics to Track:**
- API costs per user
- User retention (D1, D7, D30)
- Error rates (by type)
- Gmail API quota usage
- User-reported issues

**Review Frequency:**  
Weekly risk review, monthly deep dive
