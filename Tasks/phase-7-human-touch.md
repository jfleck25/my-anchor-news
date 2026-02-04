# Phase 7: The "Human" Touch (Weeks 13-14)

**Objective:** Capture the Commuter market (Volume Growth)  
**Theme:** Personality & Audio Quality  
**Status:** Planned

## Week 13

### Product Build: Expressive Audio ("DJ Mode")
**Status:** Planned  
**Priority:** High  
**Dependencies:** TTS API evaluation

**Description:**  
Upgrade TTS to emotional models (ElevenLabs/Google Journey). Inject "Style" variable (e.g., "High energy, morning radio").

**Acceptance Criteria:**
- [ ] New "DJ Mode" persona with expressive voice
- [ ] Voice conveys energy and personality
- [ ] SSML or API supports style injection
- [ ] User can select DJ Mode in settings

**Technical Notes:**
- Research: ElevenLabs vs. Google Journey voices
- May require API migration or additional API integration
- Consider cost implications
- See [Research/voice-apis-comparison.md](../Research/voice-apis-comparison.md)

**Marketing:**  
Short-Form Video: TikTok/Reels split screen comparing "Boring Reading" vs "My Anchor DJ Mode"

---

### Product Build: Audio Speed Ramp
**Status:** Planned  
**Priority:** Medium  
**Dependencies:** None

**Description:**  
Add 1.25x, 1.5x, 2.0x playback controls.

**Acceptance Criteria:**
- [ ] Speed control buttons in audio player
- [ ] Smooth transitions between speeds
- [ ] Speed persists during playback
- [ ] Works on mobile and desktop

**Technical Notes:**
- Use HTML5 audio `playbackRate` property
- Already partially implemented (see `playbackRate` state in Dashboard)
- Add UI controls if missing

**PLG Motion:**  
Encourage "Briefing Ben" to share with "Drive-Time Dave" friends.

---

## Week 14

### Product Build: Big Button Mode (Car View)
**Status:** Planned  
**Priority:** Medium  
**Dependencies:** None

**Description:**  
CSS update for landscape/simplified UI optimized for car use.

**Acceptance Criteria:**
- [ ] Landscape orientation support
- [ ] Large, touch-friendly buttons
- [ ] Minimal UI elements
- [ ] Auto-play option
- [ ] Works on mobile browsers

**Technical Notes:**
- Use CSS media queries for landscape detection
- Simplify UI: Hide non-essential elements
- Consider PWA for better mobile experience
- Test on actual car screens/devices

**Social Proof:**  
Share audio samples of the "DJ" voice vs. the "Analyst" voice.

---

### Product Build: Smart Audio Chunking
**Status:** Planned  
**Priority:** Low  
**Dependencies:** None

**Description:**  
Split by paragraph breaks for natural pauses instead of arbitrary byte limits.

**Acceptance Criteria:**
- [ ] Chunks break at paragraph boundaries
- [ ] Natural pauses between chunks
- [ ] No audio glitches or cuts mid-sentence
- [ ] Maintains <5000 byte limit per chunk

**Technical Notes:**
- Current chunking uses byte limits
- Parse script by paragraphs first, then chunk
- May require refactoring `generate_audio` route

---

## Phase 7 Success Criteria

- [ ] DJ Mode persona available and tested
- [ ] Audio speed controls functional
- [ ] Car View mode implemented
- [ ] Smart chunking improves audio quality
- [ ] Marketing videos created and published
- [ ] User feedback collected on audio experience

## Notes

- Focus on audio quality and personality to differentiate from competitors
- Car View mode targets "Drive-Time Dave" persona specifically
- Expressive audio is key differentiator but may require API changes
