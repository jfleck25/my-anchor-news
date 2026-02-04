# Current Architecture & Capabilities

**Date:** January 20, 2026  
**Status:** Production-ready v1 deployed on Render.com

## Technical Stack

### Frontend
- **Framework:** Single-file React 18 app (Babel standalone)
- **Styling:** Tailwind CSS
- **Features:**
  - Google Auth integration
  - Settings Modal
  - Audio Player with playback controls
  - "Deep Dive" Insight Cards
  - Red Flag Toggle (UI Only - backend ready)
  - Dark Mode support

### Backend
- **Framework:** Flask (Python 3.10)
- **Server:** Gunicorn/Docker
- **Deployment:** Render.com
- **Environment:** Secure environment variables

### Data Ingestion
- **API:** Gmail API
- **Query System:** Dynamic queries based on user-defined sources & time windows
- **Processing:** BeautifulSoup for HTML parsing, sanitization for LLM input

### Intelligence Layer
- **Model:** Gemini 2.5 Flash Lite
- **Approach:** "Deep Analysis" prompt to extract specific facts/quotes
- **Filtering:** Removes ads and fluff automatically
- **Output:** Structured JSON with story groups and remaining stories

### Audio Generation
- **Service:** Google Cloud Text-to-Speech
- **Implementation:** Chunking logic (<5000 bytes) for seamless long-form audio
- **Personas:** Multiple voice options (Anchor, Analyst, DJ)
- **Features:** SSML support, speaking rate, pitch control

### Performance Optimization
- **Caching:** Local JSON caching (cache.json)
- **Impact:** Reduces API latency from ~45s to <1s for repeated requests
- **TTL:** 15 minutes
- **Cache Keys:** Settings hash + timestamp

### Persistence
- **Database:** PostgreSQL (via Render)
- **Tables:**
  - `user_settings` - User preferences (sources, keywords, personality)
  - `shared_briefings` - Public share links with UUID

## Completed Milestones (Weeks 1-9)

✅ **Core Pipeline:** End-to-end Fetch -> Clean -> Analyze -> Speak flow is operational  
✅ **Stability:** "Gauntlet" tested. Handles Empty Inboxes and Data Overload (50+ emails) without crashing  
✅ **Cloud Deployment:** Fully dockerized and running live on Render with secure environment variables  
✅ **Auth Solved:** Overcame strict Google Cloud permissions (gRPC vs REST) to allow seamless login and audio generation  
✅ **Infrastructure:** Migrated settings to Cloud Database (PostgreSQL)  
✅ **UI Overhaul:** Implemented "High Fidelity" Newsroom aesthetic and Dark Mode  
✅ **Social Sharing:** Added public share links for briefings

## Architecture Decisions

### Single-File React App
- **Decision:** Use Babel standalone instead of build pipeline
- **Rationale:** Faster iteration, simpler deployment, no build step
- **Trade-off:** Less optimal performance, but acceptable for MVP

### Local JSON Caching
- **Decision:** File-based cache instead of Redis/Memcached
- **Rationale:** Simpler infrastructure, sufficient for MVP scale
- **Trade-off:** Not distributed, but works for single-instance deployment

### Google Cloud Integration
- **Decision:** Use Google APIs (Gmail, Gemini, TTS) instead of multi-vendor
- **Rationale:** Unified auth, better integration, single vendor relationship
- **Trade-off:** Vendor lock-in, but simplifies development

## API Endpoints

See [api-design.md](./api-design.md) for detailed endpoint documentation.

## Environment Variables

- `FLASK_SECRET_KEY` - Session encryption
- `GOOGLE_API_KEY` - Gemini API access
- `GOOGLE_CLIENT_SECRETS_JSON` - OAuth credentials
- `DATABASE_URL` - PostgreSQL connection string
- `GOOGLE_CLOUD_PROJECT` - GCP project ID
- `PORT` - Server port (default: 5000)
