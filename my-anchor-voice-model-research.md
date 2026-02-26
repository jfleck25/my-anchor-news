# My Anchor - Voice Model Research & Upgrade

**Goal:** News Anchor project - improve voice quality for audio briefings

## Decision (Feb 2026)
**Sticking with Google TTS** for now. No provider switch planned. Next step: **review other Google voice profiles** (different names/locales within Google TTS) to improve quality without changing APIs.

## Current Setup

**TTS Provider:** Google Text-to-Speech
**Voices:** 3 personality options
**Quality:** Good but could be better (from task: "want to make voice higher quality")

## Voice Quality Evaluation

**What to assess:**
- [ ] Listen to current voices - what sounds robotic or unnatural?
- [ ] Get user feedback: do beta users complain about voice quality?
- [ ] Specific issues: pronunciation, pacing, emotion, naturalness?
- [ ] Is it "good enough" or is it a blocker for daily use?

## Voice Model Options

### Option 1: Google Text-to-Speech (Current)

**Pros:**
- Already integrated
- Multiple voices available
- Reliable, fast
- WaveNet voices are decent quality

**Cons:**
- Can sound robotic for long-form content
- Limited emotional range
- Not as natural as cutting-edge options

**Pricing:** ~$4 per 1M characters (WaveNet voices)

---

### Option 2: ElevenLabs ⭐ (Premium option)

**Pros:**
- Best-in-class naturalness
- Emotion and intonation (sounds like real person)
- Voice cloning (could create custom "anchor" voices)
- Multiple languages
- Highly rated for long-form content

**Cons:**
- More expensive than Google
- Need to integrate new API
- Usage limits on free tier

**Pricing:** 
- Free: 10,000 chars/month
- Starter: $5/month for 30,000 chars
- Creator: $22/month for 100,000 chars
- Pro: $99/month for 500,000 chars

**Estimate:** Average briefing = ~2,000 words = ~10,000 characters
- 3 briefings/user/day = 30,000 chars/user/day
- Would need Pro tier for even small user base

---

### Option 3: OpenAI Text-to-Speech

**Pros:**
- Very natural-sounding (HD voices)
- Fast generation
- Part of OpenAI ecosystem (if using GPT models)
- Good pricing

**Cons:**
- Limited voice options (6 voices)
- Less control than ElevenLabs

**Pricing:** 
- Standard: $15 per 1M characters
- HD voices: $30 per 1M characters

**Estimate:** 
- 10,000 chars per briefing × 3 per user per day = 30,000 chars/user/day
- HD voices: $0.90/user/month
- More expensive than Google, cheaper than ElevenLabs

---

### Option 4: Play.ht

**Pros:**
- Ultra-realistic voices
- Voice cloning
- Good for conversational content
- Competitive pricing

**Cons:**
- Less well-known than ElevenLabs
- Need to test quality

**Pricing:** Similar to ElevenLabs (~$30-100/month for meaningful volume)

---

### Option 5: Amazon Polly

**Pros:**
- Cheap
- Neural voices available
- Reliable (AWS infrastructure)
- Easy to integrate

**Cons:**
- Quality not as good as ElevenLabs/OpenAI
- Similar to Google TTS

**Pricing:** $4 per 1M characters (Neural voices)

---

## Decision Framework

### If Quality is Priority #1:
→ **ElevenLabs** or **OpenAI HD**
- Use for premium tier ($20/month users)
- Justify higher cost with higher subscription price

### If Cost is Priority #1:
→ **Stay with Google** or **Amazon Polly**
- Use for free tier
- Good enough for most users

### If Balance of Both:
→ **OpenAI TTS (HD)** 
- Better than Google, cheaper than ElevenLabs
- $0.90/user/month is sustainable at $15-20/month pricing

## Tiered Strategy (Recommended)

**Free Tier:**
- Google TTS (current) or Amazon Polly
- Standard quality
- Cost: ~$0.12/user/month

**Premium Tier ($15-20/month):**
- ElevenLabs or OpenAI HD
- Best quality, most natural
- Cost: $0.90-3.00/user/month
- Still profitable with margin

## Testing Plan

- [ ] **Week 1:** Sign up for ElevenLabs trial + OpenAI API
- [ ] **Test:** Generate same 5 briefings with:
  - Current Google TTS
  - OpenAI HD voices
  - ElevenLabs
- [ ] **Compare:** Naturalness, pacing, pronunciation, emotion
- [ ] **Beta user test:** Send 3 versions to 5 users, ask which they prefer (blind)
- [ ] **Calculate costs:** Based on actual character counts

## Implementation Considerations

**If switching:**
- [ ] New API integration (2-4 hours of dev work)
- [ ] Update environment variables
- [ ] Test end-to-end
- [ ] Fallback plan if API fails? (keep Google as backup?)

**If offering multiple options:**
- [ ] Add voice model selector to settings
- [ ] Track which users prefer which voices
- [ ] Could be a good premium differentiator

## Success Criteria

**Voice quality is good enough if:**
- Beta users listen to full briefings (not stopping partway)
- Positive feedback on voice quality
- Users say they'd use it daily
- NPS/feedback doesn't mention voice as a problem

**Voice quality needs upgrade if:**
- Users complain it sounds robotic
- Low engagement with audio feature
- Users prefer reading text export instead

## Next Steps

1. [ ] Get beta user feedback on current voice quality
2. [ ] If feedback is negative, test ElevenLabs + OpenAI
3. [ ] Calculate actual cost per user with test data
4. [ ] Make decision: upgrade for all, or tier by subscription?
5. [ ] Implement chosen solution
