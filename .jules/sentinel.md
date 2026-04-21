## 2025-04-21 - Fix Rate Limiting Missing on Endpoints and Input Validation
**Vulnerability:** The `/api/generate_audio` and `/api/share` endpoints lacked rate limiting entirely despite performing heavy resource operations, and `/api/generate_audio` lacked input type validation.
**Learning:** Endpoints generating content or managing database insertions must always include input validation (`isinstance`) and resource protection (`@limiter.limit`) to avoid financial exhaustion (LLM APIs) and data insertion crashes.
**Prevention:** Apply `@limiter.limit` explicitly to endpoints touching external APIs and DBs and validate JSON structs before accessing dictionary keys.
