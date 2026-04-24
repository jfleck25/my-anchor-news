# Design System — My Anchor

## Product Context
- **What this is:** A personalized AI-powered daily news briefing application that filters newsletter noise into trusted intelligence.
- **Who it's for:** Knowledge workers, news junkies, and busy professionals who subscribe to 5+ high-signal newsletters.
- **Space/industry:** AI-Aggregator / News & Editorial.
- **Project type:** Web App (Flask/Python).

## Aesthetic Direction
- **Direction:** Editorial/Industrial Hybrid — Combines the high-end typography of a magazine with the utilitarian clarity of a data terminal.
- **Decoration level:** Intentional — Subtle grain texture on backgrounds to feel "analog"; clean lines and minimal chrome.
- **Mood:** Trusted, clear, and efficient. It feels like an authoritative intelligence feed, not a generic news aggregator.

## Typography
- **Display/Hero:** Instrument Serif — Used for headlines and consensus summaries. Feels premium and literary.
- **Body:** Geist — Used for UI elements and general reading. Provides maximum clarity.
- **UI/Labels:** Geist — Clean and legible at small sizes.
- **Data/Tables:** Geist Mono — Used for source timestamps, metadata, and "Perspective Split" labels to signal "raw intelligence."
- **Code:** Geist Mono.
- **Loading:** Loaded from Google Fonts (Instrument Serif, Geist, Geist Mono).
- **Scale:** Modular scale (Base 16px).
  - H1: 2.5rem
  - H2: 2rem
  - H3: 1.5rem
  - Body: 1rem
  - Small: 0.875rem
  - Detail: 0.75rem (Mono)

## Color
- **Approach:** Balanced/Trust-First — Calm neutral slates for the primary surface, with high-visibility Amber for identifying dissent.
- **Primary:** #0F172A (Slate 900) — Used for primary text and high-contrast UI elements.
- **Background:** #F8FAFC (Slate 50) — Main surface color to reduce eye strain.
- **Accent:** #F59E0B (Amber 500) — Used for "The Perspective Split" and signaling where sources differ.
- **Semantic:** 
  - Success: #10B981 (Emerald 500)
  - Warning: #F59E0B (Amber 500)
  - Error: #F43F5E (Rose 500)
  - Info: #3B82F6 (Blue 500)
- **Dark mode:** Redesign surfaces using Slate 950/900; reduce accent saturation by 10%.

## Spacing
- **Base unit:** 8px.
- **Density:** Comfortable — Generous whitespace to combat "inbox fatigue."
- **Scale:** 2xs(4) xs(8) sm(12) md(16) lg(24) xl(32) 2xl(48) 3xl(64).

## Layout
- **Approach:** Stream/Feed with Side-by-Side Splits — Optimized for scanning "Consensus vs. Dissent."
- **Grid:** 12-column grid on desktop; single-column stream on mobile.
- **Max content width:** 900px (optimized for reading line length).
- **Border radius:** Hierarchical scale:
  - sm: 4px (inputs, small buttons)
  - md: 8px (cards, UI components)
  - lg: 12px (major containers)

## Motion
- **Approach:** Minimal-Functional — Transitions should aid comprehension of the "Model Council" pipeline steps.
- **Easing:** enter(ease-out), exit(ease-in), move(ease-in-out).
- **Duration:** short(200ms) for UI feedback; medium(350ms) for layout transitions.

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-23 | Initial design system created | Created by /design-consultation focusing on "Trusted Intelligence Feed" direction. |
| 2026-04-23 | Amber Split Accent | Chosen to signal "Caution/Analysis" for source contradictions, avoiding generic blue/red. |
| 2026-04-23 | Industrial Metadata (Mono) | Using Geist Mono for source labels signals "raw transparency" and trust. |
