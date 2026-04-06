## 2024-05-30 - Fix overly permissive CORS configuration
**Vulnerability:** The application defaulted to allowing all origins (`CORS(app)`) when the `ALLOWED_ORIGINS` environment variable was missing, enabling any site to interact with the backend API.
**Learning:** Defaulting to a wide-open CORS configuration (`*`) when an environment variable isn't present introduces a significant Cross-Origin Resource Sharing vulnerability, especially dangerous given that the API handles authenticated requests.
**Prevention:** Always default to restrictive (e.g., empty or localhost-only) origins if external configuration is absent, explicitly enabling permissive rules only when expressly specified via configuration, and configure different logic for development and production environments.

## 2026-04-06 - Sensitive Information Exposure in Global Error Handler
**Vulnerability:** The global 500 error handler exposed truncated tracebacks in the `details` field of the JSON response when `DEBUG` was enabled, which could lead to path disclosure and logic inference.
**Learning:** Even in development or debug modes, exposing raw tracebacks in API responses is risky as it can reveal sensitive system details to unauthorized users.
**Prevention:** Hardcode error details to `None` or a generic message in the final response. Use server-side logging or dedicated error tracking tools (like Sentry) for debugging instead of exposing details to the client.
