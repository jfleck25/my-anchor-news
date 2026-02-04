# Analytics Implementation

**Date:** February 4, 2026  
**Status:** In Progress  
**Tool:** PostHog (free tier)

## Overview

Analytics tracking is critical for measuring success metrics and optimizing the product. We're using PostHog for its generous free tier and privacy-friendly approach.

## Events to Track

### User Actions
- `briefing_generated` - User clicks "Refresh" and briefing is created
- `audio_played` - User clicks "Play Briefing"
- `audio_completed` - User listens to full briefing
- `copy_summary_clicked` - User copies executive summary
- `share_clicked` - User shares briefing link
- `settings_updated` - User saves settings changes

### User Properties
- `personality` - Selected persona (anchor, analyst, dj)
- `source_count` - Number of sources configured
- `has_keywords` - Whether watchlist keywords are set
- `has_priority_sources` - Whether priority sources are configured

### Performance Metrics
- `briefing_generation_time` - Time to generate briefing (ms)
- `audio_generation_time` - Time to generate audio (ms)
- `cache_hit` - Whether briefing came from cache

## Implementation

### Frontend (index.html)
PostHog script added to `<head>` section. Events tracked via `posthog.capture()`.

### Backend (main.py)
- Track API response times
- Log cache hits/misses
- Monitor error rates

## Dashboard

Key metrics to monitor:
1. Daily Active Users (DAU)
2. Briefings Generated per Day
3. Audio Playback Completion Rate
4. Average Session Duration
5. Settings Update Frequency
6. Share Rate

## Privacy

- PostHog is GDPR compliant
- No PII (personally identifiable information) tracked
- User emails not tracked
- IP addresses anonymized

## Next Steps

- [x] Add PostHog script to index.html
- [x] Implement event tracking for key actions
- [ ] Create PostHog dashboard
- [ ] Set up weekly metrics review
- [ ] Add error tracking integration
